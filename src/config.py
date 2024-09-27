"""Configuration module for the Telegram auto-posting bot."""

import os
from typing import Any, Dict

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings class for storing configuration values."""

    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., description="Telegram API Hash")
    phone_number: str = Field(..., description="Phone number for Telegram account")
    personal_chat_id: str = Field(..., description="Personal chat ID for notifications")

    class Config:
        """Configuration for the Settings class."""

        env_file = ".env"
        env_file_encoding = "utf-8"


def load_yaml_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(file_path, encoding="utf-8") as file:
        return yaml.safe_load(file)


config = Settings(
    api_id=int(os.getenv("API_ID", "0")),
    api_hash=os.getenv("API_HASH", ""),
    phone_number=os.getenv("PHONE_NUMBER", ""),
    personal_chat_id=os.getenv("PERSONAL_CHAT_ID", ""),
)
yaml_config = load_yaml_config()
