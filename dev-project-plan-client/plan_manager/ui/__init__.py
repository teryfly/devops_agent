# UI package init - updated

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
from .history_dialog import HistoryDialog
from .error_dialog import ErrorDialog, show_error

# Base components
from .base_dialog import BaseDialog
from .form_builder import FormBuilder

# Specific component modules
from .document_form import DocumentForm
from .document_actions import DocumentActions
from .document_list import DocumentList
from .document_toolbar import DocumentToolbar
from .category_form import CategoryForm
from .category_list import CategoryList
from .config_form import ConfigForm
from .config_tester import ConfigTester
from .log_display import LogDisplay
from .log_toolbar import LogToolbar
from .menu_manager import MenuManager
from .toolbar_manager import ToolbarManager
from .project_form import ProjectForm
from .project_list import ProjectList
from .project_info import ProjectInfo
from .history_viewer import HistoryViewer
from .error_display import ErrorDisplay

# Main window components
from .main_window_components import WindowManager, ComponentManager, EventManager

# Widget components
from .widgets import DocumentEditor, TagManager
from .widgets.log_display import LogDisplay as WidgetLogDisplay

__all__ = [
    # Main components
    'MainWindow',
    'MenuToolbarManager',
    'ProjectPanel',
    'DocumentPanel',
    'LogPanel',
    'CategoryTabsManager',

    # Dialog components
    'ProjectDialog',
    'CategoryDialog',
    'DocumentDialog',
    'SystemConfigDialog',
    'HistoryDialog',
    'ErrorDialog',
    'show_error',

    # Base components
    'BaseDialog',
    'FormBuilder',

    # Specific components
    'DocumentForm',
    'DocumentActions',
    'DocumentList',
    'DocumentToolbar',
    'CategoryForm',
    'CategoryList',
    'ConfigForm',
    'ConfigTester',
    'LogDisplay',
    'LogToolbar',
    'MenuManager',
    'ToolbarManager',
    'ProjectForm',
    'ProjectList',
    'ProjectInfo',
    'HistoryViewer',
    'ErrorDisplay',

    # Main window components
    'WindowManager',
    'ComponentManager',
    'EventManager',

    # Widget components
    'DocumentEditor',
    'TagManager',
    'WidgetLogDisplay'
]

# Package version
__version__ = "2.0.0"
__author__ = "Plan Manager Team"

# Configuration
UI_CONFIG = {
    'default_window_size': "1200x800",
    'default_dialog_size': "500x400",
    'default_font': ("Arial", 10),
    'code_font': ("Consolas", 10),
    'max_log_lines': 1000,
    'max_tags_per_document': 20
}