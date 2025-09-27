"""
User activity logging service
"""
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_data import UserActivityLog
from app.database import get_database


class UserActivityService:
    """User activity logging service"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def log_activity(self, activity_type: str, activity_data: Optional[Dict[str, Any]] = None,
                    ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> bool:
        """Log user activity"""
        try:
            db = next(get_database())
            
            activity_log = UserActivityLog(
                user_id=int(self.user_id),
                activity_type=activity_type,
                activity_data=json.dumps(activity_data) if activity_data else None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(activity_log)
            db.commit()
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to log activity: {e}")
            return False
    
    def get_user_activities(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user activities"""
        try:
            db = next(get_database())
            
            activities = db.query(UserActivityLog).filter(
                UserActivityLog.user_id == int(self.user_id)
            ).order_by(UserActivityLog.created_at.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": activity.id,
                    "activity_type": activity.activity_type,
                    "activity_data": json.loads(activity.activity_data) if activity.activity_data else None,
                    "ip_address": activity.ip_address,
                    "user_agent": activity.user_agent,
                    "created_at": activity.created_at.isoformat()
                }
                for activity in activities
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get activities: {str(e)}"
            )
    
    def get_activity_stats(self) -> Dict[str, Any]:
        """Get user activity statistics"""
        try:
            db = next(get_database())
            
            # Get total activities
            total_activities = db.query(UserActivityLog).filter(
                UserActivityLog.user_id == int(self.user_id)
            ).count()
            
            # Get activities by type
            activities_by_type = {}
            activities = db.query(UserActivityLog).filter(
                UserActivityLog.user_id == int(self.user_id)
            ).all()
            
            for activity in activities:
                activity_type = activity.activity_type
                if activity_type not in activities_by_type:
                    activities_by_type[activity_type] = 0
                activities_by_type[activity_type] += 1
            
            # Get recent activity (last 7 days)
            from datetime import timedelta
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_activities = db.query(UserActivityLog).filter(
                UserActivityLog.user_id == int(self.user_id),
                UserActivityLog.created_at >= week_ago
            ).count()
            
            return {
                "total_activities": total_activities,
                "recent_activities": recent_activities,
                "activities_by_type": activities_by_type
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get activity stats: {str(e)}"
            )
    
    def cleanup_user_activities(self):
        """Clean up user activities (for account deletion)"""
        try:
            db = next(get_database())
            
            # Delete all user activities
            db.query(UserActivityLog).filter(
                UserActivityLog.user_id == int(self.user_id)
            ).delete()
            
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup activities: {str(e)}"
            )
