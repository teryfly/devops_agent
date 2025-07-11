from tkinter import Toplevel, scrolledtext, END, DISABLED, NORMAL

class CLIExecuteLogWindow:
    """CLI风格执行日志弹窗（非模态），可多开，线程安全"""
    def __init__(self, parent, title="执行日志"):
        self.top = Toplevel(parent) if parent else Toplevel()
        self.top.title(title)
        self.text = scrolledtext.ScrolledText(self.top, width=100, height=32, state=DISABLED, font=("Consolas", 10))
        self.text.pack(expand=True, fill='both')
        self.top.transient(parent)
        self.top.focus_set()
        self.show_log("执行准备中...\n")

    def show_log(self, msg, level="info"):
        self.text.config(state=NORMAL)
        if isinstance(msg, str):
            self.text.insert(END, msg + "\n")
        elif isinstance(msg, dict):
            self.text.insert(END, str(msg) + "\n")
        self.text.see(END)
        self.text.config(state=DISABLED)
        self.top.update()