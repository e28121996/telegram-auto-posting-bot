"""Message sending module for the Telegram auto-posting bot."""

import random
import time
from typing import List

import asyncio
from telethon import TelegramClient

from src.config import yaml_config
from src.error_handler import handle_sending_error
from src.logger import logger
from src.message_manager import message_manager


async def send_message(client: TelegramClient, group: str, message: str) -> None:
    """Send a message to a specific group."""
    logger.info(f"Preparing to send message to {group}. Message length: {len(message)}")
    start_time = time.time()
    try:
        result = await client.send_message(group, message)
        end_time = time.time()
        logger.info(
            f"Message sent to {group}. Time taken: {end_time - start_time:.2f}s. "
            f"Message ID: {result.id}"
        )
    except Exception as e:
        logger.error(f"Error sending message to {group}", exc_info=True)
        await handle_sending_error(e, group, message)

    delay = random.uniform(yaml_config["min_delay"], yaml_config["max_delay"])  # noqa: S311
    logger.debug(f"Applying delay of {delay:.2f}s before next message")
    await asyncio.sleep(delay)


async def send_mass_message(
    client: TelegramClient, groups: List[str], message: str
) -> None:
    """Send a message to multiple groups."""
    for group in groups:
        # Get a new random message for each group
        message = message_manager.get_random_message()
        await send_message(client, group, message)
        # Additional delay between groups
        await asyncio.sleep(random.uniform(5, 10))  # noqa: S311
