"""Modul cache untuk bot auto-posting Telegram."""

import time
from typing import Dict, Generic, TypeVar, Union

T = TypeVar("T")


class Cache(Generic[T]):
    """Implementasi cache sederhana dengan waktu kedaluwarsa."""

    def __init__(self) -> None:
        """Inisialisasi cache."""
        self.cache: Dict[str, Dict[str, Union[T, float]]] = {}

    def set(self, key: str, value: T, expiry: int = 3600) -> None:
        """
        Menyimpan nilai dalam cache dengan waktu kedaluwarsa.

        Args:
            key (str): Kunci untuk menyimpan nilai.
            value (T): Nilai yang akan disimpan.
            expiry (int, optional): Waktu kedaluwarsa dalam detik. Default 3600 (1 jam).
        """
        self.cache[key] = {"value": value, "expiry": time.time() + expiry}

    def get(self, key: str) -> Union[T, None]:
        """
        Mengambil nilai dari cache jika ada dan belum kedaluwarsa.

        Args:
            key (str): Kunci untuk mengambil nilai.

        Returns:
            Union[T, None]: Nilai tersimpan / None jika tidak ditemukan / kedaluwarsa.
        """
        if key in self.cache:
            cache_item = self.cache[key]
            if (
                isinstance(cache_item["expiry"], float)
                and time.time() < cache_item["expiry"]
            ):
                return cache_item["value"]  # type: ignore
            else:
                del self.cache[key]  # Hapus item yang sudah kedaluwarsa
        return None

    def clear_expired(self) -> None:
        """Menghapus semua entri yang sudah kedaluwarsa dari cache."""
        current_time = time.time()
        self.cache = {
            k: v
            for k, v in self.cache.items()
            if isinstance(v["expiry"], float) and v["expiry"] > current_time
        }


# Inisialisasi instance cache global
cache: Cache[Union[str, list]] = Cache()
