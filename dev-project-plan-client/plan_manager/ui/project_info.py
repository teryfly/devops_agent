# Project info display component

import tkinter as tk
from tkinter import ttk

class ProjectInfo:
    def __init__(self, parent):
        self.parent = parent
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup project info widgets"""
        info_frame = ttk.LabelFrame(self.parent, text="Project Info", padding=5)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.project_info_text = tk.Text(
            info_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 9)
        )

        info_scrollbar = ttk.Scrollbar(info_frame, command=self.project_info_text.yview)
        self.project_info_text.configure(yscrollcommand=info_scrollbar.set)

        self.project_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def display_project_info(self, project):
        """Display project information"""
        self.project_info_text.config(state=tk.NORMAL)
        self.project_info_text.delete("1.0", tk.END)

        if project:
            info = self._format_project_info(project)
            self.project_info_text.insert("1.0", info)
        else:
            self.project_info_text.insert("1.0", "No project selected")

        self.project_info_text.config(state=tk.DISABLED)

    def _format_project_info(self, project):
        """Format project information for display"""
        info = []
        info.append(f"ID: {project.get('id', '')}")
        info.append(f"Name: {project.get('name', '')}")
        info.append(f"Environment: {project.get('dev_environment', '')}")
        info.append(f"gRPC Server: {project.get('grpc_server_address', '')}")
        # 使用数据库字段名
        info.append(f"LLM Model Name: {project.get('llm_model', '')}")
        info.append(f"LLM Model Address: {project.get('llm_url', '')}")
        info.append(f"Created: {project.get('created_time', '')}")
        info.append(f"Updated: {project.get('updated_time', '')}")
        return "\n".join(info)