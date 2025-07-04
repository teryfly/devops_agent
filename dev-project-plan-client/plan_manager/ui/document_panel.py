# Document Panel - Document list and operations

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 延迟导入避免循环导入
def get_error_dialog():
    try:
        from ui.error_dialog import show_error
        return show_error
    except ImportError:
        def fallback_error(parent, title, message, exception=None):
            messagebox.showerror(title, message)
        return fallback_error

class DocumentPanel:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.documents = []
        self.on_document_select = None  # Callback function
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup document panel widgets"""
        # Document toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, pady=2)
        
        ttk.Label(toolbar, text="Documents", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Buttons
        ttk.Button(toolbar, text="New", command=self.new_document, width=8).pack(side=tk.RIGHT, padx=1)
        ttk.Button(toolbar, text="Edit", command=self.edit_document, width=8).pack(side=tk.RIGHT, padx=1)
        ttk.Button(toolbar, text="Delete", command=self.delete_document, width=8).pack(side=tk.RIGHT, padx=1)
        ttk.Button(toolbar, text="Execute", command=self.execute_document, width=8).pack(side=tk.RIGHT, padx=1)
        
        # Document list
        list_frame = ttk.Frame(self.parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        columns = ("Filename", "Version", "Source", "Tags", "Created")
        self.doc_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Setup columns
        self.doc_tree.heading("Filename", text="Filename")
        self.doc_tree.heading("Version", text="Ver")
        self.doc_tree.heading("Source", text="Source") 
        self.doc_tree.heading("Tags", text="Tags")
        self.doc_tree.heading("Created", text="Created")
        
        # Set column widths
        self.doc_tree.column("Filename", width=150)
        self.doc_tree.column("Version", width=40)
        self.doc_tree.column("Source", width=60)
        self.doc_tree.column("Tags", width=100)
        self.doc_tree.column("Created", width=120)
        
        # Scrollbar
        doc_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=doc_scrollbar.set)
        
        self.doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        doc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Event bindings
        self.doc_tree.bind('<<TreeviewSelect>>', self._on_document_select)
        self.doc_tree.bind('<Double-Button-1>', self.edit_document)

    def load_documents(self, project_id, category_id):
        """Load documents for specified project and category"""
        show_error = get_error_dialog()
        
        try:
            print(f"[DEBUG] Loading documents for project_id={project_id}, category_id={category_id}")
            
            # Debug: Check DocumentManager methods
            if hasattr(self.main_window, 'document_manager'):
                methods = [m for m in dir(self.main_window.document_manager) if not m.startswith('_')]
                print(f"[DEBUG] DocumentManager methods: {methods}")
            else:
                print("[ERROR] No document_manager found in main_window")
                self.main_window.update_status("Error: Document manager not initialized")
                return

            # Clear current items
            for item in self.doc_tree.get_children():
                self.doc_tree.delete(item)
            
            # Load documents using different methods based on availability
            if hasattr(self.main_window.document_manager, 'get_documents_by_category'):
                print("[DEBUG] Using get_documents_by_category method")
                self.documents = self.main_window.document_manager.get_documents_by_category(project_id, category_id)
            elif hasattr(self.main_window.document_manager, 'list_documents'):
                print("[DEBUG] Using list_documents method")
                self.documents = self.main_window.document_manager.list_documents(project_id, category_id)
            else:
                print("[ERROR] No suitable method found in DocumentManager")
                self.main_window.update_status("Error: Document loading method not available")
                return
            
            print(f"[DEBUG] Loaded {len(self.documents)} documents")
            
            # Display documents
            for i, doc in enumerate(self.documents):
                try:
                    print(f"[DEBUG] Processing document {i+1}: {doc.get('filename', 'Unknown')}")
                    
                    # Get tags safely
                    tags = []
                    try:
                        if hasattr(self.main_window.document_manager, 'get_document_tags'):
                            tags = self.main_window.document_manager.get_document_tags(doc['id'])
                    except Exception as tag_error:
                        print(f"[WARNING] Failed to get tags for document {doc['id']}: {tag_error}")
                    
                    tags_str = ", ".join(tags) if tags else ""
                    
                    # Format creation time safely
                    created_time = ""
                    try:
                        if doc.get('created_time'):
                            if hasattr(doc['created_time'], 'strftime'):
                                created_time = doc['created_time'].strftime("%Y-%m-%d %H:%M")
                            else:
                                created_time = str(doc['created_time'])[:16]  # Truncate string representation
                    except Exception as time_error:
                        print(f"[WARNING] Failed to format time for document {doc['id']}: {time_error}")
                        created_time = "Unknown"
                    
                    # Insert into tree
                    self.doc_tree.insert("", tk.END, values=(
                        doc.get('filename', 'Untitled'),
                        f"v{doc.get('version', 1)}",
                        doc.get('source', 'unknown'),
                        tags_str,
                        created_time
                    ))
                    
                except Exception as doc_error:
                    print(f"[ERROR] Failed to process document {i+1}: {doc_error}")
                    continue
            
            self.main_window.update_status(f"Loaded {len(self.documents)} documents")
            
        except Exception as e:
            print(f"[ERROR] Failed to load documents: {e}")
            import traceback
            traceback.print_exc()
            show_error(self.main_window.root, "Load Documents Error", f"Failed to load documents: {str(e)}", e)

    def show_search_results(self, results, search_text):
        """Show search results in document list"""
        show_error = get_error_dialog()
        
        try:
            print(f"[DEBUG] Showing {len(results)} search results for '{search_text}'")
            
            # Clear current items
            for item in self.doc_tree.get_children():
                self.doc_tree.delete(item)
            
            self.documents = results
            
            for doc in self.documents:
                try:
                    tags = []
                    try:
                        if hasattr(self.main_window.document_manager, 'get_document_tags'):
                            tags = self.main_window.document_manager.get_document_tags(doc['id'])
                    except Exception:
                        pass
                    
                    tags_str = ", ".join(tags) if tags else ""
                    
                    created_time = ""
                    try:
                        if doc.get('created_time'):
                            if hasattr(doc['created_time'], 'strftime'):
                                created_time = doc['created_time'].strftime("%Y-%m-%d %H:%M")
                            else:
                                created_time = str(doc['created_time'])[:16]
                    except Exception:
                        created_time = "Unknown"
                    
                    # Highlight filename if it contains search text
                    filename = doc.get('filename', 'Untitled')
                    if search_text.lower() in filename.lower():
                        filename = f"► {filename}"
                    
                    self.doc_tree.insert("", tk.END, values=(
                        filename,
                        f"v{doc.get('version', 1)}",
                        doc.get('source', 'unknown'),
                        tags_str,
                        created_time
                    ))
                except Exception as doc_error:
                    print(f"[WARNING] Failed to process search result document: {doc_error}")
                    continue
                
        except Exception as e:
            print(f"[ERROR] Failed to show search results: {e}")
            show_error(self.main_window.root, "Search Results Error", f"Failed to show search results: {str(e)}", e)

    def clear_documents(self):
        """Clear document list"""
        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)
        self.documents = []
        print("[DEBUG] Document list cleared")

    def _on_document_select(self, event):
        """Handle document selection"""
        try:
            selected_doc = self._get_selected_document()
            print(f"[DEBUG] Document selected: {selected_doc.get('filename', 'None') if selected_doc else 'None'}")
            if self.on_document_select:
                self.on_document_select(selected_doc)
        except Exception as e:
            print(f"[ERROR] Error in document selection: {e}")

    def _get_selected_document(self):
        """Get currently selected document"""
        try:
            selection = self.doc_tree.selection()
            if not selection:
                return None
            
            item = self.doc_tree.item(selection[0])
            filename = item['values'][0]
            
            # Remove search highlight marker if present
            if filename.startswith("► "):
                filename = filename[2:]
            
            # Find document by filename
            for doc in self.documents:
                if doc.get('filename') == filename:
                    return doc
            return None
        except Exception as e:
            print(f"[ERROR] Failed to get selected document: {e}")
            return None

    def new_document(self):
        """Create new document"""
        show_error = get_error_dialog()
        
        if not self.main_window.current_project:
            messagebox.showwarning("Selection", "Please select a project first.")
            return
        
        try:
            from ui.document_dialog import DocumentDialog
            dialog = DocumentDialog(
                self.main_window.root, 
                self.main_window.document_manager, 
                self.main_window.current_project,
                self.main_window.category_manager
            )
            
            # 等待对话框关闭
            self.main_window.root.wait_window(dialog.window)
            
            if dialog.result:
                # 自动刷新当前分类的文档列表
                if self.main_window.current_project and self.main_window.current_category:
                    self.load_documents(
                        self.main_window.current_project['id'], 
                        self.main_window.current_category['id']
                    )
                    self.main_window.update_status("Document created and list refreshed")
                
                # 刷新分类标签页以确保一致性
                if hasattr(self.main_window, 'category_tabs'):
                    self.main_window.category_tabs.load_categories()
                    
        except Exception as e:
            print(f"[ERROR] Failed to create new document: {e}")
            show_error(self.main_window.root, "New Document Error", f"Failed to create document: {str(e)}", e)

    def edit_document(self, event=None):
        """Edit selected document"""
        show_error = get_error_dialog()
        
        selected_doc = self._get_selected_document()
        if not selected_doc:
            messagebox.showwarning("Selection", "Please select a document to edit.")
            return
        
        try:
            from ui.document_dialog import DocumentDialog
            dialog = DocumentDialog(
                self.main_window.root, 
                self.main_window.document_manager, 
                self.main_window.current_project, 
                self.main_window.category_manager,
                selected_doc
            )
            
            # 等待对话框关闭
            self.main_window.root.wait_window(dialog.window)
            
            if dialog.result:
                # 自动刷新当前分类的文档列表
                if self.main_window.current_project and self.main_window.current_category:
                    self.load_documents(
                        self.main_window.current_project['id'], 
                        self.main_window.current_category['id']
                    )
                
                # 同时刷新分类标签页，因为文档可能被移到了其他分类
                if hasattr(self.main_window, 'category_tabs'):
                    self.main_window.category_tabs.load_categories()
                
                self.main_window.update_status("Document updated and views refreshed")
                    
        except Exception as e:
            print(f"[ERROR] Failed to edit document: {e}")
            show_error(self.main_window.root, "Edit Document Error", f"Failed to edit document: {str(e)}", e)

    def delete_document(self):
        """Delete selected document"""
        show_error = get_error_dialog()
        
        selected_doc = self._get_selected_document()
        if not selected_doc:
            messagebox.showwarning("Selection", "Please select a document to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
            f"Are you sure you want to delete document '{selected_doc.get('filename', 'Unknown')}'?\n\nThis will delete all versions of this document."):
            try:
                if hasattr(self.main_window.document_manager, 'delete_document'):
                    if self.main_window.document_manager.delete_document(selected_doc['id']):
                        if self.main_window.current_project and self.main_window.current_category:
                            self.load_documents(self.main_window.current_project['id'], self.main_window.current_category['id'])
                        self.main_window.update_status("Document deleted successfully")
                    else:
                        show_error(self.main_window.root, "Delete Error", "Failed to delete document!")
                else:
                    show_error(self.main_window.root, "Method Error", "Delete method not available!")
            except Exception as e:
                print(f"[ERROR] Failed to delete document: {e}")
                show_error(self.main_window.root, "Delete Document Error", f"Failed to delete document: {str(e)}", e)

    def execute_document(self):
        """Execute selected document"""
        show_error = get_error_dialog()
        
        selected_doc = self._get_selected_document()
        if not selected_doc:
            messagebox.showwarning("Selection", "Please select a document to execute.")
            return
        
        try:
            # TODO: Implement actual gRPC execution
            messagebox.showinfo("Execute", 
                f"Executing document: {selected_doc.get('filename', 'Unknown')}\n\n" +
                "This feature will be implemented with gRPC integration.")
        except Exception as e:
            print(f"[ERROR] Failed to execute document: {e}")
            show_error(self.main_window.root, "Execute Error", f"Failed to execute document: {str(e)}", e)


# Test if this module can be imported
if __name__ == "__main__":
    print("DocumentPanel module loaded successfully")
    print(f"DocumentPanel class available: {DocumentPanel}")