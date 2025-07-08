# Project Panel - Left side project list and info - refactored

import tkinter as tk
from tkinter import ttk, messagebox
from .project_list import ProjectList
from .project_info import ProjectInfo

class ProjectPanel:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.on_project_select = None

        self._setup_components()

    def _setup_components(self):
        """Setup project list and info components"""
        # Title
        ttk.Label(self.parent, text="Projects", font=("Arial", 12, "bold")).pack(pady=5)

        # Project list
        self.project_list = ProjectList(self.parent, self)

        # Project info display
        self.project_info = ProjectInfo(self.parent)

        # Connect events
        self.project_list.on_project_select = self._on_project_select

    def _on_project_select(self, project):
        """Handle project selection"""
        self.project_info.display_project_info(project)
        if self.on_project_select:
            self.on_project_select(project)

    def load_projects(self):
        """Load projects into the list"""
        try:
            projects = self.main_window.project_manager.list_projects()
            self.project_list.load_projects(projects)
            self.main_window.update_status(f"Loaded {len(projects)} projects")

            # Clear selection
            self.project_info.display_project_info(None)
            if self.on_project_select:
                self.on_project_select(None)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {str(e)}")
            self.main_window.update_status("Error loading projects")

    def get_selected_project(self):
        """Get currently selected project"""
        return self.project_list.get_selected_project()