# Project management dialog - refactored

from .base_dialog import BaseDialog
from .project_form import ProjectForm

class ProjectDialog(BaseDialog):
    def __init__(self, parent, project_manager, project=None):
        self.project_manager = project_manager
        self.project = project

        title = "Edit Project" if project else "Project Management"
        super().__init__(parent, title, "500x300")

        self._setup_components()
        self._setup_buttons()

        if project:
            self.form.load_project_data(project)

    def _setup_components(self):
        """Setup form component"""
        self.form = ProjectForm(self.main_frame, self.project)

    def _setup_buttons(self):
        """Setup action buttons"""
        buttons = [
            ("Save", self._save_project),
            ("Cancel", self.window.destroy)
        ]
        self.add_button_frame(buttons)

    def _save_project(self):
        """Save project using form"""
        if self.form.save_project(self.project_manager):
            self.result = True
            self.window.destroy()