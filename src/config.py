"""Modul konfigurasi untuk bot auto-posting Telegram."""

from __future__ import annotations

import os
from typing import Any
from typing import Dict
from typing import Union

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

from src.config_loader import config as yaml_config
from src.logger import logger

load_dotenv()


class Settings(BaseSettings):
    """Kelas Settings untuk menyimpan nilai-nilai konfigurasi utama."""

    api_id: int = Field(..., description="ID API Telegram")
    api_hash: str = Field(..., description="Hash API Telegram")
    phone_number: str = Field(..., description="Nomor telepon untuk akun Telegram")
    personal_chat_id: str = Field(..., description="ID chat pribadi untuk notifikasi")

    class Config:
        """Konfigurasi untuk kelas Settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings(
    api_id=int(os.environ.get("API_ID", "0")),
    api_hash=os.environ.get("API_HASH", ""),
    phone_number=os.environ.get("PHONE_NUMBER", ""),
    personal_chat_id=os.environ.get("PERSONAL_CHAT_ID", ""),
)


# ruff: noqa: ANN401
def get_config_value(key: str = "") -> Union[Dict[str, Any], Any, None]:
    """Mengambil nilai konfigurasi berdasarkan kunci."""
    config = {
        "API_ID": os.getenv("API_ID"),
        "API_HASH": os.getenv("API_HASH"),
        "PHONE_NUMBER": os.getenv("PHONE_NUMBER"),
        "directories": {
            "data": os.getenv("DATA_DIRECTORY", "./data")  # Tambahkan ini
        },
    }

    # Tambahkan logging untuk debug
    logger.debug(f"Loaded config: {config}")

    # Gabungkan dengan konfigurasi dari YAML jika ada
    if yaml_config:
        config.update(yaml_config)
    else:
        logger.warning("YAML config tidak tersedia")

    return config.get(key) if key else config


# Hapus fungsi get_config() dan load_config() yang tidak digunakan
