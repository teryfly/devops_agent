# 功能（工具）调用解析
import re
from ai_project_helper.core.action_schema import ACTION_SCHEMAS
from ai_project_helper.actions import ACTION_TYPE_ALIAS


FN_REGEX_PATTERN = r'<function=([^>]+)>(.*?)</function>'
FN_PARAM_REGEX_PATTERN = r'<parameter=([^>]+)>(.*?)</parameter>'

def parse_actions(llm_output: str):
    actions = []
    for match in re.finditer(FN_REGEX_PATTERN, llm_output, re.DOTALL):
        fn_name = match.group(1).strip()
        param_body = match.group(2)  # 必须加在这里
        # 标准化 function name
        canonical_name = ACTION_TYPE_ALIAS.get(fn_name, fn_name)
        schema = ACTION_SCHEMAS.get(canonical_name)
        if not schema:
            raise ValueError(f"Unknown function: {fn_name}")
        params = {}
        for p in re.finditer(FN_PARAM_REGEX_PATTERN, param_body, re.DOTALL):
            pname = p.group(1).strip()
            pval = p.group(2).strip()
            params[pname] = pval
        required = set(schema["parameters"].get("required", []))
        missing = required - set(params)
        if missing:
            raise ValueError(f"Missing required parameters for {fn_name}: {missing}")
        actions.append({
            "action_type": canonical_name,
            "parameters": params,
            "step_description": f"{canonical_name}({', '.join(f'{k}={repr(v)}' for k, v in params.items())})"
        })
    return actions
