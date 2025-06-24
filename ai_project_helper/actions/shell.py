import os
import subprocess
import logging
import select
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
            yield ("", "Missing command parameter", 1)
            return

        # 路径重写
        command = remap_abspath_to_workdir(command, working_dir)
        logger.info(f"Executing command: {command} (cwd={working_dir})")
        
        try:
            # 使用Popen执行命令
            proc = subprocess.Popen(
                command, 
                shell=True,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            
            # 使用select处理实时输出
            while True:
                # 检查进程是否结束
                if proc.poll() is not None:
                    break
                    
                # 非阻塞读取输出
                reads = [proc.stdout.fileno(), proc.stderr.fileno()]
                ret = select.select(reads, [], [], 0.1)[0]
                
                for fd in ret:
                    if fd == proc.stdout.fileno():
                        line = proc.stdout.readline()
                        if line:
                            yield (line, "", None)
                    if fd == proc.stderr.fileno():
                        line = proc.stderr.readline()
                        if line:
                            yield ("", line, None)
            
            # 获取退出码
            return_code = proc.poll()
            
            # 读取剩余输出
            for line in proc.stdout:
                yield (line, "", return_code)
            for line in proc.stderr:
                yield ("", line, return_code)
            
            # 根据退出码生成最终结果
            if return_code == 0:
                yield (f"Command completed successfully (exit code: {return_code})\n", "", return_code)
            else:
                raise RuntimeError(f"Command failed with exit code: {return_code}")
                
        except Exception as e:
            logger.exception("Command execution error")
            yield ("", f"Command execution failed: {str(e)}", 1)