"""Modul penjadwalan untuk bot auto-posting Telegram.

Modul ini menyediakan fungsionalitas untuk menjadwalkan dan menjalankan tugas-tugas
secara otomatis pada interval waktu tertentu menggunakan asyncio.

Kelas:
    Scheduler: Mengelola tugas-tugas terjadwal untuk bot auto-posting Telegram.

Fungsi:
    Tidak ada fungsi tingkat modul.

Variabel:
    scheduler: Instance dari kelas Scheduler untuk penggunaan global.
"""

from __future__ import annotations

import asyncio
import secrets
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import TYPE_CHECKING
from typing import Any

from src.config import get_config
from src.logger import logger

if TYPE_CHECKING:
    from collections.abc import Callable


ERROR_THRESHOLD = 5
SUCCESS_THRESHOLD = 10


def get_float_config(key: str, default: float) -> float:
    """Mengambil nilai konfigurasi float berdasarkan kunci yang diberikan.

    Fungsi ini mengambil nilai konfigurasi dari fungsi get_config dan
    mengonversinya menjadi float. Jika nilai tidak dapat dikonversi,
    nilai default akan dikembalikan.

    Args:
        key (str): Kunci konfigurasi yang ingin diambil.
        default (float): Nilai default yang akan dikembalikan jika konfigurasi
                         tidak ditemukan atau tidak dapat dikonversi ke float.

    Returns:
        float: Nilai konfigurasi yang dikonversi ke float atau nilai default.
    """
    value = get_config(key, default)
    return float(value) if isinstance(value, (int, float, str)) else default


class Scheduler:
    """Mengelola tugas-tugas terjadwal untuk bot auto-posting Telegram.

    Kelas ini bertanggung jawab untuk menjadwalkan, menambahkan, dan menjalankan
    tugas-tugas secara asinkron pada interval waktu yang ditentukan menggunakan asyncio.

    Attributes:
        tasks (list[Callable[..., Any]]): Daftar tugas yang akan dijadwalkan
                                          dan dijalankan.
    """

    def __init__(self: Scheduler) -> None:
        """Inisialisasi Scheduler dengan daftar tugas kosong."""
        self.tasks: list[Callable[..., Any]] = []
        self.min_interval = get_float_config("min_interval", 1.3)
        self.max_interval = get_float_config("max_interval", 1.5)
        self.error_count = 0
        self.success_count = 0

    async def schedule_task(self: Scheduler, task: Callable[..., Any]) -> None:
        """Menjadwalkan dan menjalankan tugas pada interval acak.

        Metode ini menjalankan tugas yang diberikan secara berulang pada interval
        waktu acak antara min_interval dan max_interval. Menggunakan asyncio untuk
        menangani operasi asinkron.

        Args:
            task (Callable[..., Any]): Fungsi tugas yang akan dijadwalkan.
            min_interval (float | None): Interval minimum dalam jam. Jika None,
                akan menggunakan nilai default dari konfigurasi.
            max_interval (float | None): Interval maksimum dalam jam. Jika None,
                akan menggunakan nilai default dari konfigurasi.

        Raises:
            ConnectionError: Jika terjadi masalah koneksi saat menjalankan tugas.
            TimeoutError: Jika tugas melebihi batas waktu yang ditentukan.
        """
        while True:
            try:
                logger.info(f"Menjalankan tugas terjadwal: {task.__name__}")
                await task()
                self.success_count += 1
                self.error_count = max(
                    0, self.error_count - 1
                )  # Decrease error count on success
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Error in scheduled task: {e}")
                self.error_count += 1
                self.success_count = max(
                    0, self.success_count - 1
                )  # Decrease success count on error

            interval = self.calculate_dynamic_interval()
            next_run = datetime.now(timezone.utc) + timedelta(hours=interval)
            logger.info(f"Tugas berikutnya dijadwalkan pada: {next_run}")
            await asyncio.sleep(interval * 3600)

    def calculate_dynamic_interval(self: Scheduler) -> float:
        """Menghitung interval dinamis berdasarkan jumlah error dan sukses.

        Returns:
            float: Interval yang dihitung dalam jam.
        """
        base_interval = secrets.SystemRandom().uniform(
            self.min_interval, self.max_interval
        )
        if self.error_count > ERROR_THRESHOLD:
            return base_interval * 1.5  # Increase interval if many errors
        if self.success_count > SUCCESS_THRESHOLD:
            return base_interval * 0.8  # Decrease interval if many successes
        return base_interval

    def add_task(self: Scheduler, task: Callable[..., Any]) -> None:
        """Menambahkan tugas ke penjadwal.

        Metode ini menambahkan fungsi tugas baru ke dalam daftar tugas yang akan
        dijadwalkan.

        Args:
            task (Callable[..., Any]): Fungsi tugas yang akan ditambahkan.
        """
        self.tasks.append(task)

    async def run(self: Scheduler) -> None:
        """Menjalankan semua tugas terjadwal."""
        logger.info("Scheduler dimulai")
        await asyncio.gather(*(self.schedule_task(task) for task in self.tasks))


scheduler = Scheduler()
