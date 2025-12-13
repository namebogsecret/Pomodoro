# Pomodoro Timer - Project Overview for Agents

**Version:** 0.2.0 (Beta)
**Status:** Production-ready beta release
**Last Updated:** 2025-12-13

---

## Project Summary

This is a **feature-complete Pomodoro Timer** application built with Python and Tkinter. The project has evolved from a basic MVP to a robust productivity tool with statistics tracking, settings persistence, and comprehensive error handling.

## Project Structure

```
/
├── README.md                 – User-facing documentation
├── ANALYSIS.md              – Detailed technical analysis and issue tracking
├── AGENTS.md                – This file - quick reference for AI agents
├── LICENSE                  – MIT License
├── setup.py                 – Package configuration (v0.2.0)
├── requirements.txt         – Pinned dependencies
├── project-tracker.yaml     – Development progress tracking
├── project-overview.yaml    – High-level project status
│
├── pomodoro/                – Main application package
│   ├── __init__.py
│   ├── main.py             – Entry point with CLI argument parsing
│   ├── config.py           – Default configuration constants
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main.py         – Tkinter GUI implementation (555 lines)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── sound.py        – Audio playback with error handling
│       ├── generate_beep.py – WAV file generation
│       ├── get_beep_filename.py – Asset path management
│       ├── settings.py     – Settings persistence (~/.pomodoro/config.json)
│       ├── statistics.py   – Pomodoro statistics tracking
│       └── logging_config.py – Logging configuration
│
├── tests/                   – Unit tests (pytest)
│   ├── test_format_time.py
│   ├── test_pause_resume.py
│   ├── test_update_times.py
│   └── test_sound_utils.py
│
├── run.sh                   – Development launcher with auto-update
├── start.sh                 – Simple launcher wrapper
│
└── helpers/                 – Internal development tools
    └── data/               – Agent workspace
```

---

## Key Features (v0.2.0)

### Core Functionality
✅ **Classic Pomodoro Technique** - 25min work / 5min break cycles
✅ **Long Breaks** - Automatic 15min break after 4 pomodoros
✅ **Pause/Resume** - Full timer control
✅ **Skip Function** - Jump to next phase
✅ **Color Indicators** - Visual state feedback (blue/red/green/purple)

### Statistics & Tracking
✅ **Session Statistics** - Track completed pomodoros
✅ **Daily/Weekly Stats** - Historical tracking
✅ **Streak Counter** - Consecutive productivity days
✅ **Progress Dots** - Visual cycle completion indicator

### Settings & Persistence
✅ **Customizable Timers** - Adjust work/break/long break durations
✅ **Auto-start Options** - Configure automatic phase transitions
✅ **Settings Persistence** - Saved to `~/.pomodoro/config.json`
✅ **Statistics Storage** - Saved to `~/.pomodoro/statistics.json`

### Technical Features
✅ **Comprehensive Logging** - Debug logs in `~/.pomodoro/logs/`
✅ **Error Handling** - Graceful degradation on audio/file errors
✅ **Input Validation** - Range checking with user feedback
✅ **CLI Arguments** - `--debug`, `--version`, `--no-log-file`

---

## Current Status

### Code Quality: 8/10 ⬆️ (was 6/10 in v0.1)

| Metric | Score | Notes |
|--------|-------|-------|
| Functionality | 9/10 | All core features implemented |
| Reliability | 8/10 | Error handling in critical paths |
| Maintainability | 7/10 | Clean code, good documentation |
| Testability | 6/10 | Basic unit tests, missing integration tests |
| Documentation | 8/10 | README, ANALYSIS, inline docs |

### Fixed Issues (v0.2.0)
- ✅ All 2 critical bugs fixed
- ✅ All 6 high-priority issues resolved
- ✅ 5/8 medium-priority issues addressed
- ⏳ 3 medium + 7 low-priority items remain

See [ANALYSIS.md](ANALYSIS.md) for detailed issue tracking.

---

## Dependencies

**Runtime:**
- Python 3.8+
- numpy >= 2.0.0, < 3.0.0
- pygame >= 2.6.0, < 3.0.0
- tkinter (included with Python)

**Development:**
- pytest (for testing)
- pytest-cov (for coverage reports)

---

## Quick Start for Development

### Installation
```bash
# Clone and setup
git clone https://github.com/namebogsecret/Pomodoro.git
cd Pomodoro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running
```bash
# Method 1: Direct module execution
python -m pomodoro

# Method 2: Development script (auto-updates dependencies)
./run.sh

# Method 3: After pip install
pip install .
pomodoro_timer --help
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=pomodoro
```

---

## Known Limitations & Future Work

### Remaining Medium-Priority Issues
1. **MD5 hashing for filenames** - Low security concern, consider SHA256
2. **Missing integration tests** - Need full cycle testing
3. **Hardcoded UI strings** - No i18n/localization support

### Future Enhancements (v0.3+)
- [ ] MVC architecture refactoring (decouple UI from logic)
- [ ] Internationalization (i18n) support
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] CHANGELOG.md
- [ ] System tray integration
- [ ] Sound customization
- [ ] Theme support (dark mode)
- [ ] Export statistics to CSV/JSON

---

## For AI Agents: Important Context

### When Working on This Project

**File Organization:**
- **DO NOT** modify `config.py` defaults without reason - users override via settings UI
- Settings are stored in `~/.pomodoro/config.json` (user's home directory)
- Statistics are stored in `~/.pomodoro/statistics.json`
- Logs go to `~/.pomodoro/logs/pomodoro.log`

**Code Style:**
- Type hints are used throughout (`from __future__ import annotations`)
- Docstrings follow Google style
- Logging is pervasive - use `logger.info/debug/warning/error`
- Error handling: catch specific exceptions, log them, gracefully degrade

**Testing:**
- All new features should have unit tests
- Tests use real Tkinter instances (consider mocking for CI)
- Run `pytest` before committing

**UI/UX Considerations:**
- All user input is validated in `update_times()`
- Timer can't be reconfigured while running/paused
- Errors show via `messagebox.showerror()`
- All times internally stored as seconds, displayed as minutes

### Common Tasks

**Adding a new setting:**
1. Add default to `config.py`
2. Add to `DEFAULT_SETTINGS` in `utils/settings.py`
3. Add UI widget in `ui/main.py:create_widgets()`
4. Update `save_current_settings()` and `__init__()` in `ui/main.py`

**Debugging:**
- Run with `--debug` flag for verbose logging
- Check `~/.pomodoro/logs/pomodoro.log`
- Use `logger.debug()` liberally

**Before Release:**
- Update version in `setup.py` and `config.py:APP_VERSION`
- Run all tests: `pytest tests/ -v`
- Update ANALYSIS.md with resolved issues
- Test pip installation: `pip install .` in clean venv

---

## Contact & Contributing

- **Repository:** https://github.com/namebogsecret/Pomodoro
- **Issues:** Report bugs and feature requests on GitHub Issues
- **License:** MIT (see LICENSE file)

### Development Philosophy
This project values:
- **Simplicity** over feature creep
- **Reliability** over bleeding-edge features
- **User experience** - settings should be intuitive
- **Code quality** - maintainability matters

---

**Last Review:** All critical and high-priority issues from ANALYSIS.md are resolved. Project is stable for end-user use.
