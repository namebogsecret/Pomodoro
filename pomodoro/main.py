"""Command line entry point for the Pomodoro GUI application."""

from __future__ import annotations

import tkinter as tk

from pomodoro.ui.main import PomodoroTimer


def main() -> None:
    """Start the Tkinter GUI application."""

    root = tk.Tk()
    app = PomodoroTimer(master=root)
    root.mainloop()


if __name__ == "__main__":
    main()


__all__ = ["main"]
