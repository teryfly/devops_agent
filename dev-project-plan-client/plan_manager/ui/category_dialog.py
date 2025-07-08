# ui/category_dialog.py
from .base_dialog import BaseDialog
from .category_form import CategoryForm
from .category_list import CategoryList

class CategoryDialog(BaseDialog):
    def __init__(self, parent, category_manager):
        self.category_manager = category_manager
        super().__init__(parent, "Category Management", "800x600")

        self._setup_components()
        self._setup_buttons()
        self._load_data()

    def _setup_components(self):
        """Setup category list and form components"""
        self.category_list = CategoryList(self.main_frame, self.category_manager)
        self.category_form = CategoryForm(self.main_frame, self.category_manager)

        # Connect events
        self.category_list.on_category_select = self.category_form.display_category_details

    def _setup_buttons(self):
        """Setup action buttons"""
        buttons = [
            ("New Category", self.category_form.new_category),
            ("Save Category", self._save_category),
            ("Delete Category", self._delete_category),
            ("Close", self.window.destroy)
        ]
        self.add_button_frame(buttons)

    def _load_data(self):
        """Load initial data"""
        self.category_list.load_categories()
        self.category_form.load_auto_save_options()

    def _save_category(self):
        """Save category using form"""
        if self.category_form.save_category():
            self.category_list.load_categories()
            self.category_form.load_auto_save_options()

    def _delete_category(self):
        """Delete selected category"""
        if self.category_form.delete_category():
            self.category_list.load_categories()
            self.category_form.load_auto_save_options()
            self.category_form.new_category()