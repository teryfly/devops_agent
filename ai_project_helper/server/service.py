#（gRPC服务实现）
import grpc
from ai_project_helper.proto import helper_pb2, helper_pb2_grpc
from ai_project_helper.core.agent import Agent
from ai_project_helper.server.utils import split_plan_into_steps
from ai_project_helper.server.llm_plan_runner import run_llm_plan_then_execute
from ai_project_helper.log_config import get_logger

import os

class AIProjectHelperServicer(helper_pb2_grpc.AIProjectHelperServicer):
    def __init__(self, config):
        self.config = config
        self.base_working_dir = config['working_dir']
        self.agent = None
        self.logger = get_logger("server.service")

    def _get_project_working_dir(self, project_id):
        project_dir = os.path.join(self.base_working_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        self.logger.info(f"使用项目目录: {project_dir}")
        return project_dir

    def _init_agent_with_project_dir(self, request):
        project_id = request.project_id
        project_dir = self._get_project_working_dir(project_id)
        config = self.config.copy()
        config['working_dir'] = project_dir
        self.agent = Agent(config)
        return self.agent

    def RunPlan(self, request, context):
        try:
            self._init_agent_with_project_dir(request)
            task_steps = split_plan_into_steps(request.plan_text)
            step_count = len(task_steps)

            for step_index, step_text in enumerate(task_steps):
                for fb in self.agent.run_step_text(step_text, step_index+1, step_count):
                    yield helper_pb2.ActionFeedback(**fb)
                    if fb.get("status") == "failed":
                        return
        except Exception as e:
            self.logger.exception("RunPlan 处理异常")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    def GetPlanThenRun(self, request, context):
        try:
            self._init_agent_with_project_dir(request)
            yield from run_llm_plan_then_execute(self.agent, self.config, request, context)
        except Exception as e:
            self.logger.exception("GetPlanThenRun 处理异常")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    def CreateProject(self, request, context):
        try:
            self._init_agent_with_project_dir(request)
            for fb in self.agent.create_project(request.project_steps):
                yield helper_pb2.ActionFeedback(**fb)
        except Exception as e:
            self.logger.exception("CreateProject 失败")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
