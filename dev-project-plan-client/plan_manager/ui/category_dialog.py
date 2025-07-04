# Category management dialog

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CategoryDialog:
    def __init__(self, parent, category_manager):
        self.parent = parent
        self.category_manager = category_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("Category Management")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        self._setup_widgets()
        self._load_categories()

    def _setup_widgets(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Category list
        list_frame = ttk.LabelFrame(main_frame, text="Categories", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for categories
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

        # Category details
        detail_frame = ttk.LabelFrame(main_frame, text="Category Details", padding=10)
        detail_frame.pack(fill=tk.X, pady=10)

        ttk.Label(detail_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.name_var, width=50).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(detail_frame, text="Method:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.method_var = tk.StringVar()
        method_combo = ttk.Combobox(detail_frame, textvariable=self.method_var, state="readonly", width=47)
        method_combo['values'] = ["PlanGetRequest", "PlanExecuteRequest", "PlanThenExecuteRequest"]
        method_combo.grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(detail_frame, text="Auto-save Category:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.auto_save_var = tk.StringVar()
        self.auto_save_combo = ttk.Combobox(detail_frame, textvariable=self.auto_save_var, state="readonly", width=47)
        self.auto_save_combo.grid(row=2, column=1, sticky="ew", padx=5)

        ttk.Label(detail_frame, text="Prompt Template:").grid(row=3, column=0, sticky="ne", padx=5, pady=2)
        self.template_text = tk.Text(detail_frame, height=8, width=60, wrap=tk.WORD)
        self.template_text.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        detail_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="New Category", command=self._new_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Category", command=self._save_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Category", command=self._delete_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

        self.selected_category = None

    def _load_categories(self):
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

        # Load auto-save combo options
        self.auto_save_combo['values'] = ["None"] + [cat['name'] for cat in categories]

    def _on_category_select(self, event):
        """Handle category selection"""
        selection = self.category_tree.selection()
        if selection:
            item = self.category_tree.item(selection[0])
            cat_id = item['values'][0]
            self.selected_category = self.category_manager.get_category(cat_id)
            self._display_category_details()

    def _display_category_details(self):
        """Display selected category details"""
        if self.selected_category:
            self.name_var.set(self.selected_category['name'])
            self.method_var.set(self.selected_category['message_method'])
            
            # Set auto-save category
            if self.selected_category['auto_save_category_id']:
                auto_save_cat = self.category_manager.get_category(self.selected_category['auto_save_category_id'])
                self.auto_save_var.set(auto_save_cat['name'] if auto_save_cat else "None")
            else:
                self.auto_save_var.set("None")
            
            self.template_text.delete("1.0", tk.END)
            self.template_text.insert("1.0", self.selected_category['prompt_template'])

    def _new_category(self):
        """Clear form for new category"""
        self.selected_category = None
        self.name_var.set("")
        self.method_var.set("PlanGetRequest")
        self.auto_save_var.set("None")
        self.template_text.delete("1.0", tk.END)
        self.template_text.insert("1.0", "Please generate plan based on:\n\nEnvironment: {env}\n\nContent:\n{doc}")

    def _save_category(self):
        """Save category"""
        name = self.name_var.get().strip()
        method = self.method_var.get().strip()
        template = self.template_text.get("1.0", tk.END).strip()
        auto_save = self.auto_save_var.get().strip()

        if not name or not method or not template:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Get auto-save category ID
        auto_save_id = None
        if auto_save and auto_save != "None":
            categories = self.category_manager.list_categories()
            for cat in categories:
                if cat['name'] == auto_save:
                    auto_save_id = cat['id']
                    break

        try:
            if self.selected_category:
                # Update existing category
                success = self.category_manager.update_category(
                    self.selected_category['id'],
                    name=name,
                    prompt_template=template,
                    message_method=method,
                    auto_save_category_id=auto_save_id
                )
                if success:
                    messagebox.showinfo("Success", "Category updated successfully!")
                else:
                    messagebox.showerror("Error", "Failed to update category!")
            else:
                # Create new category
                cat_id = self.category_manager.create_category(
                    name, template, method, auto_save_id, False
                )
                if cat_id:
                    messagebox.showinfo("Success", "Category created successfully!")
                else:
                    messagebox.showerror("Error", "Failed to create category!")
            
            self._load_categories()
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {str(e)}")

    def _delete_category(self):
        """Delete selected category"""
        if not self.selected_category:
            messagebox.showwarning("Selection", "Please select a category to delete.")
            return

        if self.selected_category['is_builtin']:
            messagebox.showwarning("Cannot Delete", "Built-in categories cannot be deleted.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{self.selected_category['name']}'?"):
            if self.category_manager.delete_category(self.selected_category['id']):
                messagebox.showinfo("Success", "Category deleted successfully!")
                self._load_categories()
                self._new_category()  # Clear form
            else:
                messagebox.showerror("Error", "Failed to delete category!")