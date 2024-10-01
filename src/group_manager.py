"""Modul manajemen grup untuk bot auto-posting Telegram.

Modul ini menyediakan fungsionalitas untuk mengelola grup Telegram,
termasuk memuat daftar grup, mengelola daftar hitam, dan memvalidasi grup.
Ini menggunakan sistem cache untuk mengoptimalkan kinerja dan mengurangi
akses berulang ke penyimpanan.
"""

import asyncio
import json
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from telethon import TelegramClient

from src.cache import cache
from src.config_loader import config as yaml_config
from src.database import Database
from src.exceptions import ConfigurationError
from src.logger import logger
from src.utils import get_current_utc_time


class GroupManager:
    """Mengelola operasi terkait grup untuk bot auto-posting Telegram.

    Kelas ini menyediakan metode untuk memuat daftar grup, mengelola daftar hitam,
    dan memvalidasi grup. Menggunakan caching untuk meningkatkan efisiensi.

    Attributes:
        groups_file (Path): Path ke file yang berisi daftar grup.
        blacklist_file (Path): Path ke file yang berisi daftar hitam grup.
        slow_mode_file (Path): Path ke file yang berisi informasi slow mode.
    """

    __slots__ = (
        "data_dir",
        "slow_mode_file",
        "slow_mode_info",
        "groups_file",
        "blacklist_file",
        "client",
        "db",
        "slow_mode_loaded",
    )

    def __init__(self: "GroupManager") -> None:
        """Inisialisasi GroupManager dengan path file konfigurasi."""
        try:
            self.data_dir = Path(yaml_config["directories"]["data"])
            self.slow_mode_file = self.data_dir / yaml_config["files"]["slow_mode_info"]
            self.groups_file = self.data_dir / yaml_config["files"]["groups"]
            self.blacklist_file = self.data_dir / yaml_config["files"]["blacklist"]
        except KeyError as e:
            error_msg = f"Konfigurasi tidak lengkap: {e}"
            raise ConfigurationError(error_msg) from e

        self.slow_mode_info: Dict[str, str] = {}
        self.slow_mode_loaded = False

    async def initialize(
        self: "GroupManager", client: TelegramClient, db: Database
    ) -> None:
        """Inisialisasi GroupManager dengan client dan database."""
        self.client = client
        self.db = db
        if not self.slow_mode_loaded:
            self.load_slow_mode_info()

    def load_slow_mode_info(self: "GroupManager") -> None:
        """Memuat informasi slow mode dari file JSON."""
        if self.slow_mode_loaded:
            return

        try:
            cached_info = cache.get("slow_mode_info")
            if cached_info and isinstance(cached_info, str):
                self.slow_mode_info = json.loads(cached_info)
            else:
                with self.slow_mode_file.open("r") as f:
                    content = f.read().strip()
                    if content:
                        loaded_info = json.loads(content)
                        if isinstance(loaded_info, dict):
                            self.slow_mode_info = loaded_info
                        else:
                            logger.warning(
                                "Loaded slow mode info is not a dictionary. "
                                "Using empty dict."
                            )
                            self.slow_mode_info = {}
                    else:
                        self.slow_mode_info = {}
                cache.set_value("slow_mode_info", json.dumps(self.slow_mode_info))

            logger.info(
                f"Berhasil memuat informasi slow mode untuk "
                f"{len(self.slow_mode_info)} grup"
            )
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Error saat memuat informasi slow mode: {e!s}")
            self.slow_mode_info = {}
        finally:
            self.slow_mode_loaded = True

    def save_slow_mode_info(self: "GroupManager") -> None:
        """Menyimpan informasi slow mode ke file JSON."""
        try:
            with self.slow_mode_file.open("w") as f:
                json.dump(self.slow_mode_info, f)
            logger.info("Berhasil menyimpan informasi slow mode")
        except OSError as e:
            logger.error(f"Gagal menyimpan informasi slow mode: {e}")

    async def clean_slow_mode_info(self: "GroupManager") -> None:
        """Membersihkan data slow mode yang sudah tidak relevan."""
        current_time = get_current_utc_time()
        expired_groups = [
            group
            for group, expiry_time_str in self.slow_mode_info.items()
            if datetime.fromisoformat(expiry_time_str) < current_time
        ]
        for group in expired_groups:
            del self.slow_mode_info[group]
        self.save_slow_mode_info()

    async def load_groups(self: "GroupManager") -> List[str]:
        """Memuat dan me-cache daftar grup dari file.

        Returns:
            list[str]: Daftar grup yang dimuat, baik dari cache atau file.
        """
        cached_groups = cache.get("groups")
        if cached_groups and isinstance(cached_groups, list):
            logger.debug(f"Menggunakan {len(cached_groups)} grup dari cache")
            return cached_groups

        async with asyncio.Lock():
            groups = await self._read_file(self.groups_file)

        logger.info(f"Memuat {len(groups)} grup dari file")
        cache.set_value("groups", groups, expiry=3600)  # Cache selama 1 jam
        return groups

    async def load_blacklist(self: "GroupManager") -> List[str]:
        """Memuat dan me-cache daftar hitam grup dari file.

        Returns:
            list[str]: Daftar grup yang masuk daftar hitam, dari cache atau file.
        """
        cached_blacklist = cache.get("blacklist")
        if cached_blacklist and isinstance(cached_blacklist, list):
            logger.debug(
                f"Menggunakan {len(cached_blacklist)} grup dari cache daftar hitam",
            )
            return cached_blacklist

        async with asyncio.Lock():
            blacklist = await self._read_file(self.blacklist_file)

        logger.info(f"Memuat {len(blacklist)} grup dari file daftar hitam")
        cache.set_value("blacklist", blacklist)
        return blacklist

    # Ganti @lru_cache dengan metode caching manual
    async def get_valid_groups(self: "GroupManager") -> List[str]:
        """Mendapatkan daftar grup yang valid."""
        groups = await self.load_groups()
        blacklist = await self.load_blacklist()
        valid_groups = [
            group
            for group in groups
            if group not in blacklist and not await self.is_in_slow_mode(group)
        ]
        logger.info(
            f"Mendapatkan {len(valid_groups)} grup valid "
            f"dari {len(groups)} total grup"
        )
        return valid_groups

    async def add_to_blacklist(self: "GroupManager", group: str) -> None:
        """Menambahkan grup ke daftar hitam dan memperbarui cache.

        Args:
            group (str): Nama grup yang akan ditambahkan ke daftar hitam.
        """
        blacklist = await self.load_blacklist()
        if group not in blacklist:
            blacklist.append(group)
            try:
                async with asyncio.Lock():
                    await self._write_file(self.blacklist_file, group)
                cache.set_value("blacklist", blacklist)
                logger.info(f"Berhasil menambahkan {group} ke daftar hitam")
            except OSError as e:
                logger.error(f"Gagal menambahkan {group} ke daftar hitam: {e}")
        else:
            logger.info(f"{group} sudah ada dalam daftar hitam")

    async def is_in_blacklist(self: "GroupManager", group: str) -> bool:
        """Memeriksa apakah grup termasuk dalam daftar hitam.

        Args:
            group (str): Nama grup yang akan diperiksa.

        Returns:
            bool: True jika grup ada dalam daftar hitam, False jika tidak.
        """
        blacklist = await self.load_blacklist()
        result = group in blacklist
        logger.debug(
            f"Memeriksa {group} dalam daftar hitam: {'Ya' if result else 'Tidak'}",
        )
        return result

    async def update_slow_mode_info(
        self: "GroupManager", group: str, wait_seconds: int
    ) -> None:
        """Memperbarui informasi slow mode untuk grup."""
        expiry_time = get_current_utc_time() + timedelta(seconds=wait_seconds)
        self.slow_mode_info[group] = expiry_time.isoformat()
        self.save_slow_mode_info()

    async def is_in_slow_mode(self: "GroupManager", group: str) -> bool:
        """Memeriksa apakah grup masih dalam slow mode."""
        if group not in self.slow_mode_info:
            return False
        expiry_time = datetime.fromisoformat(self.slow_mode_info[group])
        return get_current_utc_time() < expiry_time

    async def get_slow_mode_stats(self: "GroupManager") -> Dict[str, Any]:
        """Mendapatkan statistik slow mode untuk semua grup."""
        return {
            "total_groups": len(self.slow_mode_info),
            "active_groups": sum(
                1
                for expiry_time in self.slow_mode_info.values()
                if datetime.fromisoformat(expiry_time) > get_current_utc_time()
            ),
        }

    @staticmethod
    async def _read_file(file_path: Path) -> List[str]:
        async with asyncio.Lock():
            return await asyncio.to_thread(GroupManager._sync_read_file, file_path)

    @staticmethod
    async def _write_file(file_path: Path, content: str) -> None:
        async with asyncio.Lock():
            await asyncio.to_thread(GroupManager._sync_write_file, file_path, content)

    @staticmethod
    def _sync_read_file(file_path: Path) -> List[str]:
        with file_path.open("r") as file:
            return [line.strip() for line in file if line.strip()]

    @staticmethod
    def _sync_write_file(file_path: Path, content: str) -> None:
        with file_path.open("a") as file:
            file.write(f"{content}\n")


group_manager = GroupManager()
"""Instance GroupManager global untuk digunakan di seluruh aplikasi."""
