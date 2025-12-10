"""Tests for settings persistence."""

import json
from pathlib import Path

import pytest

from pomodoro.utils.settings import (
    load_settings,
    save_settings,
    get_setting,
    set_setting,
    DEFAULT_SETTINGS,
)


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".pomodoro"
    config_file = config_dir / "config.json"

    # Monkeypatch the config paths
    import pomodoro.utils.settings as settings_module
    monkeypatch.setattr(settings_module, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(settings_module, "CONFIG_FILE", config_file)

    return config_file


def test_load_settings_default(temp_config):
    """Test that default settings are returned when no config file exists."""
    settings = load_settings()
    assert settings == DEFAULT_SETTINGS


def test_save_and_load_settings(temp_config):
    """Test saving and loading settings."""
    custom_settings = DEFAULT_SETTINGS.copy()
    custom_settings["work_time_minutes"] = 30
    custom_settings["break_time_minutes"] = 10

    assert save_settings(custom_settings)
    loaded = load_settings()

    assert loaded["work_time_minutes"] == 30
    assert loaded["break_time_minutes"] == 10


def test_get_setting(temp_config):
    """Test getting individual settings."""
    assert get_setting("work_time_minutes") == DEFAULT_SETTINGS["work_time_minutes"]
    assert get_setting("nonexistent", "default") == "default"


def test_set_setting(temp_config):
    """Test setting individual settings."""
    assert set_setting("work_time_minutes", 45)
    assert get_setting("work_time_minutes") == 45


def test_settings_merge_with_defaults(temp_config):
    """Test that saved settings are merged with defaults."""
    # Save partial settings
    temp_config.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_config, "w") as f:
        json.dump({"work_time_minutes": 50}, f)

    loaded = load_settings()

    # Custom setting should be loaded
    assert loaded["work_time_minutes"] == 50
    # Default settings should still be present
    assert loaded["break_time_minutes"] == DEFAULT_SETTINGS["break_time_minutes"]


def test_corrupted_config_file(temp_config):
    """Test handling of corrupted config file."""
    temp_config.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_config, "w") as f:
        f.write("invalid json {{{")

    # Should return defaults without crashing
    settings = load_settings()
    assert settings == DEFAULT_SETTINGS
