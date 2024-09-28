"""Modul manajemen pesan untuk bot auto-posting Telegram."""

import os
import random
import re
from typing import Any, Dict

from src.cache import cache
from src.config import yaml_config


class MessageManager:
    """Mengelola template pesan untuk bot auto-posting Telegram."""

    def __init__(self) -> None:
        """Inisialisasi MessageManager dengan daftar path file pesan."""
        self.message_files = [
            os.path.join(yaml_config["data_directory"], file)
            for file in yaml_config["message_files"]
        ]
        self.last_used_file = None

    def load_message(self, file_path: str) -> str:
        """
        Memuat pesan dari file, menggunakan cache jika tersedia.

        Args:
            file_path (str): Path file pesan yang akan dimuat.

        Returns:
            str: Isi pesan yang dimuat.
        """
        cached_message = cache.get(file_path)
        if cached_message and isinstance(cached_message, str):
            return cached_message

        with open(file_path, encoding="utf-8") as file:
            message = file.read().strip()

        cache.set(file_path, message)
        return message

    def get_random_message(self) -> str:
        """
        Mendapatkan pesan acak dari file pesan yang tersedia.

        Returns:
            str: Pesan acak yang dipilih.
        """
        available_files = [f for f in self.message_files if f != self.last_used_file]
        if not available_files:
            available_files = self.message_files

        random_file = random.choice(available_files)  # noqa: S311
        self.last_used_file = random_file
        return self.load_message(random_file)

    def get_appropriate_message(self, group_rules: Dict[str, Any]) -> str:
        """
        Mendapatkan pesan yang sesuai berdasarkan aturan grup.

        Args:
            group_rules (Dict[str, Any]): Aturan grup yang berlaku.

        Returns:
            str: Pesan yang sesuai dengan aturan grup.
        """
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


# Inisialisasi instance MessageManager global
message_manager = MessageManager()
