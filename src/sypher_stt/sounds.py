"""Sound feedback for recording start/stop.

Uses Windows Beep API for lightweight audio cues — no WAV files needed.
"""

import logging
import threading
import sys

log = logging.getLogger(__name__)


def _beep(frequency: int, duration_ms: int) -> None:
    """Play a beep tone on Windows. No-op on other platforms."""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.Beep(frequency, duration_ms)
    except Exception as e:
        log.debug("Beep failed: %s", e)


def play_start_sound() -> None:
    """Short ascending tone — recording started."""
    threading.Thread(
        target=_beep, args=(800, 100), daemon=True,
    ).start()


def play_stop_sound() -> None:
    """Short descending tone — recording stopped."""
    threading.Thread(
        target=_beep, args=(400, 100), daemon=True,
    ).start()


def play_error_sound() -> None:
    """Low tone — error occurred."""
    threading.Thread(
        target=_beep, args=(200, 200), daemon=True,
    ).start()
