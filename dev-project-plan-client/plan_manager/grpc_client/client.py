import grpc
import threading
import time
import logging
from typing import Callable, Dict, Any
from config import ConfigManager

logger = logging.getLogger(__name__)

class GrpcClient:
    def __init__(self, server_address: str, llm_model: str = None, llm_url: str = None):
        self.server_address = server_address
        self.channel = None
        self.stub = None
        self.lock = threading.Lock()
        self.llm_model = llm_model
        self.llm_url = llm_url
        self._connect()
        config = ConfigManager()
        self.retry_config = config.get_retry_config()

    def _connect(self):
        """Establish gRPC connection"""
        try:
            options = [
                ('grpc.keepalive_time_ms', 120000),
             ('grpc.keepalive_timeout_ms', 3600000),
                ('grpc.keepalive_permit_without_calls', 0),
                ('grpc.http2.max_pings_without_data', 0),
            ]
            self.channel = grpc.insecure_channel(self.server_address, options=options)
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
                    if not self._is_channel_ready():
                        logger.info(f"Re-establishing connection to {self.server_address}")
                        self._connect()

                from . import helper_pb2

                # 合并 LLM 参数
                if self.llm_model and not request_data.get('model'):
                    request_data['model'] = self.llm_model
                if self.llm_url and not request_data.get('llm_url'):
                    request_data['llm_url'] = self.llm_url

                request, stream = self._create_request_and_stream(method_name, request_data, helper_pb2)

                # *** 这里: 每收到一条流消息都立即回调UI ***
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
        try:
            if not self.channel:
                return False
            state = self.channel._channel.check_connectivity_state(False)
            return state == grpc.ChannelConnectivity.READY
        except:
            return False

    def _create_request_and_stream(self, method_name: str, request_data: Dict[str, Any], helper_pb2):
        if method_name == "PlanGetRequest":
            request = helper_pb2.PlanGetRequest(
                requirement=request_data.get('prompt', ''),
                model=request_data.get('model', ''),
                llm_url=request_data.get('llm_url', '')
            )
            stream = self.stub.GetPlan(request, timeout=30000)
        elif method_name == "PlanExecuteRequest":
            request = helper_pb2.PlanExecuteRequest(
                plan_text=request_data.get('prompt', ''),
                project_id=request_data.get('project_id', '')
            )
            stream = self.stub.RunPlan(request, timeout=60000)
        elif method_name == "PlanThenExecuteRequest":
            request = helper_pb2.PlanThenExecuteRequest(
                requirement=request_data.get('prompt', ''),
                model=request_data.get('model', ''),
                llm_url=request_data.get('llm_url', ''),
                project_id=request_data.get('project_id', '')
            )
            stream = self.stub.GetPlanThenRun(request, timeout=90000)
        else:
            raise ValueError(f"Unknown gRPC method: {method_name}")

        return request, stream

    def _handle_stream_response(self, stream, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Handle streaming response from gRPC server"""
        try:
            for response in stream:
                # *** 不管是进度、状态、plan，都立即推给callback/UI ***
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
                feedback_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
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
        try:
            with self.lock:
                if not self._is_channel_ready():
                    self._connect()
                try:
                    grpc.channel_ready_future(self.channel).result(timeout=9.0)
                    return True
                except grpc.FutureTimeoutError:
                    logger.warning("gRPC connection test timed out")
                    return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def format_prompt(self, template: str, doc_content: str, env_config: str) -> str:
        return template.replace('{doc}', doc_content).replace('{env}', env_config)

    def close(self):
        try:
            if self.channel:
                self.channel.close()
                logger.info("gRPC connection closed")
        except Exception as e:
            logger.error(f"Error closing gRPC connection: {e}")