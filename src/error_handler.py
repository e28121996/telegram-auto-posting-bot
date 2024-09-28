"""Modul penanganan kesalahan untuk bot auto-posting Telegram."""

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

from src.config import config
from src.group_manager import group_manager
from src.logger import logger
from src.utils import truncate_message

MAX_RETRIES = 3
RETRY_DELAY = 60  # dalam detik


def format_error_message(error_code: str, error_message: str) -> str:
    """
    Memformat pesan kesalahan dengan tag dan timestamp.

    Args:
        error_code (str): Kode kesalahan.
        error_message (str): Pesan kesalahan.

    Returns:
        str: Pesan kesalahan yang telah diformat.
    """
    timestamp = datetime.now().isoformat()
    return (
        f"[KRITIS] {error_code} #KesalahanKritis\n"
        f"Timestamp: {timestamp}\n"
        f"Kesalahan: {error_message}"
    )


async def handle_sending_error(
    error: Exception, group: str, message: str, retry_count: int = 0
) -> Optional[str]:
    """
    Menangani kesalahan yang terjadi saat pengiriman pesan.

    Args:
        error (Exception): Kesalahan yang terjadi.
        group (str): Grup tempat kesalahan terjadi.
        message (str): Pesan yang gagal dikirim.
        retry_count (int, optional): Jumlah percobaan ulang. Default 0.

    Returns:
        Optional[str]: Pesan yang diperbarui jika diperlukan, None jika tidak.

    Raises:
        Exception: Jika terjadi kesalahan yang tidak dapat ditangani.
    """
    error_code = "E001"  # Kode kesalahan default
    if isinstance(error, FloodWaitError):
        error_code = "E002"
        wait_time = error.seconds
        logger.warning(f"FloodWaitError: Menunggu selama {wait_time} detik")
        await asyncio.sleep(wait_time)
    elif isinstance(error, PeerFloodError):
        error_code = "E003"
        logger.warning(
            f"PeerFloodError untuk grup {group}: Terlalu banyak pesan dikirim"
        )
        await asyncio.sleep(300)  # Menunggu selama 5 menit
    elif isinstance(error, SlowModeWaitError):
        error_code = "E004"
        logger.info(
            f"SlowModeWaitError untuk grup {group}: Melewati karena mode lambat"
        )
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
            f"Kesalahan izin atau nama pengguna untuk grup {group}: "
            f"{error.__class__.__name__}"
        )
        group_manager.add_to_blacklist(group)
    elif isinstance(error, MessageTooLongError):
        error_code = "E006"
        logger.warning(
            f"MessageTooLongError untuk grup {group}: Pesan melebihi batas karakter"
        )
        truncated_message = truncate_message(
            message, 4096
        )  # Panjang maksimum pesan Telegram
        return truncated_message
    elif isinstance(error, UnauthorizedError):
        error_code = "E007"
        logger.error("UnauthorizedError: Periksa kredensial autentikasi Anda")
    elif isinstance(error, TimeoutError):
        error_code = "E008"
        if retry_count < MAX_RETRIES:
            logger.warning(
                f"TimeoutError untuk grup {group}: Mencoba lagi dalam {RETRY_DELAY} "
                f"detik (Percobaan {retry_count + 1}/{MAX_RETRIES})"
            )
            await asyncio.sleep(RETRY_DELAY)
            return await handle_sending_error(error, group, message, retry_count + 1)
        else:
            logger.error(
                f"TimeoutError untuk grup {group}: "
                f"Batas maksimum percobaan tercapai. Melewati."
            )
            group_manager.add_to_blacklist(group)
    elif "ChatNotFoundError" in str(error) or "GroupRestrictedError" in str(error):
        error_code = "E009"
        logger.warning(f"Kesalahan akses grup untuk {group}: {error}")
        group_manager.add_to_blacklist(group)
    else:
        logger.error(f"Kesalahan tak terduga untuk grup {group}: {error}")
        group_manager.add_to_blacklist(group)

    formatted_error = format_error_message(error_code, str(error))
    logger.error(formatted_error)
    return None


async def handle_scheduler_error(error: Exception) -> None:
    """
    Menangani kesalahan yang terjadi selama penjadwalan.

    Args:
        error (Exception): Kesalahan yang terjadi.

    Raises:
        Exception: Jika terjadi kesalahan yang tidak dapat ditangani.
    """
    error_code = "E010"
    formatted_error = format_error_message(error_code, f"Kesalahan penjadwal: {error}")
    logger.error(formatted_error)
    # Implementasikan penanganan khusus untuk kesalahan penjadwal di sini


async def send_critical_error_notification(
    client: TelegramClient, error_message: str
) -> None:
    """
    Mengirim notifikasi untuk kesalahan kritis ke chat pribadi.

    Args:
        client (TelegramClient): Klien Telegram yang digunakan untuk mengirim pesan.
        error_message (str): Pesan kesalahan yang akan dikirim.

    Raises:
        Exception: Jika terjadi kesalahan saat mengirim notifikasi.
    """
    if config.personal_chat_id:
        try:
            formatted_error = format_error_message("E011", error_message)
            await client.send_message(config.personal_chat_id, formatted_error)
        except Exception as e:
            logger.error(f"Gagal mengirim notifikasi kesalahan ke chat pribadi: {e}")
    else:
        logger.error(
            "ID chat pribadi tidak dikonfigurasi. "
            "Tidak dapat mengirim notifikasi kesalahan."
        )


__all__ = [
    "handle_sending_error",
    "handle_scheduler_error",
    "send_critical_error_notification",
]
