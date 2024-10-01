"""Modul utilitas untuk bot auto-posting Telegram.

Modul ini berisi fungsi-fungsi utilitas yang digunakan di seluruh aplikasi
untuk membantu dalam pemrosesan dan manipulasi data.

Fungsi:
    truncate_message: Memotong pesan ke panjang maksimum yang ditentukan.
"""

from datetime import datetime  # Tambahkan timedelta di sini
from datetime import timedelta  # Tambahkan timedelta di sini
from datetime import timezone  # Tambahkan timedelta di sini


def truncate_message(pesan: str, panjang_maksimum: int) -> str:
    """Memotong pesan ke panjang maksimum yang ditentukan.

    Fungsi ini memeriksa panjang pesan dan memotongnya jika melebihi
    panjang maksimum yang ditentukan. Jika pesan dipotong, tiga titik ("...")
    ditambahkan di akhir untuk menunjukkan bahwa pesan telah dipotong.

    Args:
        pesan (str): Pesan yang akan dipotong.
        panjang_maksimum (int): Panjang maksimum pesan yang diinginkan.

    Returns:
        str: Pesan yang telah dipotong jika melebihi panjang maksimum,
             atau pesan asli jika tidak melebihi panjang maksimum.

    Example:
        >>> truncate_message("Ini adalah pesan panjang", 10)
        'Ini ada...'
        >>> truncate_message("Pesan pendek", 20)
        'Pesan pendek'
    """
    if len(pesan) <= panjang_maksimum:
        return pesan
    return pesan[: panjang_maksimum - 3] + "..."


def get_current_utc_time() -> datetime:
    """Mendapatkan waktu UTC saat ini."""
    return datetime.now(timezone.utc)


def format_utc_time(dt: datetime) -> str:
    """Memformat waktu UTC ke string ISO 8601."""
    return dt.isoformat()


def parse_utc_time(time_str: str) -> datetime:
    """Mengurai string waktu ISO 8601 ke objek datetime UTC."""
    return datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc)


def calculate_next_run(hours: float) -> datetime:
    """Menghitung waktu pengiriman berikutnya dalam UTC."""
    return get_current_utc_time() + timedelta(hours=hours)


# Tambahkan fungsi utilitas lainnya sesuai kebutuhan
