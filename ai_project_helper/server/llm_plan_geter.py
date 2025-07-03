import os
import re
import requests
from datetime import datetime
from ai_project_helper.log_config import get_logger
import html  # 添加导入

logger = get_logger("server.llm_plan")

def get_plan_from_llm(requirement, model, llm_url, api_key, project_id):
    plans_dir = "llm_coding_plans"
    os.makedirs(plans_dir, exist_ok=True)
    
    complete_plan_text = ""
    accumulated_parts = ""
    current_part, total_parts = 0, 1
    request_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    while current_part < total_parts:
        current_part += 1
        prompt = _build_prompt(requirement, accumulated_parts, current_part, total_parts)
        
        # 保存请求内容
        request_path = os.path.join(plans_dir, f"{project_id}-request-Part-{current_part}-of-{total_parts}-{request_timestamp}.txt")
        with open(request_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        
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
        plan_text = html.unescape(plan_text)  # 添加反转义处理
        
        # 处理多部分响应
        if current_part == 1:
            match = re.match(r'\[(\d+)/(\d+)\]', plan_text.split('\n', 1)[0].strip())
            if match:
                total_parts = int(match.group(2))
                plan_text = plan_text.split('\n', 1)[1].lstrip()
        
        # 保存计划部分
        part_path = os.path.join(plans_dir, f"{project_id}-plan-Part-{current_part}-of-{total_parts}-{request_timestamp}.txt")
        with open(part_path, "w", encoding="utf-8") as f:
            f.write(plan_text)
        
        accumulated_parts += plan_text + "\n\n"
        
        # 合并完整计划
        if complete_plan_text and not complete_plan_text.endswith('\n\n') and not plan_text.startswith('\n\n'):
            complete_plan_text += "\n\n"
        complete_plan_text += plan_text
    
    # 保存完整计划
    final_path = os.path.join(plans_dir, f"{project_id}-complete-{request_timestamp}.txt")
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(complete_plan_text)
    
    return complete_plan_text

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