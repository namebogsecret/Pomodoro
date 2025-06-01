# Project Overview

This repository contains a minimalist Pomodoro timer implemented in Python. The main application lives in the `pomodoro/` package and provides a Tkinter based GUI along with small utilities for generating and playing notification sounds.

```
/README.md        – Basic install/run instructions
/setup.py         – Packaging metadata for `pip install`
/requirements.txt – Runtime dependencies (numpy, pygame)
/pomodoro/        – Application package
    config.py     – Default timer and sound settings
    main.py       – Entry point for launching the GUI
    ui/           – Tkinter user interface code
    utils/        – Helper modules for sound generation and playback
/start.sh        – Simple wrapper running `python -m pomodoro`
/run.sh          – Update+start helper with logging
/tests/           – Pytest based unit tests
```

## Current Issues

* **Dependency installation** – Running the test suite requires `pytest`, `numpy` and `pygame`. In restricted environments without internet access these may be missing, so tests can fail to start. Consider bundling wheels or using system packages.
* **Limited features** – The timer supports basic work/break periods but still lacks presets or tray integration. Pause/resume is now implemented.
* **Audio handling** – `pygame` is used only for short beeps. A lighter alternative (or pure Tkinter sound) might simplify installation.
* **Packaging** – `setup.py` exists but the project is not published to PyPI. Continuous integration for building and distributing packages would help.

## Future Development Ideas

* Add long break cycles.
* Support saving user settings (durations, sounds).
* Provide a command line interface alongside the GUI.
* Improve unit test coverage and add CI to run them on push.

## Quick Start for Contributors

1. Create a Python virtual environment and install dependencies from `requirements.txt`.
2. Launch the app with `python -m pomodoro`, the `pomodoro_timer` console script,
   or simply run `./run.sh` which also updates dependencies and logs to `logs/`.
3. Run `pytest` to execute the tests (requires the dependencies mentioned above).

### Helpers

Internal helper scripts live in the `/helpers` directory. They are not part of the
package but can streamline maintenance tasks. Data files for the agent can be
stored under `/helpers/data`.

This file serves as a reminder of project structure and open tasks for the next development session.
