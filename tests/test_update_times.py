import tkinter as tk
from pomodoro.ui.main import PomodoroTimer


def test_update_times():
    root = tk.Tk()
    root.withdraw()
    timer = PomodoroTimer(master=root)

    timer.work_time_entry.delete(0, tk.END)
    timer.work_time_entry.insert(0, "10")

    timer.break_time_entry.delete(0, tk.END)
    timer.break_time_entry.insert(0, "2")

    timer.update_times(None)

    assert timer.work_time == 600
    assert timer.break_time == 120
    root.destroy()
