# sound.py

"""Utility helpers for playing audio feedback."""

from __future__ import annotations

from pathlib import Path
import pygame

from .generate_beep import generate_beep
from .get_beep_filename import get_beep_filename
from ..config import BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME


def _ensure_mixer_initialized() -> None:
    """Initialize the pygame mixer if it is not already."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def play_sound() -> None:
    """Play a short beep sound.

    The beep file is generated on demand and cached on disk.  This
    function works on Windows, macOS and Linux.
    """

    _ensure_mixer_initialized()

    beep_filename = Path(get_beep_filename())
    if not beep_filename.exists():
        generate_beep(BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME, str(beep_filename))

    pygame.mixer.music.load(str(beep_filename))
    pygame.mixer.music.play()


__all__ = ["play_sound"]
