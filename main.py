import tkinter as tk
from analyzer import SmartAttendanceAnalyzerApp


def main():
    root = tk.Tk()
    app = SmartAttendanceAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()