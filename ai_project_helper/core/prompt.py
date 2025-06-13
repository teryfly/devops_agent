# llm_prompt.py

from ai_project_helper.core.action_schema import ACTION_SCHEMAS

# 将ACTION_SCHEMAS中的命令工具生成为 工具prompt 
def build_functions_description():
    desc = ""
    for idx, schema in enumerate(ACTION_SCHEMAS.values(), 1):
        desc += f'---- BEGIN FUNCTION #{idx}: {schema["name"]} ----\n'
        desc += f'Description: {schema["description"]}\n'
        desc += 'Parameters:\n'
        props = schema["parameters"].get("properties", {})
        required = set(schema["parameters"].get("required", []))
        for j, (param, info) in enumerate(props.items(), 1):
            req = "required" if param in required else "optional"
            typ = info.get("type", "string")
            desc_val = info.get("description", "")
            enum_info = ""
            if "enum" in info:
                enum_values = ', '.join(f'"{v}"' for v in info["enum"])
                enum_info = f" options: [{enum_values}]"
            desc += f'  ({j}) {param} ({typ}, {req}): {desc_val}{enum_info}\n'
        desc += f'---- END FUNCTION #{idx} ----\n'
    return desc

# 输出要求
OUTPUT_RULES ="""
OUTPUT RULEs:
1. Outplut Only Strict XML-like format demonstrating as the DEMONSTRATION, Nothong else.
2. Mandatory parameters must always be included.
3. Ensure Parameter Completeness, No partial values (e.g., if replacing text, both old_str and new_str must be fully defined).
4. Paired XML tags must be properly nested and closed—every opening <tag> must have a corresponding closing </tag>
5. Values between tags must be replaced with actual content per task requirements.
6. Single function per output – no combined operations.
"""

# 输出的示例
IN_CONTEXT_EXAMPLES = """
---- BEGIN DEMONSTRATION----

<function=execute_bash>
<parameter=command>pwd && ls</parameter>
</function>

<function=str_replace_editor>
<parameter=command>update</parameter>
<parameter=path>/workdir/app.py</parameter>
<parameter=file_text>
from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
    numbers = list(range(1, 11))
    return str(numbers)
if __name__ == '__main__':
    app.run(port=5000)
</parameter>
</function>

<function=str_replace_editor>
<parameter=command>str_replace</parameter>
<parameter=path>/aiWorkDir/app.py</parameter>
<parameter=old_str>return str(numbers)</parameter>
<parameter=new_str>return '&lt;table&gt;' + ''.join([f'&lt;tr&gt;&lt;td&gt;{{i}}&lt;/td&gt;&lt;/tr&gt;' for i in numbers]) + '&lt;/table&gt;'</parameter>
</function>
---- END DEMONSTRATION----
"""

# Role:
#You are a Software Engineering Task Parser. Your role is to decompose complex tasks into executable subtasks whith the format of DEMONSTRATION below, using only the provided functions. 
def build_prompt(user_task, working_dir=None):
    if working_dir is None:
        import os
        working_dir = os.getcwd()
    return f"""
You can call functions to complete DevOps tasks, with the parameter structure of each function as follows. the workdir is always at {working_dir}.
Available Functions & Parameters:
{build_functions_description()}
{IN_CONTEXT_EXAMPLES}
{OUTPUT_RULES}
-------------------New Task-------------------
{user_task}
------------------- End -------------------
"""