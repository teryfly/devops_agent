#（LLM规划 + 执行）
from ai_project_helper.proto import helper_pb2
from ai_project_helper.server.llm_plan_geter import get_plan_from_llm
from ai_project_helper.server.llm_plan_executer import execute_plan_text

def run_llm_plan_then_execute(agent, config, request, context):
    requirement = request.requirement
    model = request.model or config['llm']['model']
    llm_url = request.llm_url or config['llm']['api_url']
    api_key = config['llm']['api_key']
    project_id = request.project_id

    plan_text = get_plan_from_llm(requirement, model, llm_url, api_key, project_id)

    # 返回完整计划
    yield helper_pb2.ActionFeedback(
        action_index=-1,
        action_type="llm_plan",
        step_description="完整计划生成完毕",
        status="success",
        complete_plan=plan_text  # 关键新增字段
    )

    # 执行计划
    yield from execute_plan_text(agent, plan_text, context)