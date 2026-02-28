"""Sypher STT — Enterprise voice-to-text dictation for Windows.

Hold a hotkey to speak, release to transcribe and paste into any window.
Fully offline using local Whisper models.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sypher-stt")
except PackageNotFoundError:
    __version__ = "0.0.0"

__app_name__ = "Sypher STT"
