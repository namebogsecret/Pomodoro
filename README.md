# Pomodoro Timer

A lightweight, cross-platform Pomodoro timer written in Python with a modern Tkinter GUI.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Features

- **Classic Pomodoro Technique**: Work sessions (25 min) followed by short breaks (5 min)
- **Long Breaks**: Automatic long break (15 min) after every 4 pomodoros
- **Visual Progress**: Progress dots showing your cycle completion
- **Statistics Tracking**: Daily, weekly, and all-time pomodoro statistics
- **Streak Counter**: Track your productivity streak
- **Customizable Settings**: Adjust work time, break time, long break, and cycle length
- **Settings Persistence**: Your preferences are saved between sessions
- **Audio Notifications**: Beep sound when timer completes
- **Color Indicators**:
  - Blue: Working
  - Red: Last 10% of work time (warning)
  - Green: Short break
  - Purple: Long break
- **Pause/Resume**: Pause your timer anytime and resume later
- **Skip Function**: Skip to the next phase if needed
- **Auto-start Options**: Optionally auto-start breaks or work sessions
- **Debug Logging**: Comprehensive logging for troubleshooting

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/namebogsecret/Pomodoro.git
   cd Pomodoro
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Using pip

```bash
pip install .
```

## Usage

### Launch the GUI

```bash
python -m pomodoro
```

Or if installed via pip:

```bash
pomodoro_timer
```

### Command Line Options

```bash
pomodoro_timer --help          # Show help
pomodoro_timer --version       # Show version
pomodoro_timer --debug         # Enable debug logging
pomodoro_timer --no-log-file   # Disable file logging
```

### Using the Run Script

The `run.sh` script handles updates, dependency installation, and launch:

```bash
./run.sh
./run.sh --quiet      # Suppress INFO messages
./run.sh --no-color   # Disable colored output
```

## How to Use

1. **Start**: Click "Start" to begin a work session
2. **Pause/Resume**: Click "Pause" to pause, "Resume" to continue
3. **Stop**: Click "Stop" to reset the timer
4. **Skip**: Click "Skip" to move to the next phase (work → break or break → work)
5. **Settings**: Click "Show Settings" to customize timer durations

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Work time | 25 min | Duration of work sessions |
| Break time | 5 min | Duration of short breaks |
| Long break | 15 min | Duration of long breaks |
| Pomos for long break | 4 | Number of pomodoros before a long break |
| Auto-start breaks | On | Automatically start break after work |
| Auto-start work | Off | Automatically start work after break |

Click "Save Settings" to persist your preferences.

## Data Storage

Settings and statistics are stored in `~/.pomodoro/`:

```
~/.pomodoro/
├── config.json      # User settings
├── statistics.json  # Pomodoro statistics
└── logs/
    └── pomodoro.log # Application logs
```

## Requirements

- Python 3.8+
- Tkinter (usually included with Python)
- NumPy >= 2.0.0
- Pygame >= 2.6.0

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=pomodoro
```

## Project Structure

```
pomodoro/
├── __init__.py
├── main.py              # Entry point
├── config.py            # Default configuration
├── ui/
│   ├── __init__.py
│   └── main.py          # Tkinter GUI
└── utils/
    ├── __init__.py
    ├── sound.py         # Audio playback
    ├── generate_beep.py # WAV file generation
    ├── get_beep_filename.py
    ├── settings.py      # Settings persistence
    ├── statistics.py    # Statistics tracking
    └── logging_config.py # Logging setup
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on the [Pomodoro Technique](https://francescocirillo.com/products/the-pomodoro-technique) by Francesco Cirillo
- Built with [Tkinter](https://docs.python.org/3/library/tkinter.html) and [Pygame](https://www.pygame.org/)
