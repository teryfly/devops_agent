# 目录操作
import os
import shutil
import logging
from .base import BaseAction

logger = logging.getLogger("ai_project_helper.actions.directory")

class DirectoryAction(BaseAction):
    def execute_stream(self):
        path = self.parameters.get("path")
        config = self.parameters.get("_config", {})
        workdir = config.get("working_dir", os.getcwd())
        abs_path = self.safe_abs_path(path, workdir)
        command = self.parameters.get("command", "create")

        try:
            if command in ("create", "mkdir"):
                os.makedirs(abs_path, exist_ok=True)
                yield (f"目录创建成功: {abs_path}\n", "")
            elif command in ("delete", "rmdir"):
                shutil.rmtree(abs_path)
                yield (f"目录删除成功: {abs_path}\n", "")
            else:
                yield ("", f"未知目录操作命令: {command}")
        except Exception as e:
            logger.exception("目录操作失败")
            yield ("", f"目录操作失败: {e}")