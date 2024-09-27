"""Scheduler module for the Telegram auto-posting bot."""

import random
from datetime import datetime, timedelta
from typing import Callable, List

import asyncio

from src.error_handler import handle_scheduler_error
from src.logger import logger


class Scheduler:
    """Manages scheduled tasks for the Telegram auto-posting bot."""

    def __init__(self) -> None:
        """Initialize the Scheduler."""
        self.tasks: List[Callable] = []

    async def schedule_task(
        self, task: Callable, min_interval: float = 1.3, max_interval: float = 1.5
    ) -> None:
        """Schedule and run a task at random intervals."""
        while True:
            try:
                await task()
            except Exception as e:
                await handle_scheduler_error(e)

            interval = random.uniform(min_interval, max_interval)  # noqa: S311
            next_run = datetime.now() + timedelta(hours=interval)
            logger.info(f"Next task scheduled at: {next_run}")
            await asyncio.sleep(interval * 3600)  # Convert hours to seconds

    def add_task(self, task: Callable) -> None:
        """Add a task to the scheduler."""
        self.tasks.append(task)

    async def run(self) -> None:
        """Run all scheduled tasks."""
        await asyncio.gather(*(self.schedule_task(task) for task in self.tasks))


scheduler = Scheduler()
