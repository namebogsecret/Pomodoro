"""Tkinter GUI implementation of the Pomodoro timer."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import logging

from ..utils.sound import play_sound
from ..utils.settings import load_settings, save_settings, DEFAULT_SETTINGS
from ..utils.statistics import record_pomodoro, get_today_stats, get_total_stats
from ..config import (
    WORK_TIME_MIN,
    BREAK_TIME_MIN,
    LONG_BREAK_TIME_MIN,
    POMODOROS_UNTIL_LONG_BREAK,
    WARNING_THRESHOLD,
    APP_NAME,
    APP_VERSION,
)

logger = logging.getLogger(__name__)


class PomodoroTimer:
    """Main widget implementing the Pomodoro timer logic with statistics tracking."""

    def __init__(self, master: tk.Tk) -> None:
        """Create and initialize the timer."""
        self.master = master
        self.master.title(f"{APP_NAME} v{APP_VERSION}")
        self.master.resizable(False, False)

        # Load settings
        self.settings = load_settings()

        # Timer durations (in seconds)
        self.work_time = self.settings.get("work_time_minutes", WORK_TIME_MIN) * 60
        self.break_time = self.settings.get("break_time_minutes", BREAK_TIME_MIN) * 60
        self.long_break_time = self.settings.get("long_break_minutes", LONG_BREAK_TIME_MIN) * 60
        self.pomodoros_until_long_break = self.settings.get(
            "pomodoros_until_long_break", POMODOROS_UNTIL_LONG_BREAK
        )

        # State
        self.is_working = True
        self.timer_running = False
        self.paused = False
        self.time_left = self.work_time
        self.settings_visible = False
        self.pomodoro_count = 0  # Count of completed pomodoros in current session
        self.total_session_pomodoros = 0  # Total pomodoros since app start

        # Auto-start settings
        self.auto_start_breaks = self.settings.get("auto_start_breaks", True)
        self.auto_start_work = self.settings.get("auto_start_work", False)

        self.create_widgets()
        self.settings_frame.grid_remove()
        self.update_stats_display()

        logger.info("Pomodoro Timer initialized")

    def create_widgets(self) -> None:
        """Create all Tkinter widgets."""
        # Main status label
        self.label = tk.Label(self.master, text="Work Time", font=("Helvetica", 24))
        self.label.grid(row=0, column=0, columnspan=3, pady=10)

        # Pomodoro counter display
        self.counter_label = tk.Label(
            self.master,
            text=self._get_counter_text(),
            font=("Helvetica", 12),
            fg="gray"
        )
        self.counter_label.grid(row=1, column=0, columnspan=3, pady=5)

        # Time display
        self.time_label = tk.Label(
            self.master,
            text=self.format_time(self.time_left),
            font=("Helvetica", 48)
        )
        self.time_label.grid(row=2, column=0, columnspan=3, pady=10)

        # Progress indicator (dots for pomodoros)
        self.progress_frame = tk.Frame(self.master)
        self.progress_frame.grid(row=3, column=0, columnspan=3, pady=5)
        self.progress_dots = []
        self._create_progress_dots()

        # Settings frame
        self.settings_frame = tk.Frame(self.master)
        self.settings_frame.grid(row=4, column=0, columnspan=3, pady=10)

        # Work time setting
        self.work_time_label = tk.Label(
            self.settings_frame,
            text="Work time (min):",
            font=("Helvetica", 12)
        )
        self.work_time_label.grid(row=0, column=0, padx=5, pady=3, sticky="e")
        self.work_time_entry = tk.Entry(self.settings_frame, font=("Helvetica", 12), width=6)
        self.work_time_entry.grid(row=0, column=1, padx=5, pady=3)
        self.work_time_entry.insert(0, str(self.work_time // 60))
        self.work_time_entry.bind("<FocusIn>", self.select_all_text)
        self.work_time_entry.bind("<FocusOut>", self.update_times)

        # Break time setting
        self.break_time_label = tk.Label(
            self.settings_frame,
            text="Break time (min):",
            font=("Helvetica", 12)
        )
        self.break_time_label.grid(row=1, column=0, padx=5, pady=3, sticky="e")
        self.break_time_entry = tk.Entry(self.settings_frame, font=("Helvetica", 12), width=6)
        self.break_time_entry.grid(row=1, column=1, padx=5, pady=3)
        self.break_time_entry.insert(0, str(self.break_time // 60))
        self.break_time_entry.bind("<FocusIn>", self.select_all_text)
        self.break_time_entry.bind("<FocusOut>", self.update_times)

        # Long break time setting
        self.long_break_label = tk.Label(
            self.settings_frame,
            text="Long break (min):",
            font=("Helvetica", 12)
        )
        self.long_break_label.grid(row=2, column=0, padx=5, pady=3, sticky="e")
        self.long_break_entry = tk.Entry(self.settings_frame, font=("Helvetica", 12), width=6)
        self.long_break_entry.grid(row=2, column=1, padx=5, pady=3)
        self.long_break_entry.insert(0, str(self.long_break_time // 60))
        self.long_break_entry.bind("<FocusIn>", self.select_all_text)
        self.long_break_entry.bind("<FocusOut>", self.update_times)

        # Pomodoros until long break
        self.pomo_count_label = tk.Label(
            self.settings_frame,
            text="Pomos for long break:",
            font=("Helvetica", 12)
        )
        self.pomo_count_label.grid(row=3, column=0, padx=5, pady=3, sticky="e")
        self.pomo_count_entry = tk.Entry(self.settings_frame, font=("Helvetica", 12), width=6)
        self.pomo_count_entry.grid(row=3, column=1, padx=5, pady=3)
        self.pomo_count_entry.insert(0, str(self.pomodoros_until_long_break))
        self.pomo_count_entry.bind("<FocusIn>", self.select_all_text)
        self.pomo_count_entry.bind("<FocusOut>", self.update_times)

        # Auto-start checkboxes
        self.auto_break_var = tk.BooleanVar(value=self.auto_start_breaks)
        self.auto_break_check = tk.Checkbutton(
            self.settings_frame,
            text="Auto-start breaks",
            variable=self.auto_break_var,
            font=("Helvetica", 10),
            command=self._update_auto_settings
        )
        self.auto_break_check.grid(row=4, column=0, columnspan=2, pady=3)

        self.auto_work_var = tk.BooleanVar(value=self.auto_start_work)
        self.auto_work_check = tk.Checkbutton(
            self.settings_frame,
            text="Auto-start work sessions",
            variable=self.auto_work_var,
            font=("Helvetica", 10),
            command=self._update_auto_settings
        )
        self.auto_work_check.grid(row=5, column=0, columnspan=2, pady=3)

        # Save settings button
        self.save_button = tk.Button(
            self.settings_frame,
            text="Save Settings",
            command=self.save_current_settings,
            font=("Helvetica", 10)
        )
        self.save_button.grid(row=6, column=0, columnspan=2, pady=5)

        # Toggle settings button
        self.toggle_button = tk.Button(
            self.master,
            text="Show Settings",
            command=self.toggle_settings,
            font=("Helvetica", 12),
        )
        self.toggle_button.grid(row=5, column=0, columnspan=3, pady=5)

        # Control buttons frame
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        self.start_button = tk.Button(
            self.button_frame,
            text="Start",
            command=self.start_timer,
            font=("Helvetica", 14),
            width=8
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = tk.Button(
            self.button_frame,
            text="Pause",
            command=self.pause_timer,
            font=("Helvetica", 14),
            width=8
        )
        self.pause_button.grid(row=0, column=1, padx=10)

        self.reset_button = tk.Button(
            self.button_frame,
            text="Stop",
            command=self.reset_timer,
            font=("Helvetica", 14),
            width=8
        )
        self.reset_button.grid(row=0, column=2, padx=10)

        # Skip button (skip to next phase)
        self.skip_button = tk.Button(
            self.master,
            text="Skip",
            command=self.skip_phase,
            font=("Helvetica", 10),
            fg="gray"
        )
        self.skip_button.grid(row=7, column=0, columnspan=3, pady=5)

        # Statistics display
        self.stats_frame = tk.Frame(self.master)
        self.stats_frame.grid(row=8, column=0, columnspan=3, pady=10)

        self.stats_label = tk.Label(
            self.stats_frame,
            text="",
            font=("Helvetica", 10),
            fg="gray"
        )
        self.stats_label.pack()

        self.set_color("white")

    def _create_progress_dots(self) -> None:
        """Create progress indicator dots."""
        # Clear existing dots
        for dot in self.progress_dots:
            dot.destroy()
        self.progress_dots.clear()

        # Create new dots
        for i in range(self.pomodoros_until_long_break):
            dot = tk.Label(
                self.progress_frame,
                text="○",
                font=("Helvetica", 16),
                fg="gray"
            )
            dot.grid(row=0, column=i, padx=3)
            self.progress_dots.append(dot)

    def _update_progress_dots(self) -> None:
        """Update progress dots to reflect completed pomodoros."""
        completed = self.pomodoro_count % self.pomodoros_until_long_break
        for i, dot in enumerate(self.progress_dots):
            if i < completed:
                dot.config(text="●", fg="tomato")
            else:
                dot.config(text="○", fg="gray")

    def _get_counter_text(self) -> str:
        """Get the text for the pomodoro counter."""
        return f"Session: {self.total_session_pomodoros} | Cycle: {self.pomodoro_count % self.pomodoros_until_long_break}/{self.pomodoros_until_long_break}"

    def update_stats_display(self) -> None:
        """Update the statistics display."""
        today = get_today_stats()
        total = get_total_stats()
        self.stats_label.config(
            text=f"Today: {today['pomodoros']} pomodoros ({today['minutes']} min) | "
                 f"All time: {total['total_pomodoros']} | Streak: {total['streak_days']} days"
        )
        self.counter_label.config(text=self._get_counter_text())
        self._update_progress_dots()

    def _update_auto_settings(self) -> None:
        """Update auto-start settings from checkboxes."""
        self.auto_start_breaks = self.auto_break_var.get()
        self.auto_start_work = self.auto_work_var.get()

    def select_all_text(self, event: tk.Event) -> None:
        """Select all text inside the given entry widget."""
        event.widget.select_range(0, "end")

    def set_color(self, color: str) -> None:
        """Set the foreground color for timer labels."""
        self.label.config(fg=color)
        self.time_label.config(fg=color)

    def toggle_settings(self) -> None:
        """Show or hide the settings frame."""
        if self.settings_visible:
            self.settings_frame.grid_remove()
            self.toggle_button.config(text="Show Settings")
        else:
            self.settings_frame.grid()
            self.toggle_button.config(text="Hide Settings")
        self.settings_visible = not self.settings_visible

    def save_current_settings(self) -> None:
        """Save current settings to file."""
        self.settings.update({
            "work_time_minutes": self.work_time // 60,
            "break_time_minutes": self.break_time // 60,
            "long_break_minutes": self.long_break_time // 60,
            "pomodoros_until_long_break": self.pomodoros_until_long_break,
            "auto_start_breaks": self.auto_start_breaks,
            "auto_start_work": self.auto_start_work,
        })
        if save_settings(self.settings):
            messagebox.showinfo("Settings", "Settings saved successfully!")
            logger.info("Settings saved")
        else:
            messagebox.showerror("Error", "Could not save settings")
            logger.error("Failed to save settings")

    def update_times(self, event: tk.Event | None = None) -> None:
        """Update the work and break times from the entry fields with validation."""
        # Prevent changes while timer is running
        if self.timer_running or self.paused:
            return

        try:
            work_minutes = int(self.work_time_entry.get())
            break_minutes = int(self.break_time_entry.get())
            long_break_minutes = int(self.long_break_entry.get())
            pomo_count = int(self.pomo_count_entry.get())

            # Validate work time
            if work_minutes <= 0 or work_minutes > 1440:
                messagebox.showerror("Invalid Input", "Work time must be between 1 and 1440 minutes")
                self.work_time_entry.delete(0, tk.END)
                self.work_time_entry.insert(0, str(self.work_time // 60))
                return

            # Validate break time
            if break_minutes <= 0 or break_minutes > 1440:
                messagebox.showerror("Invalid Input", "Break time must be between 1 and 1440 minutes")
                self.break_time_entry.delete(0, tk.END)
                self.break_time_entry.insert(0, str(self.break_time // 60))
                return

            # Validate long break time
            if long_break_minutes <= 0 or long_break_minutes > 1440:
                messagebox.showerror("Invalid Input", "Long break time must be between 1 and 1440 minutes")
                self.long_break_entry.delete(0, tk.END)
                self.long_break_entry.insert(0, str(self.long_break_time // 60))
                return

            # Validate pomodoro count
            if pomo_count <= 0 or pomo_count > 10:
                messagebox.showerror("Invalid Input", "Pomodoros for long break must be between 1 and 10")
                self.pomo_count_entry.delete(0, tk.END)
                self.pomo_count_entry.insert(0, str(self.pomodoros_until_long_break))
                return

            self.work_time = work_minutes * 60
            self.break_time = break_minutes * 60
            self.long_break_time = long_break_minutes * 60
            self.pomodoros_until_long_break = pomo_count

            # Recreate progress dots if count changed
            self._create_progress_dots()
            self._update_progress_dots()

            self.reset_timer()
            logger.info(
                "Settings updated: work=%d, break=%d, long_break=%d, pomo_count=%d",
                work_minutes, break_minutes, long_break_minutes, pomo_count
            )
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers")
            # Reset to current values
            self._reset_entry_values()

    def _reset_entry_values(self) -> None:
        """Reset entry fields to current values."""
        self.work_time_entry.delete(0, tk.END)
        self.work_time_entry.insert(0, str(self.work_time // 60))
        self.break_time_entry.delete(0, tk.END)
        self.break_time_entry.insert(0, str(self.break_time // 60))
        self.long_break_entry.delete(0, tk.END)
        self.long_break_entry.insert(0, str(self.long_break_time // 60))
        self.pomo_count_entry.delete(0, tk.END)
        self.pomo_count_entry.insert(0, str(self.pomodoros_until_long_break))

    def format_time(self, seconds: int) -> str:
        """Format seconds as ``MM:SS``."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def update_timer(self) -> None:
        """Update the countdown timer and switch modes when needed."""
        if self.timer_running:
            if self.time_left > 0:
                self.time_left -= 1

                # Update color based on state and time remaining
                if self.is_working:
                    if self.time_left <= WARNING_THRESHOLD * self.work_time:
                        self.set_color("red")
                    else:
                        self.set_color("blue")
                else:
                    self.set_color("green")

                self.time_label.config(text=self.format_time(self.time_left))
                self.master.after(1000, self.update_timer)
            else:
                self._handle_timer_complete()

    def _handle_timer_complete(self) -> None:
        """Handle completion of a timer phase."""
        play_sound()

        if self.is_working:
            # Completed a work session
            self.pomodoro_count += 1
            self.total_session_pomodoros += 1
            work_minutes = self.work_time // 60
            record_pomodoro(work_minutes)
            logger.info("Pomodoro completed! Count: %d", self.pomodoro_count)

            # Determine break type
            if self.pomodoro_count % self.pomodoros_until_long_break == 0:
                # Long break
                self.time_left = self.long_break_time
                self.label.config(text="Long Break!")
                self.set_color("purple")
                logger.info("Starting long break")
            else:
                # Short break
                self.time_left = self.break_time
                self.label.config(text="Break Time")
                self.set_color("green")
                logger.info("Starting short break")

            self.update_stats_display()

            # Auto-start or wait
            if self.auto_start_breaks:
                self.is_working = False
                self.update_timer()
            else:
                self.timer_running = False
                self.is_working = False
                self.pause_button.config(text="Pause")
                messagebox.showinfo("Break Time!", "Time for a break! Click Start when ready.")
        else:
            # Completed a break session
            self.time_left = self.work_time
            self.label.config(text="Work Time")
            self.set_color("blue")
            logger.info("Break completed, ready for work")

            # Auto-start or wait
            if self.auto_start_work:
                self.is_working = True
                self.update_timer()
            else:
                self.timer_running = False
                self.is_working = True
                self.pause_button.config(text="Pause")
                messagebox.showinfo("Work Time!", "Break is over! Click Start when ready.")

    def skip_phase(self) -> None:
        """Skip to the next timer phase."""
        if not self.timer_running and not self.paused:
            return

        # Stop current timer
        self.timer_running = False
        self.paused = False

        if self.is_working:
            # Skip work session - don't count it as completed
            if self.pomodoro_count % self.pomodoros_until_long_break == self.pomodoros_until_long_break - 1:
                self.time_left = self.long_break_time
                self.label.config(text="Long Break!")
                self.set_color("purple")
            else:
                self.time_left = self.break_time
                self.label.config(text="Break Time")
                self.set_color("green")
            self.is_working = False
        else:
            # Skip break
            self.time_left = self.work_time
            self.label.config(text="Work Time")
            self.set_color("blue")
            self.is_working = True

        self.time_label.config(text=self.format_time(self.time_left))
        self.pause_button.config(text="Pause")
        logger.info("Phase skipped")

    def start_timer(self) -> None:
        """Start or resume the timer."""
        if not self.timer_running:
            if not self.paused:
                play_sound()
            else:
                self.paused = False
            self.timer_running = True
            self.pause_button.config(text="Pause")
            logger.info("Timer started (is_working=%s)", self.is_working)
            self.update_timer()

    def pause_timer(self) -> None:
        """Pause the running timer or resume if already paused."""
        if self.timer_running:
            self.timer_running = False
            self.paused = True
            self.pause_button.config(text="Resume")
            logger.info("Timer paused")
        elif self.paused:
            self.start_timer()

    def reset_timer(self) -> None:
        """Stop the timer and reset to the initial work period."""
        self.timer_running = False
        self.paused = False
        self.is_working = True
        self.time_left = self.work_time
        self.label.config(text="Work Time")
        self.set_color("white")
        self.time_label.config(text=self.format_time(self.time_left))
        self._reset_entry_values()
        self.pause_button.config(text="Pause")
        logger.info("Timer reset")

    def reset_session(self) -> None:
        """Reset the pomodoro counter for a new session."""
        self.pomodoro_count = 0
        self.total_session_pomodoros = 0
        self.update_stats_display()
        self.reset_timer()
        logger.info("Session reset")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(master=root)
    root.mainloop()
