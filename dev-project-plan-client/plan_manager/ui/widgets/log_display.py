# Log Display Widget for formatted feedback/log data - refactored

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class LogDisplay(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._log_lines = []
        self.max_lines = 1000  # Limit to prevent memory issues
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup log display widgets"""
        # Text widget with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            font=("Consolas", 9),
            bg="#f8f8f8"
        )

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._configure_tags()

    def _configure_tags(self):
        """Configure text tags for different log levels"""
        self.text.tag_configure("info", foreground="blue")
        self.text.tag_configure("warning", foreground="orange")
        self.text.tag_configure("error", foreground="red")
        self.text.tag_configure("success", foreground="green")
        self.text.tag_configure("timestamp", foreground="gray", font=("Consolas", 8))

    def append_log(self, log_text, level="info", timestamp=True):
        """Append a log entry with optional timestamp and level"""
        if timestamp:
            time_str = datetime.now().strftime("%H:%M:%S")
            formatted_log = f"[{time_str}] {log_text}"
        else:
            formatted_log = log_text

        self._log_lines.append((formatted_log, level))
        self._trim_logs()
        self.refresh_display()

    def set_logs(self, logs):
        """Set logs (replace all existing logs)"""
        if isinstance(logs, list):
            self._log_lines = [(log, "info") for log in logs]
        else:
            self._log_lines = [(str(logs), "info")]
        self._trim_logs()
        self.refresh_display()

    def refresh_display(self):
        """Refresh the display with current logs"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        for line, level in self._log_lines:
            self.text.insert(tk.END, line + "\n", level)

        self.text.config(state=tk.DISABLED)
        self.text.see(tk.END)

    def clear(self):
        """Clear all logs"""
        self._log_lines = []
        self.refresh_display()

    def save_to_file(self, filename):
        """Save logs to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Log Export - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                for line, _ in self._log_lines:
                    f.write(line + "\n")
            return True
        except Exception as e:
            print(f"Failed to save logs: {e}")
            return False

    def get_log_count(self):
        """Get current number of log lines"""
        return len(self._log_lines)

    def _trim_logs(self):
        """Trim logs to maximum allowed lines"""
        if len(self._log_lines) > self.max_lines:
            self._log_lines = self._log_lines[-self.max_lines:]

    def set_max_lines(self, max_lines):
        """Set maximum number of log lines to keep"""
        self.max_lines = max_lines
        self._trim_logs()