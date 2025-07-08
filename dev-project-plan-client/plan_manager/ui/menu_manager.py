# ui/menu_manager.py
import tkinter as tk

class MenuManager:
    def __init__(self, root, menu_toolbar_manager):
        self.root = root
        self.mtm = menu_toolbar_manager  # menu_toolbar_manager
        self._setup_menu()

    def _setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)

        self._setup_project_menu(menubar)
        self._setup_category_menu(menubar)
        self._setup_document_menu(menubar)
        self._setup_system_menu(menubar)

        self.root.config(menu=menubar)

    def _setup_project_menu(self, menubar):
        """Setup project menu"""
        project_menu = tk.Menu(menubar, tearoff=0)
        project_menu.add_command(label="New Project", command=self.mtm.new_project)
        project_menu.add_command(label="Edit Project", command=self.mtm.edit_project)
        project_menu.add_command(label="Delete Project", command=self.mtm.delete_project)
        project_menu.add_separator()
        project_menu.add_command(label="Refresh", command=self.mtm.refresh_projects)
        menubar.add_cascade(label="Project", menu=project_menu)

    def _setup_category_menu(self, menubar):
        """Setup category menu"""
        cat_menu = tk.Menu(menubar, tearoff=0)
        cat_menu.add_command(label="Manage Categories", command=self.mtm.open_category_dialog)
        menubar.add_cascade(label="Category", menu=cat_menu)

    def _setup_document_menu(self, menubar):
        """Setup document menu"""
        doc_menu = tk.Menu(menubar, tearoff=0)
        doc_menu.add_command(label="New Document", command=self.mtm.new_document)
        doc_menu.add_command(label="Edit Document", command=self.mtm.edit_document)
        doc_menu.add_command(label="Delete Document", command=self.mtm.delete_document)
        doc_menu.add_separator()
        doc_menu.add_command(label="Execute Document", command=self.mtm.execute_document)
        menubar.add_cascade(label="Document", menu=doc_menu)

    def _setup_system_menu(self, menubar):
        """Setup system menu"""
        sys_menu = tk.Menu(menubar, tearoff=0)
        sys_menu.add_command(label="Database Configuration", command=self.mtm.open_system_config)
        sys_menu.add_command(label="Generate gRPC Files", command=self.mtm.generate_grpc_files)
        menubar.add_cascade(label="System", menu=sys_menu)