# UI package init

# Import all UI components for easier access
from .main_window import MainWindow
from .menu_toolbar import MenuToolbarManager
from .project_panel import ProjectPanel
from .document_panel import DocumentPanel
from .log_panel import LogPanel
from .category_tabs import CategoryTabsManager
from .project_dialog import ProjectDialog
from .category_dialog import CategoryDialog
from .document_dialog import DocumentDialog
from .system_config_dialog import SystemConfigDialog

__all__ = [
    'MainWindow',
    'MenuToolbarManager', 
    'ProjectPanel',
    'DocumentPanel',
    'LogPanel',
    'CategoryTabsManager',
    'ProjectDialog',
    'CategoryDialog', 
    'DocumentDialog',
    'SystemConfigDialog'
]