import redis
import json
import pickle
from typing import Any, Optional
from datetime import timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            self.redis_client.ping()  # Test connection
            self.connected = True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            self.redis_client = None
            self.connected = False
            self._memory_cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.connected and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            else:
                # Fallback to memory cache
                if key in self._memory_cache:
                    item = self._memory_cache[key]
                    if item['expires_at'] > timedelta(seconds=0):
                        return item['value']
                    else:
                        del self._memory_cache[key]
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = settings.cache_ttl
            
        try:
            if self.connected and self.redis_client:
                return self.redis_client.setex(
                    key, 
                    ttl, 
                    pickle.dumps(value)
                )
            else:
                # Fallback to memory cache
                self._memory_cache[key] = {
                    'value': value,
                    'expires_at': timedelta(seconds=ttl)
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.connected and self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                # Fallback to memory cache
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.connected and self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                return key in self._memory_cache
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.connected and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            else:
                # Fallback to memory cache
                count = 0
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                    count += 1
                return count
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
        return 0

# Global cache instance
cache_service = CacheService()
