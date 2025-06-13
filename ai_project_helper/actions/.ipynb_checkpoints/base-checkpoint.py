class BaseAction:
    def __init__(self, action_type, parameters, step_description, depends_on=None):
        self.action_type = action_type
        self.parameters = parameters
        self.step_description = step_description
        self.depends_on = depends_on or []

    def execute_stream(self):
        raise NotImplementedError

    @staticmethod
    def safe_abs_path(path, workdir):
        import os
        if os.path.isabs(path):
            rel_path = os.path.relpath(path, "/")
            safe_path = os.path.join(workdir, rel_path)
        else:
            safe_path = os.path.join(workdir, path)
        safe_path = os.path.abspath(safe_path)
        if not safe_path.startswith(os.path.abspath(workdir)):
            raise PermissionError(f"安全警告：不允许访问工作目录之外的路径: {safe_path}")
        return safe_path
