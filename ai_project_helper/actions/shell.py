# actions/shell.py

import subprocess
import os
import logging
from .base import BaseAction

logger = logging.getLogger("ai_project_helper.actions.shell")

def remap_abspath_to_workdir(cmd, workdir):
    """
    将命令字符串中的绝对路径替换为以工作目录为根的路径。
    仅替换以 / 开头的不包含空格和特殊符号的路径。
    """
    import re
    def _replace(match):
        abspath = match.group(0)
        rel_path = abspath.lstrip("/")
        safe_path = os.path.join(workdir, rel_path)
        return safe_path
    # 这里仅示例替换 /a/b/c，实际项目可用更精细的正则
    return re.sub(r'(/\w[\w\-/\.]*)', _replace, cmd)

class ShellCommandAction(BaseAction):
    def execute_stream(self):
        command = self.parameters.get("command")
        config = self.parameters.get("_config", {})  # 允许从参数传递 config
        working_dir = config.get("working_dir", os.getcwd())
        # ...在这里用 working_dir 做 cwd ...
        proc = subprocess.Popen(
            command, shell=True, cwd=working_dir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if not command:
            yield ("", "缺少命令参数")
            return

        # 路径重写
        command = remap_abspath_to_workdir(command, working_dir)
        logger.info(f"执行命令: {command} (cwd={working_dir})")
        try:
            proc = subprocess.Popen(
                command, shell=True, cwd=working_dir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            while True:
                out = proc.stdout.readline()
                err = proc.stderr.readline()
                if out:
                    yield (out, "")
                if err:
                    yield ("", err)
                if not out and not err and proc.poll() is not None:
                    break
            rc = proc.poll()
            yield (f"命令执行完成，退出码: {rc}\n", "")
        except Exception as e:
            logger.exception("命令执行出错")
            yield ("", f"命令执行失败: {e}")