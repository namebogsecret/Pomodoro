import tkinter as tk
from pomodoro.ui.main import PomodoroTimer


def test_pause_resume():
    root = tk.Tk()
    root.withdraw()
    timer = PomodoroTimer(master=root)
    timer.start_timer()
    assert timer.timer_running
    timer.pause_timer()
    assert not timer.timer_running and timer.paused
    timer.pause_timer()
    assert timer.timer_running and not timer.paused
    root.destroy()

