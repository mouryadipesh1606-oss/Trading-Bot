"""
Logging configuration for the trading bot.
Sets up both file and console handlers with structured formatting.
"""

import logging
import os
from datetime import datetime


def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Configure and return the root logger for the trading bot.

    Args:
        log_dir: Directory where log files will be stored.

    Returns:
        Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)

    log_filename = os.path.join(log_dir, f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # --- File handler: DEBUG and above, with full detail ---
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # --- Console handler: INFO and above, clean output ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(fmt="%(levelname)-8s %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialised. Log file: %s", log_filename)
    return logger
