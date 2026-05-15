# Timer

A minimal, frameless desktop timer for Windows built with PyQt5.

![Python](https://img.shields.io/badge/Python-3.13-blue) ![PyQt5](https://img.shields.io/badge/PyQt5-5.x-green) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

<img width="420" height="555" alt="PixPin_2026-05-15_18-58-01" src="https://github.com/user-attachments/assets/a1ac6599-b955-415d-9e3a-a6b202b7c4f3" />

## Features

- **Count-up & Countdown** — toggle between stopwatch and timer mode
- **Scroll to set time** — hover over hours, minutes, or seconds and scroll to adjust
- **Presets** — save up to 3 custom durations; persisted between sessions
- **Alarm** — plays audio on countdown finish, falls back to system beep
- **Always on top** — pin the window above all other apps
- **Keyboard shortcuts**

| Key | Action |
|-----|--------|
| `Space` | Start / Pause / Resume |
| `Esc` | Reset |
| `1` `2` `3` | Load preset 1 / 2 / 3 |

- Custom frameless window with macOS-style close/minimize buttons
- Windows 11 rounded corners via DWM API
- Drag the title bar to reposition

## Requirements

- Python 3.13+
- PyQt5

```
pip install PyQt5
```

## Run

```
python timer.py
```

Or double-click `timer.bat` (uses `pythonw.exe` to run without a console window).

## Project Structure

```
Timer/
├── timer.py          # Entry point
├── timer.bat         # Windows launcher (no console)
├── Flow.mp3          # Alarm sound
├── assets/
│   └── timer.ico
├── core/
│   ├── timer_engine.py   # Stateful timer logic (count-up / countdown)
│   ├── audio.py          # Audio playback wrapper
│   └── settings.py       # Preset persistence (saved to %APPDATA%\Timer)
└── ui/
    ├── main_window.py    # Main window, title bar, layout
    ├── display.py        # Time display widget
    ├── controls.py       # Start / Pause / Resume / Reset buttons
    ├── mode_toggle.py    # Count-up ↔ Countdown toggle
    ├── presets.py        # Preset bar
    └── styles.py         # Color tokens
```

## Notes

- Presets are stored at `%APPDATA%\Timer\presets.json`
- `timer.bat` is hardcoded to a local Python path — update it if your Python is elsewhere
