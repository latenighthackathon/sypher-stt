"""Single-instance enforcement using a Windows named mutex.

Prevents multiple copies of the app from running simultaneously.
"""

import ctypes
import ctypes.wintypes
import logging
import sys

from sypher_stt.constants import MUTEX_NAME

log = logging.getLogger(__name__)

ERROR_ALREADY_EXISTS = 183


def _setup_kernel32() -> ctypes.WinDLL:
    """Configure kernel32 function signatures for 64-bit safety."""
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.wintypes.HANDLE
    kernel32.CreateMutexW.argtypes = [
        ctypes.wintypes.LPVOID,  # lpMutexAttributes
        ctypes.wintypes.BOOL,    # bInitialOwner
        ctypes.wintypes.LPCWSTR, # lpName
    ]
    kernel32.CloseHandle.restype = ctypes.wintypes.BOOL
    kernel32.CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
    kernel32.ReleaseMutex.restype = ctypes.wintypes.BOOL
    kernel32.ReleaseMutex.argtypes = [ctypes.wintypes.HANDLE]
    kernel32.GetLastError.restype = ctypes.wintypes.DWORD
    kernel32.GetLastError.argtypes = []
    return kernel32


class SingleInstance:
    """Acquires a Windows named mutex. Raises if another instance exists."""

    def __init__(self) -> None:
        self._handle = None

    def acquire(self) -> bool:
        """Try to acquire the single-instance mutex.

        Returns:
            True if this is the only instance, False if another is running.
        """
        if sys.platform != "win32":
            return True  # No enforcement on non-Windows

        kernel32 = _setup_kernel32()
        self._handle = kernel32.CreateMutexW(None, True, MUTEX_NAME)
        last_error = kernel32.GetLastError()

        if last_error == ERROR_ALREADY_EXISTS:
            log.warning("Another instance of Sypher STT is already running.")
            kernel32.CloseHandle(self._handle)
            self._handle = None
            return False

        log.debug("Single-instance mutex acquired.")
        return True

    def release(self) -> None:
        """Release the mutex on shutdown."""
        if self._handle is not None:
            kernel32 = _setup_kernel32()
            kernel32.ReleaseMutex(self._handle)
            kernel32.CloseHandle(self._handle)
            self._handle = None
            log.debug("Single-instance mutex released.")
