import tkinter as tk
from tkinter import ttk

class BaseDialog:
    def __init__(self, parent, title, size="400x300"):
        self.parent = parent
        self.result = None

        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(size)
        self.window.transient(parent)
        self.window.grab_set()

        self._center_window()
        self._setup_main_frame()

    def _center_window(self):
        """Center dialog on parent"""
        try:
            x = self.parent.winfo_rootx() + 50
            y = self.parent.winfo_rooty() + 50
            self.window.geometry(f"+{x}+{y}")
        except:
            pass

    def _setup_main_frame(self):
        """Setup main frame with padding"""
        self.main_frame = ttk.Frame(self.window, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def add_button_frame(self, buttons):
        """Add button frame with specified buttons"""
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        for text, command in buttons:
            side = tk.RIGHT if text in ['Save', 'OK', 'Cancel'] else tk.LEFT
            ttk.Button(btn_frame, text=text, command=command).pack(side=side, padx=5)