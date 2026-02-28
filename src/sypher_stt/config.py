"""Configuration management for Sypher STT.

Config is stored in %APPDATA%/Sypher STT/config.json.
All values are validated against whitelists on load.
"""

import json
import logging
from typing import Optional

from sypher_stt.constants import (
    AVAILABLE_MODELS,
    CONFIG_PATH,
    DEFAULT_HOTKEY,
    DEFAULT_MODEL,
)
from sypher_stt.hotkeys import KEY_MAP

log = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "hotkey": DEFAULT_HOTKEY,
    "model": DEFAULT_MODEL,
    "audio_device": None,
    "sound_feedback": True,
}


def load_config() -> dict:
    """Load configuration from disk, or return defaults.

    Validates all values against whitelists to prevent injection
    of arbitrary model names or unknown config keys.
    """
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if not isinstance(saved, dict):
                log.warning("Config file is not a dict, using defaults.")
                return dict(DEFAULT_CONFIG)
            config = dict(DEFAULT_CONFIG)
            if saved.get("hotkey") in KEY_MAP:
                config["hotkey"] = saved["hotkey"]
            if saved.get("model") in AVAILABLE_MODELS:
                config["model"] = saved["model"]
            if saved.get("audio_device") is None or isinstance(saved.get("audio_device"), int):
                config["audio_device"] = saved["audio_device"]
            if isinstance(saved.get("sound_feedback"), bool):
                config["sound_feedback"] = saved["sound_feedback"]
            log.debug("Loaded config from %s", CONFIG_PATH)
            return config
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Failed to load config (%s), using defaults.", e)
    return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    """Save configuration to disk."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        log.debug("Saved config to %s", CONFIG_PATH)
    except IOError as e:
        log.error("Failed to save config: %s", e)
