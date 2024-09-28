"""Modul manajemen grup untuk bot auto-posting Telegram."""

import os
from typing import List

from src.cache import cache
from src.config import yaml_config
from src.logger import logger


class GroupManager:
    """Mengelola grup untuk bot auto-posting Telegram."""

    def __init__(self) -> None:
        """Inisialisasi GroupManager."""
        self.groups_file = os.path.join(
            yaml_config["data_directory"], yaml_config["groups_file"]
        )
        self.blacklist_file = os.path.join(
            yaml_config["data_directory"], yaml_config["blacklist_file"]
        )

    def load_groups(self) -> List[str]:
        """
        Memuat grup dari file grup.

        Returns:
            List[str]: Daftar grup yang dimuat.
        """
        cached_groups = cache.get("groups")
        if cached_groups and isinstance(cached_groups, list):
            return cached_groups

        with open(self.groups_file) as file:
            groups = [line.strip() for line in file if line.strip()]

        cache.set("groups", groups)
        return groups

    def load_blacklist(self) -> List[str]:
        """
        Memuat grup yang masuk daftar hitam dari file daftar hitam.

        Returns:
            List[str]: Daftar grup yang masuk daftar hitam.
        """
        cached_blacklist = cache.get("blacklist")
        if cached_blacklist and isinstance(cached_blacklist, list):
            return cached_blacklist

        with open(self.blacklist_file) as file:
            blacklist = [line.strip() for line in file if line.strip()]

        cache.set("blacklist", blacklist)
        return blacklist

    def get_valid_groups(self) -> List[str]:
        """
        Mendapatkan daftar grup yang valid (tidak masuk daftar hitam).

        Returns:
            List[str]: Daftar grup yang valid.
        """
        groups = self.load_groups()
        blacklist = self.load_blacklist()
        return [group for group in groups if group not in blacklist]

    def add_to_blacklist(self, group: str) -> None:
        """
        Menambahkan grup ke daftar hitam.

        Args:
            group (str): Nama grup yang akan ditambahkan ke daftar hitam.
        """
        blacklist = self.load_blacklist()
        if group not in blacklist:
            blacklist.append(group)
            with open(self.blacklist_file, "a") as file:
                file.write(f"{group}\n")
            cache.set("blacklist", blacklist)
            logger.info(f"Menambahkan {group} ke daftar hitam")


# Inisialisasi instance GroupManager global
group_manager = GroupManager()
