"""Fungsi-fungsi utilitas untuk bot auto-posting Telegram."""


def truncate_message(pesan: str, panjang_maksimum: int) -> str:
    """
    Memotong pesan ke panjang maksimum yang ditentukan.

    Args:
        pesan (str): Pesan yang akan dipotong.
        panjang_maksimum (int): Panjang maksimum pesan yang diinginkan.

    Returns:
        str: Pesan yang telah dipotong jika melebihi panjang maksimum,
             atau pesan asli jika tidak melebihi panjang maksimum.
    """
    if len(pesan) <= panjang_maksimum:
        return pesan
    # Potong pesan dan tambahkan elipsis
    return pesan[: panjang_maksimum - 3] + "..."


# Tambahkan fungsi utilitas lainnya sesuai kebutuhan
