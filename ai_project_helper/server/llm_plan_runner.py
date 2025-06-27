#（LLM规划 + 执行）
import os
import re
import requests
from datetime import datetime
from ai_project_helper.proto import helper_pb2
from ai_project_helper.server.utils import split_plan_into_steps
from ai_project_helper.log_config import get_logger

logger = get_logger("server.llm_plan")

def run_llm_plan_then_execute(agent, config, request, context):
    requirement = request.requirement
    model = request.model or config['llm']['model']
    llm_url = request.llm_url or config['llm']['api_url']
    api_key = config['llm']['api_key']
    project_id = request.project_id
    
    # 获取统一的时间戳（客户端请求时间）
    request_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    plans_dir = "llm_coding_plans"
    os.makedirs(plans_dir, exist_ok=True)

    complete_plan_text = ""
    accumulated_parts = ""
    current_part, total_parts = 0, 1

    while current_part < total_parts:
        current_part += 1
        prompt = _build_prompt(requirement, accumulated_parts, current_part, total_parts)

        # 请求记录文件名格式：{项目ID}-request-Part-{当前部分}-of-{总部分}-{请求时间戳}.txt
        request_path = os.path.join(plans_dir, f"{project_id}-request-Part-{current_part}-of-{total_parts}-{request_timestamp}.txt")
        with open(request_path, "w", encoding="utf-8") as f:
            f.write(prompt)

        try:
            logger.info(f"请求LLM第{current_part}/{total_parts}部分")
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

            if current_part == 1:
                match = re.match(r'\[(\d+)/(\d+)\]', plan_text.split('\n', 1)[0].strip())
                if match:
                    total_parts = int(match.group(2))
                    plan_text = plan_text.split('\n', 1)[1].lstrip()

            # 计划结果文件名格式：{项目ID}-plan-Part-{当前部分}-of-{总部分}-{请求时间戳}.txt
            part_path = os.path.join(plans_dir, f"{project_id}-plan-Part-{current_part}-of-{total_parts}-{request_timestamp}.txt")
            with open(part_path, "w", encoding="utf-8") as f:
                f.write(plan_text)

            yield helper_pb2.ActionFeedback(
                action_index=-1,
                action_type="llm_plan",
                step_description=f"LLM-B计划第{current_part}/{total_parts}部分",
                status="success",
                output=f"部分{current_part}/{total_parts}生成完毕",
                command="",
                error=""
            )

            accumulated_parts += plan_text + "\n\n"

            if not complete_plan_text.strip().endswith('------') and not plan_text.strip().startswith('------'):
                complete_plan_text += "\n------\n"
            complete_plan_text += plan_text

        except Exception as e:
            logger.exception(f"LLM 调用失败: {e}")
            context.set_code(500)
            context.set_details(f"LLM 调用失败: {e}")
            return

    # 完整计划文件名格式：{项目ID}-complete-{请求时间戳}.txt
    final_path = os.path.join(plans_dir, f"{project_id}-complete-{request_timestamp}.txt")
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(complete_plan_text)

    yield helper_pb2.ActionFeedback(
        action_index=-1,
        action_type="llm_plan",
        step_description="完整计划生成完毕",
        status="success",
        output=complete_plan_text,
        command="",
        error=""
    )

    task_steps = split_plan_into_steps(complete_plan_text)
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

def _build_prompt(requirement, history, current, total):
    if current == 1:
        return requirement
    return (
        f"{requirement}\n"
        f"--- 已经输出过的历史记录一共{current - 1}部分，记录如下 ---\n"
        f"{history}\n"
        f"--- 历史记录结束 ---\n"
        f"现在开始继续输出下一个部分（第{current}/{total}部分）"
    )

def _get_base_name_from_requirement(requirement):
    first_line = requirement.split('\n')[0].strip()
    filename = os.path.basename(first_line)
    if not filename.endswith(".txt"):
        filename = "plan.txt"
    return os.path.splitext(filename)[0]