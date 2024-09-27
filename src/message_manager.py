"""Message management module for the Telegram auto-posting bot."""

import os
import random
import re
from typing import Any, Dict

from src.cache import cache
from src.config import yaml_config


class MessageManager:
    """Manages message templates for the Telegram auto-posting bot."""

    def __init__(self) -> None:
        """Initialize the MessageManager with a list of message file paths."""
        self.message_files = [
            os.path.join(yaml_config["data_directory"], file)
            for file in yaml_config["message_files"]
        ]
        self.last_used_file = None

    def load_message(self, file_path: str) -> str:
        """Load a message from a file, using cache if available."""
        cached_message = cache.get(file_path)
        if cached_message and isinstance(cached_message, str):
            return cached_message

        with open(file_path, encoding="utf-8") as file:
            message = file.read().strip()

        cache.set(file_path, message)
        return message

    def get_random_message(self) -> str:
        """Get a random message from the available message files."""
        available_files = [f for f in self.message_files if f != self.last_used_file]
        if not available_files:
            available_files = self.message_files

        random_file = random.choice(available_files)  # noqa: S311
        self.last_used_file = random_file
        return self.load_message(random_file)

    def get_appropriate_message(self, group_rules: Dict[str, Any]) -> str:
        """Get an appropriate message based on group rules."""
        message = self.get_random_message()

        if group_rules.get("send_messages", False):
            return ""  # Tidak bisa mengirim pesan ke grup ini

        if group_rules.get("send_media", False):
            # Hapus semua URL dari pesan
            message = re.sub(r"http\S+", "", message)

        if group_rules.get("embed_links", False):
            # Hapus semua URL dari pesan
            message = re.sub(r"http\S+", "", message)

        if group_rules.get("send_stickers", False) or group_rules.get(
            "send_gifs", False
        ):
            # Hapus semua emoji dari pesan
            message = re.sub(
                r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
                "",
                message,
            )

        return message


message_manager = MessageManager()
