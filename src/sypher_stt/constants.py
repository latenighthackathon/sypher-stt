"""Application-wide constants and path resolution."""

import os
from pathlib import Path


# Application identity
APP_NAME = "Sypher STT"

# Paths — resolved at import time
_root = Path(__file__).resolve().parent.parent.parent  # project root
MODELS_DIR = _root / "models"

# User data lives in %APPDATA%/Sypher STT/ (enterprise-standard location)
_appdata = os.environ.get("APPDATA")
if not _appdata:
    raise RuntimeError(
        "APPDATA environment variable is not set. "
        "Cannot determine user data directory."
    )
APPDATA_DIR = Path(_appdata) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = APPDATA_DIR / "config.json"
LOG_DIR = APPDATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Audio
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 1024
MAX_RECORDING_SECONDS = 120

# Whisper
AVAILABLE_MODELS = [
    "tiny.en", "tiny",
    "base.en", "base",
    "small.en", "small",
    "medium.en", "medium",
    "large-v2", "large-v3", "large-v3-turbo",
]
DEFAULT_MODEL = "base.en"

# Hotkey
DEFAULT_HOTKEY = "f9"

# Mutex name for single-instance enforcement (Windows named mutex)
# Local\ scope = per-session; prevents cross-session DoS via mutex squatting
MUTEX_NAME = "Local\\SypherSTTSingleInstance"
