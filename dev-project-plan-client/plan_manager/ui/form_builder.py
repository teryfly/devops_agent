import tkinter as tk
from tkinter import ttk

class FormBuilder:
    def __init__(self, parent):
        self.parent = parent
        self.row = 0

    def add_entry(self, label_text, var, width=30, **kwargs):
        """Add label and entry field"""
        ttk.Label(self.parent, text=f"{label_text}:").grid(
            row=self.row, column=0, sticky="e", padx=5, pady=2
        )
        entry = ttk.Entry(self.parent, textvariable=var, width=width, **kwargs)
        entry.grid(row=self.row, column=1, sticky="ew", padx=5, pady=2)
        self.row += 1
        return entry

    def add_combobox(self, label_text, var, values, width=27, **kwargs):
        """Add label and combobox"""
        ttk.Label(self.parent, text=f"{label_text}:").grid(
            row=self.row, column=0, sticky="e", padx=5, pady=2
        )
        combo = ttk.Combobox(self.parent, textvariable=var,
                           values=values, width=width, **kwargs)
        combo.grid(row=self.row, column=1, sticky="ew", padx=5, pady=2)
        self.row += 1
        return combo

    def add_text_area(self, label_text, height=8, **kwargs):
        """Add label and text area"""
        ttk.Label(self.parent, text=f"{label_text}:").grid(
            row=self.row, column=0, sticky="ne", padx=5, pady=2
        )
        text_widget = tk.Text(self.parent, height=height, **kwargs)
        text_widget.grid(row=self.row, column=1, sticky="ew", padx=5, pady=2)
        self.row += 1
        return text_widget