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

import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Menyiapkan dan mengkonfigurasi logger dengan handler file dan console."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=2,
    )
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Menambahkan handler ke logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Buat logger default
logger = setup_logger("bot_logger", "logs/bot.log")
