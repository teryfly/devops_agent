# ui/project_dialog.py

import tkinter as tk
from tkinter import ttk, messagebox
from .base_dialog import BaseDialog

class ProjectDialog(BaseDialog):
    def __init__(self, parent, project_manager, project=None):
        self.project_manager = project_manager
        self.project = project  # None表示新建，否则为dict
        super().__init__(
            parent,
            "Edit Project" if project else "New Project",
            "500x340"
        )
        self._setup_fields()
        self._setup_buttons()
        if self.project:
            self._populate_fields()  # 若为编辑，填充内容

    def _setup_fields(self):
        frm = self.content_frame

        ttk.Label(frm, text="项目名称:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.name_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.name_var, width=36).grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(frm, text="gRPC地址:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        self.addr_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.addr_var, width=36).grid(row=1, column=1, padx=8, pady=8)

        ttk.Label(frm, text="开发环境:").grid(row=2, column=0, padx=8, pady=8, sticky="e")
        self.env_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.env_var, width=36).grid(row=2, column=1, padx=8, pady=8)

        ttk.Label(frm, text="LLM模型名称:").grid(row=3, column=0, padx=8, pady=8, sticky="e")
        self.llm_name_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.llm_name_var, width=36).grid(row=3, column=1, padx=8, pady=8)

        ttk.Label(frm, text="LLM模型地址:").grid(row=4, column=0, padx=8, pady=8, sticky="e")
        self.llm_addr_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.llm_addr_var, width=36).grid(row=4, column=1, padx=8, pady=8)

    def _populate_fields(self):
        """编辑模式下，将已有项目数据填入输入框"""
        self.name_var.set(self.project.get("name", ""))
        self.addr_var.set(self.project.get("grpc_server_address", ""))
        self.env_var.set(self.project.get("dev_environment", ""))
        # 这里字段名要与数据库一致
        self.llm_name_var.set(self.project.get("llm_model", ""))
        self.llm_addr_var.set(self.project.get("llm_url", ""))

    def _setup_buttons(self):
        buttons = [
            ("保存", self._save_project),
            ("取消", self.window.destroy)
        ]
        self.add_button_frame(buttons)

    def _save_project(self):
        name = self.name_var.get().strip()
        addr = self.addr_var.get().strip()
        env = self.env_var.get().strip()
        llm_name = self.llm_name_var.get().strip()
        llm_addr = self.llm_addr_var.get().strip()
        if not name:
            messagebox.showerror("校验失败", "项目名称不能为空！")
            return

        try:
            if self.project:  # 编辑
                self.project_manager.update_project(
                    self.project['id'],
                    name=name,
                    dev_environment=env,
                    grpc_server_address=addr,
                    llm_model=llm_name,
                    llm_url=llm_addr
                )
            else:  # 新建
                self.project_manager.create_project(
                    name,
                    env,
                    addr,
                    llm_name,
                    llm_addr
                )
            self.result = True
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("保存失败", f"保存项目失败：{e}")