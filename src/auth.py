"""Modul autentikasi untuk bot auto-posting Telegram.

Modul ini menyediakan fungsi untuk membuat dan mengautentikasi klien Telegram
yang digunakan oleh bot auto-posting.
"""

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from src.config import config
from src.logger import logger


async def create_client() -> TelegramClient:
    """Membuat dan mengautentikasi klien Telegram.

    Fungsi ini membuat instance TelegramClient, menghubungkannya ke server Telegram,
    dan melakukan proses autentikasi jika diperlukan. Jika verifikasi dua langkah
    diaktifkan, fungsi ini akan meminta input kata sandi dari pengguna.

    Returns:
        TelegramClient: Klien Telegram yang telah diautentikasi dan siap digunakan.

    Raises:
        Exception: Jika terjadi kesalahan selama proses koneksi atau autentikasi.
    """
    client = TelegramClient("session", config.api_id, config.api_hash)

    try:
        await client.connect()
        logger.info(
            f"Menghubungkan API ID: {config.api_id}, "
            f"No. Telepon: {config.phone_number}",
        )

        if not await client.is_user_authorized():
            logger.info("Pengguna belum diautentikasi. Mengirim permintaan kode...")
            sent = await client.send_code_request(config.phone_number)
            logger.info(f"Permintaan kode terkirim: {sent}")
            code = input("Masukkan kode yang Anda terima: ")
            try:
                logger.info("Mencoba untuk masuk...")
                await client.sign_in(config.phone_number, code)
            except SessionPasswordNeededError:
                password = input(
                    "Verifikasi dua langkah diaktifkan. Masukkan kata sandi Anda: ",
                )
                await client.sign_in(password=password)
        else:
            logger.info("Pengguna sudah diautentikasi")

        logger.info("Berhasil terhubung dengan Telegram")
    except Exception as e:
        logger.error(f"Autentikasi gagal: {e}")
        raise
    else:
        return client
