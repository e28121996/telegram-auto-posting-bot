"""Error handling module for the Telegram auto-posting bot."""

from datetime import datetime
from typing import Optional

import asyncio
from telethon import TelegramClient
from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatWriteForbiddenError,
    FloodWaitError,
    MessageTooLongError,
    PeerFloodError,
    SlowModeWaitError,
    TimeoutError,
    UnauthorizedError,
    UserBannedInChannelError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
    UserNotParticipantError,
    UserPrivacyRestrictedError,
    UserRestrictedError,
)

from src.config import config  # Tambahkan import ini
from src.group_manager import group_manager
from src.logger import logger
from src.utils import truncate_message

MAX_RETRIES = 3
RETRY_DELAY = 60  # in seconds


def format_error_message(error_code: str, error_message: str) -> str:
    """Format error message with tags and timestamp."""
    timestamp = datetime.now().isoformat()
    return (
        f"[CRITICAL] {error_code} #CriticalError\n"
        f"Timestamp: {timestamp}\n"
        f"Error: {error_message}"
    )


async def handle_sending_error(
    error: Exception, group: str, message: str, retry_count: int = 0
) -> Optional[str]:
    """Handle errors that occur during message sending."""
    error_code = "E001"  # Default error code
    if isinstance(error, FloodWaitError):
        error_code = "E002"
        wait_time = error.seconds
        logger.warning(f"FloodWaitError: Waiting for {wait_time} seconds")
        await asyncio.sleep(wait_time)
    elif isinstance(error, PeerFloodError):
        error_code = "E003"
        logger.warning(f"PeerFloodError for group {group}: Too many messages sent")
        await asyncio.sleep(300)  # Wait for 5 minutes
    elif isinstance(error, SlowModeWaitError):
        error_code = "E004"
        logger.info(f"SlowModeWaitError for group {group}: Skipping due to slow mode")
    elif isinstance(
        error,
        (
            ChatWriteForbiddenError,
            ChannelPrivateError,
            ChatAdminRequiredError,
            UserBannedInChannelError,
            UserNotParticipantError,
            UserPrivacyRestrictedError,
            UserRestrictedError,
            UsernameInvalidError,
            UsernameNotOccupiedError,
        ),
    ):
        error_code = "E005"
        logger.warning(
            f"Permission or username error for group {group}: "
            f"{error.__class__.__name__}"
        )
        group_manager.add_to_blacklist(group)
    elif isinstance(error, MessageTooLongError):
        error_code = "E006"
        logger.warning(
            f"MessageTooLongError for group {group}: Message exceeds character limit"
        )
        truncated_message = truncate_message(
            message, 4096
        )  # Telegram's max message length
        return truncated_message
    elif isinstance(error, UnauthorizedError):
        error_code = "E007"
        logger.error("UnauthorizedError: Check your authentication credentials")
    elif isinstance(error, TimeoutError):
        error_code = "E008"
        if retry_count < MAX_RETRIES:
            logger.warning(
                f"TimeoutError for group {group}: Retrying in {RETRY_DELAY} seconds "
                f"(Attempt {retry_count + 1}/{MAX_RETRIES})"
            )
            await asyncio.sleep(RETRY_DELAY)
            return await handle_sending_error(error, group, message, retry_count + 1)
        else:
            logger.error(
                f"TimeoutError for group {group}: Max retries reached. Skipping."
            )
            group_manager.add_to_blacklist(group)
    elif "ChatNotFoundError" in str(error) or "GroupRestrictedError" in str(error):
        error_code = "E009"
        logger.warning(f"Group access error for {group}: {error}")
        group_manager.add_to_blacklist(group)
    else:
        logger.error(f"Unexpected error for group {group}: {error}")
        group_manager.add_to_blacklist(group)

    formatted_error = format_error_message(error_code, str(error))
    logger.error(formatted_error)
    return None


async def handle_scheduler_error(error: Exception) -> None:
    """Handle errors that occur during scheduling."""
    error_code = "E010"
    formatted_error = format_error_message(error_code, f"Scheduler error: {error}")
    logger.error(formatted_error)
    # Implement any specific handling for scheduler errors here


async def send_critical_error_notification(
    client: TelegramClient, error_message: str
) -> None:
    """Send a notification for critical errors to the personal chat."""
    if config.personal_chat_id:
        try:
            formatted_error = format_error_message("E011", error_message)
            await client.send_message(config.personal_chat_id, formatted_error)
        except Exception as e:
            logger.error(f"Failed to send error notification to personal chat: {e}")
    else:
        logger.error(
            "Personal chat ID not configured. Unable to send error notification."
        )


__all__ = [
    "handle_sending_error",
    "handle_scheduler_error",
    "send_critical_error_notification",
]
