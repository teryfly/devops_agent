# Log Display Widget for formatted feedback/log data

import tkinter as tk
from tkinter import ttk

class LogDisplay(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED, height=20)
        self.text.pack(fill=tk.BOTH, expand=True)
        self._log_lines = []

    def append_log(self, log_text):
        self._log_lines.append(log_text)
        self.refresh_display()

    def set_logs(self, logs):
        self._log_lines = logs if isinstance(logs, list) else [logs]
        self.refresh_display()

    def refresh_display(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        for line in self._log_lines:
            self.text.insert(tk.END, line + "\n")
        self.text.config(state=tk.DISABLED)

    def clear(self):
        self._log_lines = []
        self.refresh_display()