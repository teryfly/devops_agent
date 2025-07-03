import os
import shutil
import logging
import html  # 添加导入
from .base import BaseAction

logger = logging.getLogger("ai_project_helper.actions.file_edit")

class FileEditAction(BaseAction):
    def _unescape_content(self, content):
        """处理HTML反转义"""
        if content is None:
            return ""
        return html.unescape(content)
    
    def execute_stream(self):
        path = self.parameters.get("path")
        config = self.parameters.get("_config", {})
        workdir = config.get("working_dir", os.getcwd())
        command = self.parameters.get("command")
        file_text = self.parameters.get("file_text")
        old_str = self.parameters.get("old_str")
        new_str = self.parameters.get("new_str")
        append_text = self.parameters.get("append_text")

        try:
            abs_path = self.safe_abs_path(path, workdir)
        except PermissionError as e:
            yield ("", str(e), 1)  # 添加退出码
            return

        try:
            # 处理HTML转义字符
            file_text = self._unescape_content(file_text)
            new_str = self._unescape_content(new_str)
            append_text = self._unescape_content(append_text)
            
            if command == "create":
                if os.path.exists(abs_path):
                    # 将"文件已存在"视为警告而非错误
                    yield (f"警告: 文件已存在: {abs_path} (跳过创建)\n", "", 2)  # 退出码2表示警告
                    return
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(file_text or "")
                yield (f"文件创建成功: {abs_path}\n", "", 0)

            elif command == "update":
                if not os.path.exists(abs_path):
                    yield (f"警告: 文件不存在: {abs_path} (创建新文件)\n", "", 2)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(file_text or "")
                yield (f"文件内容已覆盖更新: {abs_path}\n", "", 0)

            elif command == "str_replace":
                if not os.path.exists(abs_path):
                    yield ("", f"错误: 文件不存在: {abs_path}", 1)
                    return
                backup_path = abs_path + ".bak"
                shutil.copy2(abs_path, backup_path)
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if old_str not in content:
                    yield (f"警告: 要替换的内容未找到: {old_str} (跳过替换)\n", "", 2)
                    return
                content = content.replace(old_str, new_str or "")
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(content)
                yield (f"字符串替换成功: {abs_path}\n", "", 0)

            elif command == "append":
                if not os.path.exists(abs_path):
                    yield (f"警告: 文件不存在: {abs_path} (创建新文件)\n", "", 2)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "a", encoding="utf-8") as f:
                    f.write(append_text or "")
                yield (f"内容已追加到文件: {abs_path}\n", "", 0)

            elif command == "delete":
                if not os.path.exists(abs_path):
                    yield (f"警告: 文件不存在: {abs_path} (无需删除)\n", "", 2)
                    return
                os.remove(abs_path)
                yield (f"文件删除成功: {abs_path}\n", "", 0)

            else:
                yield ("", f"错误: 未知文件操作命令: {command}", 1)

        except Exception as e:
            logger.exception("文件编辑操作失败")
            yield ("", f"文件编辑操作失败: {e}", 1)