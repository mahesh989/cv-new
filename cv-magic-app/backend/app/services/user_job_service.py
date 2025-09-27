"""
User-aware job service for file system restructuring
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.cv import JobApplication, JobComparison
from app.services.user_file_manager import UserFileManager
from app.database import get_database


class UserJobService:
    """User-aware job service"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.file_manager = UserFileManager(user_id)
    
    def save_job_description(self, job_data: Dict[str, Any]) -> str:
        """Save job description for user"""
        try:
            # Generate filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            company = job_data.get("company", "unknown").replace(" ", "_").lower()
            filename = f"{company}_job_{timestamp}.json"
            
            # Save to user's job descriptions directory
            file_path = self.file_manager.get_user_job_path("descriptions", filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save job description: {str(e)}"
            )
    
    def save_job_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save job application for user"""
        try:
            db = next(get_database())
            
            # Create job application record
            job_application = JobApplication(
                user_id=int(self.user_id),
                cv_id=application_data.get("cv_id"),
                job_title=application_data["job_title"],
                company=application_data["company"],
                job_url=application_data.get("job_url"),
                job_description=application_data.get("job_description"),
                application_date=datetime.now(timezone.utc),
                status=application_data.get("status", "applied"),
                notes=application_data.get("notes")
            )
            
            db.add(job_application)
            db.commit()
            db.refresh(job_application)
            
            # Save to file as well
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"application_{job_application.id}_{timestamp}.json"
            file_path = self.file_manager.get_user_job_path("applications", filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(application_data, f, indent=2, ensure_ascii=False)
            
            return {
                "id": job_application.id,
                "job_title": job_application.job_title,
                "company": job_application.company,
                "status": job_application.status,
                "application_date": job_application.application_date.isoformat(),
                "file_path": str(file_path)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save job application: {str(e)}"
            )
    
    def get_user_job_applications(self) -> List[Dict[str, Any]]:
        """Get all job applications for user"""
        try:
            db = next(get_database())
            applications = db.query(JobApplication).filter(
                JobApplication.user_id == int(self.user_id)
            ).order_by(JobApplication.application_date.desc()).all()
            
            return [
                {
                    "id": app.id,
                    "cv_id": app.cv_id,
                    "job_title": app.job_title,
                    "company": app.company,
                    "job_url": app.job_url,
                    "status": app.status,
                    "notes": app.notes,
                    "match_score": app.match_score,
                    "application_date": app.application_date.isoformat(),
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat()
                }
                for app in applications
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get job applications: {str(e)}"
            )
    
    def update_job_application_status(self, application_id: int, status: str, 
                                    notes: Optional[str] = None) -> bool:
        """Update job application status for user"""
        try:
            db = next(get_database())
            application = db.query(JobApplication).filter(
                JobApplication.id == application_id,
                JobApplication.user_id == int(self.user_id)
            ).first()
            
            if not application:
                return False
            
            application.status = status
            if notes:
                application.notes = notes
            application.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update job application: {str(e)}"
            )
    
    def save_job_match(self, cv_id: int, job_data: Dict[str, Any], 
                      match_results: Dict[str, Any]) -> str:
        """Save job match results for user"""
        try:
            # Generate filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            company = job_data.get("company", "unknown").replace(" ", "_").lower()
            filename = f"match_{company}_{timestamp}.json"
            
            # Save to user's job matches directory
            file_path = self.file_manager.get_user_job_path("matches", filename)
            
            match_data = {
                "cv_id": cv_id,
                "job_data": job_data,
                "match_results": match_results,
                "timestamp": timestamp
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save job match: {str(e)}"
            )
    
    def get_user_job_stats(self) -> Dict[str, Any]:
        """Get job statistics for user"""
        try:
            db = next(get_database())
            
            # Get total applications
            total_applications = db.query(JobApplication).filter(
                JobApplication.user_id == int(self.user_id)
            ).count()
            
            # Get applications by status
            applications = db.query(JobApplication).filter(
                JobApplication.user_id == int(self.user_id)
            ).all()
            
            status_counts = {}
            for app in applications:
                status = app.status or "unknown"
                if status not in status_counts:
                    status_counts[status] = 0
                status_counts[status] += 1
            
            # Get applications with match scores
            matched_applications = [app for app in applications if app.match_score is not None]
            avg_match_score = sum(app.match_score for app in matched_applications) / len(matched_applications) if matched_applications else 0
            
            return {
                "total_applications": total_applications,
                "applications_by_status": status_counts,
                "matched_applications": len(matched_applications),
                "average_match_score": round(avg_match_score, 2) if matched_applications else None
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get job stats: {str(e)}"
            )
    
    def cleanup_user_jobs(self):
        """Clean up all job data for user (for account deletion)"""
        try:
            # Delete job files
            job_dirs = [
                self.file_manager.user_path / "jobs" / "saved",
                self.file_manager.user_path / "jobs" / "applications",
                self.file_manager.user_path / "jobs" / "descriptions",
                self.file_manager.user_path / "jobs" / "matches"
            ]
            
            for job_dir in job_dirs:
                if job_dir.exists():
                    for file_path in job_dir.glob("*"):
                        if file_path.is_file():
                            file_path.unlink()
            
            # Delete database records
            db = next(get_database())
            db.query(JobApplication).filter(
                JobApplication.user_id == int(self.user_id)
            ).delete()
            
            db.query(JobComparison).filter(
                JobComparison.user_id == int(self.user_id)
            ).delete()
            
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup jobs: {str(e)}"
            )
