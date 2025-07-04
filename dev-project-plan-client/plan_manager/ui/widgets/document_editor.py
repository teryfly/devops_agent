# Simple Document Editor Widget (Tkinter Text wrapper)

import tkinter as tk
from tkinter import ttk, messagebox

class DocumentEditor(ttk.Frame):
    def __init__(self, master, initial_text="", **kwargs):
        super().__init__(master, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, width=80, height=24)
        self.text.insert("1.0", initial_text)
        self.text.pack(fill=tk.BOTH, expand=True)

    def get_content(self):
        return self.text.get("1.0", tk.END).rstrip()

    def set_content(self, content):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)