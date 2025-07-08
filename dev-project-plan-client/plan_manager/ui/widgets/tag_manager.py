# Tag Manager Widget for Document Tags - refactored

import tkinter as tk
from tkinter import ttk

class TagManager(ttk.Frame):
    def __init__(self, master, tags=None, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.callback = callback
        self.tags = set(tags or [])
        self.max_tags = 20  # Limit number of tags

        self._setup_variables()
        self._setup_widgets()
        self.refresh_tags()

    def _setup_variables(self):
        """Initialize tag manager variables"""
        self.var = tk.StringVar()
        self.var.trace('w', self._on_text_change)

    def _setup_widgets(self):
        """Setup tag manager widgets"""
        # Input section
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, pady=2)

        ttk.Label(input_frame, text="Add Tag:").pack(side=tk.LEFT, padx=(0, 5))

        self.entry = ttk.Entry(input_frame, textvariable=self.var, width=20)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self.add_tag)
        self.entry.bind("<KeyPress>", self._on_key_press)

        self.add_btn = ttk.Button(input_frame, text="Add", command=self.add_tag, width=6)
        self.add_btn.pack(side=tk.LEFT)

        # Tags display section
        self.tags_frame = ttk.Frame(self)
        self.tags_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Scrollable frame for tags
        self._setup_scrollable_tags()

    def _setup_scrollable_tags(self):
        """Setup scrollable area for tags"""
        canvas = tk.Canvas(self.tags_frame, height=100)
        scrollbar = ttk.Scrollbar(self.tags_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_tag(self, event=None):
        """Add a new tag"""
        tag = self.var.get().strip().lower()

        if not tag:
            return

        if tag in self.tags:
            self.var.set("")
            return

        if len(self.tags) >= self.max_tags:
            tk.messagebox.showwarning("Tag Limit", f"Maximum {self.max_tags} tags allowed")
            return

        if self._is_valid_tag(tag):
            self.tags.add(tag)
            self._trigger_callback()
            self.refresh_tags()
            self.var.set("")
            self.entry.focus()

    def remove_tag(self, tag):
        """Remove a tag"""
        self.tags.discard(tag)
        self._trigger_callback()
        self.refresh_tags()

    def clear_tags(self):
        """Clear all tags"""
        self.tags.clear()
        self._trigger_callback()
        self.refresh_tags()

    def set_tags(self, tags):
        """Set tags from external source"""
        self.tags = set(tags or [])
        self.refresh_tags()

    def get_tags(self):
        """Get current tags as list"""
        return list(self.tags)

    def refresh_tags(self):
        """Refresh tag display"""
        # Clear existing tag widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create tag buttons
        row, col = 0, 0
        max_cols = 4

        for tag in sorted(self.tags):
            tag_frame = ttk.Frame(self.scrollable_frame)
            tag_frame.grid(row=row, column=col, padx=2, pady=2, sticky="ew")

            tag_label = ttk.Label(tag_frame, text=tag, background="lightblue",
                                relief="solid", padding=2)
            tag_label.pack(side=tk.LEFT)

            remove_btn = ttk.Button(tag_frame, text="×", width=3,
                                  command=lambda t=tag: self.remove_tag(t))
            remove_btn.pack(side=tk.LEFT)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Add clear all button if tags exist
        if self.tags:
            clear_frame = ttk.Frame(self.scrollable_frame)
            clear_frame.grid(row=row+1, column=0, columnspan=max_cols, pady=5)

            ttk.Button(clear_frame, text="Clear All",
                      command=self.clear_tags).pack()

    def _is_valid_tag(self, tag):
        """Validate tag format"""
        if len(tag) < 1 or len(tag) > 30:
            return False

        # Allow alphanumeric, hyphen, underscore
        allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
        return all(c in allowed_chars for c in tag)

    def _trigger_callback(self):
        """Trigger callback with current tags"""
        if self.callback:
            self.callback(list(self.tags))

    def _on_text_change(self, *args):
        """Handle text change in entry"""
        text = self.var.get()
        # Enable/disable add button based on text
        self.add_btn.config(state="normal" if text.strip() else "disabled")

    def _on_key_press(self, event):
        """Handle key press events"""
        if event.keysym == "Escape":
            self.var.set("")