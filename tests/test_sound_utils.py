from pathlib import Path

from pomodoro.utils.generate_beep import generate_beep
from pomodoro.utils.get_beep_filename import get_beep_filename


def test_generate_beep(tmp_path):
    filename = tmp_path / "beep.wav"
    generate_beep(440, 0.1, 0.1, filename)
    assert filename.exists() and filename.stat().st_size > 0


def test_get_beep_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = Path(get_beep_filename())
    assert path.name.startswith("beep_") and path.suffix == ".wav"
