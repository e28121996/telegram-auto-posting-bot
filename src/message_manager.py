"""Modul manajemen pesan untuk bot auto-posting Telegram."""

from __future__ import annotations

import re
import secrets
from pathlib import Path
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from src.config import get_config_value
from src.logger import logger

if TYPE_CHECKING:
    from telethon import TelegramClient

    from src.database import Database


class MessageManagerError(Exception):
    """Exception class for MessageManager errors."""

    ALREADY_INITIALIZED = "MessageManager sudah diinisialisasi"
    CONFIG_NOT_LOADED = "Konfigurasi tidak dapat dimuat"
    DATA_DIR_NOT_CONFIGURED = "Direktori data tidak dikonfigurasi dengan benar"
    NO_MESSAGES_AVAILABLE = "Tidak ada pesan yang tersedia"


class MessageManager:
    """Class to manage message-related operations."""

    _instance: Optional[MessageManager] = None

    def __init__(self: MessageManager, client: TelegramClient, db: Database) -> None:
        """Initialize MessageManager instance."""
        self.client = client
        self.db = db
        self.messages: List[str] = []
        self.message_files: List[Path] = []
        self.load_messages()

    @classmethod
    async def create(
        cls: type[MessageManager], client: TelegramClient, db: Database
    ) -> MessageManager:
        """Create a new instance of MessageManager."""
        if cls._instance is None:
            cls._instance = cls(client, db)
        return cls._instance

    @classmethod
    async def get_instance(cls: type[MessageManager]) -> Optional[MessageManager]:
        """Get the singleton instance of MessageManager."""
        return cls._instance

    def get_random_message(self: MessageManager) -> str:
        """Get a random message from the available messages."""
        if not self.messages:
            raise MessageManagerError(MessageManagerError.NO_MESSAGES_AVAILABLE)
        return secrets.choice(self.messages)

    def load_messages(self: MessageManager) -> None:
        """Load messages from files."""
        config = get_config_value()
        if not config:
            raise MessageManagerError(MessageManagerError.CONFIG_NOT_LOADED)

        data_dir = Path(config.get("directories", {}).get("data", ""))
        if not data_dir.is_dir():
            raise MessageManagerError(MessageManagerError.DATA_DIR_NOT_CONFIGURED)

        message_files = config.get("files", {}).get("messages", [])
        self.message_files = [data_dir / file for file in message_files]
        logger.info(f"File pesan yang dikonfigurasi: {self.message_files}")

        for file in self.message_files:
            if file.is_file():
                with file.open("r", encoding="utf-8") as f:
                    self.messages.append(f.read().strip())

        if not self.messages:
            raise MessageManagerError(MessageManagerError.NO_MESSAGES_AVAILABLE)

    def adjust_message_for_group(self: MessageManager, group: str, message: str) -> str:
        """Adjust the message based on group rules."""
        group_rules = self._get_group_rules(group)
        adjusted_message = message

        if group_rules.get("send_messages", False):
            return ""

        if group_rules.get("send_media", False):
            adjusted_message = re.sub(r"http\S+", "", adjusted_message)

        if group_rules.get("embed_links", False):
            adjusted_message = re.sub(r"http\S+", "", adjusted_message)

        if group_rules.get("send_stickers", False) or group_rules.get(
            "send_gifs", False
        ):
            adjusted_message = re.sub(
                r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
                "",
                adjusted_message,
            )

        max_length = get_int_config("message_sending.default_max_length", 4096)
        if len(adjusted_message) > max_length:
            adjusted_message = adjusted_message[: max_length - 3] + "..."

        return adjusted_message

    def _get_group_rules(self: MessageManager, _: str) -> dict:
        """Get rules for a specific group."""
        # Implementasi logika untuk mendapatkan aturan grup
        # Contoh sederhana, seharusnya diganti dengan implementasi yang sesuai
        return {}


async def get_message_manager() -> Optional[MessageManager]:
    """Mendapatkan instance MessageManager secara asinkron."""
    return await MessageManager.get_instance()


async def initialize_message_manager(client: TelegramClient, db: Database) -> None:
    """Initialize the global MessageManager instance."""
    if await MessageManager.get_instance() is None:
        await MessageManager.create(client, db)
    else:
        logger.warning("MessageManager sudah diinisialisasi sebelumnya")


def get_int_config(key: str, default: int) -> int:
    """Mengambil nilai konfigurasi integer berdasarkan kunci yang diberikan."""
    value = get_config_value(key)
    if value is None:
        return default
    try:
        return int(cast(Union[int, str], value))
    except ValueError:
        return default
