"""LRU Cache for URL lookups - Module for caching URL mappings in memory"""

from datetime import datetime
from threading import Lock
from typing import Dict, Optional

from cachetools import LRUCache


class URLCache:
    """Thread-safe LRU cache for URL lookups.

    This cache reduces database queries for frequently accessed codes by maintaining
    an in-memory cache of URL mappings with LRU eviction policy.
    """

    def __init__(self, max_size: int = 1000):
        """Initialize the cache.

        Args:
            max_size: Maximum number of entries in the cache.
        """
        self.cache: LRUCache = LRUCache(maxsize=max_size)
        self.lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[str]:
        """Get value from cache, recording hit/miss.

        Args:
            key: The short code.

        Returns:
            The original URL if found, None otherwise.
        """
        with self.lock:
            if key in self.cache:
                self.hits += 1
                return self.cache[key]
            else:
                self.misses += 1
                return None

    def set(self, key: str, value: Optional[str]) -> None:
        """Set value in cache, evicting LRU entry if necessary.

        Args:
            key: The short code.
            value: The original URL (or None if not found).
        """
        with self.lock:
            self.cache[key] = value


    def invalidate(self, key: str) -> None:
        """Remove specific key from cache.

        Args:
            key: The short code to invalidate.
        """
        with self.lock:
            self.cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict:
        """Get cache statistics.

        Returns:
            Dictionary containing cache stats including size, hit rate, etc.
        """
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            return {
                "size": len(self.cache),
                "max_size": self.cache.maxsize,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "timestamp": datetime.now().isoformat(),
            }

    def size(self) -> int:
        """Get current cache size.

        Returns:
            Number of entries currently in the cache.
        """
        with self.lock:
            return len(self.cache)
