# Simple Document Editor Widget (Tkinter Text wrapper) - refactored

import tkinter as tk
from tkinter import ttk

class DocumentEditor(ttk.Frame):
    def __init__(self, master, initial_text="", **kwargs):
        super().__init__(master, **kwargs)
        self._setup_variables()
        self._setup_widgets(initial_text)

    def _setup_variables(self):
        """Initialize editor variables"""
        self.content_changed = False
        self.on_change_callback = None

    def _setup_widgets(self, initial_text):
        """Setup editor widgets"""
        # Text widget with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=24,
            font=("Consolas", 10),
            undo=True,
            maxundo=50
        )

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insert initial text
        if initial_text:
            self.text.insert("1.0", initial_text)

        # Bind change events
        self.text.bind('<<Modified>>', self._on_text_changed)
        self.text.bind('<Control-z>', lambda e: self.text.edit_undo())
        self.text.bind('<Control-y>', lambda e: self.text.edit_redo())

    def get_content(self):
        """Get editor content"""
        return self.text.get("1.0", tk.END).rstrip()

    def set_content(self, content):
        """Set editor content"""
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.edit_modified(False)
        self.content_changed = False

    def insert_text(self, text, position=None):
        """Insert text at specified position or cursor"""
        if position is None:
            position = tk.INSERT
        self.text.insert(position, text)

    def clear_content(self):
        """Clear all content"""
        self.text.delete("1.0", tk.END)
        self.content_changed = False

    def set_readonly(self, readonly=True):
        """Set editor to readonly mode"""
        state = tk.DISABLED if readonly else tk.NORMAL
        self.text.config(state=state)

    def focus_editor(self):
        """Focus the text editor"""
        self.text.focus_set()

    def set_change_callback(self, callback):
        """Set callback for content changes"""
        self.on_change_callback = callback

    def _on_text_changed(self, event):
        """Handle text change events"""
        if self.text.edit_modified():
            self.content_changed = True
            if self.on_change_callback:
                self.on_change_callback()
            self.text.edit_modified(False)

    def has_unsaved_changes(self):
        """Check if there are unsaved changes"""
        return self.content_changed

    def mark_saved(self):
        """Mark content as saved"""
        self.content_changed = False