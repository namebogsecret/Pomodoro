"""Helpers for creating simple beep sounds."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import wave


def generate_beep(frequency: int, duration: float, volume: float, filename: str | Path) -> None:
    """Generate a sine wave beep and store it as a WAV file."""

    filename = Path(filename)
    if filename.exists():
        filename.unlink()

    sample_rate = 44_100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    tone = np.sin(frequency * t * 2 * np.pi) * volume

    tone = np.int16(tone * 32_767)

    with wave.open(filename, "w") as wav_file:
        n_channels = 1
        sampwidth = 2
        n_frames = n_samples
        comptype = "NONE"
        compname = "not compressed"
        wav_file.setparams((n_channels, sampwidth, sample_rate, n_frames, comptype, compname))
        wav_file.writeframes(tone.tobytes())

if __name__ == "__main__":
    from ..config import BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME
    from .get_beep_filename import get_beep_filename
    beep_filename = get_beep_filename()
    generate_beep(BEEP_FREQUENCY, BEEP_DURATION, BEEP_VOLUME, beep_filename)


__all__ = ["generate_beep"]
