"""Cache module for the Telegram auto-posting bot."""

import time
from typing import Dict, Generic, TypeVar, Union

T = TypeVar("T")


class Cache(Generic[T]):
    """A simple cache implementation with expiration."""

    def __init__(self) -> None:
        """Initialize the cache."""
        self.cache: Dict[str, Dict[str, Union[T, float]]] = {}

    def set(self, key: str, value: T, expiry: int = 3600) -> None:
        """Set a value in the cache with an expiration time."""
        self.cache[key] = {"value": value, "expiry": time.time() + expiry}

    def get(self, key: str) -> Union[T, None]:
        """Get a value from the cache if it exists and hasn't expired."""
        if key in self.cache:
            cache_item = self.cache[key]
            if (
                isinstance(cache_item["expiry"], float)
                and time.time() < cache_item["expiry"]
            ):
                return cache_item["value"]  # type: ignore
            else:
                del self.cache[key]
        return None

    def clear_expired(self) -> None:
        """Remove all expired entries from the cache."""
        current_time = time.time()
        self.cache = {
            k: v
            for k, v in self.cache.items()
            if isinstance(v["expiry"], float) and v["expiry"] > current_time
        }


cache: Cache[Union[str, list]] = Cache()
