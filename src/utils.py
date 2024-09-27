"""Utility functions for the Telegram auto-posting bot."""


def truncate_message(message: str, max_length: int) -> str:
    """Truncate message to a maximum length."""
    if len(message) <= max_length:
        return message
    return message[: max_length - 3] + "..."


# Add more utility functions as needed
