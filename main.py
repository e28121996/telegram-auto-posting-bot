"""Skrip utama untuk bot auto-posting Telegram.

Modul ini menginisialisasi dan menjalankan bot Telegram untuk auto-posting.
Ini menangani penjadwalan pesan, pengiriman pesan, dan penanganan kesalahan.
Modul ini juga mengatur konfigurasi logging dan mengelola siklus hidup klien Telegram.
"""

from __future__ import annotations

import asyncio
import cProfile
import io
import pstats
import secrets
import time
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from telethon import TelegramClient
from telethon.errors import RPCError

from src.auth import create_client
from src.config import (  # Pastikan untuk mengimpor ini dari modul config Anda
    ConfigError,
)
from src.config import get_config  # Pastikan untuk mengimpor ini dari modul config Anda
from src.database import Database  # Tambahkan import ini
from src.error_handler import send_critical_error_notification
from src.group_manager import group_manager
from src.logger import logger
from src.message_manager import get_message_manager  # Ubah import ini
from src.message_manager import initialize_message_manager
from src.message_sender import send_mass_message
from src.scheduler import scheduler


async def send_scheduled_messages(client: TelegramClient) -> None:
    """Mengirim pesan terjadwal ke grup-grup yang valid."""
    try:
        groups = await group_manager.get_valid_groups()
        message_manager = await get_message_manager()  # Ubah ini
        message = message_manager.get_random_message()
        logger.info(f"Mengirim pesan terjadwal ke {len(groups)} grup")
        start_time = time.time()
        await send_mass_message(client, groups, message)
        end_time = time.time()
        logger.info(
            f"Pesan terjadwal berhasil dikirim. "
            f"Waktu total: {end_time - start_time:.2f}s"
        )
    except (OSError, RPCError, ValueError) as e:
        logger.error(f"Kesalahan dalam send_scheduled_messages: {e}", exc_info=True)


async def setup_client() -> TelegramClient | None:
    """Menyiapkan dan menginisialisasi client Telegram."""
    try:
        client = await create_client()
        db = Database()  # Inisialisasi Database
        await initialize_message_manager(client, db)  # Ubah ini menjadi async
        valid_groups = await group_manager.get_valid_groups()
        logger.info(f"Jumlah grup valid: {len(valid_groups)}")
        logger.debug(f"Daftar grup valid: {valid_groups}")
    except (RPCError, ConnectionError, OSError) as e:
        logger.error(f"Gagal membuat client: {e}", exc_info=True)
        return None
    else:
        logger.info("Bot dimulai")
        return client


async def run_client(client: TelegramClient | None) -> None:
    """Menjalankan client Telegram dan menangani event-event yang terjadi."""
    if not isinstance(client, TelegramClient):
        logger.error(
            "Client bukan instance TelegramClient yang valid, tidak dapat menjalankan"
        )
        return

    try:
        # Menjalankan send_scheduled_messages segera
        logger.info("Memulai pengiriman pesan terjadwal pertama")
        await send_scheduled_messages(client)
        logger.info("Pengiriman pesan terjadwal pertama selesai")

        # Jadwalkan pengiriman pesan berikutnya
        next_run = calculate_next_run()
        logger.info(f"Jadwal pengiriman berikutnya: {next_run}")

        while True:
            now = datetime.now(timezone.utc)
            if now >= next_run:
                await send_scheduled_messages(client)
                next_run = calculate_next_run()
                logger.info(f"Jadwal pengiriman berikutnya: {next_run}")
            await asyncio.sleep(60)  # Cek setiap menit

    except asyncio.CancelledError:
        logger.info("Bot dihentikan oleh pengguna")
    except (RPCError, ConnectionError, OSError) as e:
        error_message = f"Kesalahan tak terduga dalam loop utama: {e}"
        logger.error(error_message, exc_info=True)
        if client.is_connected():
            await send_critical_error_notification(client, error_message)


def calculate_next_run() -> datetime:
    """Menghitung waktu pengiriman berikutnya."""
    min_interval = get_config("min_interval", 1.3)
    max_interval = get_config("max_interval", 1.5)
    interval = secrets.SystemRandom().uniform(
        float(min_interval) if isinstance(min_interval, (int, float)) else 1.3,
        float(max_interval) if isinstance(max_interval, (int, float)) else 1.5,
    )
    return datetime.now(timezone.utc) + timedelta(hours=interval)


async def slow_mode_maintenance() -> None:
    """Melakukan pemeliharaan berkala pada informasi slow mode."""
    while True:
        await group_manager.clean_slow_mode_info()
        stats = await group_manager.get_slow_mode_stats()
        logger.info(f"Statistik slow mode: {stats}")
        await asyncio.sleep(3600)  # Jalankan setiap jam


async def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    try:
        config = get_config("main", {})
        if not config or not isinstance(config, dict):
            error_message = "Konfigurasi utama tidak ditemukan atau tidak valid"
            logger.error(error_message)
            return  # Keluar dari fungsi main tanpa raise

        api_id = config.get("api_id")
        api_hash = config.get("api_hash")
        phone_number = config.get("phone_number")

        if not all([api_id, api_hash, phone_number]):
            error_message = (
                "Konfigurasi tidak lengkap. "
                "Diperlukan api_id, api_hash, dan phone_number."
            )
            logger.error(error_message)
            return  # Keluar dari fungsi main tanpa raise

        client = TelegramClient("user_session", int(api_id or 0), str(api_hash or ""))

        try:
            # Gunakan metode start() dengan nomor telepon
            await client.start(phone=str(phone_number or ""))  # type: ignore[awaitable-type]

            db = Database()
            await initialize_message_manager(client, db)

            group_manager.load_slow_mode_info()
            scheduler_task = asyncio.create_task(scheduler.run())
            client_task = asyncio.create_task(run_client(client))
            slow_mode_task = asyncio.create_task(slow_mode_maintenance())

            await asyncio.gather(scheduler_task, client_task, slow_mode_task)
        finally:
            group_manager.save_slow_mode_info()
            if client.is_connected():
                disconnect_result = client.disconnect()
                if asyncio.iscoroutine(disconnect_result):
                    await disconnect_result
    except ConfigError as e:
        logger.error(f"Kesalahan konfigurasi: {e}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Kesalahan tidak terduga: {e}", exc_info=True)
        return  # Keluar dari fungsi main tanpa raise


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program dihentikan oleh pengguna")
    finally:
        profiler.disable()
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(20)
        logger.debug(f"Hasil profiling:\n{s.getvalue()}")
