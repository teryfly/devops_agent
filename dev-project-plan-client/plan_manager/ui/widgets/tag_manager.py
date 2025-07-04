# Tag Manager Widget for Document Tags

import tkinter as tk
from tkinter import ttk

class TagManager(ttk.Frame):
    def __init__(self, master, tags=None, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.callback = callback
        self.tags = set(tags or [])
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("&lt;Return&gt;", self.add_tag)
        self.btn = ttk.Button(self, text="Add", command=self.add_tag)
        self.btn.pack(side=tk.LEFT)
        self.tags_frame = ttk.Frame(self)
        self.tags_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.refresh_tags()

    def add_tag(self, event=None):
        tag = self.var.get().strip()
        if tag and tag not in self.tags:
            self.tags.add(tag)
            if self.callback:
                self.callback(list(self.tags))
            self.refresh_tags()
        self.var.set("")

    def remove_tag(self, tag):
        self.tags.discard(tag)
        if self.callback:
            self.callback(list(self.tags))
        self.refresh_tags()

    def refresh_tags(self):
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        for tag in self.tags:
            b = ttk.Button(self.tags_frame, text=tag + " x", command=lambda t=tag: self.remove_tag(t))
            b.pack(side=tk.LEFT, padx=2)