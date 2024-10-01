"""Modul konfigurasi untuk bot auto-posting Telegram.

Modul ini menangani pengaturan konfigurasi dari file .env dan YAML,
serta menyediakan fungsi untuk mengakses nilai-nilai konfigurasi.
Ini mencakup kelas Settings untuk menyimpan konfigurasi utama,
fungsi untuk memuat konfigurasi YAML, dan fungsi utilitas untuk
mengakses nilai konfigurasi.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from typing import Optional
from typing import TypeVar
from typing import Union

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

T = TypeVar("T")


class Settings(BaseSettings):
    """Kelas Settings untuk menyimpan nilai-nilai konfigurasi utama.

    Kelas ini menggunakan Pydantic untuk validasi dan pengaturan
    nilai-nilai konfigurasi yang diambil dari variabel lingkungan
    atau file .env.

    Attributes:
        api_id (int): ID API Telegram untuk autentikasi.
        api_hash (str): Hash API Telegram untuk autentikasi.
        phone_number (str): Nomor telepon yang terkait dengan akun Telegram.
        personal_chat_id (str): ID chat pribadi untuk menerima notifikasi.
    """

    api_id: int = Field(..., description="ID API Telegram")
    api_hash: str = Field(..., description="Hash API Telegram")
    phone_number: str = Field(..., description="Nomor telepon untuk akun Telegram")
    personal_chat_id: str = Field(..., description="ID chat pribadi untuk notifikasi")

    class Config:
        """Konfigurasi untuk kelas Settings.

        Menentukan file .env dan encoding yang digunakan.
        """

        env_file = ".env"
        env_file_encoding = "utf-8"


class ConfigError(Exception):
    """Exception yang dilempar ketika ada masalah dengan konfigurasi."""


def load_yaml_config(file_path: str = "config.yaml") -> dict[str, Any]:
    """Memuat konfigurasi dari file YAML.

    Fungsi ini membaca dan memparse file YAML yang berisi
    konfigurasi tambahan untuk aplikasi.

    Args:
        file_path (str): Path ke file YAML. Default adalah "config.yaml".

    Returns:
        dict[str, Any]: Dictionary berisi konfigurasi yang dimuat dari file YAML.

    Raises:
        FileNotFoundError: Jika file YAML tidak ditemukan.
        yaml.YAMLError: Jika terjadi kesalahan saat parsing file YAML.
    """
    with Path(file_path).open(encoding="utf-8") as file:
        return yaml.safe_load(file)


config = Settings(
    api_id=int(os.getenv("API_ID", "0")),
    api_hash=os.getenv("API_HASH", ""),
    phone_number=os.getenv("PHONE_NUMBER", ""),
    personal_chat_id=os.getenv("PERSONAL_CHAT_ID", ""),
)


yaml_config = load_yaml_config()


def get_config(
    key: str, default: Optional[Union[int, float, str, list, dict]] = None
) -> Union[int, float, str, list, dict, None]:
    """Mengambil nilai konfigurasi berdasarkan kunci yang diberikan."""
    if key == "main":
        return {
            "api_id": config.api_id,
            "api_hash": config.api_hash,
            "phone_number": config.phone_number,
            "personal_chat_id": config.personal_chat_id,
        }

    keys = key.split(".")
    value = yaml_config
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
    return value if value is not None else default


# ... (kode selanjutnya tidak berubah)
