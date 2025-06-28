from ai_project_helper.proto import helper_pb2
from ai_project_helper.server.utils import split_plan_into_steps
from ai_project_helper.log_config import get_logger

logger = get_logger("server.llm_plan_exec")

def execute_plan_text(agent, plan_text, context):
    task_steps = split_plan_into_steps(plan_text)
    step_count = len(task_steps)

    for step_index, step_text in enumerate(task_steps):
        try:
            # 使用新的 run_step_text 方法
            for fb in agent.run_step_text(step_text, step_index + 1, step_count):
                # 转换为 ActionFeedback 对象
                yield helper_pb2.ActionFeedback(
                    action_index=fb.get("action_index", 0),
                    action_type=fb.get("action_type", ""),
                    step_description=fb.get("step_description", ""),
                    status=fb.get("status", ""),
                    output=fb.get("output", ""),
                    error=fb.get("error", ""),
                    command=fb.get("command", ""),
                    step_index=fb.get("step_index", 0),
                    total_steps=fb.get("total_steps", 0),
                    exit_code=fb.get("exit_code", 0),
                    complete_plan=fb.get("complete_plan", "")
                )
                
                # 如果状态为失败，则终止执行
                if fb.get("status") == "failed":
                    return
                    
        except Exception as e:
            logger.exception(f"执行第{step_index+1}步失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"执行失败: {e}")
            return