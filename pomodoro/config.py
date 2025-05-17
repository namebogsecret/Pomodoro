"""Default configuration values for the Pomodoro timer."""

from __future__ import annotations

# Duration of a work session in minutes
WORK_TIME_MIN: int = 25
# Duration of a break session in minutes
BREAK_TIME_MIN: int = 5
# Frequency of the notification beep in Hertz
BEEP_FREQUENCY: int = 440
# Length of the notification beep in seconds
BEEP_DURATION: float = 0.3
# Volume of the notification beep (0..1)
BEEP_VOLUME: float = 0.5

__all__ = [
    "WORK_TIME_MIN",
    "BREAK_TIME_MIN",
    "BEEP_FREQUENCY",
    "BEEP_DURATION",
    "BEEP_VOLUME",
]
