import tkinter as tk
from tkinter import ttk, messagebox
from .document_list import DocumentList
from .document_toolbar import DocumentToolbar

class DocumentPanel:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.on_document_select = None

        self._setup_components()

    def _setup_components(self):
        """Setup toolbar and document list"""
        self.toolbar = DocumentToolbar(self.parent, self)
        self.doc_list = DocumentList(self.parent, self)

        # Connect events
        self.doc_list.on_document_select = self._on_document_select

    def _on_document_select(self, document):
        """Handle document selection"""
        if self.on_document_select:
            self.on_document_select(document)

    def load_documents(self, project_id, category_id):
        """Load documents for specified project and category"""
        self.doc_list.load_documents(project_id, category_id)

    def show_search_results(self, results, search_text):
        """Show search results"""
        self.doc_list.show_search_results(results, search_text)

    def clear_documents(self):
        """Clear document list"""
        self.doc_list.clear_documents()

    def new_document(self):
        """Create new document"""
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

            self.main_window.root.wait_window(dialog.window)

            if dialog.result:
                self._refresh_after_change()

        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.main_window.root, "New Document Error",
                      f"Failed to create document: {str(e)}", e)

    def edit_document(self):
        """Edit selected document"""
        selected_doc = self.doc_list.get_selected_document()
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

            self.main_window.root.wait_window(dialog.window)

            if dialog.result:
                self._refresh_after_change()

        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.main_window.root, "Edit Document Error",
                      f"Failed to edit document: {str(e)}", e)

    def delete_document(self):
        """Delete selected document"""
        selected_doc = self.doc_list.get_selected_document()
        if not selected_doc:
            messagebox.showwarning("Selection", "Please select a document to delete.")
            return

        if messagebox.askyesno("Confirm Delete",
            f"Are you sure you want to delete document '{selected_doc.get('filename', 'Unknown')}'?"):
            try:
                if self.main_window.document_manager.delete_document(selected_doc['id']):
                    self._refresh_after_change()
                    self.main_window.update_status("Document deleted successfully")
                else:
                    messagebox.showerror("Delete Error", "Failed to delete document!")
            except Exception as e:
                from ui.error_dialog import show_error
                show_error(self.main_window.root, "Delete Document Error",
                          f"Failed to delete document: {str(e)}", e)

    def execute_document(self):
        """Execute selected document"""
        selected_doc = self.doc_list.get_selected_document()
        if not selected_doc:
            messagebox.showwarning("Selection", "Please select a document to execute.")
            return

        messagebox.showinfo("Execute",
            f"Executing document: {selected_doc.get('filename', 'Unknown')}\n\n" +
            "This feature will be implemented with gRPC integration.")

    def _refresh_after_change(self):
        """Refresh UI after document changes"""
        if self.main_window.current_project and self.main_window.current_category:
            self.load_documents(
                self.main_window.current_project['id'],
                self.main_window.current_category['id']
            )

        if hasattr(self.main_window, 'category_tabs'):
            self.main_window.category_tabs.load_categories()

        self.main_window.update_status("Document list refreshed")