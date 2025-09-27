"""
Optimized API routes with caching and performance improvements
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models.auth import UserData
from app.core.dependencies import get_current_user, get_admin_user
from app.services.cache_service import get_cache_service, cached
from app.services.api_optimization_service import optimization_service
from app.services.advanced_features_service import advanced_features_service
import logging

router = APIRouter(prefix="/optimized", tags=["optimized-api"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


@router.get("/user/files")
@optimization_service.performance_monitor("get_user_files")
async def get_user_files_optimized(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = Query(None),
    current_user: UserData = Depends(get_current_user)
):
    """Get user files with optimization and caching"""
    try:
        cache_service = get_cache_service()
        
        # Generate cache key
        cache_key = cache_service.generate_cache_key(
            "user_files",
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            file_type=file_type
        )
        
        # Try to get from cache
        cached_result = cache_service.get(cache_key)
        if cached_result is not None:
            return {
                "status": "success",
                "source": "cache",
                "data": cached_result
            }
        
        # Get data from database (simplified for demo)
        # In real implementation, this would query the database
        files_data = {
            "files": [],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": 0,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False
            }
        }
        
        # Cache the result
        cache_service.set(cache_key, files_data, ttl=300)  # 5 minutes
        
        return {
            "status": "success",
            "source": "database",
            "data": files_data
        }
        
    except Exception as e:
        logger.error(f"Get user files failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get user files failed: {str(e)}"
        )


@router.get("/user/analytics")
@optimization_service.performance_monitor("get_user_analytics")
async def get_user_analytics_optimized(
    current_user: UserData = Depends(get_current_user)
):
    """Get user analytics with optimization"""
    try:
        cache_service = get_cache_service()
        
        # Generate cache key
        cache_key = cache_service.generate_cache_key(
            "user_analytics",
            user_id=current_user.id
        )
        
        # Try to get from cache
        cached_result = cache_service.get(cache_key)
        if cached_result is not None:
            return {
                "status": "success",
                "source": "cache",
                "analytics": cached_result
            }
        
        # Get analytics data
        analytics = await advanced_features_service.get_user_statistics(int(current_user.id))
        
        # Cache the result
        cache_service.set(cache_key, analytics, ttl=600)  # 10 minutes
        
        return {
            "status": "success",
            "source": "database",
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Get user analytics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get user analytics failed: {str(e)}"
        )


@router.get("/system/stats")
@optimization_service.performance_monitor("get_system_stats")
async def get_system_stats_optimized(
    admin_user: UserData = Depends(get_admin_user)
):
    """Get system statistics with optimization"""
    try:
        cache_service = get_cache_service()
        
        # Generate cache key
        cache_key = cache_service.generate_cache_key("system_stats")
        
        # Try to get from cache
        cached_result = cache_service.get(cache_key)
        if cached_result is not None:
            return {
                "status": "success",
                "source": "cache",
                "stats": cached_result
            }
        
        # Get system analytics
        analytics = await advanced_features_service.get_system_analytics()
        
        # Cache the result
        cache_service.set(cache_key, analytics, ttl=300)  # 5 minutes
        
        return {
            "status": "success",
            "source": "database",
            "stats": analytics
        }
        
    except Exception as e:
        logger.error(f"Get system stats failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get system stats failed: {str(e)}"
        )


@router.get("/search/global")
@optimization_service.performance_monitor("global_search")
async def global_search_optimized(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserData = Depends(get_current_user)
):
    """Global search with optimization"""
    try:
        cache_service = get_cache_service()
        
        # Generate cache key
        cache_key = cache_service.generate_cache_key(
            "global_search",
            query=query,
            page=page,
            page_size=page_size,
            user_id=current_user.id
        )
        
        # Try to get from cache
        cached_result = cache_service.get(cache_key)
        if cached_result is not None:
            return {
                "status": "success",
                "source": "cache",
                "results": cached_result
            }
        
        # Perform search (simplified for demo)
        search_results = {
            "query": query,
            "results": [],
            "total_results": 0,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False
            }
        }
        
        # Cache the result
        cache_service.set(cache_key, search_results, ttl=180)  # 3 minutes
        
        return {
            "status": "success",
            "source": "database",
            "results": search_results
        }
        
    except Exception as e:
        logger.error(f"Global search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Global search failed: {str(e)}"
        )


@router.get("/performance/health")
@optimization_service.performance_monitor("performance_health")
async def get_performance_health(
    admin_user: UserData = Depends(get_admin_user)
):
    """Get performance health check"""
    try:
        # Get performance metrics
        performance_metrics = optimization_service.get_performance_metrics()
        
        # Get optimization recommendations
        recommendations = optimization_service.get_optimization_recommendations()
        
        # Get cache statistics
        cache_service = get_cache_service()
        cache_stats = cache_service.get_stats()
        
        # Calculate health score
        health_score = 100
        issues = []
        
        # Check performance metrics
        for operation, metrics in performance_metrics.items():
            if metrics['avg_time'] > 2.0:
                health_score -= 10
                issues.append(f"Slow operation: {operation}")
            
            error_rate = metrics['failed_calls'] / metrics['total_calls'] if metrics['total_calls'] > 0 else 0
            if error_rate > 0.1:
                health_score -= 15
                issues.append(f"High error rate: {operation}")
        
        # Check cache health
        if not cache_stats.get('connected', False):
            health_score -= 20
            issues.append("Cache not connected")
        
        # Determine health status
        if health_score >= 90:
            status_text = "excellent"
        elif health_score >= 70:
            status_text = "good"
        elif health_score >= 50:
            status_text = "fair"
        else:
            status_text = "poor"
        
        return {
            "status": "success",
            "health_score": health_score,
            "health_status": status_text,
            "issues": issues,
            "performance_metrics": performance_metrics,
            "recommendations": recommendations,
            "cache_stats": cache_stats
        }
        
    except Exception as e:
        logger.error(f"Get performance health failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get performance health failed: {str(e)}"
        )


@router.post("/cache/warm")
@optimization_service.performance_monitor("cache_warm")
async def warm_cache(
    cache_keys: List[str],
    admin_user: UserData = Depends(get_admin_user)
):
    """Warm cache with specific keys (admin only)"""
    try:
        cache_service = get_cache_service()
        warmed_keys = []
        failed_keys = []
        
        for key in cache_keys:
            try:
                # This would contain logic to warm specific cache keys
                # For now, we'll just mark them as warmed
                warmed_keys.append(key)
            except Exception as e:
                failed_keys.append({"key": key, "error": str(e)})
        
        return {
            "status": "success",
            "message": "Cache warming completed",
            "warmed_keys": warmed_keys,
            "failed_keys": failed_keys
        }
        
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache warming failed: {str(e)}"
        )


@router.get("/optimization/status")
async def get_optimization_status(
    admin_user: UserData = Depends(get_admin_user)
):
    """Get optimization status"""
    try:
        # Get performance metrics
        performance_metrics = optimization_service.get_performance_metrics()
        
        # Get cache statistics
        cache_service = get_cache_service()
        cache_stats = cache_service.get_stats()
        
        # Get optimization recommendations
        recommendations = optimization_service.get_optimization_recommendations()
        
        # Calculate optimization score
        optimization_score = 100
        optimization_issues = []
        
        # Check performance
        for operation, metrics in performance_metrics.items():
            if metrics['avg_time'] > 1.0:
                optimization_score -= 5
                optimization_issues.append(f"Slow {operation}")
        
        # Check cache hit rate
        hit_rate = cache_stats.get('hit_rate', 0)
        if hit_rate < 50:
            optimization_score -= 10
            optimization_issues.append("Low cache hit rate")
        
        # Check recommendations
        if len(recommendations) > 5:
            optimization_score -= 15
            optimization_issues.append("Many optimization opportunities")
        
        return {
            "status": "success",
            "optimization_score": optimization_score,
            "optimization_issues": optimization_issues,
            "performance_metrics": performance_metrics,
            "cache_stats": cache_stats,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Get optimization status failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get optimization status failed: {str(e)}"
        )
