# UI utility functions

import tkinter as tk
from tkinter import ttk
import os
import sys

def center_window(window, parent=None):
    """Center window on screen or parent"""
    window.update_idletasks()

    if parent:
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (window.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (window.winfo_height() // 2)
    else:
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)

    window.geometry(f"+{x}+{y}")

def validate_input(value, input_type, min_val=None, max_val=None):
    """Validate input based on type and constraints"""
    try:
        if input_type == 'int':
            val = int(value)
            if min_val is not None and val < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val is not None and val > max_val:
                return False, f"Value must be at most {max_val}"
            return True, val
        elif input_type == 'float':
            val = float(value)
            if min_val is not None and val < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val is not None and val > max_val:
                return False, f"Value must be at most {max_val}"
            return True, val
        elif input_type == 'string':
            if min_val is not None and len(value) < min_val:
                return False, f"Text must be at least {min_val} characters"
            if max_val is not None and len(value) > max_val:
                return False, f"Text must be at most {max_val} characters"
            return True, value
        else:
            return True, value
    except ValueError:
        return False, f"Invalid {input_type} value"

def safe_get_attribute(obj, attr, default=None):
    """Safely get attribute from object"""
    try:
        return getattr(obj, attr, default)
    except:
        return default

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text, max_length=50, suffix="..."):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def create_tooltip(widget, text):
    """Create tooltip for widget"""
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        label = ttk.Label(tooltip, text=text, background="lightyellow",
                         relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack()

        widget.tooltip = tooltip

    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

class ProgressDialog:
    """Simple progress dialog"""
    def __init__(self, parent, title="Progress", message="Processing..."):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("300x100")
        self.window.transient(parent)
        self.window.grab_set()

        center_window(self.window, parent)

        ttk.Label(self.window, text=message).pack(pady=10)

        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)

        self.progress.start()

    def close(self):
        """Close progress dialog"""
        self.progress.stop()
        self.window.destroy()