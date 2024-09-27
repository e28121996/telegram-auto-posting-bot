"""Authentication module for the Telegram auto-posting bot."""

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from src.config import config
from src.logger import logger


async def create_client() -> TelegramClient:
    """Create and authenticate a Telegram client."""
    client = TelegramClient("session", config.api_id, config.api_hash)

    try:
        await client.connect()
        logger.info(
            f"Connecting with API ID: {config.api_id}, Phone: {config.phone_number}"
        )

        if not await client.is_user_authorized():
            logger.info("User not authorized. Sending code request...")
            sent = await client.send_code_request(config.phone_number)
            logger.info(f"Code request sent: {sent}")
            code = input("Enter the code you received: ")
            try:
                logger.info("Attempting to sign in...")
                await client.sign_in(config.phone_number, code)
            except SessionPasswordNeededError:
                password = input(
                    "Two-step verification is enabled. Please enter your password: "
                )
                await client.sign_in(password=password)

        logger.info("Successfully authenticated with Telegram")
        return client
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise
