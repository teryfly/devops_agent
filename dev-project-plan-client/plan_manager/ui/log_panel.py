# Log Panel - Execution logs display

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.log_manager import LogManager

class LogPanel:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.log_manager = LogManager()
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup log panel widgets"""
        # Log toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, pady=2)
        
        ttk.Label(toolbar, text="Execution Logs", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Buttons
        ttk.Button(toolbar, text="Clear", command=self.clear_logs, width=8).pack(side=tk.RIGHT, padx=1)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_logs, width=8).pack(side=tk.RIGHT, padx=1)
        ttk.Button(toolbar, text="Export", command=self.export_logs, width=8).pack(side=tk.RIGHT, padx=1)
        
        # Log display area
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
        
        # Configure text tags for different log levels
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("timestamp", foreground="gray")
        
        self.current_document_id = None

    def load_document_logs(self, document_id):
        """Load execution logs for a document"""
        self.current_document_id = document_id
        try:
            logs = self.log_manager.list_logs(document_id)
            self._display_logs(logs)
        except Exception as e:
            self._display_error(f"Failed to load logs: {str(e)}")

    def _display_logs(self, logs):
        """Display logs in the text widget"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        
        if not logs:
            self.log_text.insert(tk.END, "No execution logs for this document.", "info")
        else:
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
                    # Truncate very long responses
                    if len(response) > 2000:
                        response = response[:2000] + "\n...[Response truncated for display]"
                    
                    self.log_text.insert(tk.END, f"Response:\n{response}\n", "info")
                
                # Request info
                size_text = f"Request size: {log['request_content_size']} bytes"
                self.log_text.insert(tk.END, size_text, "timestamp")
        
        self.log_text.config(state=tk.DISABLED)
        # Scroll to bottom
        self.log_text.see(tk.END)

    def _get_status_tag(self, status):
        """Get text tag for log status"""
        status_lower = status.lower()
        if status_lower == 'failed':
            return "error"
        elif status_lower == 'completed':
            return "success"
        elif status_lower == 'running':
            return "warning"
        else:
            return "info"

    def _display_error(self, error_message):
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
                
                messagebox.showinfo("Export", f"Logs exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")