# MainWindow for Plan Manager - Main Framework

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.menu_toolbar import MenuToolbarManager
from ui.project_panel import ProjectPanel
from ui.document_panel import DocumentPanel
from ui.log_panel import LogPanel
from ui.category_tabs import CategoryTabsManager
from ui.system_config_dialog import SystemConfigDialog
from managers.project_manager import ProjectManager
from managers.category_manager import CategoryManager
from managers.document_manager import DocumentManager
from database.connection import init_database, test_connection

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Plan Manager")
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.project_manager = ProjectManager()
        self.category_manager = CategoryManager()
        self.document_manager = DocumentManager()
        
        # Current selections
        self.current_project = None
        self.current_category = None
        
        # Check database connection on startup
        self._check_database_connection()
        
        # Setup UI components
        self._setup_widgets()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Load initial data
        self.project_panel.load_projects()

    def _check_database_connection(self):
        """Check database connection and initialize if needed"""
        success, message = test_connection()
        if not success:
            messagebox.showwarning("Database Connection", 
                f"Database connection failed: {message}\n\nPlease configure database settings.")
            SystemConfigDialog(self.root)
        else:
            # Try to initialize database
            if not init_database():
                messagebox.showwarning("Database Initialization", 
                    "Database initialization failed. Please check configuration.")

    def _setup_widgets(self):
        """Setup all UI components"""
        # Menu and toolbar
        self.menu_toolbar = MenuToolbarManager(self.root, self)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Main layout
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel: Project management
        left_frame = ttk.Frame(main_pane, width=300)
        self.project_panel = ProjectPanel(left_frame, self)
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
        self.category_tabs = CategoryTabsManager(right_pane, self)
        right_pane.add(self.category_tabs.notebook, weight=1)

        # Document and log area
        mid_split = ttk.PanedWindow(right_pane, orient=tk.HORIZONTAL)
        
        # Document panel
        doc_frame = ttk.Frame(mid_split, width=400)
        self.document_panel = DocumentPanel(doc_frame, self)
        doc_frame.pack_propagate(False)
        mid_split.add(doc_frame, weight=1)
        
        # Log panel
        log_frame = ttk.Frame(mid_split)
        self.log_panel = LogPanel(log_frame, self)
        log_frame.pack_propagate(False)
        mid_split.add(log_frame, weight=2)
        
        right_pane.add(mid_split, weight=3)

    def _setup_event_handlers(self):
        """Setup event handlers between components"""
        # Project selection changes
        self.project_panel.on_project_select = self.on_project_select
        
        # Category tab changes
        self.category_tabs.on_tab_change = self.on_category_change
        
        # Document selection changes
        self.document_panel.on_document_select = self.on_document_select

    def on_project_select(self, project):
        """Handle project selection"""
        self.current_project = project
        if project:
            self.category_tabs.load_categories()
            self.update_status(f"Selected project: {project['name']}")
        else:
            self.current_project = None
            self.current_category = None
            self.document_panel.clear_documents()
            self.log_panel.clear_logs()

    def on_category_change(self, category):
        """Handle category tab change"""
        self.current_category = category
        if self.current_project and category:
            self.document_panel.load_documents(self.current_project['id'], category['id'])
            self.update_status(f"Viewing {category['name']} documents")

    def on_document_select(self, document):
        """Handle document selection"""
        if document:
            self.log_panel.load_document_logs(document['id'])

    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)

    def refresh_all(self):
        """Refresh all data"""
        self.project_panel.load_projects()
        if self.current_project:
            self.category_tabs.load_categories()
            if self.current_category:
                self.document_panel.load_documents(self.current_project['id'], self.current_category['id'])

    def run(self):
        """Start the application"""
        self.root.mainloop()