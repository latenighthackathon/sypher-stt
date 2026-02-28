# Changelog

All notable changes to Sypher STT are documented here.

---

## [1.0.0] - 2026-02-27

### Added
- Push-to-talk voice dictation for Windows — hold a hotkey, speak, release to paste transcribed text
- Fully offline transcription using local Whisper models via faster-whisper
- System tray icon with color-coded status (blue = ready, red = recording, yellow = transcribing)
- Settings window (CustomTkinter) for hotkey, model, microphone, and sound feedback configuration
- Config saved to `%APPDATA%/Sypher STT/config.json` with whitelist validation
- Structured logging with rotating file handler (5 MB x 3 backups)
- Single-instance enforcement via Windows named mutex
- Sound feedback using Windows Beep API (toggleable)
- Model downloader script (`scripts/download_model.py`) for HuggingFace models
- Smart `run.bat` launcher with Python version discovery
- Default model: `base.en` (~142 MB, ~0.2s latency for 5s audio on CPU)
