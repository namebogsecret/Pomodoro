"""Logging configuration for the Pomodoro timer."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Log directory
LOG_DIR = Path.home() / ".pomodoro" / "logs"


def setup_logging(level: int = logging.INFO, log_to_file: bool = True) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (default: INFO)
        log_to_file: Whether to also log to a file (default: True)
    """
    # Create log directory if needed
    if log_to_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Create formatters
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Get root logger for the pomodoro package
    logger = logging.getLogger("pomodoro")
    logger.setLevel(level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_file = LOG_DIR / "pomodoro.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        logger.info("Logging to file: %s", log_file)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"pomodoro.{name}")


__all__ = ["setup_logging", "get_logger"]
