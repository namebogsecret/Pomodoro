import tkinter as tk
from pomodoro.ui.main import PomodoroTimer


def test_format_time():
    root = tk.Tk()
    root.withdraw()
    timer = PomodoroTimer(master=root)
    assert timer.format_time(0) == "00:00"
    assert timer.format_time(65) == "01:05"
    root.destroy()
