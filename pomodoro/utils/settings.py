"""Settings persistence for the Pomodoro timer."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default config file location
CONFIG_DIR = Path.home() / ".pomodoro"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default settings
DEFAULT_SETTINGS = {
    "work_time_minutes": 25,
    "break_time_minutes": 5,
    "long_break_minutes": 15,
    "pomodoros_until_long_break": 4,
    "beep_enabled": True,
    "beep_frequency": 440,
    "beep_duration": 0.3,
    "beep_volume": 0.5,
    "auto_start_breaks": True,
    "auto_start_work": False,
    "warning_threshold": 0.1,  # 10% of time remaining triggers red warning
}


def ensure_config_dir() -> None:
    """Create the config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict[str, Any]:
    """Load settings from the config file.

    Returns default settings if the file doesn't exist or is invalid.
    """
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Merge with defaults to handle new settings
                settings = DEFAULT_SETTINGS.copy()
                settings.update(saved)
                logger.info("Settings loaded from %s", CONFIG_FILE)
                return settings
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not load settings: %s. Using defaults.", e)

    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict[str, Any]) -> bool:
    """Save settings to the config file.

    Returns True if successful, False otherwise.
    """
    try:
        ensure_config_dir()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        logger.info("Settings saved to %s", CONFIG_FILE)
        return True
    except OSError as e:
        logger.error("Could not save settings: %s", e)
        return False


def get_setting(key: str, default: Any = None) -> Any:
    """Get a single setting value."""
    settings = load_settings()
    return settings.get(key, default)


def set_setting(key: str, value: Any) -> bool:
    """Set a single setting value."""
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)


__all__ = [
    "DEFAULT_SETTINGS",
    "load_settings",
    "save_settings",
    "get_setting",
    "set_setting",
]
