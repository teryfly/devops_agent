# Category Tabs Manager - refactored

import tkinter as tk
from tkinter import ttk, messagebox

class CategoryTabsManager:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.categories = []
        self.on_tab_change = None

        self._setup_widgets()

    def _setup_widgets(self):
        """Setup category tabs"""
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

    def load_categories(self):
        """Load categories as tabs"""
        self._clear_tabs()

        try:
            self.categories = self.main_window.category_manager.list_categories()
            self._create_category_tabs()
            self._select_first_tab()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")

    def _clear_tabs(self):
        """Clear existing tabs"""
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

    def _create_category_tabs(self):
        """Create tabs for each category"""
        for category in self.categories:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=category['name'])

            self._setup_tab_content(tab_frame, category)

    def _setup_tab_content(self, tab_frame, category):
        """Setup content for a category tab"""
        # Category info
        info_text = self._format_category_info(category)
        info_label = ttk.Label(tab_frame, text=info_text, font=("Arial", 9))
        info_label.pack(pady=10)

        # Prompt template preview
        self._add_template_preview(tab_frame, category)

    def _format_category_info(self, category):
        """Format category information"""
        info = f"Category: {category['name']}\n"
        info += f"Method: {category['message_method']}\n"
        info += f"Built-in: {'Yes' if category['is_builtin'] else 'No'}"
        return info

    def _add_template_preview(self, tab_frame, category):
        """Add template preview to tab"""
        template_frame = ttk.LabelFrame(tab_frame, text="Prompt Template", padding=5)
        template_frame.pack(fill=tk.X, padx=10, pady=5)

        template = category['prompt_template']
        if len(template) > 200:
            template = template[:200] + "..."

        template_text = tk.Text(
            template_frame,
            height=6,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 9)
        )
        template_text.pack(fill=tk.BOTH, expand=True)

        template_text.config(state=tk.NORMAL)
        template_text.insert("1.0", template)
        template_text.config(state=tk.DISABLED)

    def _select_first_tab(self):
        """Select first tab if available"""
        if self.categories:
            self.notebook.select(0)
            self._trigger_tab_change()

    def _on_tab_changed(self, event):
        """Handle tab change event"""
        self._trigger_tab_change()

    def _trigger_tab_change(self):
        """Trigger tab change callback"""
        try:
            selected_tab_index = self.notebook.index(self.notebook.select())
            if 0 <= selected_tab_index < len(self.categories):
                category = self.categories[selected_tab_index]
                if self.on_tab_change:
                    self.on_tab_change(category)
        except Exception:
            if self.on_tab_change:
                self.on_tab_change(None)

    def get_current_category(self):
        """Get currently selected category"""
        try:
            selected_tab_index = self.notebook.index(self.notebook.select())
            if 0 <= selected_tab_index < len(self.categories):
                return self.categories[selected_tab_index]
        except Exception:
            pass
        return None