class BaseAction:
    def __init__(self, action_type, parameters, step_description, depends_on=None):
        self.action_type = action_type
        self.parameters = parameters
        self.step_description = step_description
        self.depends_on = depends_on or []

    def execute_stream(self):
        raise NotImplementedError

    @staticmethod
    def safe_abs_path(path, workdir, project_name=None):
        import os
        workdir = os.path.abspath(workdir)
        # project_name 可以传入，也可以自动识别
        if not project_name:
            # 自动识别最后一级目录名
            project_name = ""
            elements = [p for p in path.strip("/").split("/") if p]
            if len(elements) > 1:
                project_name = elements[-2]
            elif len(elements) == 1:
                project_name = elements[0]
    
        # 处理绝对路径
        if os.path.isabs(path):
            # 找到 path 中的 project_name，截断为 project_name/后面的部分
            idx = -1
            if project_name:
                try:
                    idx = path.index(project_name)
                except ValueError:
                    idx = -1
    
            if idx >= 0:
                rel_path = path[idx:]
                safe_path = os.path.join(workdir, rel_path)
            else:
                # fallback: 只放在工作目录下一级
                safe_path = os.path.join(workdir, os.path.basename(path.rstrip("/")))
        else:
            safe_path = os.path.join(workdir, path)
        safe_path = os.path.abspath(safe_path)
        if not safe_path.startswith(workdir):
            raise PermissionError(f"安全警告：不允许访问工作目录之外的路径: {safe_path}")
        return safe_path