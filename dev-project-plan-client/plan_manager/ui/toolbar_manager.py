# ui/toolbar_manager.py
import tkinter as tk
from tkinter import ttk

class ToolbarManager:
    def __init__(self, root, menu_toolbar_manager):
        self.root = root
        self.mtm = menu_toolbar_manager
        self.search_var = tk.StringVar()
        self._setup_toolbar()

    def _setup_toolbar(self):
        """Setup toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        self._setup_action_buttons(toolbar)
        self._setup_search_section(toolbar)

    def _setup_action_buttons(self, toolbar):
        """Setup action buttons"""
        buttons = [
            ("New Project", self.mtm.new_project),
            ("Refresh", self.mtm.refresh_projects),
        ]

        for text, command in buttons:
            ttk.Button(toolbar, text=text, command=command).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

    def _setup_search_section(self, toolbar):
        """Setup search functionality"""
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(toolbar, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Search", command=self.mtm.search_documents).pack(side=tk.LEFT, padx=2)

    def get_search_text(self):
        """Get search text"""
        return self.search_var.get().strip()