"""Modul penjadwalan untuk bot auto-posting Telegram."""

import random
from datetime import datetime, timedelta
from typing import Callable, List

import asyncio

from src.error_handler import handle_scheduler_error
from src.logger import logger


class Scheduler:
    """Mengelola tugas-tugas terjadwal untuk bot auto-posting Telegram."""

    def __init__(self) -> None:
        """Inisialisasi Scheduler."""
        self.tasks: List[Callable] = []

    async def schedule_task(
        self, task: Callable, min_interval: float = 1.3, max_interval: float = 1.5
    ) -> None:
        """
        Menjadwalkan dan menjalankan tugas pada interval acak.

        Args:
            task (Callable): Fungsi tugas yang akan dijadwalkan.
            min_interval (float): Interval minimum dalam jam. Default 1.3.
            max_interval (float): Interval maksimum dalam jam. Default 1.5.
        """
        while True:
            try:
                await task()
            except Exception as e:
                await handle_scheduler_error(e)

            # Menghasilkan interval acak antara min_interval dan max_interval
            interval = random.uniform(min_interval, max_interval)  # noqa: S311
            next_run = datetime.now() + timedelta(hours=interval)
            logger.info(f"Tugas berikutnya dijadwalkan pada: {next_run}")
            await asyncio.sleep(interval * 3600)  # Konversi jam ke detik

    def add_task(self, task: Callable) -> None:
        """
        Menambahkan tugas ke penjadwal.

        Args:
            task (Callable): Fungsi tugas yang akan ditambahkan.
        """
        self.tasks.append(task)

    async def run(self) -> None:
        """Menjalankan semua tugas terjadwal."""
        await asyncio.gather(*(self.schedule_task(task) for task in self.tasks))


scheduler = Scheduler()
