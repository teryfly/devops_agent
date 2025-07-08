import tkinter as tk
from tkinter import ttk

class CategoryList:
    def __init__(self, parent, category_manager):
        self.parent = parent
        self.category_manager = category_manager
        self.on_category_select = None
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup category list widgets"""
        list_frame = ttk.LabelFrame(self.parent, text="Categories", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Name", "Method", "Built-in")
        self.category_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=scrollbar.set)

        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.category_tree.bind('<<TreeviewSelect>>', self._on_category_select)

    def load_categories(self):
        """Load categories into the tree"""
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        categories = self.category_manager.list_categories()
        for cat in categories:
            self.category_tree.insert("", tk.END, values=(
                cat['id'],
                cat['name'],
                cat['message_method'],
                "Yes" if cat['is_builtin'] else "No"
            ))

    def _on_category_select(self, event):
        """Handle category selection"""
        selection = self.category_tree.selection()
        if selection:
            item = self.category_tree.item(selection[0])
            cat_id = item['values'][0]
            selected_category = self.category_manager.get_category(cat_id)
            if self.on_category_select:
                self.on_category_select(selected_category)

    def get_selected_category(self):
        """Get currently selected category"""
        selection = self.category_tree.selection()
        if selection:
            item = self.category_tree.item(selection[0])
            cat_id = item['values'][0]
            return self.category_manager.get_category(cat_id)
        return None