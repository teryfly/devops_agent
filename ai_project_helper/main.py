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
    
    # 修正的 keepalive 选项配置
    options = [
        ('grpc.keepalive_time_ms', 30000),          # 30秒发送一次keepalive
        ('grpc.keepalive_timeout_ms', 120000),       # 120秒超时
        ('grpc.keepalive_permit_without_calls', 1), # 允许无调用时发送keepalive
        ('grpc.http2.max_pings_without_data', 0),   # 允许无数据时的ping
    ]
    
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=options  # 添加这行
    )
    
    helper_pb2_grpc.add_AIProjectHelperServicer_to_server(
        AIProjectHelperServicer(config), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("服务启动，端口 [::]:50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()