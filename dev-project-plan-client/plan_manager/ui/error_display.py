# Error display component

import tkinter as tk
from tkinter import ttk, messagebox

class ErrorDisplay:
    def __init__(self, parent, message, details):
        self.parent = parent
        self.message = message
        self.details = details

        self._setup_widgets()

    def _setup_widgets(self):
        """Setup error display widgets"""
        self._setup_header()
        self._setup_details_section()

    def _setup_header(self):
        """Setup error header with icon and message"""
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Error icon
        icon_label = ttk.Label(header_frame, text="❌", font=("Arial", 20))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Error message
        msg_label = ttk.Label(
            header_frame,
            text=self.message,
            font=("Arial", 10),
            wraplength=400
        )
        msg_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _setup_details_section(self):
        """Setup details section with scrollable text"""
        details_frame = ttk.LabelFrame(self.parent, text="Error Details", padding=5)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Details text with scrollbar
        self.details_text = tk.Text(
            details_frame,
            wrap=tk.WORD,
            height=15,
            font=("Consolas", 9),
            state=tk.DISABLED
        )

        details_scrollbar = ttk.Scrollbar(
            details_frame,
            orient=tk.VERTICAL,
            command=self.details_text.yview
        )
        self.details_text.configure(yscrollcommand=details_scrollbar.set)

        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insert details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.insert("1.0", self.details)
        self.details_text.config(state=tk.DISABLED)

    def copy_error(self):
        """Copy error message to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(self.message)
            self.parent.update()
            messagebox.showinfo("Copied", "Error message copied to clipboard")
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")

    def copy_details(self):
        """Copy full error details to clipboard"""
        try:
            full_error = f"Error: {self.message}\n\nDetails:\n{self.details}"
            self.parent.clipboard_clear()
            self.parent.clipboard_append(full_error)
            self.parent.update()
            messagebox.showinfo("Copied", "Full error details copied to clipboard")
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")