"""Determine the filename for the generated beep sound."""

from __future__ import annotations

from pathlib import Path
import hashlib
from ..config import BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME


def get_beep_filename() -> str:
    """Return an absolute path to the beep sound file."""

    base_dir = Path(__file__).resolve().parent
    assets_dir = base_dir.parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    params = f"{BEEP_FREQUENCY}_{BEEP_DURATION}_{BEEP_VOLUME}"
    params_hash = hashlib.sha256(params.encode()).hexdigest()
    return str(assets_dir / f"beep_{params_hash}.wav")


__all__ = ["get_beep_filename"]
