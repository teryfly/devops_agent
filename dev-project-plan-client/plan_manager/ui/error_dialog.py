# Error Dialog with copyable message

import tkinter as tk
from tkinter import ttk, messagebox
import traceback

class ErrorDialog:
    def __init__(self, parent, title="Error", message="An error occurred", details=None):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center on parent
        try:
            self.window.geometry("+%d+%d" % (
                parent.winfo_rootx() + 50,
                parent.winfo_rooty() + 50
            ))
        except:
            pass
        
        self.message = message
        self.details = details or traceback.format_exc()
        self._setup_widgets()

    def _setup_widgets(self):
        main_frame = ttk.Frame(self.window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Error icon and message
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Error icon (using text emoji)
        icon_label = ttk.Label(header_frame, text="❌", font=("Arial", 20))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Error message
        msg_label = ttk.Label(header_frame, text=self.message, font=("Arial", 10), wraplength=400)
        msg_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Details section
        details_frame = ttk.LabelFrame(main_frame, text="Error Details", padding=5)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Details text with scrollbar
        self.details_text = tk.Text(
            details_frame, 
            wrap=tk.WORD, 
            height=15, 
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)

        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insert details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.insert("1.0", self.details)
        self.details_text.config(state=tk.DISABLED)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Copy Error", command=self._copy_error).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Copy Details", command=self._copy_details).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(btn_frame, text="OK", command=self.window.destroy).pack(side=tk.RIGHT)

    def _copy_error(self):
        """Copy error message to clipboard"""
        try:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.message)
            self.window.update()
            messagebox.showinfo("Copied", "Error message copied to clipboard")
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")

    def _copy_details(self):
        """Copy full error details to clipboard"""
        try:
            full_error = f"Error: {self.message}\n\nDetails:\n{self.details}"
            self.window.clipboard_clear()
            self.window.clipboard_append(full_error)
            self.window.update()
            messagebox.showinfo("Copied", "Full error details copied to clipboard")
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")

def show_error(parent, title="Error", message="An error occurred", exception=None):
    """Show error dialog with optional exception details"""
    try:
        details = None
        if exception:
            details = f"Exception: {type(exception).__name__}\nMessage: {str(exception)}\n\nTraceback:\n{traceback.format_exc()}"
        ErrorDialog(parent, title, message, details)
    except Exception as e:
        # Fallback to simple messagebox if error dialog fails
        print(f"Error dialog failed: {e}")
        messagebox.showerror(title, f"{message}\n\nDetails: {str(exception) if exception else 'Unknown error'}")

# Test if this module can be imported
if __name__ == "__main__":
    print("ErrorDialog module loaded successfully")