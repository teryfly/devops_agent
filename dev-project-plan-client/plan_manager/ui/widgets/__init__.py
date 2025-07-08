# Custom UI widgets package init - updated

from .document_editor import DocumentEditor
from .log_display import LogDisplay
from .tag_manager import TagManager

__all__ = [
    'DocumentEditor',
    'LogDisplay',
    'TagManager'
]

# Widget version information
__version__ = "1.0.0"
__author__ = "Plan Manager UI Team"

# Widget configuration defaults
DEFAULT_FONT = ("Consolas", 10)
DEFAULT_BG_COLOR = "#f8f8f8"
DEFAULT_MAX_LINES = 1000
DEFAULT_MAX_TAGS = 20