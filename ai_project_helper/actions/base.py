import os
import logging

logger = logging.getLogger("ai_project_helper.actions.base")

class BaseAction:
    def __init__(self, action_type, parameters, step_description):
        self.action_type = action_type
        self.parameters = parameters
        self.step_description = step_description

    @staticmethod
    def safe_abs_path(path, workdir):
        """
        安全拼接 path 与 workdir，并防止路径逃逸（如 /etc/passwd）。
        """
        workdir = os.path.abspath(workdir)

        if os.path.isabs(path):
            path = path.lstrip("/")  # 例如 "/backend/app" → "backend/app"

        candidate_path = os.path.abspath(os.path.join(workdir, path))

        if not candidate_path.startswith(workdir):
            raise PermissionError(f"安全警告：不允许访问工作目录之外的路径: {candidate_path}")

        logger.info(f"[safe_abs_path] 输入: {path}, 最终路径: {candidate_path}")
        return candidate_path
