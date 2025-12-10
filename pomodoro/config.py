"""Default configuration values for the Pomodoro timer."""

from __future__ import annotations

# Duration of a work session in minutes
WORK_TIME_MIN: int = 25
# Duration of a break session in minutes
BREAK_TIME_MIN: int = 5
# Duration of a long break session in minutes
LONG_BREAK_TIME_MIN: int = 15
# Number of pomodoros before a long break
POMODOROS_UNTIL_LONG_BREAK: int = 4
# Frequency of the notification beep in Hertz
BEEP_FREQUENCY: int = 440
# Length of the notification beep in seconds
BEEP_DURATION: float = 0.3
# Volume of the notification beep (0..1)
BEEP_VOLUME: float = 0.5
# Warning threshold (percentage of time remaining to show red)
WARNING_THRESHOLD: float = 0.1
# Auto-start settings
AUTO_START_BREAKS: bool = True
AUTO_START_WORK: bool = False

# Application metadata
APP_NAME: str = "Pomodoro Timer"
APP_VERSION: str = "0.2.0"

__all__ = [
    "WORK_TIME_MIN",
    "BREAK_TIME_MIN",
    "LONG_BREAK_TIME_MIN",
    "POMODOROS_UNTIL_LONG_BREAK",
    "BEEP_FREQUENCY",
    "BEEP_DURATION",
    "BEEP_VOLUME",
    "WARNING_THRESHOLD",
    "AUTO_START_BREAKS",
    "AUTO_START_WORK",
    "APP_NAME",
    "APP_VERSION",
]
