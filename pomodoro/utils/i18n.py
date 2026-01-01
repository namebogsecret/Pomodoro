"""Internationalization (i18n) module for the Pomodoro Timer."""

from __future__ import annotations

import json
import locale
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default language (English)
DEFAULT_LANGUAGE = "en"

# Supported languages
SUPPORTED_LANGUAGES = ["en", "ru"]

# Current translations
_translations: dict[str, Any] = {}
_current_language: str = DEFAULT_LANGUAGE


def get_locales_dir() -> Path:
    """Get the locales directory path."""
    return Path(__file__).parent.parent / "locales"


def detect_system_language() -> str:
    """Detect system language and return supported language code."""
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            lang_code = system_locale.split("_")[0].lower()
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
    except Exception as e:
        logger.debug(f"Could not detect system language: {e}")
    return DEFAULT_LANGUAGE


def load_translations(language: str | None = None) -> bool:
    """
    Load translations for the specified language.

    Args:
        language: Language code (e.g., 'en', 'ru').
                  If None, auto-detects from system.

    Returns:
        True if translations loaded successfully, False otherwise.
    """
    global _translations, _current_language

    if language is None:
        language = detect_system_language()

    if language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Language '{language}' not supported, falling back to {DEFAULT_LANGUAGE}")
        language = DEFAULT_LANGUAGE

    locales_dir = get_locales_dir()
    translation_file = locales_dir / f"{language}.json"

    try:
        with open(translation_file, "r", encoding="utf-8") as f:
            _translations = json.load(f)
        _current_language = language
        logger.info(f"Loaded translations for language: {language}")
        return True
    except FileNotFoundError:
        logger.error(f"Translation file not found: {translation_file}")
        # Try to load default language as fallback
        if language != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in translation file {translation_file}: {e}")
        return False


def get_current_language() -> str:
    """Get current language code."""
    return _current_language


def set_language(language: str) -> bool:
    """
    Set the current language.

    Args:
        language: Language code (e.g., 'en', 'ru').

    Returns:
        True if language was set successfully, False otherwise.
    """
    return load_translations(language)


def t(key: str, **kwargs: Any) -> str:
    """
    Translate a key to the current language.

    Args:
        key: Translation key (supports nested keys with dots, e.g., 'ui.buttons.start')
        **kwargs: Format arguments for string interpolation

    Returns:
        Translated string, or the key itself if not found.
    """
    if not _translations:
        load_translations()

    # Navigate nested keys
    keys = key.split(".")
    value: Any = _translations

    try:
        for k in keys:
            value = value[k]
    except (KeyError, TypeError):
        logger.debug(f"Translation not found for key: {key}")
        return key

    if not isinstance(value, str):
        logger.debug(f"Translation value is not a string for key: {key}")
        return key

    # Apply format arguments
    if kwargs:
        try:
            return value.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing format argument for key '{key}': {e}")
            return value

    return value


def get_message_list(key: str) -> list[str]:
    """
    Get a list of messages (for random selection).

    Args:
        key: Translation key pointing to a list

    Returns:
        List of translated strings, or empty list if not found.
    """
    if not _translations:
        load_translations()

    keys = key.split(".")
    value: Any = _translations

    try:
        for k in keys:
            value = value[k]
    except (KeyError, TypeError):
        logger.debug(f"Message list not found for key: {key}")
        return []

    if isinstance(value, list):
        return value
    return []


# Convenience alias
_ = t


__all__ = [
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "load_translations",
    "get_current_language",
    "set_language",
    "detect_system_language",
    "t",
    "_",
    "get_message_list",
]
