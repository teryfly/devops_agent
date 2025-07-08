# Project list component

import tkinter as tk
from tkinter import ttk

class ProjectList:
    def __init__(self, parent, project_panel):
        self.parent = parent
        self.project_panel = project_panel
        self.projects = []
        self.on_project_select = None

        self._setup_widgets()

    def _setup_widgets(self):
        """Setup project list widgets"""
        list_frame = ttk.Frame(self.parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.project_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.project_listbox.yview)
        self.project_listbox.configure(yscrollcommand=scrollbar.set)

        self.project_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Event bindings
        self.project_listbox.bind('<<ListboxSelect>>', self._on_listbox_select)
        self.project_listbox.bind('<Double-Button-1>', self._on_double_click)

    def load_projects(self, projects):
        """Load projects into the list"""
        self.project_listbox.delete(0, tk.END)
        self.projects = projects

        for project in projects:
            display_text = f"{project['id']} - {project['name']}"
            self.project_listbox.insert(tk.END, display_text)

    def get_selected_project(self):
        """Get currently selected project"""
        selection = self.project_listbox.curselection()
        if selection:
            index = selection[0]
            return self.projects[index]
        return None

    def _on_listbox_select(self, event):
        """Handle project list selection"""
        selected_project = self.get_selected_project()
        if self.on_project_select:
            self.on_project_select(selected_project)

    def _on_double_click(self, event):
        """Handle double click to edit project"""
        selected_project = self.get_selected_project()
        if selected_project:
            self.project_panel.main_window.menu_toolbar.edit_project()