"""Modul penjadwalan untuk bot auto-posting Telegram."""

from __future__ import annotations

import asyncio
import secrets
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any
from typing import List
from typing import Union
from typing import cast

import pytz

from src.config import get_config_value
from src.logger import logger
from src.utils import calculate_next_run

if TYPE_CHECKING:
    from collections.abc import Callable


ERROR_THRESHOLD = 5
SUCCESS_THRESHOLD = 10


def get_float_config(key: str, default: float) -> float:
    """Mengambil nilai konfigurasi float berdasarkan kunci yang diberikan."""
    value = get_config_value(key)
    if value is None:
        return default
    try:
        return float(cast(Union[float, str], value))
    except ValueError:
        return default


class Scheduler:
    """Mengelola tugas-tugas terjadwal untuk bot auto-posting Telegram."""

    def __init__(self: Scheduler) -> None:
        """Initialize the Scheduler."""
        self.tasks: List[Callable[..., Any]] = []
        self.min_interval: float = get_float_config("scheduling.min_interval", 1.3)
        self.max_interval: float = get_float_config("scheduling.max_interval", 1.5)
        self.interval: float = (
            self.min_interval
            + (self.max_interval - self.min_interval) * secrets.randbelow(10000) / 10000
        )
        self.error_count: int = 0
        self.success_count: int = 0

    def add_task(self: Scheduler, task: Callable[..., Any]) -> None:
        """Menambahkan tugas ke penjadwal."""
        self.tasks.append(task)

    async def schedule_task(self: Scheduler, task: Callable[..., Any]) -> None:
        """Menjadwalkan dan menjalankan tugas pada interval acak."""
        while True:
            try:
                logger.info(f"Menjalankan tugas terjadwal: {task.__name__}")
                await task()
                self.success_count += 1
                self.error_count = max(0, self.error_count - 1)
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Error in scheduled task: {e}")
                self.error_count += 1
                self.success_count = max(0, self.success_count - 1)

            interval = self.calculate_dynamic_interval()
            next_run = calculate_next_run(interval)
            logger.info(f"Tugas berikutnya dijadwalkan pada: {next_run}")
            await asyncio.sleep(interval * 3600)

    def calculate_dynamic_interval(self: Scheduler) -> float:
        """Menghitung interval dinamis berdasarkan jumlah error dan sukses."""
        base_interval = (
            self.min_interval
            + (self.max_interval - self.min_interval) * secrets.randbelow(10000) / 10000
        )
        if self.error_count > ERROR_THRESHOLD:
            return base_interval * 1.5  # Increase interval if many errors
        if self.success_count > SUCCESS_THRESHOLD:
            return base_interval * 0.8  # Decrease interval if many successes
        return base_interval

    async def run(self: Scheduler) -> None:
        """Menjalankan semua tugas terjadwal."""
        logger.info("Scheduler dimulai")
        await asyncio.gather(*(self.schedule_task(task) for task in self.tasks))

    def get_next_run_time(self: Scheduler) -> datetime:
        """Menghitung waktu eksekusi berikutnya berdasarkan interval yang ditentukan."""
        return datetime.now(pytz.UTC) + timedelta(seconds=self.interval)

    def get_interval(self: Scheduler) -> int:
        """Mendapatkan interval waktu antara eksekusi."""
        return int(self.interval * 3600)  # Konversi jam ke detik


scheduler = Scheduler()
