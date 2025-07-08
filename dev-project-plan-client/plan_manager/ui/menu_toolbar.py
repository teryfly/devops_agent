import tkinter as tk
from tkinter import ttk, messagebox
from .menu_manager import MenuManager
from .toolbar_manager import ToolbarManager

class MenuToolbarManager:
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window

        self.menu_manager = MenuManager(root, self)
        self.toolbar_manager = ToolbarManager(root, self)

    # Project operations
    def new_project(self):
        """Create new project"""
        try:
            from ui.project_dialog import ProjectDialog
            dialog = ProjectDialog(self.root, self.main_window.project_manager)
            if dialog.result:
                self.main_window.component_manager.project_panel.load_projects()
                self.main_window.update_status("Project created successfully")
        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.root, "Create Project Error", f"Failed to create project: {str(e)}", e)

    def edit_project(self):
        """Edit current project"""
        if not self.main_window.current_project:
            messagebox.showwarning("Selection", "Please select a project to edit.")
            return

        try:
            from ui.project_dialog import ProjectDialog
            dialog = ProjectDialog(
                self.root,
                self.main_window.project_manager,
                self.main_window.current_project
            )
            if dialog.result:
                self.main_window.component_manager.project_panel.load_projects()
                self.main_window.update_status("Project updated successfully")
        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.root, "Edit Project Error", f"Failed to edit project: {str(e)}", e)

    def delete_project(self):
        """Delete current project"""
        if not self.main_window.current_project:
            messagebox.showwarning("Selection", "Please select a project to delete.")
            return

        project = self.main_window.current_project
        if messagebox.askyesno("Confirm Delete",
            f"Are you sure you want to delete project '{project['name']}'?\n\n" +
            "This will also delete all associated documents and logs."):
            try:
                if self.main_window.project_manager.delete_project(project['id']):
                    self.main_window.component_manager.project_panel.load_projects()
                    self.main_window.update_status("Project deleted successfully")
                else:
                    from ui.error_dialog import show_error
                    show_error(self.root, "Delete Error", "Failed to delete project!")
            except Exception as e:
                from ui.error_dialog import show_error
                show_error(self.root, "Delete Project Error", f"Failed to delete project: {str(e)}", e)

    def open_category_dialog(self):
        """Open category management dialog"""
        try:
            from ui.category_dialog import CategoryDialog
            dialog = CategoryDialog(self.root, self.main_window.category_manager)

            self.root.wait_window(dialog.window)

            # Refresh after category changes
            self.main_window.component_manager.category_tabs.load_categories()

            if self.main_window.current_project and self.main_window.current_category:
                self.main_window.component_manager.document_panel.load_documents(
                    self.main_window.current_project['id'],
                    self.main_window.current_category['id']
                )

            self.main_window.update_status("Categories refreshed")

        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.root, "Category Dialog Error", f"Failed to open category dialog: {str(e)}", e)

    # System operations
    def open_system_config(self):
        """Open system configuration dialog"""
        try:
            from ui.system_config_dialog import SystemConfigDialog
            SystemConfigDialog(self.root)
        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.root, "System Config Error", f"Failed to open system config: {str(e)}", e)

    def generate_grpc_files(self):
        """Generate gRPC files from proto"""
        try:
            import generate_grpc
            if generate_grpc.generate_grpc_files():
                self.main_window.update_status("gRPC files generated successfully")
            else:
                from ui.error_dialog import show_error
                show_error(self.root, "gRPC Generation Error", "Failed to generate gRPC files!")
        except ImportError:
            from ui.error_dialog import show_error
            show_error(self.root, "Import Error", "grpcio-tools not installed!")

    def refresh_projects(self):
        """Refresh all data"""
        self.main_window.refresh_all()
        self.main_window.update_status("Data refreshed")

    # 你可以视需要保留或移除搜索功能
    def search_documents(self):
        """Search documents"""
        search_text = self.toolbar_manager.get_search_text()
        if not search_text:
            messagebox.showwarning("Search", "Please enter search text.")
            return

        if not self.main_window.current_project:
            messagebox.showwarning("Search", "Please select a project first.")
            return

        try:
            results = self.main_window.document_manager.search_content(
                self.main_window.current_project['id'],
                search_text,
                self.main_window.current_category['id'] if self.main_window.current_category else None
            )

            if results:
                self.main_window.component_manager.document_panel.show_search_results(results, search_text)
                self.main_window.update_status(f"Found {len(results)} documents containing '{search_text}'")
            else:
                self.main_window.update_status(f"No results for '{search_text}'")
                messagebox.showinfo("Search Results", f"No documents found containing '{search_text}'")
        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.root, "Search Error", f"Search failed: {str(e)}", e)

    # 保留文档刷新
    def _refresh_after_document_change(self):
        """Refresh UI after document changes"""
        if self.main_window.current_category:
            self.main_window.component_manager.document_panel.load_documents(
                self.main_window.current_project['id'],
                self.main_window.current_category['id']
            )

        self.main_window.component_manager.category_tabs.load_categories()
        self.main_window.update_status("Document created successfully")