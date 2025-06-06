# Pomodoro Timer

This project provides a lightweight cross-platform Pomodoro timer written in
Python. The graphical user interface is implemented with Tkinter and audio
feedback is handled by Pygame. It runs on Windows, macOS and Linux.
The timer now supports pausing and resuming sessions.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/namebogsecret/Pomodoro.git
   cd Pomodoro
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Launch the GUI from the command line:
```bash
python -m pomodoro
```
or, if installed via ``setup.py``, simply run:
```bash
pomodoro_timer
```

Alternatively you can let `./run.sh` handle updates, dependency
installation and launch:
```bash
./run.sh
```
Logs will be saved under the `logs/` directory.

