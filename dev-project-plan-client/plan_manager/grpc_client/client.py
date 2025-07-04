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
            self.channel = grpc.insecure_channel(self.server_address)
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
                    if not self.channel or self.channel._channel.check_connectivity_state(False) != 2:  # 2 = READY
                        self._connect()

                # Import protobuf modules
                from . import helper_pb2

                if method_name == "PlanGetRequest":
                    request = helper_pb2.PlanGetRequest(
                        prompt=request_data.get('prompt', ''),
                        env_config=request_data.get('env_config', '')
                    )
                    stream = self.stub.GetPlan(request)
                elif method_name == "PlanExecuteRequest":
                    request = helper_pb2.PlanExecuteRequest(
                        prompt=request_data.get('prompt', ''),
                        env_config=request_data.get('env_config', '')
                    )
                    stream = self.stub.RunPlan(request)
                elif method_name == "PlanThenExecuteRequest":
                    request = helper_pb2.PlanThenExecuteRequest(
                        prompt=request_data.get('prompt', ''),
                        env_config=request_data.get('env_config', '')
                    )
                    stream = self.stub.GetPlanThenRun(request)
                else:
                    raise ValueError(f"Unknown gRPC method: {method_name}")

                self._handle_stream_response(stream, callback)
                return

            except grpc.RpcError as e:
                if attempt == self.retry_config['retry_max_count']:
                    callback({
                        'error': f"gRPC request failed after {attempt + 1} attempts: {str(e)}",
                        'status': 'failed'
                    })
                    return

                wait_time = self.retry_config['retry_wait_seconds']
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)

    def _handle_stream_response(self, stream, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Handle streaming response from gRPC server"""
        try:
            for response in stream:
                callback({
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
                })
        except grpc.RpcError as e:
            callback({
                'error': str(e),
                'status': 'failed'
            })

    def format_prompt(self, template: str, doc_content: str, env_config: str) -> str:
        """Format prompt template with document content and environment config"""
        return template.replace("{doc}", doc_content).replace("{env}", env_config)