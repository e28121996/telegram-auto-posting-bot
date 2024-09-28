"""Modul konfigurasi untuk bot auto-posting Telegram."""

import os
from typing import Any, Dict

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Kelas Settings untuk menyimpan nilai-nilai konfigurasi."""

    api_id: int = Field(..., description="ID API Telegram")
    api_hash: str = Field(..., description="Hash API Telegram")
    phone_number: str = Field(..., description="Nomor telepon untuk akun Telegram")
    personal_chat_id: str = Field(..., description="ID chat pribadi untuk notifikasi")

    class Config:
        """Konfigurasi untuk kelas Settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"


def load_yaml_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Memuat konfigurasi dari file YAML.

    Args:
        file_path (str): Path ke file YAML. Default adalah "config.yaml".

    Returns:
        Dict[str, Any]: Dictionary berisi konfigurasi yang dimuat dari file YAML.

    Raises:
        FileNotFoundError: Jika file YAML tidak ditemukan.
        yaml.YAMLError: Jika terjadi kesalahan saat parsing file YAML.
    """
    with open(file_path, encoding="utf-8") as file:
        return yaml.safe_load(file)


# Inisialisasi objek config dengan nilai-nilai dari variabel lingkungan
config = Settings(
    api_id=int(os.getenv("API_ID", "0")),  # Konversi ke int, default 0 jika tidak ada
    api_hash=os.getenv("API_HASH", ""),  # Default string kosong jika tidak ada
    phone_number=os.getenv("PHONE_NUMBER", ""),
    personal_chat_id=os.getenv("PERSONAL_CHAT_ID", ""),
)

# Memuat konfigurasi dari file YAML
yaml_config = load_yaml_config()
