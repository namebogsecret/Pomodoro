"""Tests for statistics tracking."""

from datetime import date, datetime
from pathlib import Path

import pytest

from pomodoro.utils.statistics import (
    load_statistics,
    record_pomodoro,
    get_today_stats,
    get_week_stats,
    get_total_stats,
)


@pytest.fixture
def temp_stats(tmp_path, monkeypatch):
    """Create a temporary stats directory."""
    stats_dir = tmp_path / ".pomodoro"
    stats_file = stats_dir / "statistics.json"

    import pomodoro.utils.statistics as stats_module
    monkeypatch.setattr(stats_module, "STATS_DIR", stats_dir)
    monkeypatch.setattr(stats_module, "STATS_FILE", stats_file)

    return stats_file


def test_load_empty_statistics(temp_stats):
    """Test loading statistics when no file exists."""
    stats = load_statistics()
    assert stats["total_pomodoros"] == 0
    assert stats["total_work_minutes"] == 0
    assert stats["daily_stats"] == {}


def test_record_pomodoro(temp_stats):
    """Test recording a completed pomodoro."""
    stats = record_pomodoro(25)

    assert stats["total_pomodoros"] == 1
    assert stats["total_work_minutes"] == 25

    today = date.today().isoformat()
    assert today in stats["daily_stats"]
    assert stats["daily_stats"][today]["pomodoros"] == 1


def test_record_multiple_pomodoros(temp_stats):
    """Test recording multiple pomodoros."""
    record_pomodoro(25)
    record_pomodoro(25)
    stats = record_pomodoro(30)

    assert stats["total_pomodoros"] == 3
    assert stats["total_work_minutes"] == 80


def test_get_today_stats(temp_stats):
    """Test getting today's statistics."""
    record_pomodoro(25)
    record_pomodoro(30)

    today = get_today_stats()
    assert today["pomodoros"] == 2
    assert today["minutes"] == 55


def test_get_week_stats(temp_stats):
    """Test getting weekly statistics."""
    record_pomodoro(25)

    week = get_week_stats()
    assert week["pomodoros"] == 1
    assert week["minutes"] == 25


def test_get_total_stats(temp_stats):
    """Test getting total statistics."""
    record_pomodoro(25)
    record_pomodoro(25)

    total = get_total_stats()
    assert total["total_pomodoros"] == 2
    assert total["total_work_minutes"] == 50


def test_streak_tracking(temp_stats):
    """Test that streaks are tracked."""
    stats = record_pomodoro(25)
    assert stats["streak_days"] == 1

    # Recording another pomodoro same day doesn't increase streak
    stats = record_pomodoro(25)
    assert stats["streak_days"] == 1
