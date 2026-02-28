"""Settings window for Sypher STT.

Provides a CustomTkinter GUI for configuring the app:
- Hotkey selection
- Whisper model selection
- Audio input device selection
- Sound feedback toggle
"""

import logging
from typing import Callable, Optional

import customtkinter as ctk
import sounddevice as sd

from sypher_stt.config import DEFAULT_CONFIG, load_config, save_config
from sypher_stt.constants import DEFAULT_MODEL
from sypher_stt.hotkeys import KEY_MAP
from sypher_stt.transcriber import get_local_models

log = logging.getLogger(__name__)


class SettingsWindow:
    """Settings dialog for Sypher STT."""

    def __init__(self, on_save: Callable[[dict], None]) -> None:
        self._on_save = on_save
        self._window: Optional[ctk.CTkToplevel] = None
        self._config = load_config()
        self._device_indices: list[Optional[int]] = []

    def show(self) -> None:
        """Open the settings window. Creates a new one if not already open."""
        if self._window is not None and self._window.winfo_exists():
            self._window.focus_force()
            return

        self._config = load_config()
        self._window = ctk.CTkToplevel()
        self._window.title("Sypher STT — Settings")
        self._window.geometry("420x440")
        self._window.resizable(False, False)
        self._window.attributes("-topmost", True)

        # Title
        ctk.CTkLabel(
            self._window,
            text="Sypher STT Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 15))

        # Hotkey
        hotkey_frame = ctk.CTkFrame(self._window)
        hotkey_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(hotkey_frame, text="Push-to-talk hotkey:").pack(side="left", padx=10, pady=10)
        hotkey_options = [k.upper() for k in KEY_MAP.keys()]
        self._hotkey_var = ctk.StringVar(value=self._config["hotkey"].upper())
        ctk.CTkOptionMenu(
            hotkey_frame, variable=self._hotkey_var, values=hotkey_options, width=120,
        ).pack(side="right", padx=10, pady=10)

        # Model
        model_frame = ctk.CTkFrame(self._window)
        model_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(model_frame, text="Whisper model:").pack(side="left", padx=10, pady=10)
        local_models = get_local_models()
        model_options = local_models if local_models else [DEFAULT_MODEL]
        current_model = self._config["model"] if self._config["model"] in model_options else model_options[0]
        self._model_var = ctk.StringVar(value=current_model)
        ctk.CTkOptionMenu(
            model_frame, variable=self._model_var, values=model_options, width=160,
        ).pack(side="right", padx=10, pady=10)

        # Audio device
        device_frame = ctk.CTkFrame(self._window)
        device_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(device_frame, text="Microphone:").pack(side="left", padx=10, pady=10)

        input_devices = self._get_input_devices()
        device_names = ["System Default"] + [name for _, name in input_devices]
        self._device_indices = [None] + [idx for idx, _ in input_devices]

        current_device = self._config.get("audio_device")
        if current_device is None:
            current_name = "System Default"
        else:
            matches = [name for idx, name in input_devices if idx == current_device]
            current_name = matches[0] if matches else "System Default"

        self._device_var = ctk.StringVar(value=current_name)
        ctk.CTkOptionMenu(
            device_frame, variable=self._device_var, values=device_names, width=200,
        ).pack(side="right", padx=10, pady=10)

        # Sound feedback toggle
        sound_frame = ctk.CTkFrame(self._window)
        sound_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(sound_frame, text="Sound feedback:").pack(side="left", padx=10, pady=10)
        self._sound_var = ctk.BooleanVar(value=self._config.get("sound_feedback", True))
        ctk.CTkSwitch(
            sound_frame, variable=self._sound_var, text="", width=40,
        ).pack(side="right", padx=10, pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(self._window, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(
            btn_frame, text="Save", command=self._save, width=100,
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            btn_frame, text="Cancel", command=self._close, width=100,
            fg_color="gray40", hover_color="gray30",
        ).pack(side="right", padx=5)

    def _save(self) -> None:
        device_name = self._device_var.get()
        device_names_list = ["System Default"] + [
            name for _, name in self._get_input_devices()
        ]
        idx_in_list = device_names_list.index(device_name) if device_name in device_names_list else 0
        device_index = self._device_indices[idx_in_list] if idx_in_list < len(self._device_indices) else None

        self._config = {
            "hotkey": self._hotkey_var.get().lower(),
            "model": self._model_var.get(),
            "audio_device": device_index,
            "sound_feedback": self._sound_var.get(),
        }
        save_config(self._config)
        self._on_save(self._config)
        self._close()
        log.info("Settings saved.")

    def _close(self) -> None:
        if self._window is not None:
            self._window.destroy()
            self._window = None

    @staticmethod
    def _get_input_devices() -> list[tuple[int, str]]:
        devices = sd.query_devices()
        return [
            (i, d["name"])
            for i, d in enumerate(devices)
            if d["max_input_channels"] > 0
        ]
