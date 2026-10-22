"""Logging configuration module for NeuroVision AI backend."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import BASE_DIR, settings

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "app.log"

FORMATTER = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_logging() -> logging.Logger:
    """Configure root logger with console and rotating file output."""
    root_logger = logging.getLogger()
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(FORMATTER)
        root_logger.addHandler(console_handler)

        # File Handler (10MB per file, up to 5 backups)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(FORMATTER)
        root_logger.addHandler(file_handler)

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Retrieve logger instance with given module name."""
    return logging.getLogger(name)
