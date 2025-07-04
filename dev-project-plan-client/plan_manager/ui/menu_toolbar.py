# Menu and Toolbar Manager

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.project_dialog import ProjectDialog
from ui.category_dialog import CategoryDialog
from ui.system_config_dialog import SystemConfigDialog
from ui.error_dialog import show_error

class MenuToolbarManager:
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self._setup_menu()
        self._setup_toolbar()

    def _setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        
        # Project menu
        project_menu = tk.Menu(menubar, tearoff=0)
        project_menu.add_command(label="New Project", command=self.new_project)
        project_menu.add_command(label="Edit Project", command=self.edit_project)
        project_menu.add_command(label="Delete Project", command=self.delete_project)
        project_menu.add_separator()
        project_menu.add_command(label="Refresh", command=self.refresh_projects)
        menubar.add_cascade(label="Project", menu=project_menu)
        
        # Category menu
        cat_menu = tk.Menu(menubar, tearoff=0)
        cat_menu.add_command(label="Manage Categories", command=self.open_category_dialog)
        menubar.add_cascade(label="Category", menu=cat_menu)
        
        # Document menu
        doc_menu = tk.Menu(menubar, tearoff=0)
        doc_menu.add_command(label="New Document", command=self.new_document)
        doc_menu.add_command(label="Edit Document", command=self.edit_document)
        doc_menu.add_command(label="Delete Document", command=self.delete_document)
        doc_menu.add_separator()
        doc_menu.add_command(label="Execute Document", command=self.execute_document)
        menubar.add_cascade(label="Document", menu=doc_menu)
        
        # System menu
        sys_menu = tk.Menu(menubar, tearoff=0)
        sys_menu.add_command(label="Database Configuration", command=self.open_system_config)
        sys_menu.add_command(label="Generate gRPC Files", command=self.generate_grpc_files)
        menubar.add_cascade(label="System", menu=sys_menu)
        
        self.root.config(menu=menubar)

    def _setup_toolbar(self):
        """Setup toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Project operations
        ttk.Button(toolbar, text="New Project", command=self.new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="New Document", command=self.new_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_projects).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Search functionality
        self.search_var = tk.StringVar()
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(toolbar, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Search", command=self.search_documents).pack(side=tk.LEFT, padx=2)

    def new_project(self):
        """Create new project"""
        try:
            dialog = ProjectDialog(self.root, self.main_window.project_manager)
            if dialog.result:
                self.main_window.project_panel.load_projects()
                self.main_window.update_status("Project created successfully")
        except Exception as e:
            show_error(self.root, "Create Project Error", f"Failed to create project: {str(e)}", e)

    def edit_project(self):
        """Edit current project"""
        if not self.main_window.current_project:
            messagebox.showwarning("Selection", "Please select a project to edit.")
            return
        
        try:
            dialog = ProjectDialog(self.root, self.main_window.project_manager, self.main_window.current_project)
            if dialog.result:
                self.main_window.project_panel.load_projects()
                self.main_window.update_status("Project updated successfully")
        except Exception as e:
            show_error(self.root, "Edit Project Error", f"Failed to edit project: {str(e)}", e)

    def delete_project(self):
        """Delete current project"""
        if not self.main_window.current_project:
            messagebox.showwarning("Selection", "Please select a project to delete.")
            return
        
        project = self.main_window.current_project
        if messagebox.askyesno("Confirm Delete", 
            f"Are you sure you want to delete project '{project['name']}'?\n\nThis will also delete all associated documents and logs."):
            try:
                if self.main_window.project_manager.delete_project(project['id']):
                    self.main_window.project_panel.load_projects()
                    self.main_window.update_status("Project deleted successfully")
                else:
                    show_error(self.root, "Delete Error", "Failed to delete project!")
            except Exception as e:
                show_error(self.root, "Delete Project Error", f"Failed to delete project: {str(e)}", e)

    def open_category_dialog(self):
        """Open category management dialog"""
        try:
            dialog = CategoryDialog(self.root, self.main_window.category_manager)
            
            # 等待对话框关闭
            self.root.wait_window(dialog.window)
            
            # 自动刷新分类标签页
            self.main_window.category_tabs.load_categories()
            
            # 如果当前有选中的项目和分类，刷新文档列表
            if self.main_window.current_project and self.main_window.current_category:
                self.main_window.document_panel.load_documents(
                    self.main_window.current_project['id'], 
                    self.main_window.current_category['id']
                )
            
            self.main_window.update_status("Categories refreshed")
            
        except Exception as e:
            show_error(self.root, "Category Dialog Error", f"Failed to open category dialog: {str(e)}", e)

    def new_document(self):
        """Create new document"""
        if not self.main_window.current_project:
            messagebox.showwarning("Selection", "Please select a project first.")
            return
        
        try:
            from ui.document_dialog import DocumentDialog
            dialog = DocumentDialog(
                self.root, 
                self.main_window.document_manager, 
                self.main_window.current_project,
                self.main_window.category_manager
            )
            
            # 等待对话框关闭
            self.root.wait_window(dialog.window)
            
            if dialog.result:
                # 自动刷新
                if self.main_window.current_category:
                    self.main_window.document_panel.load_documents(
                        self.main_window.current_project['id'], 
                        self.main_window.current_category['id']
                    )
                # 刷新分类标签页
                self.main_window.category_tabs.load_categories()
                self.main_window.update_status("Document created successfully")
                
        except Exception as e:
            show_error(self.root, "New Document Error", f"Failed to create document: {str(e)}", e)

    def edit_document(self):
        """Edit current document"""
        self.main_window.document_panel.edit_document()

    def delete_document(self):
        """Delete current document"""
        self.main_window.document_panel.delete_document()

    def execute_document(self):
        """Execute current document"""
        self.main_window.document_panel.execute_document()

    def open_system_config(self):
        """Open system configuration dialog"""
        try:
            SystemConfigDialog(self.root)
        except Exception as e:
            show_error(self.root, "System Config Error", f"Failed to open system config: {str(e)}", e)

    def generate_grpc_files(self):
        """Generate gRPC files from proto"""
        try:
            import generate_grpc
            if generate_grpc.generate_grpc_files():
                self.main_window.update_status("gRPC files generated successfully")
            else:
                show_error(self.root, "gRPC Generation Error", "Failed to generate gRPC files!")
        except ImportError:
            show_error(self.root, "Import Error", "grpcio-tools not installed!")

    def refresh_projects(self):
        """Refresh all data"""
        self.main_window.refresh_all()
        self.main_window.update_status("Data refreshed")

    def search_documents(self):
        """Search documents"""
        search_text = self.search_var.get().strip()
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
                # Show search results in document panel
                self.main_window.document_panel.show_search_results(results, search_text)
                self.main_window.update_status(f"Found {len(results)} documents containing '{search_text}'")
            else:
                self.main_window.update_status(f"No results for '{search_text}'")
                messagebox.showinfo("Search Results", f"No documents found containing '{search_text}'")
        except Exception as e:
            show_error(self.root, "Search Error", f"Search failed: {str(e)}", e)