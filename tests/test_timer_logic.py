"""Tests for timer logic."""

import tkinter as tk
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def timer():
    """Create a PomodoroTimer instance for testing."""
    root = tk.Tk()
    root.withdraw()

    # Patch settings and statistics to avoid file I/O
    with patch("pomodoro.ui.main.load_settings") as mock_settings, \
         patch("pomodoro.ui.main.get_today_stats") as mock_today, \
         patch("pomodoro.ui.main.get_total_stats") as mock_total, \
         patch("pomodoro.ui.main.record_pomodoro") as mock_record:

        mock_settings.return_value = {
            "work_time_minutes": 25,
            "break_time_minutes": 5,
            "long_break_minutes": 15,
            "pomodoros_until_long_break": 4,
            "auto_start_breaks": False,
            "auto_start_work": False,
        }
        mock_today.return_value = {"pomodoros": 0, "minutes": 0}
        mock_total.return_value = {"total_pomodoros": 0, "total_work_minutes": 0, "streak_days": 0}
        mock_record.return_value = {"total_pomodoros": 1}

        from pomodoro.ui.main import PomodoroTimer
        timer = PomodoroTimer(master=root)

    yield timer
    root.destroy()


def test_initial_state(timer):
    """Test initial timer state."""
    assert timer.is_working is True
    assert timer.timer_running is False
    assert timer.paused is False
    assert timer.time_left == 25 * 60
    assert timer.pomodoro_count == 0


def test_format_time(timer):
    """Test time formatting."""
    assert timer.format_time(0) == "00:00"
    assert timer.format_time(65) == "01:05"
    assert timer.format_time(3600) == "60:00"
    assert timer.format_time(90) == "01:30"


def test_start_timer(timer):
    """Test starting the timer."""
    with patch("pomodoro.ui.main.play_sound"):
        timer.start_timer()

    assert timer.timer_running is True
    assert timer.paused is False


def test_pause_timer(timer):
    """Test pausing the timer."""
    with patch("pomodoro.ui.main.play_sound"):
        timer.start_timer()
        timer.pause_timer()

    assert timer.timer_running is False
    assert timer.paused is True


def test_resume_timer(timer):
    """Test resuming the timer."""
    with patch("pomodoro.ui.main.play_sound"):
        timer.start_timer()
        timer.pause_timer()
        timer.pause_timer()  # Should resume

    assert timer.timer_running is True
    assert timer.paused is False


def test_reset_timer(timer):
    """Test resetting the timer."""
    with patch("pomodoro.ui.main.play_sound"):
        timer.start_timer()
        timer.time_left = 100  # Simulate some time passing
        timer.reset_timer()

    assert timer.timer_running is False
    assert timer.paused is False
    assert timer.is_working is True
    assert timer.time_left == timer.work_time


def test_skip_phase_during_work(timer):
    """Test skipping work phase."""
    with patch("pomodoro.ui.main.play_sound"):
        timer.start_timer()
        timer.skip_phase()

    assert timer.is_working is False
    assert timer.time_left == timer.break_time


def test_skip_phase_during_break(timer):
    """Test skipping break phase."""
    with patch("pomodoro.ui.main.play_sound"):
        timer.is_working = False
        timer.timer_running = True
        timer.skip_phase()

    assert timer.is_working is True
    assert timer.time_left == timer.work_time


def test_pomodoro_count_increments(timer):
    """Test that pomodoro count increments on work completion."""
    with patch("pomodoro.ui.main.play_sound"), \
         patch("pomodoro.ui.main.record_pomodoro") as mock_record, \
         patch("pomodoro.ui.main.messagebox"):

        mock_record.return_value = {"total_pomodoros": 1}

        timer.timer_running = True
        timer.time_left = 0
        timer.auto_start_breaks = False
        timer._handle_timer_complete()

    assert timer.pomodoro_count == 1
    assert timer.is_working is False


def test_long_break_after_four_pomodoros(timer):
    """Test that long break is triggered after 4 pomodoros."""
    with patch("pomodoro.ui.main.play_sound"), \
         patch("pomodoro.ui.main.record_pomodoro") as mock_record, \
         patch("pomodoro.ui.main.messagebox"):

        mock_record.return_value = {"total_pomodoros": 4}

        timer.pomodoro_count = 3  # After this one, it will be 4
        timer.timer_running = True
        timer.time_left = 0
        timer.auto_start_breaks = False
        timer._handle_timer_complete()

    assert timer.pomodoro_count == 4
    assert timer.time_left == timer.long_break_time


def test_progress_dots_update(timer):
    """Test that progress dots are updated."""
    timer.pomodoro_count = 2
    timer._update_progress_dots()

    # First 2 dots should be filled
    assert timer.progress_dots[0].cget("text") == "●"
    assert timer.progress_dots[1].cget("text") == "●"
    assert timer.progress_dots[2].cget("text") == "○"
    assert timer.progress_dots[3].cget("text") == "○"


def test_color_changes_for_warning(timer):
    """Test that color changes to red in warning zone."""
    timer.is_working = True
    timer.time_left = int(0.05 * timer.work_time)  # 5% remaining

    # This simulates what happens in update_timer
    if timer.time_left <= 0.1 * timer.work_time:
        timer.set_color("red")

    assert timer.label.cget("fg") == "red"
