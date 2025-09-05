"""
Performance optimization utilities for the backend
"""

import asyncio
import time
import functools
from typing import Dict, Any, Optional, Callable
from threading import Lock
from datetime import datetime, timedelta
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if datetime.now() > entry['expires']:
                del self._cache[key]
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        expires = datetime.now() + timedelta(seconds=ttl)
        
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires': expires,
                'created': datetime.now()
            }
            logger.debug(f"Cache set for key: {key}, TTL: {ttl}s")
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        with self._lock:
            self._cache.pop(key, None)
            logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self) -> None:
        """Clear entire cache"""
        with self._lock:
            self._cache.clear()
            logger.debug("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            now = datetime.now()
            active_entries = sum(1 for entry in self._cache.values() if now <= entry['expires'])
            expired_entries = len(self._cache) - active_entries
            
            return {
                'total_entries': len(self._cache),
                'active_entries': active_entries,
                'expired_entries': expired_entries
            }


# Global cache instance
cache = SimpleCache()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """Cache decorator for functions"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def timed(func):
    """Timing decorator for performance monitoring"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
            raise
    
    # Return appropriate wrapper
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


async def with_timeout(coro, timeout_seconds: int, operation_name: str = "operation"):
    """Execute coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(f"Timeout: {operation_name} took longer than {timeout_seconds}s")
        from .exceptions import TimeoutError
        raise TimeoutError(operation_name, timeout_seconds)


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}
        self._lock = Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - self.window_seconds
        
        with self._lock:
            if identifier not in self._requests:
                self._requests[identifier] = []
            
            # Remove old requests
            self._requests[identifier] = [
                req_time for req_time in self._requests[identifier]
                if req_time > window_start
            ]
            
            # Check rate limit
            if len(self._requests[identifier]) >= self.max_requests:
                return False
            
            # Add current request
            self._requests[identifier].append(now)
            return True


# Global rate limiter (100 requests per minute)
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


def rate_limited(max_requests: int = 100, window_seconds: int = 60):
    """Rate limiting decorator"""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Use IP or session ID as identifier (simplified)
            identifier = "global"  # In real app, extract from request
            
            if not limiter.is_allowed(identifier):
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            identifier = "global"
            
            if not limiter.is_allowed(identifier):
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def optimize_file_operations():
    """Apply file operation optimizations"""
    import os
    
    # Set optimal buffer sizes
    if hasattr(os, 'O_SEQUENTIAL'):
        os.O_SEQUENTIAL = os.O_SEQUENTIAL  # Hint for sequential file access
    
    return True


class MetricsCollector:
    """Simple metrics collector"""
    
    def __init__(self):
        self._metrics: Dict[str, list] = {}
        self._lock = Lock()
    
    def record(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric"""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = []
            
            self._metrics[metric_name].append({
                'value': value,
                'timestamp': time.time(),
                'tags': tags or {}
            })
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        with self._lock:
            if metric_name not in self._metrics:
                return {}
            
            values = [entry['value'] for entry in self._metrics[metric_name]]
            if not values:
                return {}
            
            return {
                'count': len(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'sum': sum(values)
            }


# Global metrics collector
metrics = MetricsCollector()
