"""
Script to clear Redis cache.
Run this after fixing cache serialization issues.
"""
import asyncio
from app.core.cache import cache_manager


async def clear_cache():
    """Clear all cached data."""
    print("Initializing cache connection...")
    await cache_manager.initialize()
    
    if not cache_manager.enabled:
        print("❌ Redis is not enabled or not connected")
        return
    
    print("Clearing products cache...")
    deleted = await cache_manager.clear_namespace("products")
    print(f"✅ Deleted {deleted} product cache entries")
    
    print("Clearing all cache...")
    total = await cache_manager.delete_pattern("*", "*")
    print(f"✅ Total cache entries cleared: {total}")
    
    await cache_manager.close()
    print("✨ Cache cleared successfully!")


if __name__ == "__main__":
    asyncio.run(clear_cache())

