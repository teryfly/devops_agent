import grpc
from concurrent import futures
from ai_project_helper.server.service import AIProjectHelperServicer
from ai_project_helper.proto import helper_pb2_grpc
from ai_project_helper.config import load_config
from ai_project_helper.log_config import setup_logging, get_logger

def serve():
    setup_logging()
    logger = get_logger("server.main")
    config = load_config()
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helper_pb2_grpc.add_AIProjectHelperServicer_to_server(
        AIProjectHelperServicer(config), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("服务启动，端口 [::]:50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
