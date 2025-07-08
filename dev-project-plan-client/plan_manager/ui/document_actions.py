from tkinter import messagebox

class DocumentActions:
    def __init__(self, document_manager, form, project, document=None):
        self.document_manager = document_manager
        self.form = form
        self.project = project
        self.document = document
        self.is_editing = document is not None

    def save_document(self):
        """Save document with validation"""
        form_data = self.form.get_form_data()

        if not self._validate_form_data(form_data):
            return False

        try:
            if self.is_editing:
                return self._update_document(form_data)
            else:
                return self._create_document(form_data)
        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.form.parent, "Save Error", f"Failed to save document: {str(e)}", e)
            return False

    def _validate_form_data(self, form_data):
        """Validate form data"""
        if not form_data['filename']:
            messagebox.showerror("Validation Error", "Filename is required!")
            return False
        if not form_data['content']:
            messagebox.showerror("Validation Error", "Content is required!")
            return False
        if not form_data['category']:
            messagebox.showerror("Validation Error", "Please select a category!")
            return False
        return True

    def _create_document(self, form_data):
        """Create new document"""
        doc_id = self.document_manager.create_document(
            self.project['id'],
            form_data['category']['id'],
            form_data['filename'],
            form_data['content'],
            'user'
        )

        if doc_id:
            self._handle_tags(doc_id, form_data['tags'])
            messagebox.showinfo("Success", "Document created successfully!")
            return True
        return False

    def _update_document(self, form_data):
        """Update existing document"""
        conn = self.document_manager.get_connection()
        try:
            with conn.cursor() as cur:
                update_sql = """
                    UPDATE plan_documents
                    SET content=%s, filename=%s, category_id=%s
                    WHERE id=%s
                """
                cur.execute(update_sql, (
                    form_data['content'],
                    form_data['filename'],
                    form_data['category']['id'],
                    self.document['id']
                ))

            self._handle_tags(self.document['id'], form_data['tags'])
            messagebox.showinfo("Success", "Document updated successfully!")
            return True
        finally:
            conn.close()

    def _handle_tags(self, doc_id, tags_text):
        """Handle document tags"""
        if tags_text:
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            if tags:
                try:
                    old_tags = self.document_manager.get_document_tags(doc_id)
                    if old_tags:
                        self.document_manager.remove_tags(doc_id, old_tags)
                    self.document_manager.add_tags(doc_id, tags)
                except Exception as e:
                    print(f"[WARNING] Failed to update tags: {e}")

    def execute_document(self):
        """Execute document"""
        messagebox.showinfo("Execute", "Document execution feature will be implemented with gRPC integration.")

    def view_history(self):
        """View document history"""
        if self.document:
            from ui.history_dialog import HistoryDialog
            HistoryDialog(self.form.parent, self.document_manager, self.document)