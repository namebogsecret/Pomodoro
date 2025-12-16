"""Elegant minimalist Pomodoro timer with premium dark theme."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import logging
import random

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


# ═══════════════════════════════════════════════════════════════════════════════
# ELEGANT DARK THEME - Premium color palette inspired by modern design systems
# ═══════════════════════════════════════════════════════════════════════════════

class Theme:
    """Premium dark theme color palette."""

    # Base colors
    BG_DEEP = "#0d1117"           # Deep background
    BG_SURFACE = "#161b22"        # Elevated surface
    BG_ELEVATED = "#21262d"       # Cards, inputs
    BG_HOVER = "#30363d"          # Hover states

    # Text colors
    TEXT_PRIMARY = "#e6edf3"      # Primary text
    TEXT_SECONDARY = "#7d8590"    # Secondary text
    TEXT_MUTED = "#484f58"        # Muted/disabled text

    # Accent colors - Work (calm, focused blue)
    WORK_PRIMARY = "#388bfd"      # Calm blue
    WORK_GLOW = "#1f6feb"         # Glow effect
    WORK_MUTED = "#264166"        # Muted work indicator

    # Accent colors - Break (refreshing green)
    BREAK_PRIMARY = "#3fb950"     # Refreshing green
    BREAK_GLOW = "#238636"        # Glow effect
    BREAK_SOFT = "#1a4d2e"        # Soft background

    # Accent colors - Long Break (relaxing purple)
    LONG_BREAK_PRIMARY = "#a371f7"   # Lavender purple
    LONG_BREAK_GLOW = "#8957e5"      # Glow effect
    LONG_BREAK_SOFT = "#3d2a5c"      # Soft background

    # Warning (last 10% of work)
    WARNING_PRIMARY = "#f85149"   # Alert red
    WARNING_MUTED = "#5c3a3a"     # Muted warning

    # Success/complete
    SUCCESS = "#3fb950"           # Green checkmark

    # Borders
    BORDER_DEFAULT = "#30363d"    # Default border
    BORDER_MUTED = "#21262d"      # Subtle border

    # Button colors
    BTN_PRIMARY_BG = "#238636"    # Primary button
    BTN_PRIMARY_HOVER = "#2ea043" # Primary hover
    BTN_SECONDARY_BG = "#21262d"  # Secondary button
    BTN_SECONDARY_HOVER = "#30363d"  # Secondary hover


# Break time motivational messages
BREAK_MESSAGES = [
    "Time to rest your eyes",
    "Take a deep breath",
    "Stretch your shoulders",
    "Look at something distant",
    "Hydrate yourself",
    "A moment of calm",
    "You've earned this",
    "Relax and recharge",
]

LONG_BREAK_MESSAGES = [
    "Excellent progress today",
    "Take a real break",
    "Walk around a bit",
    "Great work so far",
    "Refresh your mind",
    "You're doing great",
]


class PomodoroTimer:
    """Elegant minimalist Pomodoro timer with premium dark theme."""

    def __init__(self, master: tk.Tk) -> None:
        """Create and initialize the timer."""
        self.master = master
        self.master.title(f"{APP_NAME}")
        self.master.resizable(False, False)
        self.master.configure(bg=Theme.BG_DEEP)

        # Remove window decorations for cleaner look (optional)
        # self.master.overrideredirect(True)

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
        self.pomodoro_count = 0
        self.total_session_pomodoros = 0

        # Auto-start settings
        self.auto_start_breaks = self.settings.get("auto_start_breaks", True)
        self.auto_start_work = self.settings.get("auto_start_work", False)

        # Current motivational message
        self.current_message = ""

        self.create_widgets()
        self.settings_frame.grid_remove()
        self.update_stats_display()
        self._apply_idle_state()

        logger.info("Pomodoro Timer initialized with elegant theme")

    def create_widgets(self) -> None:
        """Create all widgets with elegant dark theme."""
        # Configure grid weights for centering
        self.master.grid_columnconfigure(0, weight=1)

        # ─────────────────────────────────────────────────────────────────────
        # TOP STATUS AREA
        # ─────────────────────────────────────────────────────────────────────

        # Subtle status label
        self.label = tk.Label(
            self.master,
            text="FOCUS",
            font=("SF Pro Display", 11, "bold"),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_DEEP,
            pady=0
        )
        self.label.grid(row=0, column=0, pady=(24, 4), sticky="n")

        # ─────────────────────────────────────────────────────────────────────
        # MAIN TIMER DISPLAY
        # ─────────────────────────────────────────────────────────────────────

        # Timer container frame
        self.timer_frame = tk.Frame(self.master, bg=Theme.BG_DEEP)
        self.timer_frame.grid(row=1, column=0, pady=(8, 8))

        # Large timer display - monospace for elegance
        self.time_label = tk.Label(
            self.timer_frame,
            text=self.format_time(self.time_left),
            font=("SF Mono", 72, "bold"),
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_DEEP
        )
        self.time_label.pack()

        # ─────────────────────────────────────────────────────────────────────
        # MOTIVATIONAL MESSAGE (shown during breaks)
        # ─────────────────────────────────────────────────────────────────────

        self.message_label = tk.Label(
            self.master,
            text="",
            font=("SF Pro Display", 13),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_DEEP
        )
        self.message_label.grid(row=2, column=0, pady=(0, 12))

        # ─────────────────────────────────────────────────────────────────────
        # PROGRESS INDICATOR - Elegant dots
        # ─────────────────────────────────────────────────────────────────────

        self.progress_frame = tk.Frame(self.master, bg=Theme.BG_DEEP)
        self.progress_frame.grid(row=3, column=0, pady=(0, 20))
        self.progress_dots = []
        self._create_progress_dots()

        # ─────────────────────────────────────────────────────────────────────
        # CONTROL BUTTONS - Minimal and elegant
        # ─────────────────────────────────────────────────────────────────────

        self.button_frame = tk.Frame(self.master, bg=Theme.BG_DEEP)
        self.button_frame.grid(row=4, column=0, pady=(0, 16))

        # Start button (primary action)
        self.start_button = tk.Button(
            self.button_frame,
            text="Start",
            command=self.start_timer,
            font=("SF Pro Display", 13, "bold"),
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BTN_PRIMARY_BG,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BTN_PRIMARY_HOVER,
            relief="flat",
            width=10,
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            pady=10
        )
        self.start_button.grid(row=0, column=0, padx=6)
        self._add_button_hover(self.start_button, Theme.BTN_PRIMARY_BG, Theme.BTN_PRIMARY_HOVER)

        # Pause button
        self.pause_button = tk.Button(
            self.button_frame,
            text="Pause",
            command=self.pause_timer,
            font=("SF Pro Display", 13),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BTN_SECONDARY_BG,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BTN_SECONDARY_HOVER,
            relief="flat",
            width=10,
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            pady=10
        )
        self.pause_button.grid(row=0, column=1, padx=6)
        self._add_button_hover(self.pause_button, Theme.BTN_SECONDARY_BG, Theme.BTN_SECONDARY_HOVER)

        # Reset button
        self.reset_button = tk.Button(
            self.button_frame,
            text="Reset",
            command=self.reset_timer,
            font=("SF Pro Display", 13),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BTN_SECONDARY_BG,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BTN_SECONDARY_HOVER,
            relief="flat",
            width=10,
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            pady=10
        )
        self.reset_button.grid(row=0, column=2, padx=6)
        self._add_button_hover(self.reset_button, Theme.BTN_SECONDARY_BG, Theme.BTN_SECONDARY_HOVER)

        # ─────────────────────────────────────────────────────────────────────
        # SECONDARY CONTROLS - Skip & Settings
        # ─────────────────────────────────────────────────────────────────────

        self.secondary_frame = tk.Frame(self.master, bg=Theme.BG_DEEP)
        self.secondary_frame.grid(row=5, column=0, pady=(0, 16))

        # Skip button (subtle)
        self.skip_button = tk.Button(
            self.secondary_frame,
            text="Skip →",
            command=self.skip_phase,
            font=("SF Pro Display", 11),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_DEEP,
            activeforeground=Theme.TEXT_SECONDARY,
            activebackground=Theme.BG_SURFACE,
            relief="flat",
            cursor="hand2",
            bd=0,
            highlightthickness=0
        )
        self.skip_button.grid(row=0, column=0, padx=16)
        self._add_button_hover(self.skip_button, Theme.BG_DEEP, Theme.BG_SURFACE,
                               Theme.TEXT_MUTED, Theme.TEXT_SECONDARY)

        # Settings toggle (subtle)
        self.toggle_button = tk.Button(
            self.secondary_frame,
            text="Settings",
            command=self.toggle_settings,
            font=("SF Pro Display", 11),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_DEEP,
            activeforeground=Theme.TEXT_SECONDARY,
            activebackground=Theme.BG_SURFACE,
            relief="flat",
            cursor="hand2",
            bd=0,
            highlightthickness=0
        )
        self.toggle_button.grid(row=0, column=1, padx=16)
        self._add_button_hover(self.toggle_button, Theme.BG_DEEP, Theme.BG_SURFACE,
                               Theme.TEXT_MUTED, Theme.TEXT_SECONDARY)

        # ─────────────────────────────────────────────────────────────────────
        # SETTINGS PANEL - Hidden by default
        # ─────────────────────────────────────────────────────────────────────

        self.settings_frame = tk.Frame(
            self.master,
            bg=Theme.BG_SURFACE,
            highlightbackground=Theme.BORDER_DEFAULT,
            highlightthickness=1
        )
        self.settings_frame.grid(row=6, column=0, pady=(0, 16), padx=24, sticky="ew")

        # Settings grid
        settings_row = 0

        # Work time
        self._create_setting_row(
            self.settings_frame, settings_row, "Work duration",
            self._create_entry("work_time_entry", self.work_time // 60)
        )
        settings_row += 1

        # Break time
        self._create_setting_row(
            self.settings_frame, settings_row, "Break duration",
            self._create_entry("break_time_entry", self.break_time // 60)
        )
        settings_row += 1

        # Long break time
        self._create_setting_row(
            self.settings_frame, settings_row, "Long break",
            self._create_entry("long_break_entry", self.long_break_time // 60)
        )
        settings_row += 1

        # Pomodoros until long break
        self._create_setting_row(
            self.settings_frame, settings_row, "Sessions until long break",
            self._create_entry("pomo_count_entry", self.pomodoros_until_long_break)
        )
        settings_row += 1

        # Auto-start checkboxes frame
        auto_frame = tk.Frame(self.settings_frame, bg=Theme.BG_SURFACE)
        auto_frame.grid(row=settings_row, column=0, columnspan=2, pady=(12, 8), sticky="w", padx=16)

        self.auto_break_var = tk.BooleanVar(value=self.auto_start_breaks)
        self.auto_break_check = tk.Checkbutton(
            auto_frame,
            text="Auto-start breaks",
            variable=self.auto_break_var,
            font=("SF Pro Display", 11),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_SURFACE,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_SURFACE,
            selectcolor=Theme.BG_ELEVATED,
            command=self._update_auto_settings
        )
        self.auto_break_check.grid(row=0, column=0, padx=(0, 24))

        self.auto_work_var = tk.BooleanVar(value=self.auto_start_work)
        self.auto_work_check = tk.Checkbutton(
            auto_frame,
            text="Auto-start work",
            variable=self.auto_work_var,
            font=("SF Pro Display", 11),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_SURFACE,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_SURFACE,
            selectcolor=Theme.BG_ELEVATED,
            command=self._update_auto_settings
        )
        self.auto_work_check.grid(row=0, column=1)
        settings_row += 1

        # Save button
        self.save_button = tk.Button(
            self.settings_frame,
            text="Save",
            command=self.save_current_settings,
            font=("SF Pro Display", 11, "bold"),
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BTN_PRIMARY_BG,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BTN_PRIMARY_HOVER,
            relief="flat",
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            padx=24,
            pady=6
        )
        self.save_button.grid(row=settings_row, column=0, columnspan=2, pady=(8, 16))
        self._add_button_hover(self.save_button, Theme.BTN_PRIMARY_BG, Theme.BTN_PRIMARY_HOVER)

        # ─────────────────────────────────────────────────────────────────────
        # STATISTICS - Minimal footer
        # ─────────────────────────────────────────────────────────────────────

        self.stats_frame = tk.Frame(self.master, bg=Theme.BG_DEEP)
        self.stats_frame.grid(row=7, column=0, pady=(0, 20))

        self.stats_label = tk.Label(
            self.stats_frame,
            text="",
            font=("SF Pro Display", 10),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_DEEP
        )
        self.stats_label.pack()

    def _add_button_hover(self, button: tk.Button, bg_normal: str, bg_hover: str,
                          fg_normal: str = None, fg_hover: str = None) -> None:
        """Add hover effects to buttons."""
        def on_enter(e):
            button.config(bg=bg_hover)
            if fg_hover:
                button.config(fg=fg_hover)

        def on_leave(e):
            button.config(bg=bg_normal)
            if fg_normal:
                button.config(fg=fg_normal)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def _create_setting_row(self, parent: tk.Frame, row: int, label_text: str,
                            entry: tk.Entry) -> None:
        """Create a settings row with label and entry."""
        label = tk.Label(
            parent,
            text=label_text,
            font=("SF Pro Display", 11),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_SURFACE
        )
        label.grid(row=row, column=0, padx=(16, 12), pady=8, sticky="e")
        entry.grid(row=row, column=1, padx=(0, 16), pady=8, sticky="w")

    def _create_entry(self, attr_name: str, default_value: int) -> tk.Entry:
        """Create a styled entry widget."""
        entry = tk.Entry(
            self.settings_frame,
            font=("SF Mono", 11),
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_ELEVATED,
            insertbackground=Theme.TEXT_PRIMARY,
            relief="flat",
            width=6,
            highlightthickness=1,
            highlightbackground=Theme.BORDER_DEFAULT,
            highlightcolor=Theme.WORK_PRIMARY
        )
        entry.insert(0, str(default_value))
        entry.bind("<FocusIn>", self.select_all_text)
        entry.bind("<FocusOut>", self.update_times)
        setattr(self, attr_name, entry)
        return entry

    def _create_progress_dots(self) -> None:
        """Create elegant progress indicator dots."""
        for dot in self.progress_dots:
            dot.destroy()
        self.progress_dots.clear()

        for i in range(self.pomodoros_until_long_break):
            dot = tk.Label(
                self.progress_frame,
                text="●",
                font=("SF Pro Display", 12),
                fg=Theme.TEXT_MUTED,
                bg=Theme.BG_DEEP
            )
            dot.grid(row=0, column=i, padx=6)
            self.progress_dots.append(dot)

    def _update_progress_dots(self) -> None:
        """Update progress dots with elegant colors."""
        completed = self.pomodoro_count % self.pomodoros_until_long_break
        for i, dot in enumerate(self.progress_dots):
            if i < completed:
                dot.config(fg=Theme.SUCCESS)
            else:
                dot.config(fg=Theme.TEXT_MUTED)

    def _apply_idle_state(self) -> None:
        """Apply idle/stopped visual state - minimal and clean."""
        self.label.config(text="FOCUS", fg=Theme.TEXT_MUTED)
        self.time_label.config(fg=Theme.TEXT_PRIMARY)
        self.message_label.config(text="")
        self.master.configure(bg=Theme.BG_DEEP)
        self._update_all_backgrounds(Theme.BG_DEEP)

    def _apply_work_state(self) -> None:
        """Apply work mode visual state - focused and calm."""
        self.label.config(text="FOCUS", fg=Theme.WORK_PRIMARY)
        self.time_label.config(fg=Theme.WORK_PRIMARY)
        self.message_label.config(text="")
        self.master.configure(bg=Theme.BG_DEEP)
        self._update_all_backgrounds(Theme.BG_DEEP)

    def _apply_warning_state(self) -> None:
        """Apply warning state - subtle alert."""
        self.label.config(text="FINISHING", fg=Theme.WARNING_PRIMARY)
        self.time_label.config(fg=Theme.WARNING_PRIMARY)

    def _apply_break_state(self) -> None:
        """Apply break mode - refreshing and decorative."""
        self.current_message = random.choice(BREAK_MESSAGES)
        self.label.config(text="BREAK", fg=Theme.BREAK_PRIMARY)
        self.time_label.config(fg=Theme.BREAK_PRIMARY)
        self.message_label.config(text=self.current_message, fg=Theme.BREAK_PRIMARY)

    def _apply_long_break_state(self) -> None:
        """Apply long break mode - relaxing and celebratory."""
        self.current_message = random.choice(LONG_BREAK_MESSAGES)
        self.label.config(text="LONG BREAK", fg=Theme.LONG_BREAK_PRIMARY)
        self.time_label.config(fg=Theme.LONG_BREAK_PRIMARY)
        self.message_label.config(text=self.current_message, fg=Theme.LONG_BREAK_PRIMARY)

    def _update_all_backgrounds(self, color: str) -> None:
        """Update all widget backgrounds for theme consistency."""
        widgets_with_bg = [
            self.label, self.timer_frame, self.time_label, self.message_label,
            self.progress_frame, self.button_frame, self.secondary_frame,
            self.stats_frame, self.stats_label, self.skip_button, self.toggle_button
        ]
        for widget in widgets_with_bg:
            try:
                widget.config(bg=color)
            except tk.TclError:
                pass

        for dot in self.progress_dots:
            dot.config(bg=color)

    def _get_counter_text(self) -> str:
        """Get minimal counter text."""
        cycle_pos = self.pomodoro_count % self.pomodoros_until_long_break
        return f"Session {self.total_session_pomodoros}  •  Cycle {cycle_pos}/{self.pomodoros_until_long_break}"

    def update_stats_display(self) -> None:
        """Update the statistics display with elegant formatting."""
        today = get_today_stats()
        total = get_total_stats()

        # Minimal stats format
        parts = []
        if today['pomodoros'] > 0:
            parts.append(f"Today: {today['pomodoros']}")
        if total['streak_days'] > 0:
            parts.append(f"Streak: {total['streak_days']}d")
        parts.append(f"Total: {total['total_pomodoros']}")

        self.stats_label.config(text="  •  ".join(parts))
        self._update_progress_dots()

    def _update_auto_settings(self) -> None:
        """Update auto-start settings from checkboxes."""
        self.auto_start_breaks = self.auto_break_var.get()
        self.auto_start_work = self.auto_work_var.get()

    def select_all_text(self, event: tk.Event) -> None:
        """Select all text inside the given entry widget."""
        event.widget.select_range(0, "end")

    def toggle_settings(self) -> None:
        """Show or hide the settings panel."""
        if self.settings_visible:
            self.settings_frame.grid_remove()
            self.toggle_button.config(text="Settings")
        else:
            self.settings_frame.grid()
            self.toggle_button.config(text="Hide")
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
            # Subtle confirmation - change button text temporarily
            self.save_button.config(text="Saved ✓")
            self.master.after(1500, lambda: self.save_button.config(text="Save"))
            logger.info("Settings saved")
        else:
            messagebox.showerror("Error", "Could not save settings")
            logger.error("Failed to save settings")

    def update_times(self, event: tk.Event | None = None) -> None:
        """Update the work and break times from the entry fields."""
        if self.timer_running or self.paused:
            return

        try:
            work_minutes = int(self.work_time_entry.get())
            break_minutes = int(self.break_time_entry.get())
            long_break_minutes = int(self.long_break_entry.get())
            pomo_count = int(self.pomo_count_entry.get())

            # Validation
            if not (1 <= work_minutes <= 1440):
                self._show_validation_error("Work time: 1-1440 min")
                self.work_time_entry.delete(0, tk.END)
                self.work_time_entry.insert(0, str(self.work_time // 60))
                return

            if not (1 <= break_minutes <= 1440):
                self._show_validation_error("Break time: 1-1440 min")
                self.break_time_entry.delete(0, tk.END)
                self.break_time_entry.insert(0, str(self.break_time // 60))
                return

            if not (1 <= long_break_minutes <= 1440):
                self._show_validation_error("Long break: 1-1440 min")
                self.long_break_entry.delete(0, tk.END)
                self.long_break_entry.insert(0, str(self.long_break_time // 60))
                return

            if not (1 <= pomo_count <= 10):
                self._show_validation_error("Sessions: 1-10")
                self.pomo_count_entry.delete(0, tk.END)
                self.pomo_count_entry.insert(0, str(self.pomodoros_until_long_break))
                return

            self.work_time = work_minutes * 60
            self.break_time = break_minutes * 60
            self.long_break_time = long_break_minutes * 60
            self.pomodoros_until_long_break = pomo_count

            self._create_progress_dots()
            self._update_progress_dots()
            self.reset_timer()

            logger.info(
                "Settings updated: work=%d, break=%d, long_break=%d, pomo_count=%d",
                work_minutes, break_minutes, long_break_minutes, pomo_count
            )
        except ValueError:
            self._show_validation_error("Enter valid numbers")
            self._reset_entry_values()

    def _show_validation_error(self, message: str) -> None:
        """Show subtle validation error."""
        original_text = self.message_label.cget("text")
        original_fg = self.message_label.cget("fg")

        self.message_label.config(text=message, fg=Theme.WARNING_PRIMARY)
        self.master.after(2000, lambda: self.message_label.config(text=original_text, fg=original_fg))

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
        """Format seconds as MM:SS."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def update_timer(self) -> None:
        """Update the countdown timer."""
        if self.timer_running:
            if self.time_left > 0:
                self.time_left -= 1

                # Update visual state based on mode
                if self.is_working:
                    if self.time_left <= WARNING_THRESHOLD * self.work_time:
                        self._apply_warning_state()
                    else:
                        self._apply_work_state()

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
                self.time_left = self.long_break_time
                self._apply_long_break_state()
                logger.info("Starting long break")
            else:
                self.time_left = self.break_time
                self._apply_break_state()
                logger.info("Starting short break")

            self.update_stats_display()

            if self.auto_start_breaks:
                self.is_working = False
                self.update_timer()
            else:
                self.timer_running = False
                self.is_working = False
                self.pause_button.config(text="Pause")
        else:
            # Completed a break
            self.time_left = self.work_time
            self._apply_work_state()
            logger.info("Break completed")

            if self.auto_start_work:
                self.is_working = True
                self.update_timer()
            else:
                self.timer_running = False
                self.is_working = True
                self.pause_button.config(text="Pause")
                self._apply_idle_state()

    def skip_phase(self) -> None:
        """Skip to the next timer phase."""
        if not self.timer_running and not self.paused:
            return

        self.timer_running = False
        self.paused = False

        if self.is_working:
            if self.pomodoro_count % self.pomodoros_until_long_break == self.pomodoros_until_long_break - 1:
                self.time_left = self.long_break_time
                self._apply_long_break_state()
            else:
                self.time_left = self.break_time
                self._apply_break_state()
            self.is_working = False
        else:
            self.time_left = self.work_time
            self._apply_idle_state()
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

            # Apply appropriate visual state
            if self.is_working:
                self._apply_work_state()
            else:
                if self.time_left == self.long_break_time:
                    self._apply_long_break_state()
                else:
                    self._apply_break_state()

            logger.info("Timer started (is_working=%s)", self.is_working)
            self.update_timer()

    def pause_timer(self) -> None:
        """Pause or resume the timer."""
        if self.timer_running:
            self.timer_running = False
            self.paused = True
            self.pause_button.config(text="Resume")
            logger.info("Timer paused")
        elif self.paused:
            self.start_timer()

    def reset_timer(self) -> None:
        """Stop and reset the timer."""
        self.timer_running = False
        self.paused = False
        self.is_working = True
        self.time_left = self.work_time
        self._apply_idle_state()
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
