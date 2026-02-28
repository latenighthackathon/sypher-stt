"""Global hotkey manager for push-to-talk recording.

Uses pynput for system-wide keyboard listening without requiring
administrator privileges on Windows.
"""

import logging
import threading
from typing import Callable, Optional

from pynput import keyboard

log = logging.getLogger(__name__)

# Map of friendly names to pynput Key objects
KEY_MAP: dict[str, keyboard.Key] = {
    "f1": keyboard.Key.f1,
    "f2": keyboard.Key.f2,
    "f3": keyboard.Key.f3,
    "f4": keyboard.Key.f4,
    "f5": keyboard.Key.f5,
    "f6": keyboard.Key.f6,
    "f7": keyboard.Key.f7,
    "f8": keyboard.Key.f8,
    "f9": keyboard.Key.f9,
    "f10": keyboard.Key.f10,
    "f11": keyboard.Key.f11,
    "f12": keyboard.Key.f12,
    "scroll_lock": keyboard.Key.scroll_lock,
    "pause": keyboard.Key.pause,
    "insert": keyboard.Key.insert,
}


class HotkeyManager:
    """Global push-to-talk hotkey listener.

    Hold the configured key to trigger on_start, release to trigger on_stop.
    Thread-safe with lock-protected state.
    """

    def __init__(
        self,
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        hotkey: str = "f9",
    ) -> None:
        self._on_start = on_start
        self._on_stop = on_stop
        self._hotkey_name = hotkey
        self._hotkey = KEY_MAP.get(hotkey)
        if self._hotkey is None:
            raise ValueError(f"Unknown hotkey '{hotkey}'. Choose from: {list(KEY_MAP.keys())}")
        self._listener: Optional[keyboard.Listener] = None
        self._is_held = False
        self._held_lock = threading.Lock()
        self._active = False

    def _on_press(self, key: keyboard.Key) -> None:
        if not self._active:
            return
        with self._held_lock:
            if key == self._hotkey and not self._is_held:
                self._is_held = True
            else:
                return
        try:
            self._on_start()
        except Exception as e:
            log.error("on_start callback error: %s", e, exc_info=True)

    def _on_release(self, key: keyboard.Key) -> None:
        if not self._active:
            return
        with self._held_lock:
            if key == self._hotkey and self._is_held:
                self._is_held = False
            else:
                return
        try:
            self._on_stop()
        except Exception as e:
            log.error("on_stop callback error: %s", e, exc_info=True)

    def start(self) -> None:
        """Start listening for the hotkey. Non-blocking."""
        self._active = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()
        log.info("Hotkey listener started (key: %s).", self._hotkey_name.upper())

    def stop(self) -> None:
        """Stop listening for the hotkey."""
        self._active = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        log.info("Hotkey listener stopped.")

    @property
    def hotkey_name(self) -> str:
        return self._hotkey_name

    @hotkey_name.setter
    def hotkey_name(self, value: str) -> None:
        new_key = KEY_MAP.get(value)
        if new_key is None:
            raise ValueError(f"Unknown hotkey '{value}'. Choose from: {list(KEY_MAP.keys())}")
        self._hotkey_name = value
        self._hotkey = new_key
        with self._held_lock:
            self._is_held = False
        log.info("Hotkey changed to %s.", value.upper())
