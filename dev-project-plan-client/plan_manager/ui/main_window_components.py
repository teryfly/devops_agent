import tkinter as tk
from tkinter import ttk, messagebox
from .menu_toolbar import MenuToolbarManager
from .project_panel import ProjectPanel
from .document_panel import DocumentPanel
from .log_panel import LogPanel
from .category_tabs import CategoryTabsManager
from .system_config_dialog import SystemConfigDialog
from database.connection import init_database, test_connection

class WindowManager:
    def __init__(self, root):
        self.root = root
        self.status_bar = None

    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Plan Manager")
        self.root.geometry("1200x800")

        # Setup status bar
        self.status_bar = ttk.Label(
            self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def check_database_connection(self):
        """Check database connection and initialize if needed"""
        success, message = test_connection()
        if not success:
            messagebox.showwarning(
                "Database Connection",
                f"Database connection failed: {message}\n\nPlease configure database settings."
            )
            SystemConfigDialog(self.root)
        else:
            if not init_database():
                messagebox.showwarning(
                    "Database Initialization",
                    "Database initialization failed. Please check configuration."
                )

    def update_status(self, message):
        """Update status bar"""
        if self.status_bar:
            self.status_bar.config(text=message)

class ComponentManager:
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self._setup_layout()

    def _setup_layout(self):
        """Setup main layout and components"""
        # Menu and toolbar
        self.menu_toolbar = MenuToolbarManager(self.root, self.main_window)

        # Main layout
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel: Project management
        left_frame = ttk.Frame(main_pane, width=300)
        self.project_panel = ProjectPanel(left_frame, self.main_window)
        left_frame.pack_propagate(False)
        main_pane.add(left_frame, weight=1)

        # Right panel: Document and log management
        right_frame = ttk.Frame(main_pane)
        self._setup_right_panel(right_frame)
        main_pane.add(right_frame, weight=4)

    def _setup_right_panel(self, parent):
        """Setup right panel with document and log areas"""
        right_pane = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        right_pane.pack(fill=tk.BOTH, expand=True)

        # Category tabs
        self.category_tabs = CategoryTabsManager(right_pane, self.main_window)
        right_pane.add(self.category_tabs.notebook, weight=1)

        # Document and log area
        mid_split = ttk.PanedWindow(right_pane, orient=tk.HORIZONTAL)

        # Document panel
        doc_frame = ttk.Frame(mid_split, width=400)
        self.document_panel = DocumentPanel(doc_frame, self.main_window)
        doc_frame.pack_propagate(False)
        mid_split.add(doc_frame, weight=1)

        # Log panel
        log_frame = ttk.Frame(mid_split)
        self.log_panel = LogPanel(log_frame, self.main_window)
        log_frame.pack_propagate(False)
        mid_split.add(log_frame, weight=2)

        right_pane.add(mid_split, weight=3)

class EventManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup event handlers between components"""
        # Project selection changes
        self.main_window.component_manager.project_panel.on_project_select = self.on_project_select

        # Category tab changes
        self.main_window.component_manager.category_tabs.on_tab_change = self.on_category_change

        # Document selection changes
        self.main_window.component_manager.document_panel.on_document_select = self.on_document_select

    def on_project_select(self, project):
        """Handle project selection"""
        self.main_window.current_project = project
        if project:
            self.main_window.component_manager.category_tabs.load_categories()
            self.main_window.update_status(f"Selected project: {project['name']}")
        else:
            self.main_window.current_project = None
            self.main_window.current_category = None
            self.main_window.component_manager.document_panel.clear_documents()
            self.main_window.component_manager.log_panel.clear_logs()

    def on_category_change(self, category):
        """Handle category tab change"""
        self.main_window.current_category = category
        if self.main_window.current_project and category:
            self.main_window.component_manager.document_panel.load_documents(
                self.main_window.current_project['id'], category['id']
            )
            self.main_window.update_status(f"Viewing {category['name']} documents")

    def on_document_select(self, document):
        """Handle document selection"""
        if document:
            self.main_window.component_manager.log_panel.load_document_logs(document['id'])