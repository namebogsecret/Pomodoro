"""Command line entry point for the Pomodoro GUI application."""

from __future__ import annotations

import argparse
import logging
import tkinter as tk

from pomodoro.ui.main import PomodoroTimer
from pomodoro.utils.logging_config import setup_logging
from pomodoro.config import APP_NAME, APP_VERSION


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - A productivity timer using the Pomodoro Technique"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"{APP_NAME} {APP_VERSION}"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="Disable logging to file"
    )
    return parser.parse_args()


def main() -> None:
    """Start the Tkinter GUI application."""
    args = parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=log_level, log_to_file=not args.no_log_file)

    logger = logging.getLogger(__name__)
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

    try:
        root = tk.Tk()
        app = PomodoroTimer(master=root)
        root.mainloop()
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        raise
    finally:
        logger.info("Application closed")


if __name__ == "__main__":
    main()


__all__ = ["main"]
