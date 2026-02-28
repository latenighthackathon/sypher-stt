"""System tray application for Sypher STT.

Provides a system tray icon with status indication and a right-click menu.
Uses pystray + Pillow to draw colored circle icons representing state.
"""

import logging
import threading
from enum import Enum
from typing import Callable, Optional

from PIL import Image, ImageDraw
import pystray

log = logging.getLogger(__name__)


class AppState(Enum):
    """Visual states for the tray icon."""
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"


STATE_COLORS: dict[AppState, str] = {
    AppState.IDLE: "#4a9eff",
    AppState.RECORDING: "#ff4444",
    AppState.TRANSCRIBING: "#ffaa00",
}

STATE_TOOLTIPS: dict[AppState, str] = {
    AppState.IDLE: "Sypher STT — Ready (Hold {hotkey} to speak)",
    AppState.RECORDING: "Sypher STT — Recording...",
    AppState.TRANSCRIBING: "Sypher STT — Transcribing...",
}


def _create_icon_image(color: str, size: int = 64) -> Image.Image:
    """Create a simple circle icon with the given color."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 4
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=color,
    )
    return img


class TrayApp:
    """System tray icon with status and menu."""

    def __init__(
        self,
        on_quit: Callable[[], None],
        on_settings: Callable[[], None],
        hotkey_name: str = "F9",
        version: str = "",
    ) -> None:
        self._on_quit = on_quit
        self._on_settings = on_settings
        self._hotkey_name = hotkey_name
        self._version = version
        self._state = AppState.IDLE
        self._icon: Optional[pystray.Icon] = None

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(
                f"Sypher STT v{self._version}",
                None,
                enabled=False,
            ),
            pystray.MenuItem(
                f"Hotkey: {self._hotkey_name.upper()}",
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", lambda: self._on_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: self._quit()),
        )

    def _quit(self) -> None:
        if self._icon is not None:
            self._icon.stop()
        self._on_quit()

    def set_state(self, state: AppState) -> None:
        self._state = state
        if self._icon is not None:
            self._icon.icon = _create_icon_image(STATE_COLORS[state])
            tooltip = STATE_TOOLTIPS[state].format(hotkey=self._hotkey_name.upper())
            self._icon.title = tooltip

    def run(self) -> None:
        """Start the tray icon. Blocks the calling thread."""
        tooltip = STATE_TOOLTIPS[AppState.IDLE].format(
            hotkey=self._hotkey_name.upper()
        )
        self._icon = pystray.Icon(
            name="sypher_stt",
            icon=_create_icon_image(STATE_COLORS[AppState.IDLE]),
            title=tooltip,
            menu=self._build_menu(),
        )
        log.info("System tray icon started.")
        self._icon.run()

    def run_detached(self) -> threading.Thread:
        t = threading.Thread(target=self.run, daemon=True, name="tray-icon")
        t.start()
        return t

    def stop(self) -> None:
        if self._icon is not None:
            self._icon.stop()

    def notify(self, title: str, message: str) -> None:
        """Show a system notification balloon."""
        if self._icon is not None:
            try:
                self._icon.notify(message, title=title)
            except Exception as e:
                log.debug("Notification failed: %s", e)

    def update_hotkey_display(self, hotkey_name: str) -> None:
        self._hotkey_name = hotkey_name
        if self._icon is not None:
            self._icon.menu = self._build_menu()
            self.set_state(self._state)
