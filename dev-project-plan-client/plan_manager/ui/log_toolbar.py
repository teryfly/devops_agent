# Log toolbar component

import tkinter as tk
from tkinter import ttk

class LogToolbar:
    def __init__(self, parent, log_panel):
        self.parent = parent
        self.log_panel = log_panel
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup log toolbar widgets"""
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, pady=2)

        ttk.Label(toolbar, text="Execution Logs", font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Action buttons
        buttons = [
            ("Export", self.log_panel.export_logs),
            ("Refresh", self.log_panel.refresh_logs),
            ("Clear", self.log_panel.clear_logs)
        ]

        for text, command in buttons:
            ttk.Button(toolbar, text=text, command=command, width=8).pack(
                side=tk.RIGHT, padx=1
            )