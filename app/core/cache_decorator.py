"""
Cache decorator for automatic caching with performance monitoring.

This module provides decorators to automatically cache function results
with detailed performance logging, keeping service layer clean.
"""
import time
import logging
from functools import wraps
from typing import Callable, Any
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


def cached(
    namespace: str,
    key_builder: Callable[..., str],
    ttl: int | None = None,
    log_performance: bool = True
):
    """
    Decorator to automatically cache function results with performance monitoring.

    Args:
        namespace: Cache namespace (e.g., 'products', 'users')
        key_builder: Function that builds cache key from function arguments
        ttl: Time to live in seconds (optional, uses default from settings)
        log_performance: Whether to log detailed performance metrics

    Example:
        @cached(
            namespace="products",
            key_builder=lambda q, skip, limit: f"list:q={q or 'all'}:skip={skip}:limit={limit}"
        )
        async def list_products(q: str = None, skip: int = 0, limit: int = 20):
            return await Product.find(...).to_list()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Build cache key from function arguments
            try:
                cache_key = key_builder(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to build cache key: {e}. Skipping cache.")
                return await func(*args, **kwargs)

            # Try to get from cache
            cache_start = time.perf_counter()
            cached_data = await cache_manager.get(namespace, cache_key)
            cache_time = (time.perf_counter() - cache_start) * 1000

            if cached_data is not None:
                if log_performance:
                    logger.info(
                        f"✅ CACHE HIT [{namespace}]: Key '{cache_key[:50]}...' "
                        f"retrieved in {cache_time:.2f}ms from Redis"
                    )
                return cached_data

            # Cache miss - execute function
            if log_performance:
                logger.info(
                    f"❌ CACHE MISS [{namespace}]: Key '{cache_key[:50]}...' "
                    f"not found (lookup: {cache_time:.2f}ms)"
                )

            # Execute original function
            func_start = time.perf_counter()
            result = await func(*args, **kwargs)
            func_time = (time.perf_counter() - func_start) * 1000

            if log_performance:
                logger.info(
                    f"📊 FUNCTION EXECUTED [{namespace}]: "
                    f"Took {func_time:.2f}ms to complete"
                )

            # Cache the result
            if result is not None:
                cache_set_start = time.perf_counter()
                await cache_manager.set(namespace, cache_key, result, ttl=ttl)
                cache_set_time = (time.perf_counter() - cache_set_start) * 1000

                total_time = cache_time + func_time + cache_set_time

                if log_performance:
                    logger.info(
                        f"💾 CACHED [{namespace}]: Stored result in Redis ({cache_set_time:.2f}ms)"
                    )
                    logger.info(
                        f"⏱️  TOTAL TIME [{namespace}]: {total_time:.2f}ms "
                        f"(Cache check: {cache_time:.2f}ms + Execution: {func_time:.2f}ms + Cache store: {cache_set_time:.2f}ms)"
                    )

            return result

        return wrapper
    return decorator


def cache_result(
    namespace: str,
    ttl: int | None = None,
    log_performance: bool = True
):
    """
    Simplified cache decorator that uses function name and args as cache key.

    This is a convenience decorator for simple caching scenarios where
    you don't need custom key building logic.

    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        log_performance: Whether to log performance metrics

    Example:
        @cache_result(namespace="products", ttl=300)
        async def get_product_by_id(product_id: str):
            return await Product.get(product_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Build simple cache key from function name and arguments
            func_name = func.__name__

            # Create key from positional args
            args_str = "_".join(str(arg) for arg in args)

            # Create key from keyword args
            kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

            # Combine all parts
            key_parts = [func_name]
            if args_str:
                key_parts.append(args_str)
            if kwargs_str:
                key_parts.append(kwargs_str)

            cache_key = ":".join(key_parts)

            # Try to get from cache
            cache_start = time.perf_counter()
            cached_data = await cache_manager.get(namespace, cache_key)
            cache_time = (time.perf_counter() - cache_start) * 1000

            if cached_data is not None:
                if log_performance:
                    logger.info(
                        f"✅ CACHE HIT [{namespace}]: '{func_name}' "
                        f"retrieved in {cache_time:.2f}ms"
                    )
                return cached_data

            # Cache miss
            if log_performance:
                logger.info(
                    f"❌ CACHE MISS [{namespace}]: '{func_name}' "
                    f"not in cache (lookup: {cache_time:.2f}ms)"
                )

            # Execute function
            func_start = time.perf_counter()
            result = await func(*args, **kwargs)
            func_time = (time.perf_counter() - func_start) * 1000

            if log_performance:
                logger.info(
                    f"📊 FUNCTION EXECUTED [{namespace}]: '{func_name}' "
                    f"completed in {func_time:.2f}ms"
                )

            # Cache result
            if result is not None:
                cache_set_start = time.perf_counter()
                await cache_manager.set(namespace, cache_key, result, ttl=ttl)
                cache_set_time = (time.perf_counter() - cache_set_start) * 1000

                total_time = cache_time + func_time + cache_set_time

                if log_performance:
                    logger.info(
                        f"💾 CACHED [{namespace}]: '{func_name}' stored ({cache_set_time:.2f}ms)"
                    )
                    logger.info(
                        f"⏱️  TOTAL TIME [{namespace}]: {total_time:.2f}ms "
                        f"(Cache: {cache_time:.2f}ms + Exec: {func_time:.2f}ms + Store: {cache_set_time:.2f}ms)"
                    )

            return result

        return wrapper
    return decorator


async def invalidate_cache(namespace: str, pattern: str = "*") -> int:
    """
    Invalidate cache entries matching the pattern.

    Args:
        namespace: Cache namespace
        pattern: Key pattern to match (supports wildcards)

    Returns:
        Number of keys deleted

    Example:
        # Delete specific product cache
        await invalidate_cache("products", "slug:gaming-laptop-pro")

        # Delete all product list caches
        await invalidate_cache("products", "list:*")
    """
    return await cache_manager.delete_pattern(namespace, pattern)
