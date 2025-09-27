"""
User-specific settings management service
"""
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_data import UserSettings
from app.database import get_database


class UserSettingsService:
    """User-specific settings management service"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def get_settings(self) -> Dict[str, Any]:
        """Get user settings"""
        try:
            db = next(get_database())
            
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == int(self.user_id)
            ).first()
            
            if not settings:
                # Create default settings
                return self._create_default_settings()
            
            return {
                "preferred_ai_model": settings.preferred_ai_model,
                "analysis_preferences": json.loads(settings.analysis_preferences) if settings.analysis_preferences else {},
                "notification_settings": json.loads(settings.notification_settings) if settings.notification_settings else {},
                "ui_preferences": json.loads(settings.ui_preferences) if settings.ui_preferences else {},
                "created_at": settings.created_at.isoformat(),
                "updated_at": settings.updated_at.isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get settings: {str(e)}"
            )
    
    def update_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user settings"""
        try:
            db = next(get_database())
            
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == int(self.user_id)
            ).first()
            
            if not settings:
                # Create new settings
                settings = UserSettings(user_id=int(self.user_id))
                db.add(settings)
            
            # Update settings
            if "preferred_ai_model" in settings_data:
                settings.preferred_ai_model = settings_data["preferred_ai_model"]
            
            if "analysis_preferences" in settings_data:
                settings.analysis_preferences = json.dumps(settings_data["analysis_preferences"])
            
            if "notification_settings" in settings_data:
                settings.notification_settings = json.dumps(settings_data["notification_settings"])
            
            if "ui_preferences" in settings_data:
                settings.ui_preferences = json.dumps(settings_data["ui_preferences"])
            
            settings.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            return self.get_settings()
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update settings: {str(e)}"
            )
    
    def update_preferred_model(self, model: str) -> bool:
        """Update preferred AI model"""
        try:
            db = next(get_database())
            
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == int(self.user_id)
            ).first()
            
            if not settings:
                settings = UserSettings(user_id=int(self.user_id))
                db.add(settings)
            
            settings.preferred_ai_model = model
            settings.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update preferred model: {str(e)}"
            )
    
    def update_analysis_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Update analysis preferences"""
        try:
            db = next(get_database())
            
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == int(self.user_id)
            ).first()
            
            if not settings:
                settings = UserSettings(user_id=int(self.user_id))
                db.add(settings)
            
            settings.analysis_preferences = json.dumps(preferences)
            settings.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update analysis preferences: {str(e)}"
            )
    
    def update_notification_settings(self, notification_settings: Dict[str, Any]) -> bool:
        """Update notification settings"""
        try:
            db = next(get_database())
            
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == int(self.user_id)
            ).first()
            
            if not settings:
                settings = UserSettings(user_id=int(self.user_id))
                db.add(settings)
            
            settings.notification_settings = json.dumps(notification_settings)
            settings.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update notification settings: {str(e)}"
            )
    
    def update_ui_preferences(self, ui_preferences: Dict[str, Any]) -> bool:
        """Update UI preferences"""
        try:
            db = next(get_database())
            
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == int(self.user_id)
            ).first()
            
            if not settings:
                settings = UserSettings(user_id=int(self.user_id))
                db.add(settings)
            
            settings.ui_preferences = json.dumps(ui_preferences)
            settings.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update UI preferences: {str(e)}"
            )
    
    def _create_default_settings(self) -> Dict[str, Any]:
        """Create default settings for new user"""
        default_settings = {
            "preferred_ai_model": "gpt-3.5-turbo",
            "analysis_preferences": {
                "temperature": 0.3,
                "max_tokens": 2000,
                "include_soft_skills": True,
                "include_technical_skills": True,
                "include_domain_keywords": True
            },
            "notification_settings": {
                "email_notifications": True,
                "analysis_complete": True,
                "job_matches": True,
                "system_updates": False
            },
            "ui_preferences": {
                "theme": "light",
                "language": "en",
                "dashboard_layout": "default"
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save default settings to database
        try:
            db = next(get_database())
            settings = UserSettings(
                user_id=int(self.user_id),
                preferred_ai_model=default_settings["preferred_ai_model"],
                analysis_preferences=json.dumps(default_settings["analysis_preferences"]),
                notification_settings=json.dumps(default_settings["notification_settings"]),
                ui_preferences=json.dumps(default_settings["ui_preferences"])
            )
            db.add(settings)
            db.commit()
        except Exception as e:
            print(f"Warning: Failed to save default settings: {e}")
        
        return default_settings
    
    def cleanup_user_settings(self):
        """Clean up user settings (for account deletion)"""
        try:
            db = next(get_database())
            
            # Delete user settings
            db.query(UserSettings).filter(
                UserSettings.user_id == int(self.user_id)
            ).delete()
            
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup settings: {str(e)}"
            )
