# ui\document_dialog.py 的修正版本

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DocumentDialog:
    def __init__(self, parent, document_manager, project, category_manager=None, document=None):
        self.parent = parent
        self.document_manager = document_manager
        self.project = project
        self.category_manager = category_manager
        self.document = document
        self.result = None
        self.is_editing = document is not None
        
        self.window = tk.Toplevel(parent)
        self.window.title("New Document" if not document else f"Edit Document - {document['filename']}")
        self.window.geometry("800x700")
        self.window.transient(parent)
        self.window.grab_set()
        self._setup_widgets()
        if document:
            self._load_document_data()
        else:
            self._set_default_filename()

    def _setup_widgets(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header info
        info_frame = ttk.LabelFrame(main_frame, text="Document Info", padding=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Project info (first row)
        ttk.Label(info_frame, text=f"Project: {self.project['name']}").grid(row=0, column=0, sticky="w", padx=5)
        
        # Category selection - 现在编辑时也显示
        if self.category_manager:
            ttk.Label(info_frame, text="Category:").grid(row=0, column=1, sticky="w", padx=20)
            self.category_var = tk.StringVar()
            self.category_combo = ttk.Combobox(info_frame, textvariable=self.category_var, state="readonly", width=20)
            
            # Load categories
            categories = self.category_manager.list_categories()
            category_names = [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
            
            # Set default selection
            if not self.is_editing and category_names:
                self.category_combo.current(0)
            # For editing, will be set in _load_document_data
            
            self.category_combo.grid(row=0, column=2, sticky="w", padx=5)
            self.category_combo.bind('<<ComboboxSelected>>', self._on_category_change)
            
            self.categories = categories
        else:
            # Fallback if no category manager
            ttk.Label(info_frame, text="Category: Unknown").grid(row=0, column=1, sticky="w", padx=20)

        # Filename (second row)
        ttk.Label(info_frame, text="Filename:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.filename_var = tk.StringVar()
        filename_entry = ttk.Entry(info_frame, textvariable=self.filename_var, width=50)
        filename_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        info_frame.columnconfigure(1, weight=1)

        # Tags
        tags_frame = ttk.LabelFrame(main_frame, text="Tags", padding=5)
        tags_frame.pack(fill=tk.X, pady=(0, 10))

        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(tags_frame, textvariable=self.tags_var, width=80)
        self.tags_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(tags_frame, text="(Separate with commas)").pack(side=tk.LEFT, padx=(10, 0))

        # Content editor
        content_frame = ttk.LabelFrame(main_frame, text="Content", padding=5)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.content_text = scrolledtext.ScrolledText(
            content_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            font=("Consolas", 10)
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # 模板内容按钮
        template_btn_frame = ttk.Frame(content_frame)
        template_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(template_btn_frame, text="Insert Template", 
                  command=self._insert_template_content).pack(side=tk.LEFT)
        ttk.Button(template_btn_frame, text="Clear Content", 
                  command=self._clear_content).pack(side=tk.LEFT, padx=(5, 0))

        # Placeholder text for new documents
        if not self.is_editing:
            self._insert_placeholder_content()

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        save_text = "Update" if self.is_editing else "Save"
        ttk.Button(btn_frame, text=save_text, command=self._save_document).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        
        if self.is_editing:
            ttk.Button(btn_frame, text="Execute", command=self._execute_document).pack(side=tk.LEFT)
            ttk.Button(btn_frame, text="View History", command=self._view_history).pack(side=tk.LEFT, padx=(5, 0))

    def _on_category_change(self, event=None):
        """Handle category selection change"""
        if not self.is_editing:
            self._set_default_filename()

    def _insert_placeholder_content(self):
        """Insert placeholder content for new documents"""
        placeholder = "在此输入文档内容...\n\n"
        placeholder += "提示：\n"
        placeholder += "- 点击 'Insert Template' 按钮可以插入当前分类的模板\n"
        placeholder += "- 可以使用占位符：{env} (项目环境), {doc} (文档内容)\n"
        placeholder += "- 使用 'Clear Content' 按钮清空内容重新开始"
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", placeholder)

    def _insert_template_content(self):
        """Insert template content based on selected category"""
        if hasattr(self, 'category_var'):
            selected_category = self._get_selected_category()
            if selected_category:
                template = selected_category.get('prompt_template', '')
                if template:
                    # Clear current content
                    self.content_text.delete("1.0", tk.END)
                    
                    # Insert template with explanation
                    content = f"# {selected_category['name']} Document\n\n"
                    content += "## 文档内容\n"
                    content += "请在此处编写您的具体内容...\n\n"
                    content += "## 参考模板\n"
                    content += "以下是该分类的提示模板，供参考：\n\n"
                    content += "```\n"
                    content += template + "\n"
                    content += "```\n\n"
                    content += "## 占位符说明\n"
                    content += "- {env}: 执行时将替换为项目的开发环境配置\n"
                    content += "- {doc}: 执行时将替换为当前文档的完整内容\n\n"
                    content += "## 您的内容\n"
                    content += "请在此处编写具体的需求、计划或其他内容..."
                    
                    self.content_text.insert("1.0", content)
                    
                    # 将光标定位到最后的编辑区域
                    self.content_text.mark_set("insert", "end-2c")
                    self.content_text.see("insert")
                    return

        messagebox.showinfo("Template", "未找到当前分类的模板，或未选择分类。")

    def _clear_content(self):
        """Clear content area"""
        if messagebox.askyesno("Clear Content", "确定要清空所有内容吗？"):
            self.content_text.delete("1.0", tk.END)

    def _set_default_filename(self):
        """Set default filename based on current time and category"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if hasattr(self, 'category_var'):
            category_name = self.category_var.get()
        else:
            category_name = "Document"
        filename = f"{category_name}_{timestamp}.txt"
        self.filename_var.set(filename)

    def _load_document_data(self):
        """Load existing document data for editing"""
        if self.document:
            self.filename_var.set(self.document['filename'])
            self.content_text.delete("1.0", tk.END)
            self.content_text.insert("1.0", self.document['content'])
            
            # Set category selection for editing
            if hasattr(self, 'category_var') and hasattr(self, 'categories'):
                try:
                    current_category = self.category_manager.get_category(self.document['category_id'])
                    if current_category:
                        self.category_var.set(current_category['name'])
                    else:
                        # If category not found, select first available
                        if self.categories:
                            self.category_var.set(self.categories[0]['name'])
                except Exception as e:
                    print(f"[WARNING] Failed to load current category: {e}")
                    if self.categories:
                        self.category_var.set(self.categories[0]['name'])
            
            # Load tags
            try:
                tags = self.document_manager.get_document_tags(self.document['id'])
                self.tags_var.set(", ".join(tags))
            except Exception as e:
                print(f"[WARNING] Failed to load tags: {e}")

    def _get_selected_category(self):
        """Get selected category"""
        if hasattr(self, 'category_var') and hasattr(self, 'categories'):
            category_name = self.category_var.get()
            for category in self.categories:
                if category['name'] == category_name:
                    return category
        return None

    def _save_document(self):
        filename = self.filename_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        tags_text = self.tags_var.get().strip()

        if not filename:
            from ui.error_dialog import show_error
            show_error(self.window, "Validation Error", "Filename is required!")
            return
        if not content:
            from ui.error_dialog import show_error
            show_error(self.window, "Validation Error", "Content is required!")
            return

        # Get selected category
        selected_category = self._get_selected_category()
        if not selected_category:
            from ui.error_dialog import show_error
            show_error(self.window, "Validation Error", "Please select a category!")
            return

        try:
            if self.is_editing:
                # For editing: update content, filename, and category
                conn = self.document_manager.get_connection()
                if not conn:
                    raise Exception("Database connection failed")
                
                try:
                    with conn.cursor() as cur:
                        # Update content, filename, and category
                        update_sql = """
                            UPDATE plan_documents 
                            SET content=%s, filename=%s, category_id=%s 
                            WHERE id=%s
                        """
                        cur.execute(update_sql, (content, filename, selected_category['id'], self.document['id']))
                        
                        doc_id = self.document['id']
                finally:
                    conn.close()
                    
                operation = "updated"
            else:
                # Create new document
                doc_id = self.document_manager.create_document(
                    self.project['id'],
                    selected_category['id'],
                    filename,
                    content,
                    'user'
                )
                if not doc_id:
                    raise Exception("Failed to create document")
                operation = "created"

            # Handle tags
            if tags_text:
                tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                if tags:
                    # Remove old tags and add new ones
                    try:
                        old_tags = self.document_manager.get_document_tags(doc_id)
                        if old_tags:
                            self.document_manager.remove_tags(doc_id, old_tags)
                        self.document_manager.add_tags(doc_id, tags)
                    except Exception as tag_error:
                        print(f"[WARNING] Failed to update tags: {tag_error}")

            self.result = True
            
            # Success notification
            messagebox.showinfo("Success", f"Document {operation} successfully!")
            
            self.window.destroy()
            
        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.window, "Save Error", f"Failed to save document: {str(e)}", e)

    def _execute_document(self):
        """Execute document (placeholder for now)"""
        messagebox.showinfo("Execute", "Document execution feature will be implemented with gRPC integration.")

    def _view_history(self):
        """View document version history"""
        if self.document:
            from ui.history_dialog import HistoryDialog
            HistoryDialog(self.window, self.document_manager, self.document)