# Log Panel - Execution logs display - refactored

import tkinter as tk
from tkinter import ttk, messagebox
from .log_display import LogDisplay
from .log_toolbar import LogToolbar
from managers.log_manager import LogManager

class LogPanel:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.log_manager = LogManager()
        self.current_document_id = None

        self._setup_components()

    def _setup_components(self):
        """Setup toolbar and log display components"""
        self.toolbar = LogToolbar(self.parent, self)
        self.log_display = LogDisplay(self.parent)

    def load_document_logs(self, document_id):
        """Load execution logs for a document"""
        self.current_document_id = document_id
        try:
            logs = self.log_manager.list_logs(document_id)
            logs = list(reversed(logs))
            self.log_display.display_logs(logs)
        except Exception as e:
            self.log_display.display_error(f"Failed to load logs: {str(e)}")

    def append_log_entry(self, log_entry):
        """Append a new log entry (for real-time updates)"""
        self.log_display.append_log_entry(log_entry)

    def clear_logs(self):
        """Clear log display"""
        self.log_display.clear_logs()

    def refresh_logs(self):
        """Refresh logs for current document"""
        if self.current_document_id:
            self.load_document_logs(self.current_document_id)
        else:
            self.clear_logs()

    def export_logs(self):
        """Export logs to file"""
        if not self.current_document_id:
            messagebox.showwarning("Export", "No document selected for log export.")
            return

        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="Export Logs",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if filename:
                logs = self.log_manager.list_logs(self.current_document_id)
                self._write_logs_to_file(filename, logs)
                messagebox.showinfo("Export", f"Logs exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")

    def _write_logs_to_file(self, filename, logs):
        """Write logs to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Execution Logs Export\n")
            f.write(f"Document ID: {self.current_document_id}\n")
            f.write(f"Export Time: {tk.datetime.now()}\n")
            f.write("="*60 + "\n\n")

            for i, log in enumerate(logs):
                if i > 0:
                    f.write("\n" + "="*60 + "\n")

                f.write(f"Request Time: {log['request_time']}\n")
                f.write(f"Status: {log['status']}\n")
                f.write(f"Duration: {log['duration_ms']}ms\n")
                f.write(f"Request Size: {log['request_content_size']} bytes\n")

                if log['error_message']:
                    f.write(f"Error: {log['error_message']}\n")

                if log['server_response']:
                    f.write(f"Response:\n{log['server_response']}\n")