import logging
import logging.handlers
import os
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure structured rotating file + console logging."""

    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # ── Console handler ──────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    root_logger.addHandler(console_handler)

    # ── Rotating file handler (all logs) ─────────────────────────────────────
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "trading_bot.log",
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    # ── Separate error log ────────────────────────────────────────────────────
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # ── Orders-specific log ───────────────────────────────────────────────────
    orders_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "orders.log",
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    orders_handler.setFormatter(formatter)
    orders_handler.setLevel(logging.DEBUG)

    orders_logger = logging.getLogger("orders")
    orders_logger.addHandler(orders_handler)
    orders_logger.propagate = True

    # Suppress noisy third-party logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging initialised — level=%s  dir=%s", settings.LOG_LEVEL, log_dir)
    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)