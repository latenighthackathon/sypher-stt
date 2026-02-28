"""Structured logging with rotating file handler.

Logs go to %APPDATA%/Sypher STT/logs/ with automatic rotation.
Console output is minimal; file logs are verbose for diagnostics.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from sypher_stt.constants import LOG_DIR


def setup_logging() -> logging.Logger:
    """Configure and return the application logger.

    Returns:
        The root 'sypher_stt' logger, configured with file + console handlers.
    """
    logger = logging.getLogger("sypher_stt")
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler — verbose, rotating (5MB x 3 backups)
    file_handler = RotatingFileHandler(
        LOG_DIR / "sypher_stt.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler — info and above only
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger
