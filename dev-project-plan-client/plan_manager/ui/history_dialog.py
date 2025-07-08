# Document version history dialog - refactored

from .base_dialog import BaseDialog
from .history_viewer import HistoryViewer

class HistoryDialog(BaseDialog):
    def __init__(self, parent, document_manager, document):
        self.document_manager = document_manager
        self.document = document

        super().__init__(parent, f"Version History - {document['filename']}", "900x700")

        self._setup_components()
        self._setup_buttons()
        self._load_data()

    def _setup_components(self):
        """Setup history viewer component"""
        self.history_viewer = HistoryViewer(self.main_frame, self.document_manager, self.document)

    def _setup_buttons(self):
        """Setup action buttons"""
        buttons = [
            ("Restore Version", self.history_viewer.restore_version),
            ("Close", self.window.destroy)
        ]
        self.add_button_frame(buttons)

    def _load_data(self):
        """Load version history data"""
        self.history_viewer.load_versions()