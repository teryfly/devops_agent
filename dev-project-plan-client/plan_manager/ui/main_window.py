# ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from .main_window_components import WindowManager, ComponentManager, EventManager
from managers.project_manager import ProjectManager
from managers.category_manager import CategoryManager
from managers.document_manager import DocumentManager

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()

        # Initialize managers
        self._init_managers()

        # Initialize components
        self._init_components()

        # Setup window
        self._setup_window()

    def _init_managers(self):
        """Initialize data managers"""
        self.project_manager = ProjectManager()
        self.category_manager = CategoryManager()
        self.document_manager = DocumentManager()

        # Current selections
        self.current_project = None
        self.current_category = None

    def _init_components(self):
        """Initialize UI components"""
        self.window_manager = WindowManager(self.root)
        self.component_manager = ComponentManager(self.root, self)
        self.event_manager = EventManager(self)

    def _setup_window(self):
        """Setup main window"""
        self.window_manager.setup_window()
        self.window_manager.check_database_connection()

        # Load initial data
        self.component_manager.project_panel.load_projects()

    def update_status(self, message):
        """Update status bar message"""
        self.window_manager.update_status(message)

    def refresh_all(self):
        """Refresh all data"""
        self.component_manager.project_panel.load_projects()
        if self.current_project:
            self.component_manager.category_tabs.load_categories()
            if self.current_category:
                self.component_manager.document_panel.load_documents(
                    self.current_project['id'],
                    self.current_category['id']
                )

    def run(self):
        """Start the application"""
        self.root.mainloop()