import logging
from core.llm import LLMClient
from core.action_parser import parse_actions
from actions import get_action_class

logger = logging.getLogger("ai_project_helper.server")

class Agent:
    def __init__(self, config):
        self.llm = LLMClient(config)
        self.model = config['llm']['model']
        self.config = config 

    def parse_plan(self, plan_text: str):
        raw = self.llm.plan_to_actions(plan_text)
        logger.info("LLM model: %s, raw response:\n%s", self.model, raw)
        actions = parse_actions(raw)
        action_types = [act.get("action_type") for act in actions]
        logger.info("LLM model: %s, action_types: %s", self.model, action_types)
        return actions

    import copy
    
    def execute_actions(self, actions):
        for idx, action_dict in enumerate(actions):
            parameters = self.copy.deepcopy(action_dict.get("parameters", {}))
            parameters["_config"] = {"working_dir": self.config.get("working_dir")}
            action_type = action_dict["action_type"]
            step_description = action_dict["step_description"]
            command = parameters.get("command", "")
            logger.info(f"Executing action_type: {action_type}, step: {step_description}")
    
            ActionCls = get_action_class(action_type)
            action = ActionCls(action_type, parameters, step_description)
    
            yield {
                "action_index": idx,
                "action_type": action_type,
                "step_description": step_description,
                "status": "running",
                "output": "",
                "error": "",
                "command": command,
            }
            try:
                for out, err in action.execute_stream():
                    yield {
                        "action_index": idx,
                        "action_type": action_type,
                        "step_description": step_description,
                        "status": "running",
                        "output": out or "",
                        "error": err or "",
                    }
                yield {
                    "action_index": idx,
                    "action_type": action_type,
                    "step_description": step_description,
                    "status": "success",
                    "output": "",
                    "error": "",
                    "command": command,

                }
            except Exception as e:
                logger.exception("Action 执行失败")
                yield {
                    "action_index": idx,
                    "action_type": action_type,
                    "step_description": step_description,
                    "status": "failed",
                    "output": "",
                    "error": str(e),
                    "command": command,

                }
                break

    def execute_action(self, action_dict):
        """
        单步执行一个 action，方便 server.py 逐步流式反馈
        """
        action_type = action_dict["action_type"]
        step_description = action_dict["step_description"]
        # 深拷贝，避免污染原始参数
        parameters = self.copy.deepcopy(action_dict.get("parameters", {}))
        command = parameters.get("command", "")
        parameters["_config"] = {"working_dir": self.config.get("working_dir")}
        logger.info(f"Executing action_type: {action_type}, step: {step_description}")

        ActionCls = get_action_class(action_type)
        parameters["_config"] = {"working_dir": self.config["working_dir"]}
        action = ActionCls(action_type, parameters, step_description)
        try:
            for out, err in action.execute_stream():
                yield out, err
        except Exception as e:
            logger.exception("Action 执行失败")
            yield "", str(e)

    def create_project(self, project_steps: str):
        """
        使用 LLM 方案步骤生成 bash 脚本并执行，流式返回输出
        """
        bash_script = self.llm.generate_bash_script(project_steps)
        logger.info(f"生成的 bash 脚本:\n{bash_script}")

        # 保存脚本到临时文件
        import tempfile, os
        workdir = self.config.get("working_dir") or os.getcwd()
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".sh", dir=workdir) as tf:
            tf.write(bash_script)
            tf.flush()
            script_path = tf.name

        # 增加可执行权限
        os.chmod(script_path, 0o755)

        # 构造shell action
        action_dict = {
            "action_type": "shell_command",
            "parameters": {
                "command": f"bash {script_path}",
                "_config": {"working_dir": workdir}      # ← 这里必须有
            },
            "step_description": f"执行生成的项目初始化脚本: {script_path}"
        }        
        # 用统一执行接口
        yield from self.execute_actions([action_dict])