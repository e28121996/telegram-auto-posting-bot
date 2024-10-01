"""Modul logging untuk bot auto-posting Telegram.

Modul ini menyediakan konfigurasi dan setup untuk sistem logging aplikasi,
termasuk logging ke file dan console. Ini mencakup fungsi untuk menyiapkan
logger dengan berbagai handler dan formatter, serta instance logger global
untuk digunakan di seluruh aplikasi.

Fungsi:
    setup_logger: Menyiapkan dan mengkonfigurasi logger dengan handler file dan console.

Variabel:
    logger: Instance logger global yang dikonfigurasi untuk seluruh aplikasi.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from src.config import yaml_config


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Menyiapkan dan mengkonfigurasi logger dengan handler file dan console."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler untuk semua log
    file_handler = TimedRotatingFileHandler(
        filename=str(
            Path(yaml_config["directories"]["logs"]) / yaml_config["files"]["log"]
        ),
        when="midnight",
        interval=1,
        backupCount=7,
    )
    file_handler.setLevel(logging.INFO)

    # File handler untuk error log
    error_file_handler = RotatingFileHandler(
        filename=str(
            Path(yaml_config["directories"]["logs"]) / yaml_config["files"]["error_log"]
        ),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    error_file_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    error_file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Menambahkan handler ke logger
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    logger.addHandler(console_handler)

    return logger


# Mengubah level logging default menjadi INFO
logger: logging.Logger = setup_logger(
    "bot_logger",
    getattr(logging, yaml_config["logging"]["level"]),
)
"""Logger global yang digunakan di seluruh aplikasi.

Instance ini telah dikonfigurasi dengan level log yang ditentukan dalam konfigurasi YAML
dan mencakup handler untuk logging ke file (termasuk rotasi harian dan log error
terpisah) serta output ke console.
"""
