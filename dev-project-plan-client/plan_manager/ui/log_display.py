# Log display component

import tkinter as tk
from tkinter import ttk

class LogDisplay:
    def __init__(self, parent):
        self.parent = parent
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup log display widgets"""
        log_frame = ttk.Frame(self.parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Log text with scrollbar
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 9),
            bg="#f8f8f8"
        )

        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._configure_text_tags()

    def _configure_text_tags(self):
        """Configure text tags for different log levels"""
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("timestamp", foreground="gray")

    def display_logs(self, logs):
        """Display logs in the text widget"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)

        if not logs:
            self.log_text.insert(tk.END, "No execution logs for this document.", "info")
        else:
            self._format_and_insert_logs(logs)

        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def _format_and_insert_logs(self, logs):
        """Format and insert logs into text widget"""
        for i, log in enumerate(logs):
            if i > 0:
                self.log_text.insert(tk.END, "\n" + "="*60 + "\n", "info")

            # Log header
            header = f"[{log['request_time']}] Status: {log['status'].upper()}"
            tag = self._get_status_tag(log['status'])
            self.log_text.insert(tk.END, header, tag)

            # Duration info
            if log['duration_ms']:
                duration_text = f" | Duration: {log['duration_ms']}ms"
                self.log_text.insert(tk.END, duration_text, "timestamp")

            self.log_text.insert(tk.END, "\n")

            # Error message
            if log['error_message']:
                self.log_text.insert(tk.END, f"Error: {log['error_message']}\n", "error")

            # Server response
            if log['server_response']:
                response = log['server_response']
                if len(response) > 2000:
                    response = response[:2000] + "\n...[Response truncated for display]"

                self.log_text.insert(tk.END, f"Response:\n{response}\n", "info")

            # Request info
            size_text = f"Request size: {log['request_content_size']} bytes"
            self.log_text.insert(tk.END, size_text, "timestamp")

    def _get_status_tag(self, status):
        """Get text tag for log status"""
        status_lower = status.lower()
        status_map = {
            'failed': "error",
            'completed': "success",
            'running': "warning"
        }
        return status_map.get(status_lower, "info")

    def display_error(self, error_message):
        """Display error message"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, error_message, "error")
        self.log_text.config(state=tk.DISABLED)

    def append_log_entry(self, log_entry):
        """Append a new log entry (for real-time updates)"""
        self.log_text.config(state=tk.NORMAL)

        # Add separator if not empty
        if self.log_text.get("1.0", tk.END).strip():
            self.log_text.insert(tk.END, "\n" + "-"*40 + "\n", "info")

        # Format and insert log entry
        if isinstance(log_entry, dict):
            timestamp = log_entry.get('timestamp', 'Unknown time')
            status = log_entry.get('status', 'unknown')
            message = log_entry.get('message', '')

            header = f"[{timestamp}] {message}"
            tag = self._get_status_tag(status)
            self.log_text.insert(tk.END, header, tag)
        else:
            self.log_text.insert(tk.END, str(log_entry), "info")

        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def clear_logs(self):
        """Clear log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, "Logs cleared.", "info")
        self.log_text.config(state=tk.DISABLED)