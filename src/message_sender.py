"""Modul pengiriman pesan untuk bot auto-posting Telegram."""

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
    """
    Mengirim pesan ke grup tertentu.

    Args:
        client (TelegramClient): Klien Telegram yang digunakan untuk mengirim pesan.
        group (str): Nama atau ID grup tujuan.
        message (str): Pesan yang akan dikirim.

    Raises:
        Exception: Jika terjadi kesalahan saat mengirim pesan.
    """
    logger.info(f"Bersiap mengirim pesan ke {group}. Panjang pesan: {len(message)}")
    start_time = time.time()
    try:
        result = await client.send_message(group, message)
        end_time = time.time()
        logger.info(
            f"Pesan terkirim ke {group}. Waktu: {end_time - start_time:.2f}s. "
            f"ID Pesan: {result.id}"
        )
    except Exception as e:
        logger.error(f"Kesalahan saat mengirim pesan ke {group}", exc_info=True)
        await handle_sending_error(e, group, message)

    # Menerapkan jeda acak sebelum pesan berikutnya
    delay = random.uniform(yaml_config["min_delay"], yaml_config["max_delay"])  # noqa: S311
    logger.debug(f"Menerapkan jeda selama {delay:.2f}s sebelum pesan berikutnya")
    await asyncio.sleep(delay)


async def send_mass_message(
    client: TelegramClient, groups: List[str], message: str
) -> None:
    """
    Mengirim pesan ke beberapa grup.

    Args:
        client (TelegramClient): Klien Telegram yang digunakan untuk mengirim pesan.
        groups (List[str]): Daftar grup tujuan.
        message (str): Pesan awal yang akan dikirim (akan diganti untuk setiap grup).
    """
    for group in groups:
        # Mendapatkan pesan acak baru untuk setiap grup
        message = message_manager.get_random_message()
        await send_message(client, group, message)
        # Jeda tambahan antara pengiriman ke grup-grup
        await asyncio.sleep(random.uniform(5, 10))  # noqa: S311
