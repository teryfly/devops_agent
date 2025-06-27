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

    def GetPlan(self, request, context):
        try:
            self._init_agent_with_project_dir(request)
            model = request.model or self.config['llm']['model']
            llm_url = request.llm_url or self.config['llm']['api_url']
            api_key = self.config['llm']['api_key']
            project_id = request.project_id

            plan_text = get_plan_from_llm(
                request.requirement, model, llm_url, api_key, project_id
            )
            
            # 返回完整计划
            yield helper_pb2.ActionFeedback(
                action_index=-1,
                action_type="llm_plan",
                step_description="完整计划生成完毕",
                status="success",
                complete_plan=plan_text  # 关键新增字段
            )
            
        except Exception as e:
            self.logger.exception("GetPlan 处理异常")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    def GetPlanThenRun(self, request, context):
        try:
            self._init_agent_with_project_dir(request)
            plan_text = get_plan_from_llm(
                request.requirement,
                request.model or self.config['llm']['model'],
                request.llm_url or self.config['llm']['api_url'],
                self.config['llm']['api_key'],
                request.project_id
            )
            
            # 先返回完整计划
            yield helper_pb2.ActionFeedback(
                action_index=-1,
                action_type="llm_plan",
                step_description="完整计划生成完毕",
                status="success",
                complete_plan=plan_text  # 关键新增字段
            )
            
            # 再执行计划
            for fb in execute_plan_text(self.agent, plan_text, context):
                yield fb
                
        except Exception as e:
            self.logger.exception("GetPlanThenRun 处理异常")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e)) 
