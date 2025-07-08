import tkinter as tk
from tkinter import ttk, messagebox
from .form_builder import FormBuilder

class CategoryForm:
    def __init__(self, parent, category_manager):
        self.parent = parent
        self.category_manager = category_manager
        self.selected_category = None

        self._setup_variables()
        self._setup_widgets()

    def _setup_variables(self):
        """Initialize form variables"""
        self.name_var = tk.StringVar()
        self.method_var = tk.StringVar()
        self.auto_save_var = tk.StringVar()

    def _setup_widgets(self):
        """Setup form widgets"""
        detail_frame = ttk.LabelFrame(self.parent, text="Category Details", padding=10)
        detail_frame.pack(fill=tk.X, pady=10)

        form_builder = FormBuilder(detail_frame)

        # Basic fields
        form_builder.add_entry("Name", self.name_var, width=50)

        form_builder.add_combobox(
            "Method", self.method_var,
            ["PlanGetRequest", "PlanExecuteRequest", "PlanThenExecuteRequest"],
            width=47
        )

        # Auto-save category combobox
        self.auto_save_combo = form_builder.add_combobox(
            "Auto-save Category", self.auto_save_var, [], width=47
        )

        # Template text area
        self.template_text = form_builder.add_text_area(
            "Prompt Template", height=8, width=60, wrap=tk.WORD
        )

        detail_frame.columnconfigure(1, weight=1)

    def load_auto_save_options(self):
        """Load auto-save combo options"""
        categories = self.category_manager.list_categories()
        self.auto_save_combo['values'] = ["None"] + [cat['name'] for cat in categories]

    def display_category_details(self, category):
        """Display selected category details"""
        self.selected_category = category
        if category:
            self.name_var.set(category['name'])
            self.method_var.set(category['message_method'])

            # Set auto-save category
            if category['auto_save_category_id']:
                auto_save_cat = self.category_manager.get_category(category['auto_save_category_id'])
                self.auto_save_var.set(auto_save_cat['name'] if auto_save_cat else "None")
            else:
                self.auto_save_var.set("None")

            self.template_text.delete("1.0", tk.END)
            self.template_text.insert("1.0", category['prompt_template'])

    def new_category(self):
        """Clear form for new category"""
        self.selected_category = None
        self.name_var.set("")
        self.method_var.set("PlanGetRequest")
        self.auto_save_var.set("None")
        self.template_text.delete("1.0", tk.END)
        self.template_text.insert("1.0", "Please generate plan based on:\n\nEnvironment: {env}\n\nContent:\n{doc}")

    def save_category(self):
        """Save category"""
        if not self._validate_form():
            return False

        try:
            name = self.name_var.get().strip()
            method = self.method_var.get().strip()
            template = self.template_text.get("1.0", tk.END).strip()
            auto_save_id = self._get_auto_save_id()

            if self.selected_category:
                success = self.category_manager.update_category(
                    self.selected_category['id'],
                    name=name,
                    prompt_template=template,
                    message_method=method,
                    auto_save_category_id=auto_save_id
                )
                message = "Category updated successfully!" if success else "Failed to update category!"
            else:
                cat_id = self.category_manager.create_category(
                    name, template, method, auto_save_id, False
                )
                success = bool(cat_id)
                message = "Category created successfully!" if success else "Failed to create category!"

            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

            return success

        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {str(e)}")
            return False

    def delete_category(self):
        """Delete selected category"""
        if not self.selected_category:
            messagebox.showwarning("Selection", "Please select a category to delete.")
            return False

        if self.selected_category['is_builtin']:
            messagebox.showwarning("Cannot Delete", "Built-in categories cannot be deleted.")
            return False

        if messagebox.askyesno("Confirm Delete",
            f"Are you sure you want to delete category '{self.selected_category['name']}'?"):

            try:
                if self.category_manager.delete_category(self.selected_category['id']):
                    messagebox.showinfo("Success", "Category deleted successfully!")
                    return True
                else:
                    messagebox.showerror("Error", "Failed to delete category!")
                    return False
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {str(e)}")
                return False

    def _validate_form(self):
        """Validate form data"""
        name = self.name_var.get().strip()
        method = self.method_var.get().strip()
        template = self.template_text.get("1.0", tk.END).strip()

        if not name or not method or not template:
            messagebox.showerror("Error", "All fields are required!")
            return False
        return True

    def _get_auto_save_id(self):
        """Get auto-save category ID"""
        auto_save = self.auto_save_var.get().strip()
        if auto_save and auto_save != "None":
            categories = self.category_manager.list_categories()
            for cat in categories:
                if cat['name'] == auto_save:
                    return cat['id']
        return None