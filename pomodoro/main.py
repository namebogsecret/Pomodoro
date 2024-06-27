from pomodoro.ui.main import PomodoroTimer

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    app = PomodoroTimer(master=root)
    root.mainloop()
