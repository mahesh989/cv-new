"""
Advanced features routes for bulk operations and search
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models.auth import UserData
from app.core.dependencies import get_current_user, get_admin_user
from app.services.advanced_features_service import advanced_features_service
from app.services.cache_service import get_cache_service
from app.services.api_optimization_service import optimization_service
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/advanced", tags=["advanced-features"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


class BulkUploadRequest(BaseModel):
    """Bulk upload request model"""
    files: List[Dict[str, Any]]


class BulkDeleteRequest(BaseModel):
    """Bulk delete request model"""
    file_ids: List[str]


class BulkExportRequest(BaseModel):
    """Bulk export request model"""
    data_types: List[str]


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    file_types: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None


class BatchProcessRequest(BaseModel):
    """Batch process request model"""
    file_ids: List[str]
    operation: str
    parameters: Optional[Dict[str, Any]] = None


@router.post("/bulk-upload")
async def bulk_upload_files(
    request: BulkUploadRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Bulk upload multiple files"""
    try:
        result = await advanced_features_service.bulk_upload_files(
            int(current_user.id), request.files
        )
        
        return {
            "status": "success",
            "message": "Bulk upload completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Bulk upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk upload failed: {str(e)}"
        )


@router.post("/bulk-delete")
async def bulk_delete_files(
    request: BulkDeleteRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Bulk delete multiple files"""
    try:
        result = await advanced_features_service.bulk_delete_files(
            int(current_user.id), request.file_ids
        )
        
        return {
            "status": "success",
            "message": "Bulk delete completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Bulk delete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk delete failed: {str(e)}"
        )


@router.post("/bulk-export")
async def bulk_export_data(
    request: BulkExportRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Bulk export user data"""
    try:
        result = await advanced_features_service.bulk_export_data(
            int(current_user.id), request.data_types
        )
        
        return {
            "status": "success",
            "message": "Bulk export completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Bulk export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk export failed: {str(e)}"
        )


@router.post("/search")
async def search_files(
    request: SearchRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Search user files with advanced filtering"""
    try:
        results = await advanced_features_service.search_files(
            int(current_user.id),
            request.query,
            request.file_types,
            request.date_range
        )
        
        return {
            "status": "success",
            "message": "Search completed",
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/statistics")
async def get_user_statistics(current_user: UserData = Depends(get_current_user)):
    """Get comprehensive user statistics"""
    try:
        stats = await advanced_features_service.get_user_statistics(int(current_user.id))
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Get user statistics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get user statistics failed: {str(e)}"
        )


@router.post("/batch-process")
async def batch_process_files(
    request: BatchProcessRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Batch process multiple files"""
    try:
        result = await advanced_features_service.batch_process_files(
            int(current_user.id),
            request.file_ids,
            request.operation,
            **(request.parameters or {})
        )
        
        return {
            "status": "success",
            "message": "Batch processing completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )


@router.get("/analytics")
async def get_system_analytics(admin_user: UserData = Depends(get_admin_user)):
    """Get system-wide analytics (admin only)"""
    try:
        analytics = await advanced_features_service.get_system_analytics()
        
        return {
            "status": "success",
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Get system analytics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get system analytics failed: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_old_data(
    days: int = Query(30, description="Days of data to keep"),
    admin_user: UserData = Depends(get_admin_user)
):
    """Clean up old data (admin only)"""
    try:
        result = await advanced_features_service.cleanup_old_data(days)
        
        return {
            "status": "success",
            "message": "Data cleanup completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data cleanup failed: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_statistics(admin_user: UserData = Depends(get_admin_user)):
    """Get cache statistics (admin only)"""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_stats()
        
        return {
            "status": "success",
            "cache_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Get cache statistics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get cache statistics failed: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="Cache key pattern to clear"),
    admin_user: UserData = Depends(get_admin_user)
):
    """Clear cache (admin only)"""
    try:
        cache_service = get_cache_service()
        
        if pattern:
            cleared_count = cache_service.clear_pattern(pattern)
            message = f"Cleared {cleared_count} cache entries matching pattern: {pattern}"
        else:
            # Clear all cache entries
            cleared_count = cache_service.clear_pattern("*")
            message = f"Cleared {cleared_count} cache entries"
        
        return {
            "status": "success",
            "message": message,
            "cleared_count": cleared_count
        }
        
    except Exception as e:
        logger.error(f"Clear cache failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clear cache failed: {str(e)}"
        )


@router.get("/performance/metrics")
async def get_performance_metrics(admin_user: UserData = Depends(get_admin_user)):
    """Get API performance metrics (admin only)"""
    try:
        metrics = optimization_service.get_performance_metrics()
        
        return {
            "status": "success",
            "performance_metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Get performance metrics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get performance metrics failed: {str(e)}"
        )


@router.get("/performance/recommendations")
async def get_optimization_recommendations(admin_user: UserData = Depends(get_admin_user)):
    """Get optimization recommendations (admin only)"""
    try:
        recommendations = optimization_service.get_optimization_recommendations()
        
        return {
            "status": "success",
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Get optimization recommendations failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get optimization recommendations failed: {str(e)}"
        )


@router.post("/performance/clear-metrics")
async def clear_performance_metrics(admin_user: UserData = Depends(get_admin_user)):
    """Clear performance metrics (admin only)"""
    try:
        optimization_service.clear_metrics()
        
        return {
            "status": "success",
            "message": "Performance metrics cleared"
        }
        
    except Exception as e:
        logger.error(f"Clear performance metrics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clear performance metrics failed: {str(e)}"
        )


@router.get("/health/detailed")
async def get_detailed_health_check(admin_user: UserData = Depends(get_admin_user)):
    """Get detailed health check (admin only)"""
    try:
        # Get cache health
        cache_service = get_cache_service()
        cache_stats = cache_service.get_stats()
        
        # Get performance metrics
        performance_metrics = optimization_service.get_performance_metrics()
        
        # Get optimization recommendations
        recommendations = optimization_service.get_optimization_recommendations()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health": {
                "cache": cache_stats,
                "performance": performance_metrics,
                "recommendations": recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailed health check failed: {str(e)}"
        )
