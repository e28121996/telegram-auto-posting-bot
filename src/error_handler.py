"""Modul penanganan kesalahan untuk bot auto-posting Telegram.

Modul ini menyediakan fungsi-fungsi untuk menangani berbagai jenis kesalahan
yang mungkin terjadi selama operasi bot auto-posting Telegram. Ini mencakup
penanganan kesalahan pengiriman pesan, kesalahan penjadwalan, dan pengiriman
notifikasi untuk kesalahan kritis.

Fungsi-fungsi utama:
- format_error_message: Memformat pesan kesalahan dengan kode dan timestamp.
- handle_sending_error: Menangani kesalahan saat mengirim pesan.
- handle_scheduler_error: Menangani kesalahan yang terjadi dalam penjadwal.
- send_critical_error_notification: Mengirim notifikasi untuk kesalahan kritis.

Modul ini juga mendefinisikan konstanta-konstanta konfigurasi dan mengimpor
dependensi yang diperlukan dari modul-modul lain dalam proyek.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING
from typing import Union
from typing import cast

from telethon.errors import ChannelPrivateError
from telethon.errors import ChatAdminRequiredError
from telethon.errors import ChatWriteForbiddenError
from telethon.errors import FloodWaitError
from telethon.errors import MessageTooLongError
from telethon.errors import PeerFloodError
from telethon.errors import SlowModeWaitError
from telethon.errors import TimeoutError
from telethon.errors import UnauthorizedError
from telethon.errors import UserBannedInChannelError
from telethon.errors import UsernameInvalidError
from telethon.errors import UsernameNotOccupiedError
from telethon.errors import UserNotParticipantError
from telethon.errors import UserPrivacyRestrictedError
from telethon.errors import UserRestrictedError

from src.config import config
from src.config import get_config_value
from src.group_manager import group_manager
from src.logger import logger
from src.utils import truncate_message

if TYPE_CHECKING:
    from telethon import TelegramClient


def get_int_config(key: str, default: int) -> int:
    value = get_config_value(key)
    if value is None:
        return default
    try:
        return int(cast(Union[int, str], value))
    except ValueError:
        return default


def get_float_config(key: str, default: float) -> float:
    value = get_config_value(key)
    if value is None:
        return default
    try:
        return float(cast(Union[float, str], value))
    except ValueError:
        return default


MAX_RETRIES = get_int_config("max_retries", 3)
RETRY_DELAY = get_float_config("retry_delay", 60.0)


def format_error_message(error_code: str, error_message: str) -> str:
    """Memformat pesan kesalahan dengan tag dan timestamp.

    Fungsi ini mengambil kode kesalahan dan pesan kesalahan, lalu menggabungkannya
    dengan timestamp saat ini untuk membuat pesan kesalahan yang terformat.

    Args:
        error_code (str): Kode unik yang mengidentifikasi jenis kesalahan.
        error_message (str): Deskripsi rinci tentang kesalahan yang terjadi.

    Returns:
        str: Pesan kesalahan yang telah diformat, termasuk tag kritis, timestamp,
             kode kesalahan, dan deskripsi kesalahan.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    return (
        f"[KRITIS] {error_code} #KesalahanKritis\n"
        f"Timestamp: {timestamp}\n"
        f"Kesalahan: {error_message}"
    )


async def handle_sending_error(
    error: Exception,
    group: str,
    message: str,
    retry_count: int = 0,
) -> str | None:
    """Menangani kesalahan yang terjadi saat pengiriman pesan.

    Fungsi ini menangani berbagai jenis kesalahan yang mungkin terjadi saat
    mengirim pesan ke grup Telegram. Tindakan yang diambil tergantung pada
    jenis kesalahan yang ditemui.

    Args:
        error (Exception): Objek kesalahan yang ditangkap.
        group (str): Nama atau ID grup tempat pesan dikirim.
        message (str): Isi pesan yang gagal dikirim.
        retry_count: int = 0,
        # Jumlah percobaan pengiriman yang telah dilakukan.

    Returns:
        str | None: Pesan yang diperbarui jika perlu dimodifikasi,
                    atau None jika tidak ada perubahan.
    """
    error_code = "E001"
    if isinstance(error, FloodWaitError):
        error_code = "E002"
        wait_time = getattr(error, "seconds", 60)
        logger.warning(f"FloodWaitError: Menunggu selama {wait_time} detik")
        await asyncio.sleep(wait_time)
    elif isinstance(error, PeerFloodError):
        error_code = "E003"
        logger.warning(
            f"PeerFloodError untuk grup {group}: Terlalu banyak pesan dikirim",
        )
        await asyncio.sleep(300)
    elif isinstance(error, SlowModeWaitError):
        error_code = "E004"
        logger.info(
            f"SlowModeWaitError untuk grup {group}: Melewati karena mode lambat",
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
            f"{error.__class__.__name__}",
        )
        await group_manager.add_to_blacklist(group)
    elif isinstance(error, MessageTooLongError):
        error_code = "E006"
        logger.warning(
            f"MessageTooLongError untuk grup {group}: Pesan melebihi batas karakter",
        )
        return truncate_message(message, 4096)
    elif isinstance(error, UnauthorizedError):
        error_code = "E007"
        logger.error("UnauthorizedError: Periksa kredensial autentikasi Anda")
    elif isinstance(error, TimeoutError):
        error_code = "E008"
        if retry_count < MAX_RETRIES:
            logger.warning(
                f"TimeoutError untuk grup {group}: Mencoba lagi dalam "
                f"{RETRY_DELAY} detik (Percobaan {retry_count + 1}/{MAX_RETRIES})",
            )
            await asyncio.sleep(RETRY_DELAY)
            return await handle_sending_error(error, group, message, retry_count + 1)
        logger.error(
            f"TimeoutError untuk grup {group}: "
            "Batas maksimum percobaan tercapai. Melewati.",
        )
        await group_manager.add_to_blacklist(group)
    elif "ChatNotFoundError" in str(error) or "GroupRestrictedError" in str(error):
        error_code = "E009"
        logger.warning(f"Kesalahan akses grup untuk {group}: {error}")
        await group_manager.add_to_blacklist(group)
    else:
        logger.error(f"Kesalahan tak terduga untuk grup {group}: {error}")
        await group_manager.add_to_blacklist(group)

    formatted_error = format_error_message(error_code, str(error))
    logger.error(formatted_error)
    return None


async def handle_scheduler_error(error: Exception) -> None:
    """Menangani kesalahan yang terjadi selama penjadwalan.

    Fungsi ini menangani kesalahan-kesalahan yang mungkin terjadi dalam
    komponen penjadwalan bot. Ini mencakup logging kesalahan dan
    implementasi penanganan khusus jika diperlukan.

    Args:
        error (Exception): Objek kesalahan yang ditangkap dari penjadwal.

    Raises:
        Exception: Jika terjadi kesalahan yang tidak dapat ditangani.
    """
    error_code = "E010"
    formatted_error = format_error_message(error_code, f"Kesalahan penjadwal: {error}")
    logger.error(formatted_error)
    # Implementasikan penanganan khusus untuk kesalahan penjadwal di sini


async def send_critical_error_notification(
    client: TelegramClient,
    error_message: str,
) -> None:
    """Mengirim notifikasi untuk kesalahan kritis ke chat pribadi.

    Fungsi ini mengirim pesan notifikasi ke chat pribadi yang telah dikonfigurasi
    ketika terjadi kesalahan kritis dalam operasi bot. Ini membantu administrator
    untuk segera mengetahui dan menanggapi masalah serius.

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
        except (ConnectionError, TimeoutError) as e:
            logger.error(
                f"Gagal mengirim notifikasi kesalahan ke chat pribadi: {e}",
            )
    else:
        logger.error(
            "ID chat pribadi tidak dikonfigurasi. "
            "Tidak dapat mengirim notifikasi kesalahan.",
        )


__all__ = [
    "handle_sending_error",
    "handle_scheduler_error",
    "send_critical_error_notification",
]
