import os
import copy
import logging
from core.llm import LLMClient
from core.action_parser import parse_actions
from actions import get_action_class
from pprint import pformat


logger = logging.getLogger("ai_project_helper.server")

class Agent:
    def __init__(self, config):
        self.llm = LLMClient(config)
        self.model = config['llm']['model']
        self.config = config
        # 确保工作目录存在
        working_dir = config.get('working_dir')
        if working_dir:
            os.makedirs(working_dir, exist_ok=True)
            logger.info(f"Agent工作目录设置为: {working_dir}")

    def parse_plan(self, plan_text: str):
        raw = self.llm.plan_to_actions(plan_text)
        logger.info("LLM model: %s, raw response:\n%s", self.model, raw)
        actions = parse_actions(raw)
        action_types = [act.get("action_type") for act in actions]
        logger.info("LLM model: %s, action_types: %s", self.model, action_types)
        return actions
    
    def execute_actions(self, actions, step_index=1, step_count=1):
        for idx, action_dict in enumerate(actions):
            parameters = dict(action_dict["parameters"])  # ✅ 使用已清洗参数
            parameters["_config"] = {"working_dir": self.config.get("working_dir")}

            action_type = action_dict["action_type"]
            base_description = action_dict.get("step_description", "")
            command = parameters.get("command", "")

            ActionCls = get_action_class(action_type)
            action = ActionCls(action_type, parameters, base_description)

            def format_description(status):
                # 简化描述格式，只保留动作信息
                return f"Action[{idx+1}] - [{status}] {action_type}: {base_description}"

            logger.info(f"🚀 执行 {format_description('running')}")

            yield {
                "action_index": idx,
                "action_type": action_type,
                "step_description": format_description("running"),
                "status": "running",
                "output": "",
                "error": "",
                "command": command,
            }
                
            # 操作完成后发送成功状态        
            try:
                output_gen = action.execute_stream()
                exit_code = 0  # 默认退出码
                
                for result in output_gen:
                    # 处理不同类型的返回值
                    if isinstance(result, tuple):
                        if len(result) == 2:  # 兼容旧版本
                            out, err = result
                            exit_code = 0
                        elif len(result) == 3:
                            out, err, exit_code = result
                        else:
                            out, err, exit_code = "", "Invalid result format", 1
                    else:  # 处理可能的其他格式
                        out = result.get("out", "")
                        err = result.get("err", "")
                        exit_code = result.get("exit_code", 0)
                    # 过滤大文本输出
                    out = out or ""
                    if "file_text" in out and len(out) > 80:
                        out = "<file_text content filtered>"
                    yield {
                        "action_index": idx,
                        "action_type": action_type,
                        "step_description": format_description("running"),
                        "status": "running",
                        "output": out or "",
                        "error": err or "",
                        "command": command,
                        "exit_code": exit_code
                    }
                
                # 操作完成后发送成功状态
                yield {
                    "action_index": idx,
                    "action_type": action_type,
                    "step_description": format_description("success"),
                    "status": "success",
                    "output": "",
                    "error": "",
                    "command": command,
                    "exit_code": exit_code
                }

            except Exception as e:
                logger.exception("❌ Action 执行失败")
                yield {
                    "action_index": idx,
                    "action_type": action_type,
                    "step_description": format_description("failed"),
                    "status": "failed",
                    "output": "",
                    "error": str(e),
                    "command": command,
                    "exit_code": 1  # 非零表示错误
                }
                break
    
        
    def execute_action(self, action_dict):
        """
        单步执行一个 action，方便 server.py 逐步流式反馈
        """
        action_type = action_dict["action_type"]
        step_description = action_dict["step_description"]
        # 深拷贝，避免污染原始参数
        parameters = copy.deepcopy(action_dict.get("parameters", {}))
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

    def run_step_text(self, step_text: str, step_index: int, step_count: int):
        try:
            actions = self.parse_plan(step_text)
            for action in actions:
                self.normalize_action_paths(action)

        except Exception as e:
            raise RuntimeError(f"Step {step_index}/{step_count} 解析失败: {e}")

        for fb in self.execute_actions(actions):
            # 添加步骤索引信息
            fb["step_index"] = step_index
            fb["total_steps"] = step_count
            yield fb
            if fb.get("status") == "failed":
                break
    
    def normalize_action_paths(self, action_dict):
        working_dir = os.path.abspath(self.config.get("working_dir", os.getcwd()))
        original_params = action_dict.get("parameters", {})
        new_params = {}
        
        for key, value in original_params.items():
            # 不再过滤文件内容
            if key in ("path", "file_path", "dir_path") and isinstance(value, str):
                try:
                    # 如果路径是绝对路径，直接使用（但会经过安全检查）
                    if os.path.isabs(value):
                        # 保留绝对路径，后续安全函数会处理
                        new_params[key] = value
                    else:
                        # 对于相对路径，直接使用而不做额外处理
                        new_params[key] = value

                    logger.info(f"[路径清洗] {key}: {value} → {new_params[key]}")
                except Exception as e:
                    logger.warning(f"[路径清洗失败] {key}: {value} → {e}")
                    new_params[key] = value
            else:
                new_params[key] = value  # 保持文件内容完整

        # ✅ 添加 _config 工作目录配置
        new_params["_config"] = {"working_dir": working_dir}
        
        # ✅ 更新回 action_dict
        action_dict["parameters"] = new_params

        # ✅ 简化描述 - 避免过长的文件内容显示
        action_type = action_dict.get("action_type", "unknown_action")
        
        # 创建简化的参数描述
        simplified_params = {}
        for key, value in new_params.items():
            if key == "file_text" and value and len(value) > 100:
                simplified_params[key] = f"<{len(value.splitlines())}行内容>"
            elif key == "append_text" and value and len(value) > 100:
                simplified_params[key] = f"<{len(value)}字符内容>"
            else:
                simplified_params[key] = value
        
        # 使用简化参数创建描述
        pretty_desc = f"{action_type}({', '.join(f'{k}={repr(v)}' for k, v in simplified_params.items())})"
        action_dict["step_description"] = pretty_desc

        logger.info(f"[路径清洗后] 参数已更新: {new_params}")
        logger.info(f"[路径清洗后] 描述已更新: {pretty_desc}")
        







