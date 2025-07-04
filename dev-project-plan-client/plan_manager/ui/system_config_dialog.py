# System configuration dialog

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ConfigManager
from database.connection import test_connection, init_database

class SystemConfigDialog:
    def __init__(self, parent):
        self.parent = parent
        self.config_manager = ConfigManager()
        self.window = tk.Toplevel(parent)
        self.window.title("System Configuration")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        self._setup_widgets()
        self._load_config()

    def _setup_widgets(self):
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Database Configuration
        db_frame = ttk.LabelFrame(main_frame, text="Database Configuration", padding=10)
        db_frame.pack(fill=tk.X, pady=5)

        ttk.Label(db_frame, text="Host:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.db_host_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_host_var, width=30).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(db_frame, text="Port:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.db_port_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_port_var, width=30).grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(db_frame, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.db_user_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_user_var, width=30).grid(row=2, column=1, sticky="ew", padx=5)

        ttk.Label(db_frame, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.db_password_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_password_var, show="*", width=30).grid(row=3, column=1, sticky="ew", padx=5)

        ttk.Label(db_frame, text="Database:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.db_name_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_name_var, width=30).grid(row=4, column=1, sticky="ew", padx=5)

        db_frame.columnconfigure(1, weight=1)

        # gRPC Configuration
        grpc_frame = ttk.LabelFrame(main_frame, text="gRPC Configuration", padding=10)
        grpc_frame.pack(fill=tk.X, pady=5)

        ttk.Label(grpc_frame, text="Max Retry Count:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.retry_count_var = tk.StringVar()
        ttk.Entry(grpc_frame, textvariable=self.retry_count_var, width=30).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(grpc_frame, text="Retry Wait (seconds):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.retry_wait_var = tk.StringVar()
        ttk.Entry(grpc_frame, textvariable=self.retry_wait_var, width=30).grid(row=1, column=1, sticky="ew", padx=5)

        grpc_frame.columnconfigure(1, weight=1)

        # Log Configuration
        log_frame = ttk.LabelFrame(main_frame, text="Log Configuration", padding=10)
        log_frame.pack(fill=tk.X, pady=5)

        ttk.Label(log_frame, text="Log Level:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.log_level_var = tk.StringVar()
        log_combo = ttk.Combobox(log_frame, textvariable=self.log_level_var, state="readonly", width=27)
        log_combo['values'] = ["DEBUG", "INFO", "WARNING", "ERROR"]
        log_combo.grid(row=0, column=1, sticky="ew", padx=5)

        log_frame.columnconfigure(1, weight=1)

        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_text = tk.Text(status_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Test Connection", command=self._test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Initialize Database", command=self._init_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save", command=self._save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_config(self):
        self.db_host_var.set(self.config_manager.get_config('db_host', 'localhost'))
        self.db_port_var.set(self.config_manager.get_config('db_port', '3306'))
        self.db_user_var.set(self.config_manager.get_config('db_user', 'sa'))
        self.db_password_var.set(self.config_manager.get_config('db_password', 'dm257758'))
        self.db_name_var.set(self.config_manager.get_config('db_name', 'plan_manager'))
        self.retry_count_var.set(self.config_manager.get_config('retry_max_count', '3'))
        self.retry_wait_var.set(self.config_manager.get_config('retry_wait_seconds', '60'))
        self.log_level_var.set(self.config_manager.get_config('log_level', 'INFO'))

    def _update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert("1.0", message)
        self.status_text.config(state=tk.DISABLED)

    def _test_connection(self):
        # Get current config from UI
        config = {
            'db_host': self.db_host_var.get(),
            'db_port': self.db_port_var.get(),
            'db_user': self.db_user_var.get(),
            'db_password': self.db_password_var.get(),
            'db_name': self.db_name_var.get()
        }
        
        success, message = test_connection(config)
        self._update_status(message)
        
        if success:
            messagebox.showinfo("Connection Test", "Database connection successful!")
        else:
            messagebox.showerror("Connection Test", f"Database connection failed:\n{message}")

    def _init_database(self):
        # Save current config first
        self._save_config_to_manager()
        
        success = init_database()
        if success:
            self._update_status("Database initialized successfully!")
            messagebox.showinfo("Database Init", "Database initialized successfully!")
        else:
            self._update_status("Database initialization failed!")
            messagebox.showerror("Database Init", "Database initialization failed!")

    def _save_config_to_manager(self):
        """Save configuration to ConfigManager"""
        self.config_manager.set_config('db_host', self.db_host_var.get())
        self.config_manager.set_config('db_port', self.db_port_var.get())
        self.config_manager.set_config('db_user', self.db_user_var.get())
        self.config_manager.set_config('db_password', self.db_password_var.get())
        self.config_manager.set_config('db_name', self.db_name_var.get())
        self.config_manager.set_config('retry_max_count', self.retry_count_var.get())
        self.config_manager.set_config('retry_wait_seconds', self.retry_wait_var.get())
        self.config_manager.set_config('log_level', self.log_level_var.get())

    def _save_config(self):
        try:
            # Validate input
            port = int(self.db_port_var.get())
            retry_count = int(self.retry_count_var.get())
            retry_wait = int(self.retry_wait_var.get())
            
            if port <= 0 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
            if retry_count < 0:
                raise ValueError("Retry count must be non-negative")
            if retry_wait < 0:
                raise ValueError("Retry wait time must be non-negative")
                
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid input: {e}")
            return

        self._save_config_to_manager()
        self._update_status("Configuration saved successfully!")
        messagebox.showinfo("Configuration", "Configuration saved successfully!")
        self.window.destroy()