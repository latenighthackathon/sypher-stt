"""Clipboard and paste module for outputting transcribed text.

Copies text to the system clipboard and simulates Ctrl+V to paste
into whatever window is currently focused.

Note: Non-text clipboard content (images, files) cannot be preserved
by pyperclip. If the user had non-text content, it will be lost.
"""

import logging
import sys
import time
import threading

import pyperclip
import pyautogui

log = logging.getLogger(__name__)

pyautogui.PAUSE = 0.02

# Clipboard format constants (Win32)
_CF_TEXT = 1
_CF_UNICODETEXT = 13
_TEXT_FORMATS = {_CF_TEXT, _CF_UNICODETEXT}


def _clipboard_has_text_only() -> bool:
    """Check if the clipboard contains only text (no images/files).

    Returns True if clipboard is empty or text-only.
    Returns True on non-Windows (can't detect, assume text).
    """
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        user32 = ctypes.windll.user32
        if not user32.OpenClipboard(None):
            return True
        try:
            fmt = 0
            has_non_text = False
            while True:
                fmt = user32.EnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                if fmt not in _TEXT_FORMATS:
                    has_non_text = True
                    break
            return not has_non_text
        finally:
            user32.CloseClipboard()
    except Exception:
        return True  # Assume text on error


def paste_text(text: str, restore_clipboard: bool = True) -> None:
    """Copy text to clipboard and paste into the active window.

    Args:
        text: The text to paste.
        restore_clipboard: If True, restores the previous clipboard
            contents after a short delay.
    """
    if not text:
        return

    old_clipboard = None
    can_restore = False

    if restore_clipboard:
        if _clipboard_has_text_only():
            try:
                old_clipboard = pyperclip.paste()
                can_restore = True
            except Exception:
                old_clipboard = None
        else:
            log.debug("Clipboard contains non-text content; cannot preserve.")

    pyperclip.copy(text)
    time.sleep(0.05)

    try:
        pyautogui.hotkey("ctrl", "v")
    except Exception as e:
        log.error("Failed to simulate Ctrl+V: %s", e)
        return

    log.debug("Pasted %d chars into active window.", len(text))

    if can_restore:
        def _restore() -> None:
            time.sleep(0.1)
            try:
                pyperclip.copy(old_clipboard if old_clipboard else "")
            except Exception:
                pass
        threading.Thread(target=_restore, daemon=True).start()
