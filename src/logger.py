"""Logging module for the Telegram auto-posting bot."""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from src.config import yaml_config


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up and configure a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    log_dir = yaml_config["log_directory"]
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, yaml_config["log_file"])
    error_log_file = os.path.join(log_dir, yaml_config["error_log_file"])

    # File handler untuk semua log
    file_handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    # File handler untuk error saja
    error_handler = RotatingFileHandler(
        error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(error_handler)

    return logger


logger = setup_logger("bot_logger", getattr(logging, yaml_config["log_level"]))
