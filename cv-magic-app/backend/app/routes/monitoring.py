"""
Monitoring and health check routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.models.auth import UserData
from app.core.dependencies import get_admin_user
from app.services.monitoring_service import monitoring_service
from app.services.logging_service import get_logger
import logging

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = get_logger(__name__)


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        # Get current health status
        current_metrics = monitoring_service.get_current_metrics()
        health_status = current_metrics.get('health')
        
        if not health_status:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "No health data available",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Determine HTTP status code
        if health_status['status'] == 'healthy':
            http_status = 200
        elif health_status['status'] == 'degraded':
            http_status = 200  # Still operational
        else:
            http_status = 503
        
        return JSONResponse(
            status_code=http_status,
            content={
                "status": health_status['status'],
                "overall_score": health_status['overall_score'],
                "checks": health_status['checks'],
                "timestamp": health_status['timestamp']
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "Health check failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@router.get("/health/detailed")
async def detailed_health_check(admin_user: UserData = Depends(get_admin_user)):
    """Detailed health check (admin only)"""
    try:
        current_metrics = monitoring_service.get_current_metrics()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": current_metrics
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailed health check failed: {str(e)}"
        )


@router.get("/metrics")
async def get_metrics(admin_user: UserData = Depends(get_admin_user)):
    """Get current metrics (admin only)"""
    try:
        current_metrics = monitoring_service.get_current_metrics()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": current_metrics
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/metrics/history")
async def get_metrics_history(
    hours: int = 24,
    admin_user: UserData = Depends(get_admin_user)
):
    """Get metrics history (admin only)"""
    try:
        if hours > 168:  # Max 1 week
            hours = 168
        
        metrics_history = monitoring_service.get_metrics_history(hours)
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "period_hours": hours,
            "metrics": metrics_history
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics history: {str(e)}"
        )


@router.get("/status")
async def get_status():
    """Get application status"""
    try:
        current_metrics = monitoring_service.get_current_metrics()
        
        # Extract key information
        system_metrics = current_metrics.get('system', {})
        app_metrics = current_metrics.get('application', {})
        health_status = current_metrics.get('health', {})
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "application": {
                "status": health_status.get('status', 'unknown'),
                "score": health_status.get('overall_score', 0),
                "active_users": app_metrics.get('active_users', 0),
                "total_users": app_metrics.get('total_users', 0),
                "active_sessions": app_metrics.get('active_sessions', 0)
            },
            "system": {
                "cpu_percent": system_metrics.get('cpu_percent', 0),
                "memory_percent": system_metrics.get('memory_percent', 0),
                "disk_percent": system_metrics.get('disk_percent', 0)
            },
            "performance": {
                "total_requests": app_metrics.get('total_requests', 0),
                "successful_requests": app_metrics.get('successful_requests', 0),
                "failed_requests": app_metrics.get('failed_requests', 0),
                "error_rate": app_metrics.get('error_rate', 0),
                "average_response_time": app_metrics.get('average_response_time', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.get("/alerts")
async def get_alerts(admin_user: UserData = Depends(get_admin_user)):
    """Get current alerts (admin only)"""
    try:
        current_metrics = monitoring_service.get_current_metrics()
        alerts = []
        
        # Check for alerts based on metrics
        system_metrics = current_metrics.get('system', {})
        app_metrics = current_metrics.get('application', {})
        health_status = current_metrics.get('health', {})
        
        # System alerts
        if system_metrics.get('cpu_percent', 0) > 80:
            alerts.append({
                "type": "system",
                "severity": "warning",
                "message": f"High CPU usage: {system_metrics.get('cpu_percent', 0):.1f}%",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        if system_metrics.get('memory_percent', 0) > 80:
            alerts.append({
                "type": "system",
                "severity": "warning",
                "message": f"High memory usage: {system_metrics.get('memory_percent', 0):.1f}%",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        if system_metrics.get('disk_percent', 0) > 90:
            alerts.append({
                "type": "system",
                "severity": "critical",
                "message": f"High disk usage: {system_metrics.get('disk_percent', 0):.1f}%",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Application alerts
        if app_metrics.get('error_rate', 0) > 0.05:
            alerts.append({
                "type": "application",
                "severity": "warning",
                "message": f"High error rate: {app_metrics.get('error_rate', 0):.2%}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        if app_metrics.get('average_response_time', 0) > 2.0:
            alerts.append({
                "type": "application",
                "severity": "warning",
                "message": f"Slow response time: {app_metrics.get('average_response_time', 0):.2f}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Health alerts
        if health_status.get('status') == 'unhealthy':
            alerts.append({
                "type": "health",
                "severity": "critical",
                "message": "Application health is unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alerts": alerts,
            "alert_count": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.post("/metrics/collect")
async def collect_metrics(admin_user: UserData = Depends(get_admin_user)):
    """Manually trigger metrics collection (admin only)"""
    try:
        # Force metrics collection
        system_metrics = monitoring_service._collect_system_metrics()
        app_metrics = monitoring_service._collect_application_metrics()
        health_status = monitoring_service._check_health_status()
        
        return {
            "status": "success",
            "message": "Metrics collected successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "system": system_metrics.__dict__,
                "application": app_metrics.__dict__,
                "health": health_status.__dict__
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to collect metrics: {str(e)}"
        )


@router.get("/logs")
async def get_logs(
    level: Optional[str] = None,
    limit: int = 100,
    admin_user: UserData = Depends(get_admin_user)
):
    """Get application logs (admin only)"""
    try:
        # This is a simplified version - in production, you'd use a proper log aggregation system
        return {
            "status": "success",
            "message": "Log retrieval not implemented in this version",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Use external log aggregation system (e.g., ELK stack, Fluentd) for production"
        }
        
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get logs: {str(e)}"
        )
