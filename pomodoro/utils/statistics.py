"""Statistics tracking for completed pomodoros."""

from __future__ import annotations

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Statistics file location (same directory as config)
STATS_DIR = Path.home() / ".pomodoro"
STATS_FILE = STATS_DIR / "statistics.json"


def ensure_stats_dir() -> None:
    """Create the statistics directory if it doesn't exist."""
    STATS_DIR.mkdir(parents=True, exist_ok=True)


def load_statistics() -> dict[str, Any]:
    """Load statistics from file."""
    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not load statistics: %s", e)

    return {
        "total_pomodoros": 0,
        "total_work_minutes": 0,
        "daily_stats": {},
        "weekly_stats": {},
        "streak_days": 0,
        "last_pomodoro_date": None,
    }


def save_statistics(stats: dict[str, Any]) -> bool:
    """Save statistics to file."""
    try:
        ensure_stats_dir()
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        return True
    except OSError as e:
        logger.error("Could not save statistics: %s", e)
        return False


def record_pomodoro(work_minutes: int) -> dict[str, Any]:
    """Record a completed pomodoro session.

    Args:
        work_minutes: Duration of the completed work session in minutes.

    Returns:
        Updated statistics dictionary.
    """
    stats = load_statistics()

    today = date.today().isoformat()
    now = datetime.now()
    week_key = f"{now.year}-W{now.isocalendar()[1]:02d}"

    # Update totals
    stats["total_pomodoros"] += 1
    stats["total_work_minutes"] += work_minutes

    # Update daily stats
    if today not in stats["daily_stats"]:
        stats["daily_stats"][today] = {"pomodoros": 0, "minutes": 0}
    stats["daily_stats"][today]["pomodoros"] += 1
    stats["daily_stats"][today]["minutes"] += work_minutes

    # Update weekly stats
    if week_key not in stats["weekly_stats"]:
        stats["weekly_stats"][week_key] = {"pomodoros": 0, "minutes": 0}
    stats["weekly_stats"][week_key]["pomodoros"] += 1
    stats["weekly_stats"][week_key]["minutes"] += work_minutes

    # Update streak
    last_date = stats.get("last_pomodoro_date")
    if last_date:
        last = date.fromisoformat(last_date)
        diff = (date.today() - last).days
        if diff == 1:
            stats["streak_days"] += 1
        elif diff > 1:
            stats["streak_days"] = 1
    else:
        stats["streak_days"] = 1

    stats["last_pomodoro_date"] = today

    save_statistics(stats)
    logger.info("Recorded pomodoro: %d minutes. Total: %d", work_minutes, stats["total_pomodoros"])

    return stats


def get_today_stats() -> dict[str, int]:
    """Get statistics for today."""
    stats = load_statistics()
    today = date.today().isoformat()
    return stats["daily_stats"].get(today, {"pomodoros": 0, "minutes": 0})


def get_week_stats() -> dict[str, int]:
    """Get statistics for current week."""
    stats = load_statistics()
    now = datetime.now()
    week_key = f"{now.year}-W{now.isocalendar()[1]:02d}"
    return stats["weekly_stats"].get(week_key, {"pomodoros": 0, "minutes": 0})


def get_total_stats() -> dict[str, int]:
    """Get total statistics."""
    stats = load_statistics()
    return {
        "total_pomodoros": stats["total_pomodoros"],
        "total_work_minutes": stats["total_work_minutes"],
        "streak_days": stats["streak_days"],
    }


__all__ = [
    "record_pomodoro",
    "get_today_stats",
    "get_week_stats",
    "get_total_stats",
    "load_statistics",
]
