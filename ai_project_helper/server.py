import grpc
from concurrent import futures

from ai_project_helper.proto import helper_pb2, helper_pb2_grpc
from ai_project_helper.core.agent import Agent
from ai_project_helper.config import load_config
from ai_project_helper.log_config import setup_logging, get_logger
from ai_project_helper.core.prompt import build_prompt

import requests
# 初始化日志
setup_logging()
logger = get_logger("server")

class AIProjectHelperServicer(helper_pb2_grpc.AIProjectHelperServicer):
    def __init__(self, config):
        self.config = config
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
    
    def GetPlanThenRun(self, request, context):
       

        requirement = request.requirement
        model = request.model or self.config['llm']['model']
        llm_url = request.llm_url or self.config['llm']['api_url']
        api_key = self.config['llm']['api_key']

        # 第一步：向 LLM-B 请求生成 plan
        try:
            prompt = requirement  # 直接将客户需求作为 prompt 请求远程 LLM
            logger.info(f"请求 LLM-B（{model}@{llm_url}）生成 plan: {prompt}")
            response = requests.post(
                llm_url,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048,
                    "temperature": 0,
                },
                headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            plan_text = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"LLM-B 调用失败: {e}")
            return

        # 第二步：将 plan_text 反馈给客户端
        yield helper_pb2.ActionFeedback(
            action_index=-1,
            action_type="llm_plan",
            step_description="LLM-B生成的计划内容",
            status="success",
            output=plan_text,
            command="",
            error=""
        )

        # 第三步：使用本地 LLM-A 解析 plan_text 为 actions，并执行
        try:
            actions = self.agent.parse_plan(plan_text)
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"解析 plan 失败: {e}")
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