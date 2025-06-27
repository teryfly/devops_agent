# 通过LLM-A执行计划的模块
from ai_project_helper.proto import helper_pb2
from ai_project_helper.server.utils import split_plan_into_steps
from ai_project_helper.log_config import get_logger

logger = get_logger("server.llm_plan_exec")

def execute_plan_text(agent, plan_text, context):
    task_steps = split_plan_into_steps(plan_text)
    step_count = len(task_steps)

    for step_index, step_text in enumerate(task_steps):
        try:
            for fb in agent.run_step_text(step_text, step_index + 1, step_count):
                yield helper_pb2.ActionFeedback(**fb)
                if fb.get("status") == "failed":
                    return
        except Exception as e:
            logger.exception(f"执行第{step_index+1}步失败: {e}")
            context.set_code(500)
            context.set_details(f"执行失败: {e}")
            return
