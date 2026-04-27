from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "runtime" / "logs"
INFO_LOG = LOG_DIR / "info.log"
ERROR_LOG = LOG_DIR / "error.log"

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 10 * 1024 * 1024
BACKUP_COUNT = 5


class _BelowErrorFilter(logging.Filter):
    """Allow records below ERROR so info and error logs stay separated."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


def _build_file_handler(path: Path, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    return handler


def setup_logger(level: int = logging.INFO) -> None:
    """Configure root logging for the Cerehub runtime."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if any(getattr(handler, "_cerehub_runtime_logger", False) for handler in root_logger.handlers):
        return

    info_handler = _build_file_handler(INFO_LOG, logging.INFO)
    info_handler.addFilter(_BelowErrorFilter())

    error_handler = _build_file_handler(ERROR_LOG, logging.ERROR)

    for handler in (info_handler, error_handler):
        handler._cerehub_runtime_logger = True
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, ensuring runtime file logging is ready."""

    setup_logger()
    return logging.getLogger(name)
