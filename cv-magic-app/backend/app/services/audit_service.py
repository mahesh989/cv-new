"""
Audit logging service for security and compliance
"""
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import Request
from app.database import get_database
from app.models.user_data import UserActivityLog
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Audit logging service for security and compliance"""
    
    def __init__(self):
        self.sensitive_fields = {
            "password", "hashed_password", "api_key", "token", 
            "secret", "private_key", "ssn", "credit_card"
        }
    
    def log_authentication_event(self, user_id: Optional[int], event_type: str, 
                               success: bool, request: Request, 
                               additional_data: Optional[Dict[str, Any]] = None):
        """Log authentication events"""
        try:
            audit_data = {
                "event_type": event_type,
                "success": success,
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "additional_data": additional_data or {}
            }
            
            self._log_activity(user_id, "authentication", audit_data, request)
            
        except Exception as e:
            logger.error(f"Failed to log authentication event: {str(e)}")
    
    def log_security_event(self, user_id: Optional[int], event_type: str, 
                          severity: str, request: Request, 
                          additional_data: Optional[Dict[str, Any]] = None):
        """Log security events"""
        try:
            audit_data = {
                "event_type": event_type,
                "severity": severity,
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "additional_data": additional_data or {}
            }
            
            self._log_activity(user_id, "security", audit_data, request)
            
            # Log to application logs for immediate attention
            if severity in ["high", "critical"]:
                logger.warning(f"Security event: {event_type} - {audit_data}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    def log_data_access_event(self, user_id: int, resource_type: str, 
                             resource_id: str, action: str, request: Request,
                             additional_data: Optional[Dict[str, Any]] = None):
        """Log data access events"""
        try:
            audit_data = {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "additional_data": additional_data or {}
            }
            
            self._log_activity(user_id, "data_access", audit_data, request)
            
        except Exception as e:
            logger.error(f"Failed to log data access event: {str(e)}")
    
    def log_admin_action(self, admin_user_id: int, action: str, 
                        target_user_id: Optional[int], request: Request,
                        additional_data: Optional[Dict[str, Any]] = None):
        """Log admin actions"""
        try:
            audit_data = {
                "action": action,
                "target_user_id": target_user_id,
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "additional_data": additional_data or {}
            }
            
            self._log_activity(admin_user_id, "admin_action", audit_data, request)
            
        except Exception as e:
            logger.error(f"Failed to log admin action: {str(e)}")
    
    def log_system_event(self, event_type: str, severity: str, 
                         additional_data: Optional[Dict[str, Any]] = None):
        """Log system events"""
        try:
            audit_data = {
                "event_type": event_type,
                "severity": severity,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "additional_data": additional_data or {}
            }
            
            # Log to application logs
            if severity in ["high", "critical"]:
                logger.error(f"System event: {event_type} - {audit_data}")
            else:
                logger.info(f"System event: {event_type} - {audit_data}")
            
        except Exception as e:
            logger.error(f"Failed to log system event: {str(e)}")
    
    def get_audit_logs(self, user_id: Optional[int] = None, 
                      activity_type: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get audit logs"""
        try:
            db = next(get_database())
            query = db.query(UserActivityLog)
            
            if user_id:
                query = query.filter(UserActivityLog.user_id == user_id)
            
            if activity_type:
                query = query.filter(UserActivityLog.activity_type == activity_type)
            
            logs = query.order_by(UserActivityLog.created_at.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "activity_type": log.activity_type,
                    "activity_data": json.loads(log.activity_data) if log.activity_data else {},
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Failed to get audit logs: {str(e)}")
            return []
    
    def get_security_events(self, severity: Optional[str] = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get security events"""
        try:
            db = next(get_database())
            query = db.query(UserActivityLog).filter(
                UserActivityLog.activity_type == "security"
            )
            
            if severity:
                # Filter by severity in activity_data
                query = query.filter(
                    UserActivityLog.activity_data.contains(f'"severity":"{severity}"')
                )
            
            events = query.order_by(UserActivityLog.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": event.id,
                    "user_id": event.user_id,
                    "activity_data": json.loads(event.activity_data) if event.activity_data else {},
                    "ip_address": event.ip_address,
                    "user_agent": event.user_agent,
                    "created_at": event.created_at.isoformat()
                }
                for event in events
            ]
            
        except Exception as e:
            logger.error(f"Failed to get security events: {str(e)}")
            return []
    
    def _log_activity(self, user_id: Optional[int], activity_type: str, 
                     activity_data: Dict[str, Any], request: Request):
        """Log activity to database"""
        try:
            db = next(get_database())
            
            # Sanitize sensitive data
            sanitized_data = self._sanitize_data(activity_data)
            
            activity_log = UserActivityLog(
                user_id=user_id,
                activity_type=activity_type,
                activity_data=json.dumps(sanitized_data),
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent", "")
            )
            
            db.add(activity_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data from audit logs"""
        sanitized = {}
        
        for key, value in data.items():
            if key.lower() in self.sensitive_fields:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate audit report for compliance"""
        try:
            db = next(get_database())
            
            # Get all activities in date range
            activities = db.query(UserActivityLog).filter(
                UserActivityLog.created_at >= start_date,
                UserActivityLog.created_at <= end_date
            ).all()
            
            # Generate statistics
            total_activities = len(activities)
            activities_by_type = {}
            activities_by_user = {}
            security_events = 0
            
            for activity in activities:
                # Count by type
                activity_type = activity.activity_type
                if activity_type not in activities_by_type:
                    activities_by_type[activity_type] = 0
                activities_by_type[activity_type] += 1
                
                # Count by user
                user_id = activity.user_id or "anonymous"
                if user_id not in activities_by_user:
                    activities_by_user[user_id] = 0
                activities_by_user[user_id] += 1
                
                # Count security events
                if activity_type == "security":
                    security_events += 1
            
            return {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_activities": total_activities,
                "activities_by_type": activities_by_type,
                "activities_by_user": activities_by_user,
                "security_events": security_events,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate audit report: {str(e)}")
            return {}


# Global audit service instance
audit_service = AuditService()
