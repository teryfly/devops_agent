# ui/error_dialog.py

from .base_dialog import BaseDialog
from .error_display import ErrorDisplay

class ErrorDialog(BaseDialog):
    def __init__(self, parent, title="Error", message="An error occurred", details=None):
        self.message = message
        self.details = details or self._get_traceback()

        super().__init__(parent, title, "500x400")
        self._setup_components()
        self._setup_buttons()

    def _setup_components(self):
        """Setup error display component"""
        # 内容区用 self.content_frame
        self.error_display = ErrorDisplay(self.content_frame, self.message, self.details)

    def _setup_buttons(self):
        """Setup action buttons"""
        buttons = [
            ("Copy Error", self.error_display.copy_error),
            ("Copy Details", self.error_display.copy_details),
            ("OK", self.window.destroy)
        ]
        self.add_button_frame(buttons)

    def _get_traceback(self):
        """Get current traceback"""
        import traceback
        return traceback.format_exc()

def show_error(parent, title="Error", message="An error occurred", exception=None):
    """Show error dialog with optional exception details"""
    try:
        details = None
        if exception:
            import traceback
            details = f"Exception: {type(exception).__name__}\nMessage: {str(exception)}\n\nTraceback:\n{traceback.format_exc()}"
        ErrorDialog(parent, title, message, details)
    except Exception as e:
        # Fallback to simple messagebox if error dialog fails
        print(f"Error dialog failed: {e}")
        import tkinter.messagebox as messagebox
        messagebox.showerror(title, f"{message}\n\nDetails: {str(exception) if exception else 'Unknown error'}")