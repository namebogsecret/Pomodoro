# sound.py

"""Utility helpers for playing audio feedback."""

from __future__ import annotations

from pathlib import Path
import sys

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False

from .generate_beep import generate_beep
from .get_beep_filename import get_beep_filename
from ..config import BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME


def _ensure_mixer_initialized() -> None:
    """Initialize the pygame mixer if it is not already."""
    if not PYGAME_AVAILABLE:
        return
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def play_sound() -> None:
    """Play a short beep sound with error handling.

    The beep file is generated on demand and cached on disk.  This
    function works on Windows, macOS and Linux.

    Errors are logged to stderr but do not crash the application.
    If pygame is not available, sound playback is silently skipped.
    """
    if not PYGAME_AVAILABLE:
        return

    try:
        _ensure_mixer_initialized()

        beep_filename = Path(get_beep_filename())
        if not beep_filename.exists():
            generate_beep(BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME, str(beep_filename))

        pygame.mixer.music.load(str(beep_filename))
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Warning: Could not play sound: {e}", file=sys.stderr)
    except OSError as e:
        print(f"Warning: Audio file error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Unexpected audio error: {e}", file=sys.stderr)


__all__ = ["play_sound"]
