"""Modul autentikasi untuk bot auto-posting Telegram.

Modul ini menyediakan fungsi untuk membuat dan mengautentikasi klien Telegram
yang digunakan oleh bot auto-posting.
"""

from telethon import TelegramClient

from src.config import get_config_value
from src.exceptions import ConfigurationError


async def create_client() -> TelegramClient:
    """Membuat dan mengembalikan instance TelegramClient."""
    config = get_config_value()
    if not config:
        error_msg = "Konfigurasi tidak tersedia"
        raise ConfigurationError(error_msg)

    api_id = config.get("API_ID")
    api_hash = config.get("API_HASH")

    if not api_id or not api_hash:
        error_msg = "API_ID atau API_HASH tidak tersedia dalam konfigurasi"
        raise ConfigurationError(error_msg)

    return TelegramClient("anon", api_id=int(api_id), api_hash=api_hash)
