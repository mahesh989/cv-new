"""
User-specific file management service
"""
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_data import UserFileStorage
from app.database import get_database


class UserFileManager:
    """User-specific file management service"""
    
    def __init__(self, user_id: str, base_path: Optional[str] = None):
        self.user_id = user_id
        if base_path is None:
            base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/user_data"
        
        self.base_path = Path(base_path)
        self.user_path = self.base_path / "users" / user_id
        self.ensure_user_directories()
    
    def ensure_user_directories(self):
        """Create user-specific directories"""
        directories = [
            # CV directories
            self.user_path / "cvs" / "original",
            self.user_path / "cvs" / "tailored",
            self.user_path / "cvs" / "processed",
            
            # Analysis directories
            self.user_path / "analysis" / "skills",
            self.user_path / "analysis" / "recommendations",
            self.user_path / "analysis" / "results",
            self.user_path / "analysis" / "comparisons",
            
            # Job directories
            self.user_path / "jobs" / "saved",
            self.user_path / "jobs" / "applications",
            self.user_path / "jobs" / "descriptions",
            self.user_path / "jobs" / "matches",
            
            # Export and temporary directories
            self.user_path / "exports",
            self.user_path / "temp",
            self.user_path / "backups",
            
            # Configuration directories
            self.user_path / "config",
            self.user_path / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_user_cv_path(self, filename: str, is_tailored: bool = False) -> Path:
        """Get user-specific CV file path"""
        subdir = "tailored" if is_tailored else "original"
        return self.user_path / "cvs" / subdir / filename
    
    def get_user_analysis_path(self, analysis_type: str, filename: str) -> Path:
        """Get user-specific analysis path"""
        return self.user_path / "analysis" / analysis_type / filename
    
    def get_user_job_path(self, job_type: str, filename: str) -> Path:
        """Get user-specific job path"""
        return self.user_path / "jobs" / job_type / filename
    
    def get_user_export_path(self, filename: str) -> Path:
        """Get user-specific export path"""
        return self.user_path / "exports" / filename
    
    def save_file(self, file_data: bytes, filename: str, file_type: str, 
                  subdirectory: str = "", mime_type: Optional[str] = None) -> str:
        """Save file to user-specific directory"""
        try:
            # Determine target directory
            if file_type == "cv":
                target_dir = self.user_path / "cvs" / subdirectory
            elif file_type == "analysis":
                target_dir = self.user_path / "analysis" / subdirectory
            elif file_type == "job":
                target_dir = self.user_path / "jobs" / subdirectory
            elif file_type == "export":
                target_dir = self.user_path / "exports"
            else:
                target_dir = self.user_path / "temp"
            
            # Ensure directory exists
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = target_dir / filename
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Record in database
            self._record_file_storage(file_path, filename, file_type, len(file_data), mime_type)
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    def get_file(self, file_path: str) -> bytes:
        """Get file content from user-specific path"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            with open(path, 'rb') as f:
                return f.read()
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}"
            )
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from user-specific path"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                self._remove_file_storage(file_path)
                return True
            return False
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    def list_user_files(self, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all files for the user"""
        try:
            db = next(get_database())
            query = db.query(UserFileStorage).filter(
                UserFileStorage.user_id == int(self.user_id),
                UserFileStorage.is_active == True
            )
            
            if file_type:
                query = query.filter(UserFileStorage.file_type == file_type)
            
            files = query.all()
            
            return [
                {
                    "id": file.id,
                    "file_type": file.file_type,
                    "file_path": file.file_path,
                    "original_filename": file.original_filename,
                    "file_size": file.file_size,
                    "mime_type": file.mime_type,
                    "created_at": file.created_at.isoformat()
                }
                for file in files
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}"
            )
    
    def get_user_storage_stats(self) -> Dict[str, Any]:
        """Get user storage statistics"""
        try:
            db = next(get_database())
            files = db.query(UserFileStorage).filter(
                UserFileStorage.user_id == int(self.user_id),
                UserFileStorage.is_active == True
            ).all()
            
            total_files = len(files)
            total_size = sum(file.file_size for file in files)
            
            # Group by file type
            file_types = {}
            for file in files:
                file_type = file.file_type
                if file_type not in file_types:
                    file_types[file_type] = {"count": 0, "size": 0}
                file_types[file_type]["count"] += 1
                file_types[file_type]["size"] += file.file_size
            
            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_types": file_types
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get storage stats: {str(e)}"
            )
    
    def _record_file_storage(self, file_path: Path, filename: str, file_type: str, 
                           file_size: int, mime_type: Optional[str] = None):
        """Record file storage in database"""
        try:
            db = next(get_database())
            file_storage = UserFileStorage(
                user_id=int(self.user_id),
                file_type=file_type,
                file_path=str(file_path),
                original_filename=filename,
                file_size=file_size,
                mime_type=mime_type
            )
            db.add(file_storage)
            db.commit()
        except Exception as e:
            print(f"Warning: Failed to record file storage: {e}")
    
    def _remove_file_storage(self, file_path: str):
        """Remove file storage record from database"""
        try:
            db = next(get_database())
            file_storage = db.query(UserFileStorage).filter(
                UserFileStorage.user_id == int(self.user_id),
                UserFileStorage.file_path == file_path
            ).first()
            
            if file_storage:
                file_storage.is_active = False
                db.commit()
        except Exception as e:
            print(f"Warning: Failed to remove file storage record: {e}")
    
    def cleanup_user_data(self):
        """Clean up all user data (for account deletion)"""
        try:
            # Remove all files
            if self.user_path.exists():
                shutil.rmtree(self.user_path)
            
            # Mark all file storage records as inactive
            db = next(get_database())
            db.query(UserFileStorage).filter(
                UserFileStorage.user_id == int(self.user_id)
            ).update({"is_active": False})
            db.commit()
            
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup user data: {str(e)}"
            )
