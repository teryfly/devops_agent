# server.py
import grpc
from concurrent import futures

from ai_project_helper.proto import helper_pb2, helper_pb2_grpc
from ai_project_helper.core.agent import Agent
from ai_project_helper.config import load_config
from ai_project_helper.log_config import setup_logging, get_logger

# 初始化日志
setup_logging()
logger = get_logger("server")

class AIProjectHelperServicer(helper_pb2_grpc.AIProjectHelperServicer):
    def __init__(self, config):
        self.agent = Agent(config)
        self.logger = get_logger("server.servicer")
    def RunPlan(self, request, context):
        """
        gRPC流式接口：接收用户输入的plan_text，解析为actions，逐步执行actions并实时yield反馈
        """
        plan_text = request.plan_text
        logger.info(f"==================接收到客户端请求==================：\n{plan_text[:88]}...\n =============================================================================================================")

        # 1. 构建出 LLM Prompt 并打印
        try:
            # 获取 LLM 请求内容（如有 build_prompt，推荐直接调用）
            prompt = self.agent.llm.build_prompt(plan_text)
        except Exception:
            prompt = None

        # 2. 解析 action 及执行
        try:
            actions = self.agent.parse_plan(plan_text)
        except Exception as e:
            logger.error(f"Failed to parse plan: {e}")
            context.set_details(f"Failed to parse plan: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return

        for fb in self.agent.execute_actions(actions):
            yield helper_pb2.ActionFeedback(**fb)
            
    def CreateProject(self, request, context):
        steps = request.project_steps
        logger.info(f"Received project creation steps:\n{steps}")

        try:
            for fb in self.agent.create_project(steps):
                yield helper_pb2.ActionFeedback(**fb)
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            context.set_details(f"Failed to create project: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return
            
def serve():
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