"""Skrip utama untuk bot auto-posting Telegram."""

import inspect
from typing import Optional

import asyncio
from telethon import TelegramClient

from src.auth import create_client
from src.error_handler import send_critical_error_notification
from src.group_manager import group_manager
from src.logger import logger
from src.message_manager import message_manager
from src.message_sender import send_mass_message
from src.scheduler import scheduler


async def send_scheduled_messages(client: TelegramClient) -> None:
    """
    Mengirim pesan terjadwal ke grup-grup yang valid.

    Args:
        client (TelegramClient): Klien Telegram yang digunakan untuk mengirim pesan.

    Raises:
        Exception: Jika terjadi kesalahan saat mengirim pesan.
    """
    try:
        groups = group_manager.get_valid_groups()
        message = message_manager.get_random_message()
        await send_mass_message(client, groups, message)
    except Exception as e:
        logger.error(f"Kesalahan dalam send_scheduled_messages: {e}")


async def main() -> None:
    """
    Menjalankan loop utama bot.

    Raises:
        KeyboardInterrupt: Jika bot dihentikan oleh pengguna.
        Exception: Jika terjadi kesalahan tak terduga dalam loop utama.
    """
    client: Optional[TelegramClient] = None
    try:
        client = await create_client()
        logger.info("Bot dimulai")

        # Menambahkan tugas pengiriman pesan terjadwal ke scheduler
        scheduler.add_task(lambda: send_scheduled_messages(client))

        # Menjalankan scheduler
        await scheduler.run()
    except asyncio.CancelledError:
        logger.info("Bot dihentikan oleh pengguna")
    except Exception as e:
        error_message = f"Kesalahan tak terduga dalam loop utama: {e}"
        logger.error(error_message)
        if client:
            await send_critical_error_notification(client, error_message)
    finally:
        if client:
            try:
                if client.is_connected():
                    disconnect_method = client.disconnect()
                    if inspect.isawaitable(disconnect_method):
                        await disconnect_method
                    logger.info("Client terputus")
            except Exception as e:
                logger.error(f"Kesalahan saat memutuskan koneksi client: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program dihentikan oleh pengguna")
