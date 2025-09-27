"""
Advanced features service for bulk operations and advanced functionality
"""
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import get_database
from app.models.user import User
from app.models.user_data import UserFileStorage, UserActivityLog
from app.services.cache_service import get_cache_service
from app.services.logging_service import get_logger
import json

logger = get_logger(__name__)


class AdvancedFeaturesService:
    """Advanced features service for bulk operations and advanced functionality"""
    
    def __init__(self):
        self.cache_service = get_cache_service()
    
    async def bulk_upload_files(self, user_id: int, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk upload multiple files"""
        try:
            results = []
            successful_uploads = 0
            failed_uploads = 0
            
            for file_data in files:
                try:
                    # Process each file
                    result = await self._process_single_file(user_id, file_data)
                    results.append({
                        'filename': file_data.get('filename'),
                        'status': 'success',
                        'file_id': result.get('id'),
                        'message': 'Upload successful'
                    })
                    successful_uploads += 1
                except Exception as e:
                    results.append({
                        'filename': file_data.get('filename'),
                        'status': 'failed',
                        'error': str(e),
                        'message': 'Upload failed'
                    })
                    failed_uploads += 1
            
            return {
                'total_files': len(files),
                'successful_uploads': successful_uploads,
                'failed_uploads': failed_uploads,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Bulk upload failed: {e}")
            raise
    
    async def _process_single_file(self, user_id: int, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single file upload"""
        # This would contain the actual file processing logic
        # For now, we'll simulate the process
        return {
            'id': f"file_{user_id}_{datetime.now().timestamp()}",
            'filename': file_data.get('filename'),
            'size': file_data.get('size', 0),
            'type': file_data.get('type', 'unknown')
        }
    
    async def bulk_delete_files(self, user_id: int, file_ids: List[str]) -> Dict[str, Any]:
        """Bulk delete multiple files"""
        try:
            db = next(get_database())
            results = []
            successful_deletes = 0
            failed_deletes = 0
            
            for file_id in file_ids:
                try:
                    # Delete file from database
                    file_record = db.query(UserFileStorage).filter(
                        UserFileStorage.id == file_id,
                        UserFileStorage.user_id == user_id
                    ).first()
                    
                    if file_record:
                        db.delete(file_record)
                        results.append({
                            'file_id': file_id,
                            'status': 'success',
                            'message': 'File deleted successfully'
                        })
                        successful_deletes += 1
                    else:
                        results.append({
                            'file_id': file_id,
                            'status': 'not_found',
                            'message': 'File not found'
                        })
                        failed_deletes += 1
                        
                except Exception as e:
                    results.append({
                        'file_id': file_id,
                        'status': 'failed',
                        'error': str(e),
                        'message': 'Delete failed'
                    })
                    failed_deletes += 1
            
            db.commit()
            
            return {
                'total_files': len(file_ids),
                'successful_deletes': successful_deletes,
                'failed_deletes': failed_deletes,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Bulk delete failed: {e}")
            raise
    
    async def bulk_export_data(self, user_id: int, data_types: List[str]) -> Dict[str, Any]:
        """Bulk export user data"""
        try:
            export_data = {}
            
            for data_type in data_types:
                if data_type == 'profile':
                    export_data['profile'] = await self._export_user_profile(user_id)
                elif data_type == 'files':
                    export_data['files'] = await self._export_user_files(user_id)
                elif data_type == 'activity':
                    export_data['activity'] = await self._export_user_activity(user_id)
                elif data_type == 'settings':
                    export_data['settings'] = await self._export_user_settings(user_id)
            
            return {
                'user_id': user_id,
                'export_timestamp': datetime.now(timezone.utc).isoformat(),
                'data_types': data_types,
                'data': export_data
            }
            
        except Exception as e:
            logger.error(f"Bulk export failed: {e}")
            raise
    
    async def _export_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Export user profile data"""
        try:
            db = next(get_database())
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {}
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            
        except Exception as e:
            logger.error(f"Export user profile failed: {e}")
            return {}
    
    async def _export_user_files(self, user_id: int) -> List[Dict[str, Any]]:
        """Export user files data"""
        try:
            db = next(get_database())
            files = db.query(UserFileStorage).filter(UserFileStorage.user_id == user_id).all()
            
            return [
                {
                    'id': file.id,
                    'file_type': file.file_type,
                    'file_path': file.file_path,
                    'original_filename': file.original_filename,
                    'file_size': file.file_size,
                    'mime_type': file.mime_type,
                    'created_at': file.created_at.isoformat()
                }
                for file in files
            ]
            
        except Exception as e:
            logger.error(f"Export user files failed: {e}")
            return []
    
    async def _export_user_activity(self, user_id: int) -> List[Dict[str, Any]]:
        """Export user activity data"""
        try:
            db = next(get_database())
            activities = db.query(UserActivityLog).filter(
                UserActivityLog.user_id == user_id
            ).order_by(UserActivityLog.created_at.desc()).limit(1000).all()
            
            return [
                {
                    'id': activity.id,
                    'activity_type': activity.activity_type,
                    'activity_data': json.loads(activity.activity_data) if activity.activity_data else {},
                    'ip_address': activity.ip_address,
                    'user_agent': activity.user_agent,
                    'created_at': activity.created_at.isoformat()
                }
                for activity in activities
            ]
            
        except Exception as e:
            logger.error(f"Export user activity failed: {e}")
            return []
    
    async def _export_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Export user settings data"""
        try:
            db = next(get_database())
            from app.models.user_data import UserSettings
            
            settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            
            if not settings:
                return {}
            
            return {
                'id': settings.id,
                'preferred_ai_model': settings.preferred_ai_model,
                'analysis_preferences': json.loads(settings.analysis_preferences) if settings.analysis_preferences else {},
                'notification_settings': json.loads(settings.notification_settings) if settings.notification_settings else {},
                'ui_preferences': json.loads(settings.ui_preferences) if settings.ui_preferences else {},
                'created_at': settings.created_at.isoformat(),
                'updated_at': settings.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Export user settings failed: {e}")
            return {}
    
    async def search_files(self, user_id: int, query: str, 
                          file_types: Optional[List[str]] = None,
                          date_range: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Search user files with advanced filtering"""
        try:
            db = next(get_database())
            
            # Build query
            search_query = db.query(UserFileStorage).filter(UserFileStorage.user_id == user_id)
            
            # Add text search
            if query:
                search_query = search_query.filter(
                    UserFileStorage.original_filename.ilike(f"%{query}%")
                )
            
            # Add file type filter
            if file_types:
                search_query = search_query.filter(UserFileStorage.file_type.in_(file_types))
            
            # Add date range filter
            if date_range:
                start_date = datetime.fromisoformat(date_range.get('start_date', ''))
                end_date = datetime.fromisoformat(date_range.get('end_date', ''))
                search_query = search_query.filter(
                    UserFileStorage.created_at >= start_date,
                    UserFileStorage.created_at <= end_date
                )
            
            files = search_query.order_by(UserFileStorage.created_at.desc()).all()
            
            return [
                {
                    'id': file.id,
                    'file_type': file.file_type,
                    'file_path': file.file_path,
                    'original_filename': file.original_filename,
                    'file_size': file.file_size,
                    'mime_type': file.mime_type,
                    'created_at': file.created_at.isoformat()
                }
                for file in files
            ]
            
        except Exception as e:
            logger.error(f"Search files failed: {e}")
            return []
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            db = next(get_database())
            
            # Get user info
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Get file statistics
            total_files = db.query(UserFileStorage).filter(UserFileStorage.user_id == user_id).count()
            file_types = db.query(UserFileStorage.file_type).filter(
                UserFileStorage.user_id == user_id
            ).distinct().all()
            
            # Get activity statistics
            total_activities = db.query(UserActivityLog).filter(
                UserActivityLog.user_id == user_id
            ).count()
            
            # Get recent activity
            recent_activities = db.query(UserActivityLog).filter(
                UserActivityLog.user_id == user_id
            ).order_by(UserActivityLog.created_at.desc()).limit(10).all()
            
            return {
                'user_id': user_id,
                'username': user.username,
                'email': user.email,
                'account_created': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'files': {
                    'total_files': total_files,
                    'file_types': [ft[0] for ft in file_types]
                },
                'activity': {
                    'total_activities': total_activities,
                    'recent_activities': [
                        {
                            'type': activity.activity_type,
                            'timestamp': activity.created_at.isoformat()
                        }
                        for activity in recent_activities
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Get user statistics failed: {e}")
            return {}
    
    async def batch_process_files(self, user_id: int, file_ids: List[str], 
                                 operation: str, **kwargs) -> Dict[str, Any]:
        """Batch process multiple files"""
        try:
            results = []
            successful_operations = 0
            failed_operations = 0
            
            for file_id in file_ids:
                try:
                    result = await self._process_single_file_operation(
                        user_id, file_id, operation, **kwargs
                    )
                    results.append({
                        'file_id': file_id,
                        'status': 'success',
                        'result': result
                    })
                    successful_operations += 1
                except Exception as e:
                    results.append({
                        'file_id': file_id,
                        'status': 'failed',
                        'error': str(e)
                    })
                    failed_operations += 1
            
            return {
                'operation': operation,
                'total_files': len(file_ids),
                'successful_operations': successful_operations,
                'failed_operations': failed_operations,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Batch process files failed: {e}")
            raise
    
    async def _process_single_file_operation(self, user_id: int, file_id: str, 
                                            operation: str, **kwargs) -> Any:
        """Process a single file operation"""
        # This would contain the actual file processing logic
        # For now, we'll simulate the process
        return {
            'file_id': file_id,
            'operation': operation,
            'status': 'processed',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics"""
        try:
            db = next(get_database())
            
            # Get user statistics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            verified_users = db.query(User).filter(User.is_verified == True).count()
            
            # Get file statistics
            total_files = db.query(UserFileStorage).count()
            file_types = db.query(UserFileStorage.file_type).distinct().all()
            
            # Get activity statistics
            total_activities = db.query(UserActivityLog).count()
            recent_activities = db.query(UserActivityLog).order_by(
                UserActivityLog.created_at.desc()
            ).limit(100).all()
            
            return {
                'users': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'verified_users': verified_users
                },
                'files': {
                    'total_files': total_files,
                    'file_types': [ft[0] for ft in file_types]
                },
                'activity': {
                    'total_activities': total_activities,
                    'recent_activities': [
                        {
                            'type': activity.activity_type,
                            'user_id': activity.user_id,
                            'timestamp': activity.created_at.isoformat()
                        }
                        for activity in recent_activities
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Get system analytics failed: {e}")
            return {}
    
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old data"""
        try:
            db = next(get_database())
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Clean up old activity logs
            old_activities = db.query(UserActivityLog).filter(
                UserActivityLog.created_at < cutoff_date
            ).all()
            
            for activity in old_activities:
                db.delete(activity)
            
            db.commit()
            
            return {
                'cutoff_date': cutoff_date.isoformat(),
                'cleaned_activities': len(old_activities),
                'message': 'Old data cleaned up successfully'
            }
            
        except Exception as e:
            logger.error(f"Cleanup old data failed: {e}")
            raise


# Global advanced features service instance
advanced_features_service = AdvancedFeaturesService()
