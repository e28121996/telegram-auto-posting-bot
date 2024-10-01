"""Modul manajemen pesan untuk bot auto-posting Telegram.

Modul ini menyediakan fungsionalitas untuk mengelola dan memilih pesan
yang akan dikirim oleh bot auto-posting Telegram. Ini mencakup pemilihan
pesan acak, penyesuaian pesan berdasarkan aturan grup, dan pengelolaan
cache untuk meningkatkan efisiensi.
"""

from __future__ import annotations

import re
import secrets
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import List
from typing import Type

if TYPE_CHECKING:
    from telethon import TelegramClient

    from src.database import Database  # Pastikan file ini ada

from src.cache import cache
from src.config import get_config
from src.logger import logger


class ConfigurationError(Exception):
    """Exception khusus untuk kesalahan konfigurasi."""

    DATA_DIRECTORY = "Data directory"
    MESSAGE_FILES = "Message files"


class MessageManagerError(Exception):
    """Exception khusus untuk kesalahan MessageManager."""

    ALREADY_INITIALIZED = "MessageManager sudah diinisialisasi"
    NOT_INITIALIZED = "MessageManager belum diinisialisasi"


class MessageManager:
    """Mengelola template pesan untuk bot auto-posting Telegram."""

    _instance: MessageManager | None = None

    def __init__(self: MessageManager, client: TelegramClient, db: Database) -> None:
        """Inisialisasi MessageManager dengan daftar path file pesan."""
        if MessageManager._instance is not None:
            raise MessageManagerError(MessageManagerError.ALREADY_INITIALIZED)

        self.client = client
        self.db = db
        data_dir = get_config("directories.data")
        message_files = get_config("files.messages", [])

        if not data_dir:
            raise ConfigurationError(
                ConfigurationError.DATA_DIRECTORY + " tidak dikonfigurasi atau kosong"
            )

        if not isinstance(data_dir, str):
            raise ConfigurationError(
                ConfigurationError.DATA_DIRECTORY + " harus berupa string"
            )

        data_path = Path(data_dir)
        if not data_path.exists():
            error_message = (
                ConfigurationError.DATA_DIRECTORY + " tidak ditemukan: " + str(data_dir)
            )
            raise ConfigurationError(error_message)

        self.message_files: List[Path] = []
        if isinstance(message_files, list):
            for file in message_files:
                if file is not None and isinstance(file, str):
                    file_path = data_path / file
                    if file_path.exists():
                        self.message_files.append(file_path)
                    else:
                        logger.warning("File pesan tidak ditemukan: %s", file_path)

        if not self.message_files:
            raise ConfigurationError(
                ConfigurationError.MESSAGE_FILES + " tidak valid atau kosong"
            )

        self.last_used_file: Path | None = None

    @classmethod
    async def create(
        cls: Type[MessageManager], client: TelegramClient, db: Database
    ) -> MessageManager:
        """Inisialisasi instance MessageManager."""
        if cls._instance is None:
            cls._instance = cls(client, db)
        return cls._instance

    @classmethod
    async def get_instance(cls: Type[MessageManager]) -> MessageManager:
        """Mendapatkan instance MessageManager."""
        if cls._instance is None:
            raise MessageManagerError(MessageManagerError.NOT_INITIALIZED)
        return cls._instance

    def load_message(self: MessageManager, file_path: Path) -> str:
        """Memuat pesan dari file, menggunakan cache jika tersedia."""
        cached_message = cache.get(str(file_path))
        if cached_message and isinstance(cached_message, str):
            return cached_message

        with file_path.open(encoding="utf-8") as file:
            message = file.read().strip()

        cache.set_value(str(file_path), message)
        return message

    def get_random_message(self: MessageManager) -> str:
        """Mendapatkan pesan acak dari file pesan yang tersedia."""
        available_files = [f for f in self.message_files if f != self.last_used_file]
        if not available_files:
            available_files = self.message_files

        random_file = secrets.choice(available_files)
        self.last_used_file = random_file
        return self.load_message(random_file)

    def get_appropriate_message(
        self: MessageManager, group_rules: dict[str, Any]
    ) -> str:
        """Mendapatkan pesan yang sesuai berdasarkan aturan grup."""
        message = self.get_random_message()

        if group_rules.get("send_messages", False):
            return ""

        if group_rules.get("send_media", False):
            message = re.sub(r"http\S+", "", message)

        if group_rules.get("embed_links", False):
            message = re.sub(r"http\S+", "", message)

        if group_rules.get("send_stickers", False) or group_rules.get(
            "send_gifs", False
        ):
            message = re.sub(
                r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
                "",
                message,
            )

        max_length = get_int_config("message_sending.default_max_length", 4096)
        if len(message) > max_length:
            message = message[: max_length - 3] + "..."

        return message


async def get_message_manager() -> MessageManager:
    """Mendapatkan instance MessageManager secara asinkron."""
    return await MessageManager.get_instance()


async def initialize_message_manager(client: TelegramClient, db: Database) -> None:
    """Inisialisasi instance global MessageManager."""
    await MessageManager.create(client, db)


def get_int_config(key: str, default: int) -> int:
    """Mengambil nilai konfigurasi integer berdasarkan kunci yang diberikan.

    Fungsi ini mengambil nilai konfigurasi dari fungsi get_config dan
    mengonversinya menjadi integer. Jika nilai tidak dapat dikonversi,
    nilai default akan dikembalikan.

    Args:
        key (str): Kunci konfigurasi yang ingin diambil.
        default (int): Nilai default yang akan dikembalikan jika konfigurasi
                       tidak ditemukan atau tidak dapat dikonversi ke integer.

    Returns:
        int: Nilai konfigurasi yang dikonversi ke integer atau nilai default.
    """
    value = get_config(key, default)
    return int(value) if isinstance(value, (int, float, str)) else default
