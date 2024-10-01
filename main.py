"""Skrip utama untuk bot auto-posting Telegram."""

from __future__ import annotations

import asyncio
import os
import secrets
import signal
from contextlib import suppress
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from getpass import getpass
from typing import Any
from typing import Dict
from typing import NoReturn
from typing import Optional
from typing import TypedDict

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import RPCError
from telethon.errors import SessionPasswordNeededError

from src.auth import create_client
from src.config import get_config_value
from src.database import Database
from src.error_handler import send_critical_error_notification
from src.exceptions import ConfigurationError
from src.group_manager import GroupManager  # Tambahkan impor ini
from src.logger import logger
from src.message_manager import MessageManagerError
from src.message_manager import get_message_manager
from src.message_manager import initialize_message_manager
from src.message_sender import send_mass_message
from src.scheduler import scheduler

load_dotenv()

# Inisialisasi group_manager sebagai variabel global
group_manager = GroupManager()


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Mengambil nilai dari variabel lingkungan."""
    value = os.getenv(key, default)
    if value is None:
        logger.error(f"Variabel lingkungan {key} tidak ditemukan")
    return value


class ConfigDict(TypedDict):
    """Struktur konfigurasi untuk bot Telegram."""

    telegram: Dict[str, Any]


def raise_config_error(message: str) -> NoReturn:
    """Raise a ValueError with the given message."""
    logger.error(message)
    raise ValueError(message)


def validate_config(config: Optional[Dict[str, Any]]) -> None:
    """Memvalidasi konfigurasi bot."""
    if not isinstance(config, dict):
        config_error = "Konfigurasi harus berupa dictionary"
        raise TypeError(config_error)

    telegram_config = config.get("telegram")
    if not isinstance(telegram_config, dict):
        telegram_config_error = "Konfigurasi telegram harus berupa dictionary"
        raise TypeError(telegram_config_error)


def get_safe_config() -> Dict[str, Any]:
    """Mendapatkan konfigurasi yang aman untuk digunakan."""
    config = get_config_value()
    if not isinstance(config, dict):
        error_message = "Konfigurasi yang dikembalikan bukan dictionary"
        logger.error(error_message)
        raise TypeError(error_message)

    required_keys = ["API_ID", "API_HASH", "PHONE_NUMBER"]
    missing_keys = [key for key in required_keys if not config.get(key)]

    if missing_keys:
        error_message = (
            f"Kunci konfigurasi berikut tidak tersedia: {', '.join(missing_keys)}"
        )
        logger.error(error_message)
        raise ValueError(error_message)

    return config


async def send_scheduled_messages(client: TelegramClient) -> None:
    """Mengirim pesan terjadwal ke grup-grup."""
    message_manager = await get_message_manager()
    if message_manager is None:
        logger.error("MessageManager tidak tersedia. Tidak dapat mengirim pesan.")
        return

    groups = await group_manager.get_valid_groups()
    if not groups:
        logger.warning("Tidak ada grup valid untuk mengirim pesan.")
        return

    try:
        message = message_manager.get_random_message()
        await send_mass_message(client, groups, message)
    except (MessageManagerError, RPCError, ConnectionError) as e:
        logger.exception(f"Terjadi kesalahan saat mengirim pesan terjadwal: {e}")


async def setup_client() -> TelegramClient | None:
    """Menyiapkan dan menginisialisasi client Telegram."""
    try:
        client = await create_client()
        db = Database()
        await initialize_message_manager(client, db)
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
        return
    try:
        logger.info("Memulai pengiriman pesan terjadwal pertama")
        await send_scheduled_messages(client)
        logger.info("Pengiriman pesan terjadwal pertama selesai")
        logger.info("Pengiriman pesan terjadwal pertama selesai")
        next_run = calculate_next_run()
        logger.info(f"Jadwal pengiriman berikutnya: {next_run}")
        logger.info(f"Jadwal pengiriman berikutnya: {next_run}")
        while True:
            now = datetime.now(timezone.utc)
            if now >= next_run:
                await send_scheduled_messages(client)
                next_run = calculate_next_run()
                logger.info(f"Jadwal pengiriman berikutnya: {next_run}")
            await asyncio.sleep(60)
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logger.info("Bot dihentikan oleh pengguna")
    except (RPCError, ConnectionError, OSError) as e:
        error_message = f"Kesalahan tak terduga dalam loop utama: {e}"
        logger.error(error_message, exc_info=True)
        if client.is_connected():
            await send_critical_error_notification(client, error_message)


def calculate_next_run() -> datetime:
    """Menghitung waktu pengiriman berikutnya."""
    config = get_safe_config()
    min_interval = config.get("scheduling.min_interval") or 1.3
    max_interval = config.get("scheduling.max_interval") or 1.5
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


async def connect_client(client: TelegramClient, phone_number: str) -> None:
    """Menghubungkan client ke Telegram dan melakukan otentikasi jika diperlukan."""
    await client.connect()
    if await client.is_user_authorized():
        logger.info("Client berhasil terhubung")
    else:
        await client.send_code_request(phone=phone_number)
        code = input("Masukkan kode: ")
        try:
            await client.sign_in(phone=phone_number, code=code)
        except SessionPasswordNeededError:
            password = getpass("Two-step verification diaktifkan. Masukkan password: ")
            await client.sign_in(password=password)
        logger.info("Client berhasil terhubung")


async def disconnect_client(client: TelegramClient) -> None:
    """Memutuskan koneksi client dari Telegram."""
    if client.is_connected():
        try:
            disconnect_result = client.disconnect()
            if disconnect_result is not None:
                await disconnect_result
        except RPCError as e:
            logger.error(f"Error saat memutuskan koneksi: {e}")
        logger.info("Client terputus")


async def main() -> None:
    """Fungsi utama untuk menjalankan bot Telegram."""
    client = None
    try:
        config: Dict[str, Any] = get_safe_config()
        logger.info("Konfigurasi berhasil dimuat")
        logger.debug(f"Config: {config}")

        # Log direktori data
        data_dir = config.get("directories", {}).get("data")
        logger.info(f"Direktori data dari konfigurasi: {data_dir}")

        if not all(
            [config.get("API_ID"), config.get("API_HASH"), config.get("PHONE_NUMBER")]
        ):
            raise_config_error("API_ID, API_HASH, dan PHONE_NUMBER harus diisi")

        client = await create_client()
        await connect_client(client, config["PHONE_NUMBER"])

        # Inisialisasi database dan group manager
        db = Database()
        try:
            await group_manager.initialize(client, db)
            await initialize_message_manager(client, db)
        except ConfigurationError as e:
            logger.error(f"Kesalahan konfigurasi: {e}")
            return
        except MessageManagerError as e:
            logger.warning(f"MessageManager: {e}")
            # Lanjutkan eksekusi meskipun MessageManager sudah diinisialisasi

        # Tambahkan logika utama aplikasi di sini
        stop_event = asyncio.Event()

        def signal_handler() -> None:
            logger.info("Menerima sinyal penghentian. Menghentikan aplikasi...")
            stop_event.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        async def main_loop() -> None:
            while not stop_event.is_set():
                await send_scheduled_messages(client)
                next_run = (
                    scheduler.get_next_run_time()
                )  # Menggunakan metode yang benar
                logger.info(f"Jadwal pengiriman berikutnya: {next_run}")
                with suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(
                        stop_event.wait(), timeout=scheduler.get_interval()
                    )  # Menggunakan metode yang benar

        await main_loop()

    except (ValueError, RPCError, ConfigurationError) as e:
        logger.exception(f"Terjadi kesalahan: {e!s}")
    finally:
        if client:
            await disconnect_client(client)
        logger.info("Aplikasi dihentikan.")


if __name__ == "__main__":
    asyncio.run(main())
