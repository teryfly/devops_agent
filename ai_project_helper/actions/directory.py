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
        command = self.parameters.get("command", "create")

        try:
            abs_path = self.safe_abs_path(path, workdir)
            logger.info(f"创建路径: {abs_path}")
        except PermissionError as e:
            yield ("", str(e), 1)  # 添加退出码
            return

        try:
            if command in ("create", "mkdir"):
                if os.path.exists(abs_path):
                    yield (f"目录已存在: {abs_path}\n", "", 0)
                else:
                    os.makedirs(abs_path, exist_ok=True)
                    yield (f"目录创建成功: {abs_path}\n", "", 0)

            elif command in ("delete", "rmdir"):
                if not os.path.exists(abs_path):
                    yield (f"目录不存在: {abs_path}\n", "", 0)
                else:
                    shutil.rmtree(abs_path)
                    yield (f"目录删除成功: {abs_path}\n", "", 0)

            else:
                yield ("", f"未知目录操作命令: {command}", 1)

        except Exception as e:
            logger.exception("目录操作失败")
            yield ("", f"目录操作失败: {e}", 1)
