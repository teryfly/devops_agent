# Main program entry point for Plan Manager
# Launches the Tkinter UI

from ui.main_window import MainWindow

def main():
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()