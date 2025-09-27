"""
Redis caching service for performance optimization
"""
import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
                 default_ttl: int = 3600, key_prefix: str = "cv_app"):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, 
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _get_key(self, key: str) -> str:
        """Generate full cache key"""
        return f"{self.key_prefix}:{key}"
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for storage"""
        try:
            # Try JSON first for simple data types
            if isinstance(data, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(data).encode('utf-8')
            else:
                # Use pickle for complex objects
                return pickle.dumps(data)
        except Exception as e:
            logger.warning(f"Serialization failed, using pickle: {e}")
            return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Fall back to pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Deserialization failed: {e}")
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._get_key(key)
            serialized_value = self._serialize(value)
            ttl = ttl or self.default_ttl
            
            result = self.redis_client.setex(full_key, ttl, serialized_value)
            return result
        except RedisError as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        if not self.redis_client:
            return None
        
        try:
            full_key = self._get_key(key)
            data = self.redis_client.get(full_key)
            
            if data is None:
                return None
            
            return self._deserialize(data)
        except RedisError as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache value"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._get_key(key)
            result = self.redis_client.delete(full_key)
            return result > 0
        except RedisError as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._get_key(key)
            return self.redis_client.exists(full_key) > 0
        except RedisError as e:
            logger.error(f"Cache exists check failed for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._get_key(key)
            return self.redis_client.expire(full_key, ttl)
        except RedisError as e:
            logger.error(f"Cache expire failed for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get TTL for key"""
        if not self.redis_client:
            return -1
        
        try:
            full_key = self._get_key(key)
            return self.redis_client.ttl(full_key)
        except RedisError as e:
            logger.error(f"Cache TTL check failed for key {key}: {e}")
            return -1
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            full_pattern = self._get_key(pattern)
            keys = self.redis_client.keys(full_pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Cache clear pattern failed for {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set using factory function"""
        value = self.get(key)
        if value is not None:
            return value
        
        # Generate new value
        try:
            value = factory_func()
            if value is not None:
                self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Factory function failed for key {key}: {e}")
            return None
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value"""
        if not self.redis_client:
            return None
        
        try:
            full_key = self._get_key(key)
            return self.redis_client.incrby(full_key, amount)
        except RedisError as e:
            logger.error(f"Cache increment failed for key {key}: {e}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement numeric value"""
        if not self.redis_client:
            return None
        
        try:
            full_key = self._get_key(key)
            return self.redis_client.decrby(full_key, amount)
        except RedisError as e:
            logger.error(f"Cache decrement failed for key {key}: {e}")
            return None
    
    def hash_set(self, key: str, field: str, value: Any) -> bool:
        """Set hash field"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._get_key(key)
            serialized_value = self._serialize(value)
            return self.redis_client.hset(full_key, field, serialized_value)
        except RedisError as e:
            logger.error(f"Cache hash set failed for key {key}: {e}")
            return False
    
    def hash_get(self, key: str, field: str) -> Optional[Any]:
        """Get hash field"""
        if not self.redis_client:
            return None
        
        try:
            full_key = self._get_key(key)
            data = self.redis_client.hget(full_key, field)
            
            if data is None:
                return None
            
            return self._deserialize(data)
        except RedisError as e:
            logger.error(f"Cache hash get failed for key {key}: {e}")
            return None
    
    def hash_get_all(self, key: str) -> Dict[str, Any]:
        """Get all hash fields"""
        if not self.redis_client:
            return {}
        
        try:
            full_key = self._get_key(key)
            data = self.redis_client.hgetall(full_key)
            
            result = {}
            for field, value in data.items():
                result[field.decode('utf-8')] = self._deserialize(value)
            
            return result
        except RedisError as e:
            logger.error(f"Cache hash get all failed for key {key}: {e}")
            return {}
    
    def list_push(self, key: str, *values: Any) -> Optional[int]:
        """Push values to list"""
        if not self.redis_client:
            return None
        
        try:
            full_key = self._get_key(key)
            serialized_values = [self._serialize(v) for v in values]
            return self.redis_client.lpush(full_key, *serialized_values)
        except RedisError as e:
            logger.error(f"Cache list push failed for key {key}: {e}")
            return None
    
    def list_pop(self, key: str) -> Optional[Any]:
        """Pop value from list"""
        if not self.redis_client:
            return None
        
        try:
            full_key = self._get_key(key)
            data = self.redis_client.rpop(full_key)
            
            if data is None:
                return None
            
            return self._deserialize(data)
        except RedisError as e:
            logger.error(f"Cache list pop failed for key {key}: {e}")
            return None
    
    def list_get(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get list values"""
        if not self.redis_client:
            return []
        
        try:
            full_key = self._get_key(key)
            data = self.redis_client.lrange(full_key, start, end)
            
            return [self._deserialize(item) for item in data]
        except RedisError as e:
            logger.error(f"Cache list get failed for key {key}: {e}")
            return []
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{':'.join(f'{k}={v}' for k, v in sorted_kwargs)}"
        
        # Hash long keys
        if len(key_data) > 200:
            key_data = hashlib.md5(key_data.encode()).hexdigest()
        
        return key_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"connected": False}
        
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except RedisError as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return (hits / total) * 100


# Global cache service instance
cache_service = None


def get_cache_service() -> CacheService:
    """Get global cache service instance"""
    global cache_service
    if cache_service is None:
        from app.config import settings
        cache_service = CacheService(
            redis_url=getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
            default_ttl=getattr(settings, 'CACHE_TTL', 3600),
            key_prefix=getattr(settings, 'CACHE_KEY_PREFIX', 'cv_app')
        )
    return cache_service


def cache_key(prefix: str, **kwargs) -> str:
    """Generate cache key helper"""
    return get_cache_service().generate_cache_key(prefix, **kwargs)


def cached(ttl: int = 3600, key_prefix: str = "default"):
    """Decorator for caching function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = cache_key(
                f"{key_prefix}:{func.__name__}",
                args=str(args),
                kwargs=str(sorted(kwargs.items()))
            )
            
            # Try to get from cache
            cache_service = get_cache_service()
            result = cache_service.get(cache_key_str)
            
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache_service.set(cache_key_str, result, ttl)
            
            return result
        
        return wrapper
    return decorator
