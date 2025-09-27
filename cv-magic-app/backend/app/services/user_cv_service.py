"""
User-aware CV service for file system restructuring
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.models.cv import CV
from app.models.user_data import UserFileStorage
from app.services.user_file_manager import UserFileManager
from app.database import get_database


class UserCVService:
    """User-aware CV service"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.file_manager = UserFileManager(user_id)
    
    async def upload_cv(self, file: UploadFile, title: Optional[str] = None, 
                       description: Optional[str] = None) -> Dict[str, Any]:
        """Upload CV for specific user"""
        try:
            # Read file data
            file_data = await file.read()
            
            # Generate unique filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            
            # Save to user-specific directory
            file_path = self.file_manager.save_file(
                file_data=file_data,
                filename=filename,
                file_type="cv",
                subdirectory="original",
                mime_type=file.content_type
            )
            
            # Create CV record in database
            db = next(get_database())
            cv_record = CV(
                user_id=int(self.user_id),
                filename=filename,
                original_filename=file.filename,
                title=title or file.filename,
                description=description,
                file_path=str(file_path),
                file_size=len(file_data),
                file_type=file.content_type or "application/octet-stream",
                is_active=True
            )
            
            db.add(cv_record)
            db.commit()
            db.refresh(cv_record)
            
            return {
                "id": cv_record.id,
                "filename": cv_record.filename,
                "original_filename": cv_record.original_filename,
                "title": cv_record.title,
                "file_path": cv_record.file_path,
                "file_size": cv_record.file_size,
                "created_at": cv_record.created_at.isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload CV: {str(e)}"
            )
    
    def get_user_cvs(self) -> List[Dict[str, Any]]:
        """Get all CVs for user"""
        try:
            db = next(get_database())
            cvs = db.query(CV).filter(
                CV.user_id == int(self.user_id),
                CV.is_active == True
            ).order_by(CV.created_at.desc()).all()
            
            return [
                {
                    "id": cv.id,
                    "filename": cv.filename,
                    "original_filename": cv.original_filename,
                    "title": cv.title,
                    "description": cv.description,
                    "file_size": cv.file_size,
                    "file_type": cv.file_type,
                    "is_analyzed": cv.analyzed_at is not None,
                    "analyzed_at": cv.analyzed_at.isoformat() if cv.analyzed_at else None,
                    "created_at": cv.created_at.isoformat(),
                    "updated_at": cv.updated_at.isoformat()
                }
                for cv in cvs
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get CVs: {str(e)}"
            )
    
    def get_cv_by_id(self, cv_id: int) -> Optional[Dict[str, Any]]:
        """Get specific CV by ID for user"""
        try:
            db = next(get_database())
            cv = db.query(CV).filter(
                CV.id == cv_id,
                CV.user_id == int(self.user_id),
                CV.is_active == True
            ).first()
            
            if not cv:
                return None
            
            return {
                "id": cv.id,
                "filename": cv.filename,
                "original_filename": cv.original_filename,
                "title": cv.title,
                "description": cv.description,
                "file_path": cv.file_path,
                "file_size": cv.file_size,
                "file_type": cv.file_type,
                "technical_skills": cv.technical_skills,
                "soft_skills": cv.soft_skills,
                "domain_keywords": cv.domain_keywords,
                "is_analyzed": cv.analyzed_at is not None,
                "analyzed_at": cv.analyzed_at.isoformat() if cv.analyzed_at else None,
                "created_at": cv.created_at.isoformat(),
                "updated_at": cv.updated_at.isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get CV: {str(e)}"
            )
    
    def delete_cv(self, cv_id: int) -> bool:
        """Delete CV for user"""
        try:
            db = next(get_database())
            cv = db.query(CV).filter(
                CV.id == cv_id,
                CV.user_id == int(self.user_id)
            ).first()
            
            if not cv:
                return False
            
            # Delete file from filesystem
            if os.path.exists(cv.file_path):
                os.remove(cv.file_path)
            
            # Mark as inactive in database
            cv.is_active = False
            db.commit()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete CV: {str(e)}"
            )
    
    def save_tailored_cv(self, cv_id: int, tailored_content: str, 
                        filename: Optional[str] = None) -> str:
        """Save tailored CV for user"""
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                filename = f"tailored_cv_{timestamp}.txt"
            
            # Save to user's tailored CV directory
            file_path = self.file_manager.get_user_cv_path(filename, is_tailored=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(tailored_content)
            
            # Update CV record with tailored path
            db = next(get_database())
            cv = db.query(CV).filter(
                CV.id == cv_id,
                CV.user_id == int(self.user_id)
            ).first()
            
            if cv:
                # Create a new CV record for the tailored version
                tailored_cv = CV(
                    user_id=int(self.user_id),
                    filename=filename,
                    original_filename=cv.original_filename,
                    title=f"Tailored: {cv.title}",
                    description="AI-tailored CV",
                    file_path=str(file_path),
                    file_size=len(tailored_content.encode('utf-8')),
                    file_type="text/plain",
                    is_active=True
                )
                
                db.add(tailored_cv)
                db.commit()
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save tailored CV: {str(e)}"
            )
    
    def get_cv_file_content(self, cv_id: int) -> bytes:
        """Get CV file content for user"""
        try:
            db = next(get_database())
            cv = db.query(CV).filter(
                CV.id == cv_id,
                CV.user_id == int(self.user_id),
                CV.is_active == True
            ).first()
            
            if not cv:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="CV not found"
                )
            
            # Read file content
            with open(cv.file_path, 'rb') as f:
                return f.read()
                
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV file not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read CV file: {str(e)}"
            )
    
    def update_cv_analysis(self, cv_id: int, analysis_data: Dict[str, Any]) -> bool:
        """Update CV with analysis results"""
        try:
            db = next(get_database())
            cv = db.query(CV).filter(
                CV.id == cv_id,
                CV.user_id == int(self.user_id)
            ).first()
            
            if not cv:
                return False
            
            # Update analysis fields
            if "technical_skills" in analysis_data:
                cv.technical_skills = analysis_data["technical_skills"]
            if "soft_skills" in analysis_data:
                cv.soft_skills = analysis_data["soft_skills"]
            if "domain_keywords" in analysis_data:
                cv.domain_keywords = analysis_data["domain_keywords"]
            
            cv.analyzed_at = datetime.now(timezone.utc)
            db.commit()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update CV analysis: {str(e)}"
            )
    
    def get_user_cv_stats(self) -> Dict[str, Any]:
        """Get CV statistics for user"""
        try:
            db = next(get_database())
            
            # Get total CVs
            total_cvs = db.query(CV).filter(
                CV.user_id == int(self.user_id),
                CV.is_active == True
            ).count()
            
            # Get analyzed CVs
            analyzed_cvs = db.query(CV).filter(
                CV.user_id == int(self.user_id),
                CV.is_active == True,
                CV.analyzed_at.isnot(None)
            ).count()
            
            # Get total file size
            cvs = db.query(CV).filter(
                CV.user_id == int(self.user_id),
                CV.is_active == True
            ).all()
            
            total_size = sum(cv.file_size for cv in cvs)
            
            return {
                "total_cvs": total_cvs,
                "analyzed_cvs": analyzed_cvs,
                "unanalyzed_cvs": total_cvs - analyzed_cvs,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get CV stats: {str(e)}"
            )
