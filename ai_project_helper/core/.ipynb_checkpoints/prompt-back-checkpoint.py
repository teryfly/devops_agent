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
            desc += f'  ({j}) {param} ({typ}, {req}): {desc_val}\n'
        desc += f'---- END FUNCTION #{idx} ----\n'
    return desc
# build_functions_description 生成效果示例
'''  
---- BEGIN FUNCTION #1: shell_command ----
Description: Execute a shell command.
Parameters:
  (1) command (string, required): Shell command to execute
  (2) cwd (string, optional): working directory (optional)
---- END FUNCTION #1 ----
---- BEGIN FUNCTION #2: file_edit ----
Description: Edit file: create, replace, append, or delete.
Parameters:
  (1) command (string, required): create/str_replace/append/delete
  (2) path (string, required): File path
  (3) file_text (string, optional): File content (for create)
  (4) old_str (string, optional): String to replace
  (5) new_str (string, optional): Replacement string
  (6) append_text (string, optional): Text to append
---- END FUNCTION #2 ----
---- BEGIN FUNCTION #3: directory ----
Description: Create or delete directory
Parameters:
  (1) command (string, required): create/mkdir/delete/rmdir
  (2) path (string, required): Directory path
---- END FUNCTION #3 ----

''' 

# 工具prompt 之后的，要示例
IN_CONTEXT_EXAMPLES = """
示例:
<function=execute_bash>
<parameter=command>pwd && ls</parameter>
</function>

<function=str_replace_editor>
<parameter=command>create</parameter>
<parameter=path>/aiWorkDir/app.py</parameter>
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
"""

def build_prompt(user_task):
    return f"""
你可以调用以下函数来完成开发运维任务，每个函数的参数结构如下：

{build_functions_description()}

{IN_CONTEXT_EXAMPLES}

请严格按照上述格式，每条消息只输出一个函数调用，所有必需参数必须包含，参数内容要完整。

------------------- 新任务描述 -------------------
{user_task}
------------------- 结束 -------------------
"""