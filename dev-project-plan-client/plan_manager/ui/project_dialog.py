# Project management dialog

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.error_dialog import show_error

class ProjectDialog:
    def __init__(self, parent, project_manager, project=None):
        self.parent = parent
        self.project_manager = project_manager
        self.project = project
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Project Management" if not project else "Edit Project")
        self.window.geometry("500x300")
        self.window.transient(parent)
        self.window.grab_set()
        self._setup_widgets()
        if project:
            self._load_project_data()

    def _setup_widgets(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Project Name
        ttk.Label(main_frame, text="Project Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        name_entry.focus()

        # Development Environment
        ttk.Label(main_frame, text="Development Environment:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.env_var = tk.StringVar()
        env_combo = ttk.Combobox(main_frame, textvariable=self.env_var, width=37)
        env_combo['values'] = [
            "Python+FastAPI",
            "React+Vite", 
            "Java+SpringBoot",
            ".NET Core+EF",
            "Node.js+Express",
            "Vue.js+Vite",
            "Angular+TypeScript",
            "Django+Python",
            "Flask+Python",
            "Other"
        ]
        env_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        if not self.project:
            env_combo.current(0)

        # gRPC Server Address
        ttk.Label(main_frame, text="gRPC Server Address:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.grpc_var = tk.StringVar(value="192.168.120.238:50051")
        ttk.Entry(main_frame, textvariable=self.grpc_var, width=40).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        main_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Save", command=self._save_project).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_project_data(self):
        """Load existing project data for editing"""
        if self.project:
            self.name_var.set(self.project['name'])
            self.env_var.set(self.project['dev_environment'])
            self.grpc_var.set(self.project['grpc_server_address'])

    def _save_project(self):
        name = self.name_var.get().strip()
        env = self.env_var.get().strip()
        grpc = self.grpc_var.get().strip()

        if not name:
            show_error(self.window, "Validation Error", "Project name is required!")
            return
        if not env:
            show_error(self.window, "Validation Error", "Development environment is required!")
            return
        if not grpc:
            show_error(self.window, "Validation Error", "gRPC server address is required!")
            return

        try:
            if self.project:
                # Update existing project
                success = self.project_manager.update_project(
                    self.project['id'],
                    name=name,
                    dev_environment=env,
                    grpc_server_address=grpc
                )
                if success:
                    self.result = True
                    self.window.destroy()
                else:
                    show_error(self.window, "Update Error", "Failed to update project!")
            else:
                # Create new project
                project_id = self.project_manager.create_project(name, env, grpc)
                if project_id:
                    self.result = True
                    self.window.destroy()
                else:
                    show_error(self.window, "Create Error", "Failed to create project!")
        except Exception as e:
            operation = "update" if self.project else "create"
            show_error(self.window, f"Project {operation.title()} Error", f"Failed to {operation} project: {str(e)}", e)