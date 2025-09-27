"""
API optimization service for performance improvements
"""
import time
import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from app.services.cache_service import get_cache_service, cached
from app.services.logging_service import get_logger

logger = get_logger(__name__)


class APIOptimizationService:
    """API optimization service for performance improvements"""
    
    def __init__(self):
        self.cache_service = get_cache_service()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.performance_metrics = {}
    
    def performance_monitor(self, operation_name: str):
        """Decorator for monitoring API performance"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metrics(operation_name, execution_time, success=True)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._record_metrics(operation_name, execution_time, success=False, error=str(e))
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metrics(operation_name, execution_time, success=True)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._record_metrics(operation_name, execution_time, success=False, error=str(e))
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def _record_metrics(self, operation_name: str, execution_time: float, 
                       success: bool, error: Optional[str] = None):
        """Record performance metrics"""
        if operation_name not in self.performance_metrics:
            self.performance_metrics[operation_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'errors': []
            }
        
        metrics = self.performance_metrics[operation_name]
        metrics['total_calls'] += 1
        metrics['total_time'] += execution_time
        
        if success:
            metrics['successful_calls'] += 1
        else:
            metrics['failed_calls'] += 1
            if error:
                metrics['errors'].append(error)
        
        metrics['avg_time'] = metrics['total_time'] / metrics['total_calls']
        metrics['min_time'] = min(metrics['min_time'], execution_time)
        metrics['max_time'] = max(metrics['max_time'], execution_time)
        
        # Keep only last 100 errors
        if len(metrics['errors']) > 100:
            metrics['errors'] = metrics['errors'][-100:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    def clear_metrics(self):
        """Clear performance metrics"""
        self.performance_metrics.clear()
    
    def batch_operations(self, operations: List[Callable], max_workers: int = 4) -> List[Any]:
        """Execute multiple operations in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_operation = {
                executor.submit(op): op for op in operations
            }
            
            for future in as_completed(future_to_operation):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Batch operation failed: {e}")
                    results.append(None)
        
        return results
    
    async def async_batch_operations(self, operations: List[Callable], 
                                   max_concurrent: int = 10) -> List[Any]:
        """Execute multiple async operations concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(operation):
            async with semaphore:
                return await operation()
        
        tasks = [execute_with_semaphore(op) for op in operations]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def paginate_results(self, data: List[Any], page: int = 1, 
                        page_size: int = 20) -> Dict[str, Any]:
        """Paginate results for better performance"""
        total_items = len(data)
        total_pages = (total_items + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_data = data[start_idx:end_idx]
        
        return {
            'data': paginated_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    
    def optimize_query(self, query_func: Callable, cache_key: str, 
                      ttl: int = 3600, **kwargs) -> Any:
        """Optimize database queries with caching"""
        # Try to get from cache first
        cached_result = self.cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute query and cache result
        result = query_func(**kwargs)
        if result is not None:
            self.cache_service.set(cache_key, result, ttl)
        
        return result
    
    def lazy_loading(self, data: List[Dict], key_field: str, 
                    loader_func: Callable) -> Dict[str, Any]:
        """Implement lazy loading for related data"""
        result = {}
        
        for item in data:
            key = item.get(key_field)
            if key:
                # Load related data only when needed
                related_data = loader_func(key)
                result[key] = {
                    'item': item,
                    'related': related_data
                }
        
        return result
    
    def data_compression(self, data: Any) -> bytes:
        """Compress data for storage/transmission"""
        import gzip
        import json
        
        try:
            json_data = json.dumps(data).encode('utf-8')
            compressed_data = gzip.compress(json_data)
            return compressed_data
        except Exception as e:
            logger.error(f"Data compression failed: {e}")
            return None
    
    def data_decompression(self, compressed_data: bytes) -> Any:
        """Decompress data"""
        import gzip
        import json
        
        try:
            decompressed_data = gzip.decompress(compressed_data)
            return json.loads(decompressed_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Data decompression failed: {e}")
            return None
    
    def response_caching(self, cache_key: str, ttl: int = 3600):
        """Decorator for caching API responses"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Try to get from cache
                cached_response = self.cache_service.get(cache_key)
                if cached_response is not None:
                    return cached_response
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                if result is not None:
                    self.cache_service.set(cache_key, result, ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Try to get from cache
                cached_response = self.cache_service.get(cache_key)
                if cached_response is not None:
                    return cached_response
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                if result is not None:
                    self.cache_service.set(cache_key, result, ttl)
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def rate_limiting(self, max_requests: int = 100, window_seconds: int = 60):
        """Decorator for rate limiting"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Get client identifier (simplified)
                client_id = kwargs.get('client_id', 'default')
                rate_key = f"rate_limit:{client_id}"
                
                # Check current rate
                current_requests = self.cache_service.increment(rate_key, 1)
                if current_requests == 1:
                    self.cache_service.expire(rate_key, window_seconds)
                
                if current_requests > max_requests:
                    raise Exception("Rate limit exceeded")
                
                return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Get client identifier (simplified)
                client_id = kwargs.get('client_id', 'default')
                rate_key = f"rate_limit:{client_id}"
                
                # Check current rate
                current_requests = self.cache_service.increment(rate_key, 1)
                if current_requests == 1:
                    self.cache_service.expire(rate_key, window_seconds)
                
                if current_requests > max_requests:
                    raise Exception("Rate limit exceeded")
                
                return func(*args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def data_validation(self, schema: Dict[str, Any]):
        """Decorator for data validation"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Validate input data
                for field, validation in schema.items():
                    if field in kwargs:
                        value = kwargs[field]
                        if not validation(value):
                            raise ValueError(f"Invalid {field}: {value}")
                
                return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Validate input data
                for field, validation in schema.items():
                    if field in kwargs:
                        value = kwargs[field]
                        if not validation(value):
                            raise ValueError(f"Invalid {field}: {value}")
                
                return func(*args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def error_handling(self, default_return: Any = None):
        """Decorator for error handling"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    return default_return
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    return default_return
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations based on metrics"""
        recommendations = []
        
        for operation, metrics in self.performance_metrics.items():
            # Check for slow operations
            if metrics['avg_time'] > 2.0:
                recommendations.append({
                    'type': 'performance',
                    'operation': operation,
                    'issue': 'Slow operation',
                    'avg_time': metrics['avg_time'],
                    'suggestion': 'Consider caching or optimization'
                })
            
            # Check for high error rate
            error_rate = metrics['failed_calls'] / metrics['total_calls']
            if error_rate > 0.1:  # 10% error rate
                recommendations.append({
                    'type': 'reliability',
                    'operation': operation,
                    'issue': 'High error rate',
                    'error_rate': error_rate,
                    'suggestion': 'Investigate and fix errors'
                })
            
            # Check for high variance
            if metrics['max_time'] > metrics['avg_time'] * 3:
                recommendations.append({
                    'type': 'consistency',
                    'operation': operation,
                    'issue': 'High performance variance',
                    'variance': metrics['max_time'] - metrics['min_time'],
                    'suggestion': 'Optimize for consistency'
                })
        
        return recommendations


# Global optimization service instance
optimization_service = APIOptimizationService()
