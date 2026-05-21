"""
Utility helpers for log file reading and manipulation.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def read_recent_logs(
    log_file: str = "trading_bot.log",
    lines: int = 100,
) -> dict:
    """
    Read the last N lines from a log file.

    Args:
        log_file: filename within the LOG_DIR (e.g. 'trading_bot.log')
        lines: number of tail lines to return

    Returns:
        dict with keys: lines (list[str]), log_file (str), total_lines (int)
    """
    log_path = Path(settings.LOG_DIR) / log_file

    if not log_path.exists():
        return {"lines": [], "log_file": log_file, "total_lines": 0}

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        tail = [line.rstrip("\n") for line in all_lines[-lines:]]
        return {
            "lines": tail,
            "log_file": log_file,
            "total_lines": len(all_lines),
        }
    except OSError as exc:
        logger.error("Failed to read log file %s: %s", log_path, exc)
        return {"lines": [f"Error reading log: {exc}"], "log_file": log_file, "total_lines": 0}


def list_log_files() -> list[str]:
    """Return names of all log files in the log directory."""
    log_dir = Path(settings.LOG_DIR)
    if not log_dir.exists():
        return []
    return sorted(f.name for f in log_dir.glob("*.log"))