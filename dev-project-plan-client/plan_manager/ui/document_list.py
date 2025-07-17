import tkinter as tk
from tkinter import ttk

class DocumentList:
    def __init__(self, parent, document_panel):
        self.parent = parent
        self.document_panel = document_panel
        self.documents = []
        self.on_document_select = None
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup document list widgets"""
        list_frame = ttk.Frame(self.parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        columns = ("Filename", "Version", "Source", "Tags", "Created")
        self.doc_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        self._setup_columns()
        self._setup_scrollbar(list_frame)
        self._setup_events()

    def _setup_columns(self):
        """Setup treeview columns"""
        column_config = {
            "Filename": 150,
            "Version": 40,
            "Source": 60,
            "Tags": 100,
            "Created": 120
        }
        for col, width in column_config.items():
            self.doc_tree.heading(col, text=col)
            self.doc_tree.column(col, width=width)

    def _setup_scrollbar(self, parent):
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=scrollbar.set)
        self.doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _setup_events(self):
        self.doc_tree.bind('<<TreeviewSelect>>', self._on_document_select)
        self.doc_tree.bind('<Double-Button-1>', lambda e: self.document_panel.edit_document())

    def load_documents(self, project_id, category_id):
        try:
            print(f"[DEBUG] Loading documents for project_id={project_id}, category_id={category_id}")
            self._clear_list()
            doc_manager = self.document_panel.main_window.document_manager
            if hasattr(doc_manager, 'get_documents_by_category'):
                self.documents = doc_manager.get_documents_by_category(project_id, category_id)
            elif hasattr(doc_manager, 'list_documents'):
                self.documents = doc_manager.list_documents(project_id, category_id)
            else:
                print("[ERROR] No suitable method found in DocumentManager")
                return
            self._populate_list()
            self.document_panel.main_window.update_status(f"Loaded {len(self.documents)} documents")
        except Exception as e:
            print(f"[ERROR] Failed to load documents: {e}")
            from ui.error_dialog import show_error
            show_error(
                self.document_panel.main_window.root,
                "Load Documents Error",
                f"Failed to load documents: {str(e)}", e
            )

    def show_search_results(self, results, search_text):
        try:
            print(f"[DEBUG] Showing {len(results)} search results for '{search_text}'")
            self._clear_list()
            self.documents = results
            self._populate_list(search_text)
        except Exception as e:
            print(f"[ERROR] Failed to show search results: {e}")

    def clear_documents(self):
        self._clear_list()
        self.documents = []
        print("[DEBUG] Document list cleared")

    def get_selected_document(self):
        try:
            selection = self.doc_tree.selection()
            if not selection:
                return None
            selected_iid = selection[0]
            doc_id = int(selected_iid)
            for doc in self.documents:
                if doc.get('id') == doc_id:
                    return doc
            return None
        except Exception as e:
            print(f"[ERROR] Failed to get selected document: {e}")
            return None

    def _clear_list(self):
        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)

    def _populate_list(self, search_text=None):
        for doc in self.documents:
            try:
                tags = self._get_document_tags(doc['id'])
                tags_str = ", ".join(tags) if tags else ""
                created_time = self._format_time(doc.get('created_time'))
                filename = doc.get('filename', 'Untitled')
                if search_text and search_text.lower() in filename.lower():
                    filename = f"► {filename}"
                # 用id做iid
                self.doc_tree.insert(
                    "", tk.END, iid=str(doc['id']),
                    values=(
                        filename,
                        f"v{doc.get('version', 1)}",
                        doc.get('source', 'unknown'),
                        tags_str,
                        created_time
                    )
                )
            except Exception as doc_error:
                print(f"[WARNING] Failed to process document: {doc_error}")
                continue

    def _get_document_tags(self, doc_id):
        try:
            doc_manager = self.document_panel.main_window.document_manager
            if hasattr(doc_manager, 'get_document_tags'):
                return doc_manager.get_document_tags(doc_id)
        except Exception:
            pass
        return []

    def _format_time(self, time_obj):
        try:
            if time_obj:
                if hasattr(time_obj, 'strftime'):
                    return time_obj.strftime("%Y-%m-%d %H:%M")
                else:
                    return str(time_obj)[:16]
        except Exception:
            pass
        return "Unknown"

    def _on_document_select(self, event):
        try:
            selected_doc = self.get_selected_document()
            print(f"[DEBUG] Document selected: {selected_doc.get('filename', 'None') if selected_doc else 'None'}")
            if self.on_document_select:
                self.on_document_select(selected_doc)
        except Exception as e:
            print(f"[ERROR] Error in document selection: {e}")