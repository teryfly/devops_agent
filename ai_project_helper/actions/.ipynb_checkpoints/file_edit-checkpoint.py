# 文件写入/编辑/替换
import os
import shutil
import logging
from .base import BaseAction

logger = logging.getLogger("ai_project_helper.actions.file_edit")

class FileEditAction(BaseAction):
    def execute_stream(self):
        path = self.parameters.get("path")
        config = self.parameters.get("_config", {})
        workdir = config.get("working_dir", os.getcwd())
        abs_path = self.safe_abs_path(path, workdir)        
        command = self.parameters.get("command")
        file_text = self.parameters.get("file_text")
        old_str = self.parameters.get("old_str")
        new_str = self.parameters.get("new_str")
        append_text = self.parameters.get("append_text")

        root_dir = os.path.abspath(os.getcwd())
        abs_path = os.path.abspath(path)
        if not abs_path.startswith(root_dir):
            yield ("", f"安全警告：不允许访问工作目录之外的文件: {abs_path}")
            return

        try:
            if command == "create":
                if os.path.exists(abs_path):
                    yield ("", f"文件已存在: {abs_path}")
                    return
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(file_text or "")
                yield (f"文件创建成功: {abs_path}\n", "")

            elif command == "str_replace":
                if not os.path.exists(abs_path):
                    yield ("", f"文件不存在: {abs_path}")
                    return
                backup_path = abs_path + ".bak"
                shutil.copy2(abs_path, backup_path)
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if old_str not in content:
                    yield ("", f"要替换的内容未找到: {old_str}")
                    return
                content = content.replace(old_str, new_str or "")
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(content)
                yield (f"字符串替换成功: {abs_path}\n", "")

            elif command == "append":
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "a", encoding="utf-8") as f:
                    f.write(append_text or "")
                yield (f"内容已追加到文件: {abs_path}\n", "")

            elif command == "delete":
                if not os.path.exists(abs_path):
                    yield ("", f"文件不存在: {abs_path}")
                    return
                os.remove(abs_path)
                yield (f"文件删除成功: {abs_path}\n", "")

            else:
                yield ("", f"未知文件操作命令: {command}")

        except Exception as e:
            logger.exception("文件编辑操作失败")
            yield ("", f"文件编辑操作失败: {e}")
