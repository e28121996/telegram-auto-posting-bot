"""Modul autentikasi untuk bot auto-posting Telegram."""

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from src.config import config
from src.logger import logger


async def create_client() -> TelegramClient:
    """
    Membuat dan mengautentikasi klien Telegram.

    Returns:
        TelegramClient: Klien Telegram yang telah diautentikasi.

    Raises:
        Exception: Jika autentikasi gagal.
    """
    client = TelegramClient("session", config.api_id, config.api_hash)

    try:
        await client.connect()
        logger.info(
            f"Menghubungkan API ID: {config.api_id}, No. Telepon: {config.phone_number}"
        )

        if not await client.is_user_authorized():
            logger.info("Pengguna belum diotorisasi. Mengirim permintaan kode...")
            sent = await client.send_code_request(config.phone_number)
            logger.info(f"Permintaan kode terkirim: {sent}")
            code = input("Masukkan kode yang Anda terima: ")
            try:
                logger.info("Mencoba untuk masuk...")
                await client.sign_in(config.phone_number, code)
            except SessionPasswordNeededError:
                # Verifikasi dua langkah diaktifkan
                password = input(
                    "Verifikasi dua langkah diaktifkan. Masukkan kata sandi Anda: "
                )
                await client.sign_in(password=password)

        logger.info("Berhasil diautentikasi dengan Telegram")
        return client
    except Exception as e:
        logger.error(f"Autentikasi gagal: {e}")
        raise  # Melempar kembali exception untuk penanganan di tingkat yg lebih tinggi
