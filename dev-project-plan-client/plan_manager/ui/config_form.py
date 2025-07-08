# Configuration form component

import tkinter as tk
from tkinter import ttk, messagebox
from config import ConfigManager
from .form_builder import FormBuilder

class ConfigForm:
    def __init__(self, parent):
        self.parent = parent
        self.config_manager = ConfigManager()

        self._setup_variables()
        self._setup_widgets()

    def _setup_variables(self):
        """Initialize form variables"""
        self.db_host_var = tk.StringVar()
        self.db_port_var = tk.StringVar()
        self.db_user_var = tk.StringVar()
        self.db_password_var = tk.StringVar()
        self.db_name_var = tk.StringVar()
        self.retry_count_var = tk.StringVar()
        self.retry_wait_var = tk.StringVar()
        self.log_level_var = tk.StringVar()

    def _setup_widgets(self):
        """Setup form widgets"""
        self._setup_database_section()
        self._setup_grpc_section()
        self._setup_log_section()

    def _setup_database_section(self):
        """Setup database configuration section"""
        db_frame = ttk.LabelFrame(self.parent, text="Database Configuration", padding=10)
        db_frame.pack(fill=tk.X, pady=5)

        form_builder = FormBuilder(db_frame)
        form_builder.add_entry("Host", self.db_host_var, width=30)
        form_builder.add_entry("Port", self.db_port_var, width=30)
        form_builder.add_entry("Username", self.db_user_var, width=30)
        form_builder.add_entry("Password", self.db_password_var, width=30, show="*")
        form_builder.add_entry("Database", self.db_name_var, width=30)

        db_frame.columnconfigure(1, weight=1)

    def _setup_grpc_section(self):
        """Setup gRPC configuration section"""
        grpc_frame = ttk.LabelFrame(self.parent, text="gRPC Configuration", padding=10)
        grpc_frame.pack(fill=tk.X, pady=5)

        form_builder = FormBuilder(grpc_frame)
        form_builder.add_entry("Max Retry Count", self.retry_count_var, width=30)
        form_builder.add_entry("Retry Wait (seconds)", self.retry_wait_var, width=30)

        grpc_frame.columnconfigure(1, weight=1)

    def _setup_log_section(self):
        """Setup log configuration section"""
        log_frame = ttk.LabelFrame(self.parent, text="Log Configuration", padding=10)
        log_frame.pack(fill=tk.X, pady=5)

        form_builder = FormBuilder(log_frame)
        form_builder.add_combobox(
            "Log Level", self.log_level_var,
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            width=27
        )

        log_frame.columnconfigure(1, weight=1)

    def load_config(self):
        """Load configuration from ConfigManager"""
        self.db_host_var.set(self.config_manager.get_config('db_host', 'localhost'))
        self.db_port_var.set(self.config_manager.get_config('db_port', '3306'))
        self.db_user_var.set(self.config_manager.get_config('db_user', 'sa'))
        self.db_password_var.set(self.config_manager.get_config('db_password', 'dm257758'))
        self.db_name_var.set(self.config_manager.get_config('db_name', 'plan_manager'))
        self.retry_count_var.set(self.config_manager.get_config('retry_max_count', '3'))
        self.retry_wait_var.set(self.config_manager.get_config('retry_wait_seconds', '60'))
        self.log_level_var.set(self.config_manager.get_config('log_level', 'INFO'))

    def get_config_dict(self):
        """Get configuration as dictionary"""
        return {
            'db_host': self.db_host_var.get(),
            'db_port': self.db_port_var.get(),
            'db_user': self.db_user_var.get(),
            'db_password': self.db_password_var.get(),
            'db_name': self.db_name_var.get(),
            'retry_max_count': self.retry_count_var.get(),
            'retry_wait_seconds': self.retry_wait_var.get(),
            'log_level': self.log_level_var.get()
        }

    def save_config(self):
        """Save configuration"""
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
            return False

        # Save to ConfigManager
        config = self.get_config_dict()
        for key, value in config.items():
            self.config_manager.set_config(key, value)

        messagebox.showinfo("Configuration", "Configuration saved successfully!")
        return True