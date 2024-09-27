"""Main script for the Telegram auto-posting bot."""

import contextlib
from typing import Optional

import asyncio
from telethon import TelegramClient

from src.auth import create_client
from src.cache import cache
from src.config import yaml_config
from src.error_handler import send_critical_error_notification
from src.group_manager import group_manager
from src.logger import logger
from src.message_manager import message_manager
from src.message_sender import send_mass_message
from src.scheduler import scheduler


async def send_scheduled_messages(client: TelegramClient) -> None:
    """Send scheduled messages to valid groups."""
    try:
        groups = group_manager.get_valid_groups()
        message = message_manager.get_random_message()
        await send_mass_message(client, groups, message)
    except Exception as e:
        logger.error(f"Error in send_scheduled_messages: {e}")


async def clear_cache_periodically() -> None:
    """Clear expired cache entries periodically."""
    while True:
        try:
            await asyncio.sleep(yaml_config["cache_expiry"])
            cache.clear_expired()
            logger.info("Cleared expired cache entries")
        except Exception as e:
            logger.error(f"Error in clear_cache_periodically: {e}")


async def main() -> None:
    """Run the main bot loop."""
    client: Optional[TelegramClient] = None
    try:
        client = await create_client()
        logger.info("Bot started")

        scheduler.add_task(lambda: send_scheduled_messages(client))

        await asyncio.gather(scheduler.run(), clear_cache_periodically())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        error_message = f"Unexpected error in main loop: {e}"
        logger.error(error_message)
        if client:  # Add this check
            await send_critical_error_notification(client, error_message)
        else:
            logger.error("Unable to send critical error notification: Client is None")
    finally:
        if client and client.is_connected():
            with contextlib.suppress(Exception):
                await client.disconnect()  # type: ignore
            logger.info("Client disconnected")


if __name__ == "__main__":
    asyncio.run(main())
