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
        """安全拼接 path 与 workdir，并防止路径逃逸"""
        workdir = os.path.abspath(workdir)
        
        # 处理绝对路径
        if os.path.isabs(path):
            # 自动重写路径：将根目录替换为工作目录
            base_dir = os.path.dirname(workdir.rstrip(os.sep))
            if path.startswith(base_dir):
                rel_path = os.path.relpath(path, base_dir)
                path = os.path.join(workdir, rel_path)
                logger.info(f"[路径重写] 将 {path} 重写为 {path} 相对于工作目录 {workdir}")
            
            # 直接使用绝对路径，但进行安全检查
            candidate_path = os.path.abspath(path)
        else:
            # 相对路径：直接拼接工作目录
            candidate_path = os.path.abspath(os.path.join(workdir, path))
        
        # 安全检查：确保路径在工作目录内
        if not candidate_path.startswith(workdir):
            raise PermissionError(
                f"安全警告：不允许访问工作目录之外的路径: {candidate_path}\n"
                f"工作目录: {workdir}"
            )
        
        logger.info(f"[safe_abs_path] 输入: {path}, 工作目录: {workdir}, 最终路径: {candidate_path}")
        return candidate_path