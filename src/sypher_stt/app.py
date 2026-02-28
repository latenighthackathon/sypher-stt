"""Sypher STT — Main application orchestrator.

Wires all components together:
  HotkeyManager -> AudioRecorder -> Transcriber -> clipboard paste
  TrayApp provides status, SettingsWindow provides configuration.
"""

import logging
import sys
import threading
import time

import customtkinter as ctk

from sypher_stt import __version__
from sypher_stt.audio import AudioRecorder
from sypher_stt.clipboard import paste_text
from sypher_stt.config import load_config
from sypher_stt.hotkeys import HotkeyManager
from sypher_stt.instance import SingleInstance
from sypher_stt.logger import setup_logging
from sypher_stt.settings import SettingsWindow
from sypher_stt.sounds import play_error_sound, play_start_sound, play_stop_sound
from sypher_stt.transcriber import Transcriber
from sypher_stt.tray import AppState, TrayApp

log = logging.getLogger(__name__)


class SypherSTT:
    """Main application class."""

    def __init__(self) -> None:
        self._config = load_config()

        # Core
        self._recorder = AudioRecorder(device=self._config.get("audio_device"))
        self._transcriber = Transcriber(model_size=self._config.get("model", "base.en"))

        # Hotkey
        self._hotkey_manager = HotkeyManager(
            on_start=self._on_hotkey_press,
            on_stop=self._on_hotkey_release,
            hotkey=self._config.get("hotkey", "f9"),
        )

        # UI
        self._tray = TrayApp(
            on_quit=self._quit,
            on_settings=self._open_settings,
            hotkey_name=self._config.get("hotkey", "f9"),
            version=__version__,
        )
        self._settings_window = SettingsWindow(on_save=self._apply_settings)

        # State
        self._processing = False
        self._state_lock = threading.Lock()
        self._root: ctk.CTk = None

    def _on_hotkey_press(self) -> None:
        with self._state_lock:
            if self._processing:
                return

        log.info("Recording started.")
        self._tray.set_state(AppState.RECORDING)
        if self._config.get("sound_feedback", True):
            play_start_sound()

        try:
            self._recorder.start_recording()
        except Exception as e:
            log.error("Failed to start recording: %s", e)
            self._tray.set_state(AppState.IDLE)
            self._tray.notify("Recording Error", str(e))
            if self._config.get("sound_feedback", True):
                play_error_sound()

    def _on_hotkey_release(self) -> None:
        with self._state_lock:
            if self._processing:
                return
            self._processing = True

        if self._config.get("sound_feedback", True):
            play_stop_sound()

        log.info("Recording stopped, transcribing...")
        self._tray.set_state(AppState.TRANSCRIBING)
        audio = self._recorder.stop_recording()

        def _transcribe() -> None:
            try:
                text = self._transcriber.transcribe(audio)
                if text:
                    log.info("Transcribed %d chars.", len(text))
                    paste_text(text)
                else:
                    log.info("No speech detected.")
            except Exception as e:
                log.error("Transcription error: %s", e, exc_info=True)
                self._tray.notify("Transcription Error", str(e))
                if self._config.get("sound_feedback", True):
                    play_error_sound()
            finally:
                with self._state_lock:
                    self._processing = False
                self._tray.set_state(AppState.IDLE)

        threading.Thread(target=_transcribe, daemon=True).start()

    def _open_settings(self) -> None:
        if self._root is not None:
            self._root.after(0, self._settings_window.show)

    def _apply_settings(self, config: dict) -> None:
        self._config = config
        log.info("Settings updated.")

        self._hotkey_manager.hotkey_name = config.get("hotkey", "f9")
        self._tray.update_hotkey_display(config.get("hotkey", "f9"))
        self._transcriber.model_size = config.get("model", "base.en")

        # Stop old recorder before replacing to avoid orphaned audio streams
        if self._recorder.is_recording:
            self._recorder.stop_recording()
        self._recorder = AudioRecorder(device=config.get("audio_device"))

    def _quit(self) -> None:
        log.info("Shutting down.")
        self._hotkey_manager.stop()
        self._tray.stop()
        if self._root is not None:
            self._root.after(0, self._root.destroy)

    def run(self) -> None:
        log.info("=" * 50)
        log.info("Sypher STT v%s starting.", __version__)
        log.info("Hotkey: %s | Model: %s",
                 self._config.get("hotkey", "f9").upper(),
                 self._config.get("model", "base.en"))
        log.info("=" * 50)

        # Pre-load model
        def _preload() -> None:
            try:
                self._transcriber.ensure_model()
                log.info("Model ready.")
                self._tray.notify("Sypher STT", "Model loaded. Ready to transcribe.")
            except Exception as e:
                log.error("Failed to load model: %s", e)
                self._tray.notify("Model Error", str(e))

        threading.Thread(target=_preload, daemon=True).start()

        # Start hotkey listener
        self._hotkey_manager.start()

        # Start tray icon
        self._tray.run_detached()
        time.sleep(0.5)

        # Tkinter main loop (needed for settings window)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._root = ctk.CTk()
        self._root.withdraw()
        self._root.title("Sypher STT")
        self._root.protocol("WM_DELETE_WINDOW", lambda: None)
        self._root.mainloop()


def main() -> None:
    """Application entry point."""
    setup_logging()

    # Single-instance check
    guard = SingleInstance()
    if not guard.acquire():
        print("Sypher STT is already running. Exiting.")
        sys.exit(1)

    try:
        app = SypherSTT()
        app.run()
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
    except Exception as e:
        log.critical("Unhandled exception: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        guard.release()
