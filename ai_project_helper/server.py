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
        gRPC流式接口：接收用户输入的plan_text，按 ------ 拆分后逐步调用LLM构造actions并执行，实时yield反馈
        """
        plan_text = request.plan_text
        logger.info(f"==================接收到客户端请求==================：\n{plan_text[:88]}...\n =============================================================================================================")

        task_steps = [s.strip() for s in plan_text.split("------") if s.strip()]
        step_count = len(task_steps)

        for step_index, step_text in enumerate(task_steps):
            try:
                for fb in self.agent.run_step_text(step_text, step_index=step_index+1, step_count=step_count):
                    yield helper_pb2.ActionFeedback(**fb)
                    if fb.get("status") == "failed":
                        logger.error(f"第 {step_index+1} 步执行失败，终止后续步骤")
                        return
            except Exception as e:
                logger.exception(f"第 {step_index+1} 步执行异常")
                context.set_details(f"Step {step_index+1} execution error: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return
   
 
    # 远程 LLM 生成 plan → 本地 LLM 执行 plan”的链式代理
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
                    "max_tokens": 2048000,
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

        # 第三步：将 plan_text 拆分为 steps
        task_steps = [s.strip() for s in plan_text.split("------") if s.strip()]
        step_count = len(task_steps)

        # 第四步：逐步使用本地 LLM-A 解析并执行每个 step
        for step_index, step_text in enumerate(task_steps):
            try:
                for fb in self.agent.run_step_text(step_text, step_index=step_index + 1, step_count=step_count):
                    yield helper_pb2.ActionFeedback(**fb)
                    if fb.get("status") == "failed":
                        return
            except Exception as e:
                logger.exception(f"Step {step_index+1} 执行失败")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"执行第 {step_index+1} 步失败: {e}")
                return
       
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