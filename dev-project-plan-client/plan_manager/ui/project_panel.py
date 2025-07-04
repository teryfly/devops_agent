# Project Panel - Left side project list and info

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProjectPanel:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.projects = []
        self.on_project_select = None  # Callback function
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup project panel widgets"""
        # Title
        ttk.Label(self.parent, text="Projects", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Project list with scrollbar
        list_frame = ttk.Frame(self.parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.project_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.project_listbox.yview)
        self.project_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.project_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Event bindings
        self.project_listbox.bind('<<ListboxSelect>>', self._on_listbox_select)
        self.project_listbox.bind('<Double-Button-1>', self._on_double_click)
        
        # Project info display
        info_frame = ttk.LabelFrame(self.parent, text="Project Info", padding=5)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 9))
        info_scrollbar = ttk.Scrollbar(info_frame, command=self.project_info_text.yview)
        self.project_info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.project_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_projects(self):
        """Load projects into the list"""
        try:
            self.project_listbox.delete(0, tk.END)
            self.projects = self.main_window.project_manager.list_projects()
            
            for project in self.projects:
                display_text = f"{project['id']} - {project['name']}"
                self.project_listbox.insert(tk.END, display_text)
            
            self.main_window.update_status(f"Loaded {len(self.projects)} projects")
            
            # Clear selection
            self._display_project_info(None)
            if self.on_project_select:
                self.on_project_select(None)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {str(e)}")
            self.main_window.update_status("Error loading projects")

    def _on_listbox_select(self, event):
        """Handle project list selection"""
        selection = self.project_listbox.curselection()
        if selection:
            index = selection[0]
            project = self.projects[index]
            self._display_project_info(project)
            if self.on_project_select:
                self.on_project_select(project)
        else:
            self._display_project_info(None)
            if self.on_project_select:
                self.on_project_select(None)

    def _on_double_click(self, event):
        """Handle double click to edit project"""
        if self.main_window.current_project:
            self.main_window.menu_toolbar.edit_project()

    def _display_project_info(self, project):
        """Display project information"""
        self.project_info_text.config(state=tk.NORMAL)
        self.project_info_text.delete("1.0", tk.END)
        
        if project:
            info = f"ID: {project['id']}\n"
            info += f"Name: {project['name']}\n"
            info += f"Environment: {project['dev_environment']}\n"
            info += f"gRPC Server: {project['grpc_server_address']}\n"
            info += f"Created: {project['created_time']}\n"
            info += f"Updated: {project['updated_time']}"
            self.project_info_text.insert("1.0", info)
        else:
            self.project_info_text.insert("1.0", "No project selected")
            
        self.project_info_text.config(state=tk.DISABLED)

    def get_selected_project(self):
        """Get currently selected project"""
        selection = self.project_listbox.curselection()
        if selection:
            index = selection[0]
            return self.projects[index]
        return None