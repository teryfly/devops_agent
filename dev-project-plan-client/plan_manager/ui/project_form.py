# ui/project_form.py

import tkinter as tk
from tkinter import ttk, messagebox
from .form_builder import FormBuilder

class ProjectForm:
    def __init__(self, parent, project=None):
        self.parent = parent
        self.project = project

        self._setup_variables()
        self._setup_widgets()

    def _setup_variables(self):
        self.name_var = tk.StringVar()
        self.env_var = tk.StringVar()
        self.grpc_var = tk.StringVar(value="192.168.120.238:50051")

    def _setup_widgets(self):
        form_builder = FormBuilder(self.parent)
        name_entry = form_builder.add_entry("Project Name", self.name_var, width=40)
        name_entry.focus()

        env_values = [
            "Python+FastAPI", "React+Vite", "Java+SpringBoot",
            ".NET Core+EF", "Node.js+Express", "Vue.js+Vite",
            "Angular+TypeScript", "Django+Python", "Flask+Python", "Other"
        ]
        env_combo = form_builder.add_combobox("Development Environment", self.env_var, env_values, width=37)

        if not self.project:
            env_combo.current(0)

        form_builder.add_entry("gRPC Server Address", self.grpc_var, width=40)
        self.parent.columnconfigure(1, weight=1)

    def load_project_data(self, project):
        if project:
            self.name_var.set(project['name'])
            self.env_var.set(project['dev_environment'])
            self.grpc_var.set(project['grpc_server_address'])

    def get_form_data(self):
        return {
            'name': self.name_var.get().strip(),
            'env': self.env_var.get().strip(),
            'grpc': self.grpc_var.get().strip()
        }

    def validate_form(self):
        data = self.get_form_data()
        if not data['name']:
            messagebox.showerror("Validation Error", "Project name is required!")
            return False
        if not data['env']:
            messagebox.showerror("Validation Error", "Development environment is required!")
            return False
        if not data['grpc']:
            messagebox.showerror("Validation Error", "gRPC server address is required!")
            return False
        return True

    def save_project(self, project_manager):
        if not self.validate_form():
            return False
        try:
            data = self.get_form_data()
            if self.project:
                success = project_manager.update_project(
                    self.project['id'],
                    name=data['name'],
                    dev_environment=data['env'],
                    grpc_server_address=data['grpc']
                )
                if not success:
                    messagebox.showerror("Update Error", "Failed to update project!")
                    return False
            else:
                project_id = project_manager.create_project(data['name'], data['env'], data['grpc'])
                if not project_id:
                    messagebox.showerror("Create Error", "Failed to create project!")
                    return False
            return True
        except Exception as e:
            operation = "update" if self.project else "create"
            from ui.error_dialog import show_error
            show_error(self.parent, f"Project {operation.title()} Error",
                       f"Failed to {operation} project: {str(e)}", e)
            return False