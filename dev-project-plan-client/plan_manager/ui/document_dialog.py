# ui/document_dialog.py
import tkinter as tk
from tkinter import ttk
from .base_dialog import BaseDialog
from .document_form import DocumentForm
from .document_actions import DocumentActions

class DocumentDialog(BaseDialog):
    def __init__(self, parent, document_manager, project, category_manager=None, document=None):
        self.document_manager = document_manager
        self.project = project
        self.category_manager = category_manager
        self.document = document
        self.is_editing = document is not None

        title = "Edit Document" if document else "New Document"
        super().__init__(parent, title, "800x700")

        self._setup_components()
        self._setup_buttons()

        if document:
            self.form.load_document_data(document)
        else:
            self.form.set_default_values()

    def _setup_components(self):
        """Setup form and actions components"""
        self.form = DocumentForm(
            self.main_frame,
            self.project,
            self.category_manager,
            self.is_editing
        )

        self.actions = DocumentActions(
            self.document_manager,
            self.form,
            self.project,
            self.document
        )

    def _setup_buttons(self):
        """Setup action buttons"""
        buttons = []

        if self.is_editing:
            buttons.extend([
                ("Execute", self.actions.execute_document),
                ("View History", self.actions.view_history)
            ])

        buttons.extend([
            (("Update" if self.is_editing else "Save"), self._save_document),
            ("Cancel", self.window.destroy)
        ])

        self.add_button_frame(buttons)

    def _save_document(self):
        """Save document using actions component"""
        success = self.actions.save_document()
        if success:
            self.result = True
            self.window.destroy()