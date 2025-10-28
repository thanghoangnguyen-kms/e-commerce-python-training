"""
Redis cache manager for the application.

This module provides a centralized caching layer with best practices:
- Connection pooling
- Automatic serialization/deserialization
- TTL (Time To Live) management
- Error handling and graceful degradation
- Cache key namespacing
- Batch operations support
"""
import json
import logging
from typing import Any, Optional
from redis import asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages Redis cache connections and operations.
    Implements singleton pattern for connection reuse.
    """

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.enabled = settings.redis_enabled

    async def initialize(self):
        """Initialize Redis connection pool."""
        if not self.enabled:
            logger.info("Redis caching is disabled")
            return

        try:
            self.redis = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10
            )
            # Test connection
            await self.redis.ping()
            logger.info(f"Redis connected successfully at {settings.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Continuing without cache - will operate in degraded mode")
            self.enabled = False
            self.redis = None

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    def _make_key(self, namespace: str, key: str) -> str:
        """
        Create namespaced cache key to avoid collisions.

        Args:
            namespace: Category of data (e.g., 'product', 'user')
            key: Specific identifier

        Returns:
            Formatted cache key
        """
        return f"ecommerce:{namespace}:{key}"

    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            namespace: Category of data
            key: Cache key

        Returns:
            Deserialized value or None if not found
        """
        if not self.enabled or not self.redis:
            return None

        try:
            cache_key = self._make_key(namespace, key)
            value = await self.redis.get(cache_key)

            if value:
                logger.debug(f"Cache HIT: {cache_key}")
                return json.loads(value)
            else:
                logger.debug(f"Cache MISS: {cache_key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error for {namespace}:{key}: {e}")
            return None

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with optional TTL.

        Args:
            namespace: Category of data
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default from settings)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            serialized = json.dumps(value, default=str)  # default=str handles datetime, ObjectId, etc.

            ttl = ttl or settings.cache_ttl_seconds
            await self.redis.setex(cache_key, ttl, serialized)

            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for {namespace}:{key}: {e}")
            return False

    async def delete(self, namespace: str, key: str) -> bool:
        """
        Delete a specific key from cache.

        Args:
            namespace: Category of data
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            await self.redis.delete(cache_key)
            logger.debug(f"Cache DELETE: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for {namespace}:{key}: {e}")
            return False

    async def delete_pattern(self, namespace: str, pattern: str = "*") -> int:
        """
        Delete all keys matching a pattern within a namespace.
        Useful for cache invalidation.

        Args:
            namespace: Category of data
            pattern: Pattern to match (default: all keys in namespace)

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis:
            return 0

        try:
            search_pattern = self._make_key(namespace, pattern)
            keys = []

            # Scan for keys (safer than KEYS command for production)
            async for key in self.redis.scan_iter(match=search_pattern, count=100):
                keys.append(key)

            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cache invalidation: deleted {deleted} keys matching {search_pattern}")
                return deleted

            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {namespace}:{pattern}: {e}")
            return 0

    async def get_many(self, namespace: str, keys: list[str]) -> dict[str, Any]:
        """
        Get multiple values from cache in one operation.
        More efficient than multiple get() calls.

        Args:
            namespace: Category of data
            keys: List of cache keys

        Returns:
            Dictionary mapping keys to their values (None if not found)
        """
        if not self.enabled or not self.redis or not keys:
            return {key: None for key in keys}

        try:
            cache_keys = [self._make_key(namespace, key) for key in keys]
            values = await self.redis.mget(cache_keys)

            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
                else:
                    result[key] = None

            return result
        except Exception as e:
            logger.error(f"Cache get_many error for {namespace}: {e}")
            return {key: None for key in keys}

    async def set_many(
        self,
        namespace: str,
        items: dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set multiple values in cache.

        Args:
            namespace: Category of data
            items: Dictionary mapping keys to values
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis or not items:
            return False

        try:
            pipeline = self.redis.pipeline()
            ttl = ttl or settings.cache_ttl_seconds

            for key, value in items.items():
                cache_key = self._make_key(namespace, key)
                serialized = json.dumps(value, default=str)
                await pipeline.setex(cache_key, ttl, serialized)

            await pipeline.execute()
            logger.debug(f"Cache SET_MANY: {len(items)} items in {namespace}")
            return True
        except Exception as e:
            logger.error(f"Cache set_many error for {namespace}: {e}")
            return False


# Global cache manager instance
cache_manager = CacheManager()

