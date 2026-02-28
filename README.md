# Sypher STT

Voice-to-text dictation for Windows. Hold a hotkey, speak, and the transcribed text is pasted into whatever window is active. Runs locally, fully offline using local Whisper models — no data leaves your machine. Designed for privacy and security.

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/latenighthackathon/sypher-stt.git
cd sypher-stt
pip install -e .

# 2. Download the default Whisper model (~142 MB, one-time)
python scripts/download_model.py

# 3. Run
python -m sypher_stt
```

A blue circle appears in your system tray — the app is ready. Hold **F9**, speak, release, and the text is pasted at your cursor.

## How It Works

```
Hold F9 → Record mic → Release F9 → Transcribe (Whisper) → Paste into active window
```

- **Fully offline** — Whisper model runs locally on your CPU, nothing is sent to the cloud
- **Works in any app** — pastes via clipboard into whatever window has focus
- **System tray** — color-coded icon shows status (blue = ready, red = recording, yellow = transcribing)
- **Sound feedback** — beeps on record start/stop (can be toggled off)

## Configuration

Right-click the tray icon → **Settings** to change:

| Setting | Options | Default |
|---------|---------|---------|
| Hotkey | F1–F12, Scroll Lock, Pause, Insert | F9 |
| Model | Any model downloaded to `models/` | base.en |
| Microphone | Any connected input device | System default |
| Sound feedback | On / Off | On |

Settings are saved to `%APPDATA%/Sypher STT/config.json`.

## Models

Models are stored in the `models/` directory. Download one before first use:

```bash
python scripts/download_model.py              # base.en (default, ~142 MB)
python scripts/download_model.py small.en      # better accuracy (~466 MB)
python scripts/download_model.py medium.en     # high accuracy (~1.5 GB)
python scripts/download_model.py --list        # show all available models
```

| Model | Size | Speed (5s audio, CPU) | Best For |
|-------|------|----------------------|----------|
| tiny.en | ~75 MB | ~0.1s | Fastest, lower accuracy |
| base.en | ~142 MB | ~0.2s | Good balance (recommended) |
| small.en | ~466 MB | ~0.5s | Better accuracy |
| medium.en | ~1.5 GB | ~1.5s | High accuracy |
| large-v3 | ~2.9 GB | ~4s | Best accuracy (GPU recommended) |

## Requirements

- Windows 10/11
- Python 3.10+
- A microphone

## Installation

```bash
pip install -e .
```

To also install the model downloader dependency:

```bash
pip install -e ".[download]"
```

## Project Structure

```
sypher-stt/
├── src/sypher_stt/          # Main application package
│   ├── app.py               # Orchestrator
│   ├── audio.py             # Microphone capture
│   ├── transcriber.py       # Whisper STT engine
│   ├── clipboard.py         # Paste into active window
│   ├── hotkeys.py           # Global push-to-talk hotkey
│   ├── tray.py              # System tray icon
│   ├── settings.py          # Settings UI
│   ├── config.py            # Config management
│   ├── logger.py            # Structured logging
│   ├── sounds.py            # Audio feedback
│   ├── instance.py          # Single-instance enforcement
│   └── constants.py         # App-wide constants
├── scripts/
│   └── download_model.py    # Model downloader
├── models/                  # Local Whisper models (gitignored)
├── pyproject.toml           # Package config
└── run.bat                  # Windows launcher
```

## Logs

Logs are written to `%APPDATA%/Sypher STT/logs/sypher_stt.log` with automatic rotation (5 MB x 3 backups).

## License

MIT
