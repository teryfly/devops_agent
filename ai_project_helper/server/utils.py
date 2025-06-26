import re

def split_plan_into_steps(plan_text: str):
    """按 ------ 分割计划文本为步骤"""
    step_delimiter = re.compile(r'^\s*------', re.MULTILINE)
    matches = list(step_delimiter.finditer(plan_text))
    task_steps = []

    if not matches:
        if plan_text.strip():
            task_steps.append(plan_text.strip())
    else:
        start_idx = 0
        for match in matches:
            end_idx = match.start()
            segment = plan_text[start_idx:end_idx].strip()
            if segment:
                task_steps.append(segment)
            start_idx = match.end()

        final_segment = plan_text[start_idx:].strip()
        if final_segment:
            task_steps.append(final_segment)

    return task_steps
