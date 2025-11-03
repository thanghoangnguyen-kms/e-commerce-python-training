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
from typing import Any
from redis import asyncio as aioredis
from beanie import Document
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages Redis cache connections and operations.
    Implements singleton pattern for connection reuse.
    """

    def __init__(self):
        self.redis: aioredis.Redis | None = None
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

    def _serialize_value(self, value: Any) -> Any:
        """
        Serialize value for caching, handling Beanie Documents properly.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serializable value (dict, list, or primitive)
        """
        if isinstance(value, Document):
            # Convert Beanie Document to dict using model_dump
            return value.model_dump(mode='json')
        elif isinstance(value, list):
            # Handle list of Documents
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            # Handle dict with Document values
            return {k: self._serialize_value(v) for k, v in value.items()}
        else:
            return value

    async def get(self, namespace: str, key: str) -> Any | None:
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
        ttl: int | None = None
    ) -> bool:
        """
        Set value in cache with optional TTL.

        Args:
            namespace: Category of data
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            
            # Properly serialize Beanie Documents and other objects
            serializable_value = self._serialize_value(value)
            serialized = json.dumps(serializable_value, default=str)

            ttl = ttl or settings.cache_ttl_seconds
            await self.redis.setex(cache_key, ttl, serialized)

            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for {namespace}:{key}: {e}")
            return False

    async def delete(self, namespace: str, key: str) -> bool:
        """
        Delete a specific cache entry.

        Args:
            namespace: Category of data
            key: Cache key

        Returns:
            True if deleted, False otherwise
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

    async def delete_pattern(self, namespace: str, pattern: str) -> int:
        """
        Delete all cache keys matching a pattern.

        Args:
            namespace: Category of data
            pattern: Pattern to match (supports * wildcard)

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

    async def clear_namespace(self, namespace: str) -> int:
        """
        Clear all cache entries in a namespace.

        Args:
            namespace: Category to clear

        Returns:
            Number of keys deleted
        """
        return await self.delete_pattern(namespace, "*")


# Singleton instance
cache_manager = CacheManager()


async def invalidate_cache(namespace: str, pattern: str = "*") -> int:
    """
    Invalidate cache entries matching a pattern.

    Args:
        namespace: Cache namespace
        pattern: Pattern to match (supports * wildcard)

    Returns:
        Number of keys deleted
    """
    return await cache_manager.delete_pattern(namespace, pattern)
