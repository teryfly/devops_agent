# History viewer component

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class HistoryViewer:
    def __init__(self, parent, document_manager, document):
        self.parent = parent
        self.document_manager = document_manager
        self.document = document
        self.selected_version = None

        self._setup_widgets()

    def _setup_widgets(self):
        """Setup history viewer widgets"""
        # Split pane: versions list on left, content on right
        paned = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: versions list
        self._setup_version_list(paned)

        # Right: content display
        self._setup_content_display(paned)

    def _setup_version_list(self, paned):
        """Setup versions list"""
        left_frame = ttk.LabelFrame(paned, text="Versions", padding=5)
        left_frame.pack_propagate(False)

        columns = ("Version", "Source", "Created")
        self.version_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.version_tree.heading(col, text=col)
            self.version_tree.column(col, width=80)

        version_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.version_tree.yview)
        self.version_tree.configure(yscrollcommand=version_scroll.set)

        self.version_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        version_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.version_tree.bind('<<TreeviewSelect>>', self._on_version_select)

        paned.add(left_frame, weight=1)

    def _setup_content_display(self, paned):
        """Setup content display"""
        right_frame = ttk.LabelFrame(paned, text="Content", padding=5)

        self.content_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=60,
            height=30,
            state=tk.DISABLED,
            font=("Consolas", 10)
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)

        paned.add(right_frame, weight=2)

    def load_versions(self):
        """Load all versions of the document"""
        try:
            versions = self.document_manager.get_document_versions(self.document['id'])

            for version in versions:
                created_time = ""
                if version['created_time']:
                    created_time = version['created_time'].strftime("%Y-%m-%d %H:%M:%S")

                self.version_tree.insert("", tk.END, values=(
                    f"v{version['version']}",
                    version['source'],
                    created_time
                ))

            # Select the latest version
            if versions:
                children = self.version_tree.get_children()
                if children:
                    self.version_tree.selection_set(children[0])
                    self._on_version_select(None)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load versions: {str(e)}")

    def _on_version_select(self, event):
        """Handle version selection"""
        selection = self.version_tree.selection()
        if selection:
            item = self.version_tree.item(selection[0])
            version_str = item['values'][0]  # e.g., "v3"
            version_num = int(version_str[1:])  # Extract number

            try:
                version_doc = self.document_manager.get_document_version(self.document['id'], version_num)
                if version_doc:
                    self._display_version_content(version_doc)
                    self.selected_version = version_doc
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load version content: {str(e)}")

    def _display_version_content(self, version_doc):
        """Display version content"""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", version_doc['content'])
        self.content_text.config(state=tk.DISABLED)

    def restore_version(self):
        """Restore selected version as the current version"""
        if not self.selected_version:
            messagebox.showwarning("Selection", "Please select a version to restore.")
            return

        if messagebox.askyesno("Confirm Restore",
            f"Are you sure you want to restore version {self.selected_version['version']}?\n\n" +
            "This will create a new version with the selected content."):
            try:
                new_doc_id = self.document_manager.update_document(
                    self.document['id'],
                    self.selected_version['content']
                )
                if new_doc_id:
                    messagebox.showinfo("Success", "Version restored successfully!")
                    self.load_versions()  # Refresh the list
                else:
                    messagebox.showerror("Error", "Failed to restore version!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore version: {str(e)}")