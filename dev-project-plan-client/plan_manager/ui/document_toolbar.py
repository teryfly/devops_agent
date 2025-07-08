import tkinter as tk
from tkinter import ttk

class DocumentToolbar:
    def __init__(self, parent, document_panel):
        self.parent = parent
        self.document_panel = document_panel
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup document toolbar widgets"""
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, pady=2)

        ttk.Label(toolbar, text="Documents", font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Action buttons
        buttons = [
            ("Execute", self.document_panel.execute_document),
            ("Delete", self.document_panel.delete_document),
            ("Edit", self.document_panel.edit_document),
            ("New", self.document_panel.new_document)
        ]

        for text, command in buttons:
            ttk.Button(toolbar, text=text, command=command, width=8).pack(
                side=tk.RIGHT, padx=1
            )