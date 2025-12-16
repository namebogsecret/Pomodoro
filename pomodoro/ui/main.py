"""Premium minimalist Pomodoro timer with elegant floating design."""

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
# PREMIUM DARK THEME - Sophisticated, understated elegance
# ═══════════════════════════════════════════════════════════════════════════════

class Theme:
    """Premium dark theme - refined and sophisticated."""

    # Background gradient simulation (deep charcoal)
    BG_PRIMARY = "#1a1a2e"        # Rich dark blue-gray
    BG_SECONDARY = "#16213e"      # Slightly lighter
    BG_CARD = "#1f2937"           # Card background
    BG_INPUT = "#111827"          # Input fields

    # Text hierarchy
    TEXT_PRIMARY = "#f8fafc"      # Bright white
    TEXT_SECONDARY = "#94a3b8"    # Muted silver
    TEXT_MUTED = "#64748b"        # Subtle gray
    TEXT_DISABLED = "#475569"     # Disabled state

    # Accent - Focus mode (elegant blue)
    FOCUS_PRIMARY = "#60a5fa"     # Soft sky blue
    FOCUS_SECONDARY = "#3b82f6"   # Medium blue
    FOCUS_MUTED = "#1e40af"       # Deep blue

    # Accent - Break mode (calming green)
    BREAK_PRIMARY = "#4ade80"     # Fresh mint
    BREAK_SECONDARY = "#22c55e"   # Green
    BREAK_MUTED = "#166534"       # Deep green

    # Accent - Long break (relaxing violet)
    LONG_BREAK_PRIMARY = "#c084fc" # Soft lavender
    LONG_BREAK_SECONDARY = "#a855f7"  # Purple
    LONG_BREAK_MUTED = "#6b21a8"  # Deep purple

    # Warning (subtle amber)
    WARNING_PRIMARY = "#fbbf24"   # Warm amber
    WARNING_MUTED = "#92400e"     # Deep amber

    # Interactive elements
    BUTTON_PRIMARY = "#3b82f6"    # Blue button
    BUTTON_HOVER = "#2563eb"      # Hover state
    BUTTON_SUBTLE = "#334155"     # Subtle button
    BUTTON_SUBTLE_HOVER = "#475569"

    # Borders and dividers
    BORDER_SUBTLE = "#334155"     # Subtle borders
    BORDER_ACTIVE = "#60a5fa"     # Active/focus border


# Motivational messages
BREAK_MESSAGES = [
    "Rest your eyes",
    "Deep breath",
    "Stretch a little",
    "Look away",
    "Stay hydrated",
    "Relax",
]

LONG_BREAK_MESSAGES = [
    "Great progress",
    "Well deserved",
    "Take a walk",
    "Refresh your mind",
]


class RoundedButton(tk.Canvas):
    """Elegant rounded button using Canvas."""

    def __init__(self, parent, text, command, width=100, height=36,
                 bg=Theme.BUTTON_SUBTLE, hover_bg=Theme.BUTTON_SUBTLE_HOVER,
                 fg=Theme.TEXT_SECONDARY, active_fg=Theme.TEXT_PRIMARY,
                 font=("Helvetica Neue", 11), radius=18, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=Theme.BG_PRIMARY, highlightthickness=0, **kwargs)

        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.active_fg = active_fg
        self.font = font
        self.radius = radius
        self.is_hovered = False
        self.is_disabled = False

        self._draw()
        self._bind_events()

    def _draw(self):
        """Draw the rounded button."""
        self.delete("all")

        r = self.radius
        w = self.width
        h = self.height

        color = self.hover_bg if self.is_hovered else self.bg
        text_color = self.active_fg if self.is_hovered else self.fg

        if self.is_disabled:
            color = Theme.BG_CARD
            text_color = Theme.TEXT_DISABLED

        # Draw rounded rectangle
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=color, outline="")
        self.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=color, outline="")
        self.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=color, outline="")
        self.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=color, outline="")
        self.create_rectangle(r, 0, w-r, h, fill=color, outline="")
        self.create_rectangle(0, r, w, h-r, fill=color, outline="")

        # Draw text
        self.create_text(w/2, h/2, text=self.text, fill=text_color, font=self.font)

    def _bind_events(self):
        """Bind mouse events."""
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, event):
        if not self.is_disabled:
            self.is_hovered = True
            self._draw()
            self.config(cursor="hand2")

    def _on_leave(self, event):
        self.is_hovered = False
        self._draw()
        self.config(cursor="")

    def _on_click(self, event):
        if not self.is_disabled and self.command:
            self.command()

    def set_text(self, text):
        """Update button text."""
        self.text = text
        self._draw()

    def set_disabled(self, disabled):
        """Enable/disable button."""
        self.is_disabled = disabled
        self._draw()

    def set_colors(self, bg=None, hover_bg=None, fg=None, active_fg=None):
        """Update button colors."""
        if bg:
            self.bg = bg
        if hover_bg:
            self.hover_bg = hover_bg
        if fg:
            self.fg = fg
        if active_fg:
            self.active_fg = active_fg
        self._draw()

    def update_bg(self, parent_bg):
        """Update canvas background to match parent."""
        self.config(bg=parent_bg)


class PomodoroTimer:
    """Premium minimalist Pomodoro timer."""

    def __init__(self, master: tk.Tk) -> None:
        """Initialize the timer."""
        self.master = master
        self.master.title(APP_NAME)
        self.master.resizable(False, False)
        self.master.configure(bg=Theme.BG_PRIMARY)

        # Load settings
        self.settings = load_settings()

        # Timer durations
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
        self.current_accent = Theme.FOCUS_PRIMARY

        # Auto-start
        self.auto_start_breaks = self.settings.get("auto_start_breaks", True)
        self.auto_start_work = self.settings.get("auto_start_work", False)

        self.current_message = ""

        self._create_ui()
        self.settings_frame.grid_remove()
        self.update_stats_display()

        logger.info("Premium Pomodoro Timer initialized")

    def _create_ui(self) -> None:
        """Create the elegant UI."""
        self.master.grid_columnconfigure(0, weight=1)

        # ───────────────────────────────────────────────────────────────────
        # MODE INDICATOR (subtle, top)
        # ───────────────────────────────────────────────────────────────────

        self.mode_label = tk.Label(
            self.master,
            text="FOCUS",
            font=("Helvetica Neue", 10, "bold"),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_PRIMARY,
            pady=0
        )
        self.mode_label.grid(row=0, column=0, pady=(28, 0))

        # ───────────────────────────────────────────────────────────────────
        # TIMER DISPLAY (large, elegant)
        # ───────────────────────────────────────────────────────────────────

        self.timer_frame = tk.Frame(self.master, bg=Theme.BG_PRIMARY)
        self.timer_frame.grid(row=1, column=0, pady=(4, 0))

        self.time_label = tk.Label(
            self.timer_frame,
            text=self.format_time(self.time_left),
            font=("Helvetica Neue", 64, "bold"),
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_PRIMARY
        )
        self.time_label.pack()

        # ───────────────────────────────────────────────────────────────────
        # MESSAGE (shown during breaks)
        # ───────────────────────────────────────────────────────────────────

        self.message_label = tk.Label(
            self.master,
            text="",
            font=("Helvetica Neue", 12),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_PRIMARY
        )
        self.message_label.grid(row=2, column=0, pady=(0, 8))

        # ───────────────────────────────────────────────────────────────────
        # PROGRESS DOTS
        # ───────────────────────────────────────────────────────────────────

        self.progress_frame = tk.Frame(self.master, bg=Theme.BG_PRIMARY)
        self.progress_frame.grid(row=3, column=0, pady=(0, 24))
        self.progress_dots = []
        self._create_progress_dots()

        # ───────────────────────────────────────────────────────────────────
        # MAIN CONTROL BUTTONS (elegant pills)
        # ───────────────────────────────────────────────────────────────────

        self.button_frame = tk.Frame(self.master, bg=Theme.BG_PRIMARY)
        self.button_frame.grid(row=4, column=0, pady=(0, 12))

        # Start button (primary - colored)
        self.start_button = RoundedButton(
            self.button_frame,
            text="Start",
            command=self.start_timer,
            width=90,
            height=36,
            bg=Theme.BUTTON_PRIMARY,
            hover_bg=Theme.BUTTON_HOVER,
            fg=Theme.TEXT_PRIMARY,
            active_fg=Theme.TEXT_PRIMARY,
            font=("Helvetica Neue", 11, "bold"),
            radius=18
        )
        self.start_button.grid(row=0, column=0, padx=4)

        # Pause button
        self.pause_button = RoundedButton(
            self.button_frame,
            text="Pause",
            command=self.pause_timer,
            width=90,
            height=36,
            radius=18
        )
        self.pause_button.grid(row=0, column=1, padx=4)

        # Reset button
        self.reset_button = RoundedButton(
            self.button_frame,
            text="Reset",
            command=self.reset_timer,
            width=90,
            height=36,
            radius=18
        )
        self.reset_button.grid(row=0, column=2, padx=4)

        # ───────────────────────────────────────────────────────────────────
        # SECONDARY CONTROLS (subtle text buttons)
        # ───────────────────────────────────────────────────────────────────

        self.secondary_frame = tk.Frame(self.master, bg=Theme.BG_PRIMARY)
        self.secondary_frame.grid(row=5, column=0, pady=(0, 16))

        self.skip_button = tk.Label(
            self.secondary_frame,
            text="Skip",
            font=("Helvetica Neue", 10),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_PRIMARY,
            cursor="hand2"
        )
        self.skip_button.grid(row=0, column=0, padx=20)
        self.skip_button.bind("<Button-1>", lambda e: self.skip_phase())
        self.skip_button.bind("<Enter>", lambda e: self.skip_button.config(fg=Theme.TEXT_SECONDARY))
        self.skip_button.bind("<Leave>", lambda e: self.skip_button.config(fg=Theme.TEXT_MUTED))

        self.settings_toggle = tk.Label(
            self.secondary_frame,
            text="Settings",
            font=("Helvetica Neue", 10),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_PRIMARY,
            cursor="hand2"
        )
        self.settings_toggle.grid(row=0, column=1, padx=20)
        self.settings_toggle.bind("<Button-1>", lambda e: self.toggle_settings())
        self.settings_toggle.bind("<Enter>", lambda e: self.settings_toggle.config(fg=Theme.TEXT_SECONDARY))
        self.settings_toggle.bind("<Leave>", lambda e: self.settings_toggle.config(fg=Theme.TEXT_MUTED))

        # ───────────────────────────────────────────────────────────────────
        # SETTINGS PANEL (hidden by default)
        # ───────────────────────────────────────────────────────────────────

        self.settings_frame = tk.Frame(
            self.master,
            bg=Theme.BG_CARD,
            highlightthickness=0
        )
        self.settings_frame.grid(row=6, column=0, pady=(0, 16), padx=32, sticky="ew")

        # Settings content
        settings_inner = tk.Frame(self.settings_frame, bg=Theme.BG_CARD)
        settings_inner.pack(padx=16, pady=12)

        row = 0
        self.work_time_entry = self._create_setting_row(settings_inner, row, "Work", self.work_time // 60)
        row += 1
        self.break_time_entry = self._create_setting_row(settings_inner, row, "Break", self.break_time // 60)
        row += 1
        self.long_break_entry = self._create_setting_row(settings_inner, row, "Long break", self.long_break_time // 60)
        row += 1
        self.pomo_count_entry = self._create_setting_row(settings_inner, row, "Sessions", self.pomodoros_until_long_break)
        row += 1

        # Auto-start options
        auto_frame = tk.Frame(settings_inner, bg=Theme.BG_CARD)
        auto_frame.grid(row=row, column=0, columnspan=2, pady=(8, 4), sticky="w")

        self.auto_break_var = tk.BooleanVar(value=self.auto_start_breaks)
        self.auto_break_check = tk.Checkbutton(
            auto_frame,
            text="Auto breaks",
            variable=self.auto_break_var,
            font=("Helvetica Neue", 10),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_CARD,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_CARD,
            selectcolor=Theme.BG_INPUT,
            command=self._update_auto_settings
        )
        self.auto_break_check.pack(side="left", padx=(0, 16))

        self.auto_work_var = tk.BooleanVar(value=self.auto_start_work)
        self.auto_work_check = tk.Checkbutton(
            auto_frame,
            text="Auto work",
            variable=self.auto_work_var,
            font=("Helvetica Neue", 10),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_CARD,
            activeforeground=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_CARD,
            selectcolor=Theme.BG_INPUT,
            command=self._update_auto_settings
        )
        self.auto_work_check.pack(side="left")
        row += 1

        # Save button
        self.save_button = RoundedButton(
            settings_inner,
            text="Save",
            command=self.save_current_settings,
            width=80,
            height=32,
            bg=Theme.BUTTON_PRIMARY,
            hover_bg=Theme.BUTTON_HOVER,
            fg=Theme.TEXT_PRIMARY,
            active_fg=Theme.TEXT_PRIMARY,
            font=("Helvetica Neue", 10, "bold"),
            radius=16
        )
        self.save_button.config(bg=Theme.BG_CARD)
        self.save_button.grid(row=row, column=0, columnspan=2, pady=(8, 0))

        # ───────────────────────────────────────────────────────────────────
        # STATS FOOTER
        # ───────────────────────────────────────────────────────────────────

        self.stats_label = tk.Label(
            self.master,
            text="",
            font=("Helvetica Neue", 10),
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_PRIMARY
        )
        self.stats_label.grid(row=7, column=0, pady=(0, 20))

    def _create_setting_row(self, parent, row, label_text, value):
        """Create a settings row."""
        label = tk.Label(
            parent,
            text=label_text,
            font=("Helvetica Neue", 10),
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_CARD
        )
        label.grid(row=row, column=0, padx=(0, 12), pady=4, sticky="e")

        entry = tk.Entry(
            parent,
            font=("Helvetica Neue", 10),
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_INPUT,
            insertbackground=Theme.TEXT_PRIMARY,
            relief="flat",
            width=5,
            highlightthickness=1,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightcolor=Theme.BORDER_ACTIVE
        )
        entry.insert(0, str(value))
        entry.bind("<FocusIn>", self.select_all_text)
        entry.bind("<FocusOut>", self.update_times)
        entry.grid(row=row, column=1, pady=4, sticky="w")

        return entry

    def _create_progress_dots(self) -> None:
        """Create progress dots."""
        for dot in self.progress_dots:
            dot.destroy()
        self.progress_dots.clear()

        for i in range(self.pomodoros_until_long_break):
            dot = tk.Canvas(
                self.progress_frame,
                width=10,
                height=10,
                bg=Theme.BG_PRIMARY,
                highlightthickness=0
            )
            dot.create_oval(1, 1, 9, 9, fill=Theme.TEXT_DISABLED, outline="")
            dot.grid(row=0, column=i, padx=4)
            self.progress_dots.append(dot)

    def _update_progress_dots(self) -> None:
        """Update progress dots."""
        completed = self.pomodoro_count % self.pomodoros_until_long_break
        for i, dot in enumerate(self.progress_dots):
            dot.delete("all")
            color = Theme.BREAK_PRIMARY if i < completed else Theme.TEXT_DISABLED
            dot.create_oval(1, 1, 9, 9, fill=color, outline="")

    def _apply_idle_state(self) -> None:
        """Apply idle visual state."""
        self.mode_label.config(text="FOCUS", fg=Theme.TEXT_MUTED)
        self.time_label.config(fg=Theme.TEXT_PRIMARY)
        self.message_label.config(text="")
        self.current_accent = Theme.TEXT_PRIMARY

    def _apply_work_state(self) -> None:
        """Apply work mode visual state."""
        self.mode_label.config(text="FOCUS", fg=Theme.FOCUS_PRIMARY)
        self.time_label.config(fg=Theme.FOCUS_PRIMARY)
        self.message_label.config(text="")
        self.current_accent = Theme.FOCUS_PRIMARY

    def _apply_warning_state(self) -> None:
        """Apply warning state."""
        self.mode_label.config(text="FINISHING", fg=Theme.WARNING_PRIMARY)
        self.time_label.config(fg=Theme.WARNING_PRIMARY)
        self.current_accent = Theme.WARNING_PRIMARY

    def _apply_break_state(self) -> None:
        """Apply break mode."""
        self.current_message = random.choice(BREAK_MESSAGES)
        self.mode_label.config(text="BREAK", fg=Theme.BREAK_PRIMARY)
        self.time_label.config(fg=Theme.BREAK_PRIMARY)
        self.message_label.config(text=self.current_message, fg=Theme.BREAK_PRIMARY)
        self.current_accent = Theme.BREAK_PRIMARY

    def _apply_long_break_state(self) -> None:
        """Apply long break mode."""
        self.current_message = random.choice(LONG_BREAK_MESSAGES)
        self.mode_label.config(text="LONG BREAK", fg=Theme.LONG_BREAK_PRIMARY)
        self.time_label.config(fg=Theme.LONG_BREAK_PRIMARY)
        self.message_label.config(text=self.current_message, fg=Theme.LONG_BREAK_PRIMARY)
        self.current_accent = Theme.LONG_BREAK_PRIMARY

    def update_stats_display(self) -> None:
        """Update statistics display."""
        today = get_today_stats()
        total = get_total_stats()

        parts = []
        if today['pomodoros'] > 0:
            parts.append(f"Today: {today['pomodoros']}")
        parts.append(f"Total: {total['total_pomodoros']}")

        self.stats_label.config(text="  ·  ".join(parts))
        self._update_progress_dots()

    def _update_auto_settings(self) -> None:
        """Update auto-start settings."""
        self.auto_start_breaks = self.auto_break_var.get()
        self.auto_start_work = self.auto_work_var.get()

    def select_all_text(self, event: tk.Event) -> None:
        """Select all text in entry."""
        event.widget.select_range(0, "end")

    def toggle_settings(self) -> None:
        """Toggle settings panel."""
        if self.settings_visible:
            self.settings_frame.grid_remove()
        else:
            self.settings_frame.grid()
        self.settings_visible = not self.settings_visible

    def save_current_settings(self) -> None:
        """Save settings."""
        self.settings.update({
            "work_time_minutes": self.work_time // 60,
            "break_time_minutes": self.break_time // 60,
            "long_break_minutes": self.long_break_time // 60,
            "pomodoros_until_long_break": self.pomodoros_until_long_break,
            "auto_start_breaks": self.auto_start_breaks,
            "auto_start_work": self.auto_start_work,
        })
        if save_settings(self.settings):
            self.save_button.set_text("Saved")
            self.master.after(1500, lambda: self.save_button.set_text("Save"))
            logger.info("Settings saved")
        else:
            messagebox.showerror("Error", "Could not save settings")
            logger.error("Failed to save settings")

    def update_times(self, event: tk.Event | None = None) -> None:
        """Update times from entry fields."""
        if self.timer_running or self.paused:
            return

        try:
            work_minutes = int(self.work_time_entry.get())
            break_minutes = int(self.break_time_entry.get())
            long_break_minutes = int(self.long_break_entry.get())
            pomo_count = int(self.pomo_count_entry.get())

            if not (1 <= work_minutes <= 1440):
                self._show_validation_error("Work: 1-1440")
                self._reset_entry_values()
                return

            if not (1 <= break_minutes <= 1440):
                self._show_validation_error("Break: 1-1440")
                self._reset_entry_values()
                return

            if not (1 <= long_break_minutes <= 1440):
                self._show_validation_error("Long break: 1-1440")
                self._reset_entry_values()
                return

            if not (1 <= pomo_count <= 10):
                self._show_validation_error("Sessions: 1-10")
                self._reset_entry_values()
                return

            self.work_time = work_minutes * 60
            self.break_time = break_minutes * 60
            self.long_break_time = long_break_minutes * 60
            self.pomodoros_until_long_break = pomo_count

            self._create_progress_dots()
            self._update_progress_dots()
            self.reset_timer()

            logger.info("Settings updated")
        except ValueError:
            self._show_validation_error("Invalid number")
            self._reset_entry_values()

    def _show_validation_error(self, message: str) -> None:
        """Show validation error."""
        original = self.message_label.cget("text")
        self.message_label.config(text=message, fg=Theme.WARNING_PRIMARY)
        self.master.after(2000, lambda: self.message_label.config(text=original, fg=Theme.TEXT_MUTED))

    def _reset_entry_values(self) -> None:
        """Reset entry values."""
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
        """Update countdown."""
        if self.timer_running:
            if self.time_left > 0:
                self.time_left -= 1

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
        """Handle timer completion."""
        play_sound()

        if self.is_working:
            self.pomodoro_count += 1
            self.total_session_pomodoros += 1
            record_pomodoro(self.work_time // 60)
            logger.info("Pomodoro completed: %d", self.pomodoro_count)

            if self.pomodoro_count % self.pomodoros_until_long_break == 0:
                self.time_left = self.long_break_time
                self._apply_long_break_state()
            else:
                self.time_left = self.break_time
                self._apply_break_state()

            self.update_stats_display()

            if self.auto_start_breaks:
                self.is_working = False
                self.update_timer()
            else:
                self.timer_running = False
                self.is_working = False
                self.pause_button.set_text("Pause")
        else:
            self.time_left = self.work_time
            self._apply_work_state()

            if self.auto_start_work:
                self.is_working = True
                self.update_timer()
            else:
                self.timer_running = False
                self.is_working = True
                self.pause_button.set_text("Pause")
                self._apply_idle_state()

    def skip_phase(self) -> None:
        """Skip to next phase."""
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
        self.pause_button.set_text("Pause")
        logger.info("Phase skipped")

    def start_timer(self) -> None:
        """Start or resume timer."""
        if not self.timer_running:
            if not self.paused:
                play_sound()
            else:
                self.paused = False

            self.timer_running = True
            self.pause_button.set_text("Pause")

            if self.is_working:
                self._apply_work_state()
            else:
                if self.time_left == self.long_break_time:
                    self._apply_long_break_state()
                else:
                    self._apply_break_state()

            logger.info("Timer started")
            self.update_timer()

    def pause_timer(self) -> None:
        """Pause or resume timer."""
        if self.timer_running:
            self.timer_running = False
            self.paused = True
            self.pause_button.set_text("Resume")
            logger.info("Timer paused")
        elif self.paused:
            self.start_timer()

    def reset_timer(self) -> None:
        """Reset timer."""
        self.timer_running = False
        self.paused = False
        self.is_working = True
        self.time_left = self.work_time
        self._apply_idle_state()
        self.time_label.config(text=self.format_time(self.time_left))
        self._reset_entry_values()
        self.pause_button.set_text("Pause")
        logger.info("Timer reset")

    def reset_session(self) -> None:
        """Reset session counter."""
        self.pomodoro_count = 0
        self.total_session_pomodoros = 0
        self.update_stats_display()
        self.reset_timer()
        logger.info("Session reset")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(master=root)
    root.mainloop()
