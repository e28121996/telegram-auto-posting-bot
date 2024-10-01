"""Modul untuk memuat konfigurasi dari file YAML."""

import logging
from pathlib import Path

import yaml

# Buat logger untuk modul ini
logger = logging.getLogger(__name__)


def load_yaml_config(file_path: str = "config.yaml") -> dict:
    """Memuat konfigurasi dari file YAML."""
    try:
        with Path(file_path).open(encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except (OSError, yaml.YAMLError):
        logger.exception("Error loading config")
        return {}
    else:
        logger.info("Konfigurasi berhasil dimuat dari %s", file_path)
        return config


config = load_yaml_config()
