# System configuration dialog - refactored

from .base_dialog import BaseDialog
from .config_form import ConfigForm
from .config_tester import ConfigTester

class SystemConfigDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__(parent, "System Configuration", "600x500")

        self._setup_components()
        self._setup_buttons()
        self._load_initial_data()

    def _setup_components(self):
        """Setup form and tester components"""
        self.config_form = ConfigForm(self.main_frame)
        self.config_tester = ConfigTester(self.main_frame, self.config_form)

    def _setup_buttons(self):
        """Setup action buttons"""
        buttons = [
            ("Test Connection", self.config_tester.test_connection),
            ("Initialize Database", self.config_tester.init_database),
            ("Save", self._save_config),
            ("Cancel", self.window.destroy)
        ]
        self.add_button_frame(buttons)

    def _load_initial_data(self):
        """Load initial configuration data"""
        self.config_form.load_config()

    def _save_config(self):
        """Save configuration"""
        if self.config_form.save_config():
            self.window.destroy()