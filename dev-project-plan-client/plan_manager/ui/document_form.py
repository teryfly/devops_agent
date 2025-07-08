import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from .form_builder import FormBuilder

class DocumentForm:
    def __init__(self, parent, project, category_manager, is_editing=False):
        self.parent = parent
        self.project = project
        self.category_manager = category_manager
        self.is_editing = is_editing
        self.categories = []

        self._setup_variables()
        self._setup_widgets()

    def _setup_variables(self):
        """Initialize form variables"""
        self.filename_var = tk.StringVar()
        self.tags_var = tk.StringVar()
        self.category_var = tk.StringVar()

    def _setup_widgets(self):
        """Setup form widgets"""
        self._setup_info_section()
        self._setup_tags_section()
        self._setup_content_section()

    def _setup_info_section(self):
        """Setup document info section"""
        info_frame = ttk.LabelFrame(self.parent, text="Document Info", padding=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Project info
        ttk.Label(info_frame, text=f"Project: {self.project['name']}").grid(
            row=0, column=0, sticky="w", padx=5
        )

        # Category selection
        if self.category_manager:
            self._setup_category_selection(info_frame)

        # Filename
        form_builder = FormBuilder(info_frame)
        form_builder.row = 1
        self.filename_entry = form_builder.add_entry("Filename", self.filename_var, width=50)

        info_frame.columnconfigure(1, weight=1)

    def _setup_category_selection(self, parent):
        """Setup category selection combobox"""
        ttk.Label(parent, text="Category:").grid(row=0, column=1, sticky="w", padx=20)

        self.category_combo = ttk.Combobox(
            parent, textvariable=self.category_var, state="readonly", width=20
        )

        # Load categories
        self.categories = self.category_manager.list_categories()
        category_names = [cat['name'] for cat in self.categories]
        self.category_combo['values'] = category_names

        if not self.is_editing and category_names:
            self.category_combo.current(0)

        self.category_combo.grid(row=0, column=2, sticky="w", padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', self._on_category_change)

    def _setup_tags_section(self):
        """Setup tags section"""
        tags_frame = ttk.LabelFrame(self.parent, text="Tags", padding=5)
        tags_frame.pack(fill=tk.X, pady=(0, 10))

        self.tags_entry = ttk.Entry(tags_frame, textvariable=self.tags_var, width=80)
        self.tags_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(tags_frame, text="(Separate with commas)").pack(side=tk.LEFT, padx=(10, 0))

    def _setup_content_section(self):
        """Setup content editor section"""
        content_frame = ttk.LabelFrame(self.parent, text="Content", padding=5)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.content_text = scrolledtext.ScrolledText(
            content_frame, wrap=tk.WORD, width=80, height=25, font=("Consolas", 10)
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)

        self._setup_content_buttons(content_frame)

    def _setup_content_buttons(self, parent):
        """Setup content action buttons"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        insert_btn = ttk.Button(btn_frame, text="Insert Template", command=self._insert_template)
        insert_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame, text="Clear Content", command=self._clear_content)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def _on_category_change(self, event=None):
        """Handle category selection change"""
        if not self.is_editing:
            self._set_default_filename()

    def _set_default_filename(self):
        """Set default filename based on current time and category"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category_name = self.category_var.get() or "Document"
        filename = f"{category_name}_{timestamp}.txt"
        self.filename_var.set(filename)

    def _insert_template(self):
        """Insert template content"""
        selected_category = self.get_selected_category()
        if selected_category and selected_category.get('prompt_template'):
            template = selected_category['prompt_template']

            content = f"# {selected_category['name']} Document\n\n"
            content += "## 文档内容\n请在此处编写您的具体内容...\n\n"
            content += "## 参考模板\n```\n" + template + "\n```\n\n"
            content += "## 您的内容\n请在此处编写具体的需求、计划或其他内容..."

            self.content_text.delete("1.0", tk.END)
            self.content_text.insert("1.0", content)
            self.content_text.mark_set("insert", "end-2c")
            self.content_text.see("insert")
        else:
            messagebox.showinfo("Template", "未找到当前分类的模板，或未选择分类。")

    def _clear_content(self):
        """Clear content area"""
        if messagebox.askyesno("Clear Content", "确定要清空所有内容吗？"):
            self.content_text.delete("1.0", tk.END)

    def get_selected_category(self):
        """Get selected category"""
        category_name = self.category_var.get()
        for category in self.categories:
            if category['name'] == category_name:
                return category
        return None

    def get_form_data(self):
        """Get form data as dictionary"""
        return {
            'filename': self.filename_var.get().strip(),
            'content': self.content_text.get("1.0", tk.END).strip(),
            'tags': self.tags_var.get().strip(),
            'category': self.get_selected_category()
        }

    def load_document_data(self, document):
        """Load document data for editing"""
        self.filename_var.set(document['filename'])
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", document['content'])

        # Set category
        try:
            current_category = self.category_manager.get_category(document['category_id'])
            if current_category:
                self.category_var.set(current_category['name'])
        except Exception as e:
            print(f"[WARNING] Failed to load category: {e}")

    def set_default_values(self):
        """Set default values for new document"""
        self._set_default_filename()
        placeholder = "在此输入文档内容...\n\n提示：\n- 点击 'Insert Template' 按钮可以插入当前分类的模板"
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", placeholder)