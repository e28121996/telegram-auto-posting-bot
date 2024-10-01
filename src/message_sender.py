"""Modul pengiriman pesan untuk bot auto-posting Telegram.

Modul ini menyediakan fungsi-fungsi untuk mengirim pesan ke grup Telegram
secara otomatis. Ini mencakup pengiriman pesan tunggal ke grup tertentu
dan pengiriman massal ke beberapa grup.

Fungsi utama:
- send_message: Mengirim pesan ke satu grup Telegram.
- send_mass_message: Mengirim pesan ke beberapa grup Telegram.

Modul ini juga menangani penundaan pengiriman, penanganan kesalahan,
dan logging aktivitas pengiriman pesan.
"""

import asyncio
import secrets  # Ganti random dengan secrets
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypedDict
from typing import Union
from typing import cast

from telethon import TelegramClient
from telethon import errors

from src.cache import cache
from src.config import get_config_value
from src.error_handler import handle_sending_error
from src.group_manager import group_manager
from src.logger import logger
from src.message_manager import get_message_manager  # Tambahkan ini di bagian atas file


class ConfigDict(TypedDict):
    """Struktur konfigurasi untuk pengiriman pesan."""

    message_sending: Dict[str, Any]


config = get_config_value()
logger.debug(f"Config returned: {config}")

if not config:
    error_message = "Konfigurasi kosong atau tidak valid"
    logger.error(error_message)
    raise ValueError(error_message)

message_sending_config = config.get("message_sending", {})
if not isinstance(message_sending_config, dict):
    error_message = "Konfigurasi message_sending harus berupa dictionary"
    logger.error(error_message)
    raise TypeError(error_message)

# Ganti konstanta ini dengan nilai dari konfigurasi
MIN_INTRA_BATCH_DELAY = message_sending_config.get("min_intra_batch_delay", 1.0)
MAX_INTRA_BATCH_DELAY = message_sending_config.get("max_intra_batch_delay", 3.0)
BATCH_SIZE = message_sending_config.get("batch_size", 4)
MIN_INTER_BATCH_DELAY = message_sending_config.get("min_inter_batch_delay", 20)
MAX_INTER_BATCH_DELAY = message_sending_config.get("max_inter_batch_delay", 30)
DEFAULT_MAX_LENGTH = message_sending_config.get("default_max_length", 4096)


async def is_group_in_slow_mode(group: str) -> bool:
    """Memeriksa apakah grup dalam mode slow."""
    slow_mode_info = cache.get(f"slow_mode_{group}")
    if isinstance(slow_mode_info, str):
        try:
            expiry_time = int(slow_mode_info)
            return time.time() < expiry_time
        except ValueError:
            return False
    return False


async def update_slow_mode_info(group: str, wait_seconds: int) -> None:
    """Memperbarui informasi slow mode untuk grup tertentu."""
    expiry_time = int(time.time() + wait_seconds)
    cache.set_value(f"slow_mode_{group}", str(expiry_time), expiry=wait_seconds)


async def get_available_groups(groups: List[str]) -> Tuple[List[str], int]:
    """Mendapatkan daftar grup yang tersedia untuk pengiriman pesan."""
    available = [
        group
        for group in groups
        if not (
            await group_manager.is_in_blacklist(group)
            or await is_group_in_slow_mode(group)
        )
    ]
    skipped = len(groups) - len(available)
    return available, skipped


async def send_message(client: TelegramClient, group: str, message: str) -> None:
    """Mengirim pesan ke grup Telegram tertentu."""
    if await group_manager.is_in_slow_mode(group):
        logger.info(f"Melewati {group} karena masih dalam waktu tunggu slow mode")
        return

    try:
        logger.info(f"Bersiap mengirim pesan ke {group}. Panjang pesan: {len(message)}")
        start_time = time.time()
        result = await client.send_message(group, message)
        end_time = time.time()
        logger.info(
            f"Pesan terkirim ke {group}. Waktu: {end_time - start_time:.2f}s. "
            f"ID Pesan: {result.id}"
        )
    except errors.SlowModeWaitError as e:
        logger.warning(f"SlowModeWaitError untuk {group}: {e}")
        await group_manager.update_slow_mode_info(group, e.seconds)
    except (errors.RPCError, ValueError) as e:
        logger.error(
            f"Kesalahan saat mengirim pesan ke {group}: {e!s}",
            exc_info=True,
        )
        await handle_sending_error(e, group, message)

    # Tambahkan jeda konsisten setelah setiap pengiriman pesan
    intra_batch_delay = (
        MIN_INTRA_BATCH_DELAY
        + (MAX_INTRA_BATCH_DELAY - MIN_INTRA_BATCH_DELAY)
        * secrets.randbelow(1000)
        / 1000
    )
    logger.info(
        f"Menerapkan jeda {intra_batch_delay:.2f}s sebelum pesan berikutnya dalam batch"
    )
    await asyncio.sleep(intra_batch_delay)


async def send_mass_message(
    client: TelegramClient,
    groups: List[str],
    message: str,
) -> None:
    """Mengirim pesan ke beberapa grup Telegram."""
    available_groups, skipped_groups = await get_available_groups(groups)
    logger.info(
        f"Total grup: {len(groups)}, Tersedia: {len(available_groups)}, "
        f"Dilewati: {skipped_groups}"
    )

    for group in groups:
        if await group_manager.is_in_blacklist(group):
            logger.info(f"Melewati {group}: Grup dalam daftar hitam")
        elif await group_manager.is_in_slow_mode(group):
            logger.info(f"Melewati {group}: Grup dalam mode lambat")
            logger.info(f"Melewati {group}: Grup dalam mode lambat")
    batch_size = BATCH_SIZE  # Bisa disesuaikan berdasarkan performa
    total_batches = (len(available_groups) - 1) // batch_size + 1
    message_manager = await get_message_manager()  # Tambahkan ini
    for i in range(0, len(available_groups), batch_size):
        batch = available_groups[i : i + batch_size]
        current_batch = i // batch_size + 1
        logger.info(f"Mengirim pesan ke batch {current_batch} dari {total_batches}")
        tasks = []
        for group in batch:
            if message_manager:
                tasks.append(
                    send_message(client, group, message_manager.get_random_message())
                )
            else:
                logger.warning(
                    f"MessageManager tidak tersedia untuk grup {group}. "
                    "Menggunakan pesan default."
                )
                tasks.append(send_message(client, group, message))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(
            1 for result in results if not isinstance(result, Exception)
        )
        logger.info(
            f"Batch {current_batch} selesai. Berhasil: {success_count}/{len(batch)}"
        )

        batch_delay = secrets.randbelow(11) + 20  # 20-30 detik
        logger.info(f"Menerapkan jeda {batch_delay:.2f}s sebelum batch berikutnya")
        await asyncio.sleep(batch_delay)

    logger.info(
        f"Pengiriman pesan selesai. Total terkirim: {len(available_groups)}, "
        f"Dilewati: {skipped_groups}"
    )


def get_float_config(key: str, default: float) -> float:
    """Mengambil nilai konfigurasi float berdasarkan kunci yang diberikan.

    Args:
        key (str): Kunci konfigurasi yang akan diambil nilainya.
        default (float): Nilai default yang akan dikembalikan jika kunci tidak
            ditemukan.

    Returns:
        float: Nilai konfigurasi yang sesuai dengan kunci, atau nilai default jika
            tidak ditemukan.
    """
    value: Optional[Any] = get_config_value(key)
    if value is None:
        return default
    try:
        return float(cast(Union[float, str], value))
    except ValueError:
        return default
