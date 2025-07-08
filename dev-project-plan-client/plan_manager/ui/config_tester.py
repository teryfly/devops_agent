# Configuration testing component

import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import test_connection, init_database

class ConfigTester:
    def __init__(self, parent, config_form):
        self.parent = parent
        self.config_form = config_form
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup status display widgets"""
        status_frame = ttk.LabelFrame(self.parent, text="Connection Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_text = tk.Text(status_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)

    def test_connection(self):
        """Test database connection"""
        config = self.config_form.get_config_dict()
        success, message = test_connection(config)

        self._update_status(message)

        if success:
            messagebox.showinfo("Connection Test", "Database connection successful!")
        else:
            messagebox.showerror("Connection Test", f"Database connection failed:\n{message}")

    def init_database(self):
        """Initialize database"""
        # Save current config first
        self.config_form.save_config()

        success = init_database()
        if success:
            self._update_status("Database initialized successfully!")
            messagebox.showinfo("Database Init", "Database initialized successfully!")
        else:
            self._update_status("Database initialization failed!")
            messagebox.showerror("Database Init", "Database initialization failed!")

    def _update_status(self, message):
        """Update status display"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert("1.0", message)
        self.status_text.config(state=tk.DISABLED)