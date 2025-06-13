import subprocess
import os
import logging

from .base import BaseAction

logger = logging.getLogger("ai_project_helper.actions.shell")

def remap_abspath_to_workdir(cmd, workdir):
    """
    将命令字符串中的绝对路径替换为以工作目录为根的路径。
    仅替换以 / 开头的路径。
    """
    import re
    def _replace(match):
        abspath = match.group(0)
        rel_path = abspath.lstrip("/")
        safe_path = os.path.join(workdir, rel_path)
        return safe_path
    # 简单匹配 /a/b/c 等路径
    return re.sub(r'(/\w[\w\-/\.]*)', _replace, cmd)

class ShellCommandAction(BaseAction):
    def execute_stream(self):
        command = self.parameters.get("command")
        config = self.parameters.get("_config", {})
        working_dir = config.get("working_dir", os.getcwd())
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