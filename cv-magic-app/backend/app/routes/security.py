"""
Security routes for audit logs and session management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.models.auth import UserData
from app.core.dependencies import get_admin_user
from app.services.audit_service import audit_service
from app.services.session_service import session_service

router = APIRouter(prefix="/security", tags=["security"])
security = HTTPBearer()


@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[int] = None,
    activity_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    admin_user: UserData = Depends(get_admin_user)
):
    """Get audit logs (admin only)"""
    try:
        logs = audit_service.get_audit_logs(user_id, activity_type, limit, offset)
        
        # Log admin access
        audit_service.log_admin_action(
            int(admin_user.id), "audit_logs_accessed", None, None,
            {"filters": {"user_id": user_id, "activity_type": activity_type}}
        )
        
        return {"logs": logs}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}"
        )


@router.get("/security-events")
async def get_security_events(
    severity: Optional[str] = None,
    limit: int = 100,
    admin_user: UserData = Depends(get_admin_user)
):
    """Get security events (admin only)"""
    try:
        events = audit_service.get_security_events(severity, limit)
        
        # Log admin access
        audit_service.log_admin_action(
            int(admin_user.id), "security_events_accessed", None, None,
            {"filters": {"severity": severity}}
        )
        
        return {"events": events}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security events: {str(e)}"
        )


@router.get("/audit-report")
async def generate_audit_report(
    days: int = 30,
    admin_user: UserData = Depends(get_admin_user)
):
    """Generate audit report (admin only)"""
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        report = audit_service.generate_audit_report(start_date, end_date)
        
        # Log admin action
        audit_service.log_admin_action(
            int(admin_user.id), "audit_report_generated", None, None,
            {"report_period_days": days}
        )
        
        return {"report": report}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audit report: {str(e)}"
        )


@router.get("/user-sessions/{user_id}")
async def get_user_sessions(
    user_id: int,
    admin_user: UserData = Depends(get_admin_user)
):
    """Get user sessions (admin only)"""
    try:
        sessions = session_service.get_user_sessions(user_id)
        
        # Log admin action
        audit_service.log_admin_action(
            int(admin_user.id), "user_sessions_accessed", user_id, None
        )
        
        return {"sessions": sessions}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user sessions: {str(e)}"
        )


@router.post("/invalidate-user-sessions/{user_id}")
async def invalidate_user_sessions(
    user_id: int,
    reason: str = "Admin action",
    admin_user: UserData = Depends(get_admin_user)
):
    """Invalidate all sessions for a user (admin only)"""
    try:
        count = session_service.invalidate_all_user_sessions(user_id, reason)
        
        # Log admin action
        audit_service.log_admin_action(
            int(admin_user.id), "user_sessions_invalidated", user_id, None,
            {"reason": reason, "sessions_invalidated": count}
        )
        
        return {
            "message": f"Invalidated {count} sessions for user {user_id}",
            "sessions_invalidated": count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate user sessions: {str(e)}"
        )


@router.post("/cleanup-sessions")
async def cleanup_expired_sessions(admin_user: UserData = Depends(get_admin_user)):
    """Clean up expired sessions (admin only)"""
    try:
        count = session_service.cleanup_expired_sessions()
        
        # Log admin action
        audit_service.log_admin_action(
            int(admin_user.id), "sessions_cleanup", None, None,
            {"sessions_cleaned": count}
        )
        
        return {
            "message": f"Cleaned up {count} expired sessions",
            "sessions_cleaned": count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup sessions: {str(e)}"
        )


@router.get("/security-stats")
async def get_security_stats(admin_user: UserData = Depends(get_admin_user)):
    """Get security statistics (admin only)"""
    try:
        # Get recent security events
        recent_events = audit_service.get_security_events(limit=100)
        
        # Count by severity
        severity_counts = {}
        for event in recent_events:
            activity_data = event.get("activity_data", {})
            severity = activity_data.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Get total sessions
        from app.database import get_database
        from app.models.user import UserSession
        db = next(get_database())
        total_sessions = db.query(UserSession).filter(
            UserSession.is_blacklisted == False,
            UserSession.expires_at > datetime.now(timezone.utc)
        ).count()
        
        # Get active users (users with active sessions)
        active_users = db.query(UserSession.user_id).filter(
            UserSession.is_blacklisted == False,
            UserSession.expires_at > datetime.now(timezone.utc)
        ).distinct().count()
        
        stats = {
            "total_active_sessions": total_sessions,
            "active_users": active_users,
            "security_events_by_severity": severity_counts,
            "recent_security_events": len(recent_events)
        }
        
        # Log admin access
        audit_service.log_admin_action(
            int(admin_user.id), "security_stats_accessed", None, None
        )
        
        return {"stats": stats}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security stats: {str(e)}"
        )


@router.post("/log-security-event")
async def log_security_event(
    event_type: str,
    severity: str,
    additional_data: Optional[Dict[str, Any]] = None,
    admin_user: UserData = Depends(get_admin_user)
):
    """Log a security event (admin only)"""
    try:
        audit_service.log_security_event(
            int(admin_user.id), event_type, severity, None, additional_data
        )
        
        return {"message": "Security event logged successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log security event: {str(e)}"
        )
