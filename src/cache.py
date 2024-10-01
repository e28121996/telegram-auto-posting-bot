"""Modul cache untuk bot auto-posting Telegram.

Modul ini menyediakan implementasi cache sederhana dengan waktu kedaluwarsa
untuk meningkatkan kinerja aplikasi dengan menyimpan data yang sering diakses.
Ini mencakup kelas Cache yang mengelola penyimpanan dan pengambilan data cache,
serta instance cache global untuk digunakan di seluruh aplikasi.
"""

from __future__ import annotations

import time
from typing import Any
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import Union
from typing import cast

from src.config import get_config_value  # Updated import

T = TypeVar("T")


def get_config(
    key: str, default: Union[float, str, list, dict, None] = None
) -> Union[float, str, list, dict, None]:
    """Wrapper function for config_get_config that adds default value handling."""
    value = get_config_value(key)
    if isinstance(value, (int, float)):
        return float(value)
    return value if value is not None else default


class Cache(Generic[T]):
    """Implementasi cache sederhana dengan waktu kedaluwarsa."""

    def __init__(self: Cache[Any]) -> None:
        """Inisialisasi objek Cache dengan dictionary cache kosong."""
        self.cache: dict[str, dict[str, T | float]] = {}

    def set_value(
        self: Cache[T], key: str, value: T, expiry: Union[float, None] = None
    ) -> None:
        """Menyimpan nilai dalam cache dengan waktu kedaluwarsa."""
        if expiry is None:
            config_expiry = get_config("cache_expiry", 3600.0)
            expiry = (
                float(config_expiry)
                if isinstance(config_expiry, (int, float))
                else 3600.0
            )
        self.cache[key] = {"value": value, "expiry": time.time() + expiry}

    def get(self: Cache[T], key: str) -> Optional[T]:
        """Mengambil nilai dari cache jika ada dan belum kedaluwarsa."""
        if key in self.cache:
            cache_item = self.cache[key]
            if (
                isinstance(cache_item["expiry"], float)
                and time.time() < cache_item["expiry"]
            ):
                return cast(T, cache_item["value"])
            del self.cache[key]  # Hapus item yang sudah kedaluwarsa
        return None

    def clear_expired(self: Cache[T]) -> None:
        """Menghapus semua entri yang sudah kedaluwarsa dari cache.

        Metode ini memeriksa semua item dalam cache dan menghapus
        yang sudah melewati waktu kedaluwarsanya.
        """
        current_time = time.time()
        self.cache = {
            k: v
            for k, v in self.cache.items()
            if isinstance(v["expiry"], float) and v["expiry"] > current_time
        }


cache: Cache[str | list] = Cache()
"""Instance cache global yang digunakan di seluruh aplikasi.

Instance ini menyediakan akses ke fungsionalitas caching untuk
komponen-komponen lain dalam aplikasi.
"""
