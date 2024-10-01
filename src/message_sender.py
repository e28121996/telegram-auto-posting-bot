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
import secrets
import time
from typing import List
from typing import Tuple

from telethon import TelegramClient
from telethon import errors

from src.cache import cache
from src.config import get_config
from src.error_handler import handle_sending_error
from src.group_manager import group_manager
from src.logger import logger
from src.message_manager import get_message_manager  # Tambahkan ini di bagian atas file

# Tambahkan konstanta untuk jeda minimum dan maksimum antar pesan dalam batch
MIN_INTRA_BATCH_DELAY = 1.0  # 1 detik
MAX_INTRA_BATCH_DELAY = 3.0  # 3 detik


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
    available = []
    skipped = 0
    for group in groups:
        if await group_manager.is_in_blacklist(group) or await is_group_in_slow_mode(
            group
        ):
            skipped += 1
        else:
            available.append(group)
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
    _: str,
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

    batch_size = 4  # Bisa disesuaikan berdasarkan performa
    total_batches = (len(available_groups) - 1) // batch_size + 1
    message_manager = await get_message_manager()  # Tambahkan ini
    for i in range(0, len(available_groups), batch_size):
        batch = available_groups[i : i + batch_size]
        current_batch = i // batch_size + 1
        logger.info(f"Mengirim pesan ke batch {current_batch} dari {total_batches}")
        tasks = [
            send_message(client, group, message_manager.get_random_message())
            for group in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(
            1 for result in results if not isinstance(result, Exception)
        )
        logger.info(
            f"Batch {current_batch} selesai. " f"Berhasil: {success_count}/{len(batch)}"
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

    Fungsi ini mengambil nilai konfigurasi dari fungsi get_config dan
    mengonversinya menjadi float. Jika nilai tidak dapat dikonversi,
    nilai default akan dikembalikan.

    Args:
        key (str): Kunci konfigurasi yang ingin diambil.
        default (float): Nilai default yang akan dikembalikan jika konfigurasi
                         tidak ditemukan atau tidak dapat dikonversi ke float.

    Returns:
        float: Nilai konfigurasi yang dikonversi ke float atau nilai default.
    """
    value = get_config(key, default)
    return float(value) if isinstance(value, (int, float, str)) else default
