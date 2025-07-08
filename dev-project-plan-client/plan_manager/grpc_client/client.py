import grpc
import threading
import time
import logging
from typing import Callable, Dict, Any
from config import ConfigManager

logger = logging.getLogger(__name__)

class GrpcClient:
    def __init__(self, server_address: str):
        self.server_address = server_address
        self.channel = None
        self.stub = None
        self.lock = threading.Lock()
        self._connect()
        config = ConfigManager()
        self.retry_config = config.get_retry_config()

    def _connect(self):
        """Establish gRPC connection"""
        try:
            # Add connection timeout
            options = [
                ('grpc.keepalive_time_ms', 10000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.http2.min_ping_interval_without_data_ms', 300000)
            ]
            
            self.channel = grpc.insecure_channel(self.server_address, options=options)
            
            # Import generated protobuf modules
            from . import helper_pb2, helper_pb2_grpc
            self.stub = helper_pb2_grpc.AIProjectHelperStub(self.channel)
            logger.info(f"gRPC client connected to {self.server_address}")
        except Exception as e:
            logger.error(f"gRPC connection failed: {str(e)}")
            raise

    def send_request(self, method_name: str, request_data: Dict[str, Any],
                    callback: Callable[[Dict[str, Any]], None]) -> None:
        """Send gRPC request with retry logic"""
        for attempt in range(self.retry_config['retry_max_count'] + 1):
            try:
                with self.lock:
                    # Check and re-establish connection if needed
                    if not self._is_channel_ready():
                        logger.info(f"Re-establishing connection to {self.server_address}")
                        self._connect()

                # Import protobuf modules
                from . import helper_pb2

                # Create request and get stream based on method type
                request, stream = self._create_request_and_stream(method_name, request_data, helper_pb2)
                
                # Handle stream response
                self._handle_stream_response(stream, callback)
                return

            except grpc.RpcError as e:
                error_code = e.code()
                error_details = e.details()
                
                logger.error(f"gRPC error on attempt {attempt + 1}: {error_code} - {error_details}")
                
                if attempt == self.retry_config['retry_max_count']:
                    callback({
                        'error': f"gRPC request failed after {attempt + 1} attempts: {error_details}",
                        'status': 'failed',
                        'error_code': error_code.name if error_code else 'UNKNOWN'
                    })
                    return

                # Wait before retry
                wait_time = self.retry_config['retry_wait_seconds']
                logger.warning(f"Retrying in {wait_time}s... (attempt {attempt + 1}/{self.retry_config['retry_max_count']})")
                time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Unexpected error in gRPC request: {e}")
                callback({
                    'error': f"Unexpected error: {str(e)}",
                    'status': 'failed'
                })
                return

    def _is_channel_ready(self):
        """Check if channel is ready"""
        try:
            if not self.channel:
                return False
            
            state = self.channel._channel.check_connectivity_state(False)
            return state == grpc.ChannelConnectivity.READY
        except:
            return False

    def _create_request_and_stream(self, method_name: str, request_data: Dict[str, Any], helper_pb2):
        """Create request and get stream based on method name"""
        if method_name == "PlanGetRequest":
            request = helper_pb2.PlanGetRequest(
                requirement=request_data.get('prompt', ''),
                model=request_data.get('model', 'default'),
                llm_url=request_data.get('llm_url', '')
            )
            stream = self.stub.GetPlan(request, timeout=300)  # 5 minute timeout
            
        elif method_name == "PlanExecuteRequest":
            request = helper_pb2.PlanExecuteRequest(
                plan_text=request_data.get('prompt', ''),
                project_id=request_data.get('project_id', '')
            )
            stream = self.stub.RunPlan(request, timeout=600)  # 10 minute timeout
            
        elif method_name == "PlanThenExecuteRequest":
            request = helper_pb2.PlanThenExecuteRequest(
                requirement=request_data.get('prompt', ''),
                model=request_data.get('model', 'default'),
                llm_url=request_data.get('llm_url', ''),
                project_id=request_data.get('project_id', '')
            )
            stream = self.stub.GetPlanThenRun(request, timeout=900)  # 15 minute timeout
            
        else:
            raise ValueError(f"Unknown gRPC method: {method_name}")
        
        return request, stream

    def _handle_stream_response(self, stream, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Handle streaming response from gRPC server"""
        try:
            for response in stream:
                # Convert protobuf response to dictionary
                feedback_dict = {
                    'action_index': response.action_index,
                    'action_type': response.action_type,
                    'step_description': response.step_description,
                    'status': response.status,
                    'output': response.output,
                    'error': response.error,
                    'command': response.command,
                    'step_index': response.step_index,
                    'total_steps': response.total_steps,
                    'exit_code': response.exit_code,
                    'complete_plan': response.complete_plan
                }
                
                # Add timestamp for logging
                feedback_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Call callback with feedback
                callback(feedback_dict)
                
        except grpc.RpcError as e:
            error_code = e.code()
            error_details = e.details()
            logger.error(f"Stream response error: {error_code} - {error_details}")
            callback({
                'error': f"Stream error: {error_details}",
                'status': 'failed',
                'error_code': error_code.name if error_code else 'UNKNOWN',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            logger.error(f"Unexpected stream error: {e}")
            callback({
                'error': f"Unexpected stream error: {str(e)}",
                'status': 'failed',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })

    def test_connection(self) -> bool:
        """Test gRPC connection with timeout"""
        try:
            with self.lock:
                # Try to establish connection if not already connected
                if not self._is_channel_ready():
                    self._connect()
                
                # Test with a quick connectivity check
                try:
                    # Wait for channel to be ready with timeout
                    grpc.channel_ready_future(self.channel).result(timeout=5.0)
                    return True
                except grpc.FutureTimeoutError:
                    logger.warning("gRPC connection test timed out")
                    return False
                    
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def format_prompt(self, template: str, doc_content: str, env_config: str) -> str:
        """Format prompt template with document content and environment config"""
        return template.replace('{doc}', doc_content).replace('{env}', env_config)

    def close(self):
        """Close gRPC connection"""
        try:
            if self.channel:
                self.channel.close()
                logger.info("gRPC connection closed")
        except Exception as e:
            logger.error(f"Error closing gRPC connection: {e}")