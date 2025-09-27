"""
User-aware analysis service for file system restructuring
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.cv import CVAnalysis
from app.services.user_file_manager import UserFileManager
from app.services.user_api_key_service import UserAPIKeyService
from app.database import get_database


class UserAnalysisService:
    """User-aware analysis service"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.file_manager = UserFileManager(user_id)
        self.api_key_service = UserAPIKeyService(user_id)
    
    def save_skills_analysis(self, cv_id: int, analysis_data: Dict[str, Any]) -> str:
        """Save skills analysis results for user"""
        try:
            # Generate filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"skills_analysis_{timestamp}.json"
            
            # Save to user's analysis directory
            file_path = self.file_manager.get_user_analysis_path("skills", filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            # Save to database
            db = next(get_database())
            analysis_record = CVAnalysis(
                cv_id=cv_id,
                user_id=int(self.user_id),
                technical_skills=json.dumps(analysis_data.get("technical_skills", [])),
                soft_skills=json.dumps(analysis_data.get("soft_skills", [])),
                domain_keywords=json.dumps(analysis_data.get("domain_keywords", [])),
                experience_years=analysis_data.get("experience_years"),
                education=analysis_data.get("education"),
                analysis_version="1.0",
                analysis_model=analysis_data.get("model", "gpt-3.5-turbo")
            )
            
            db.add(analysis_record)
            db.commit()
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save skills analysis: {str(e)}"
            )
    
    def save_recommendations(self, cv_id: int, recommendations: Dict[str, Any]) -> str:
        """Save AI recommendations for user"""
        try:
            # Generate filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"recommendations_{timestamp}.json"
            
            # Save to user's recommendations directory
            file_path = self.file_manager.get_user_analysis_path("recommendations", filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save recommendations: {str(e)}"
            )
    
    def save_analysis_results(self, cv_id: int, results: Dict[str, Any]) -> str:
        """Save complete analysis results for user"""
        try:
            # Generate filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_results_{timestamp}.json"
            
            # Save to user's results directory
            file_path = self.file_manager.get_user_analysis_path("results", filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save analysis results: {str(e)}"
            )
    
    def get_user_analyses(self, cv_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all analyses for user"""
        try:
            db = next(get_database())
            query = db.query(CVAnalysis).filter(CVAnalysis.user_id == int(self.user_id))
            
            if cv_id:
                query = query.filter(CVAnalysis.cv_id == cv_id)
            
            analyses = query.order_by(CVAnalysis.created_at.desc()).all()
            
            return [
                {
                    "id": analysis.id,
                    "cv_id": analysis.cv_id,
                    "technical_skills": json.loads(analysis.technical_skills) if analysis.technical_skills else [],
                    "soft_skills": json.loads(analysis.soft_skills) if analysis.soft_skills else [],
                    "domain_keywords": json.loads(analysis.domain_keywords) if analysis.domain_keywords else [],
                    "experience_years": analysis.experience_years,
                    "education": analysis.education,
                    "analysis_version": analysis.analysis_version,
                    "analysis_model": analysis.analysis_model,
                    "created_at": analysis.created_at.isoformat()
                }
                for analysis in analyses
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get analyses: {str(e)}"
            )
    
    def get_analysis_file(self, analysis_id: int) -> Dict[str, Any]:
        """Get analysis file content for user"""
        try:
            db = next(get_database())
            analysis = db.query(CVAnalysis).filter(
                CVAnalysis.id == analysis_id,
                CVAnalysis.user_id == int(self.user_id)
            ).first()
            
            if not analysis:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Analysis not found"
                )
            
            return {
                "id": analysis.id,
                "cv_id": analysis.cv_id,
                "technical_skills": json.loads(analysis.technical_skills) if analysis.technical_skills else [],
                "soft_skills": json.loads(analysis.soft_skills) if analysis.soft_skills else [],
                "domain_keywords": json.loads(analysis.domain_keywords) if analysis.domain_keywords else [],
                "experience_years": analysis.experience_years,
                "education": analysis.education,
                "analysis_version": analysis.analysis_version,
                "analysis_model": analysis.analysis_model,
                "created_at": analysis.created_at.isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get analysis: {str(e)}"
            )
    
    def save_job_comparison(self, cv_id: int, job_data: Dict[str, Any], 
                           comparison_results: Dict[str, Any]) -> str:
        """Save job comparison results for user"""
        try:
            # Generate filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"job_comparison_{timestamp}.json"
            
            # Save to user's comparisons directory
            file_path = self.file_manager.get_user_analysis_path("comparisons", filename)
            
            comparison_data = {
                "cv_id": cv_id,
                "job_data": job_data,
                "comparison_results": comparison_results,
                "timestamp": timestamp
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(comparison_data, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save job comparison: {str(e)}"
            )
    
    def get_user_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics for user"""
        try:
            db = next(get_database())
            
            # Get total analyses
            total_analyses = db.query(CVAnalysis).filter(
                CVAnalysis.user_id == int(self.user_id)
            ).count()
            
            # Get analyses by model
            analyses = db.query(CVAnalysis).filter(
                CVAnalysis.user_id == int(self.user_id)
            ).all()
            
            models = {}
            for analysis in analyses:
                model = analysis.analysis_model or "unknown"
                if model not in models:
                    models[model] = 0
                models[model] += 1
            
            return {
                "total_analyses": total_analyses,
                "analyses_by_model": models
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get analysis stats: {str(e)}"
            )
    
    def cleanup_user_analyses(self):
        """Clean up all analysis data for user (for account deletion)"""
        try:
            # Delete analysis files
            analysis_dirs = [
                self.file_manager.user_path / "analysis" / "skills",
                self.file_manager.user_path / "analysis" / "recommendations",
                self.file_manager.user_path / "analysis" / "results",
                self.file_manager.user_path / "analysis" / "comparisons"
            ]
            
            for analysis_dir in analysis_dirs:
                if analysis_dir.exists():
                    for file_path in analysis_dir.glob("*"):
                        if file_path.is_file():
                            file_path.unlink()
            
            # Delete database records
            db = next(get_database())
            db.query(CVAnalysis).filter(
                CVAnalysis.user_id == int(self.user_id)
            ).delete()
            
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup analyses: {str(e)}"
            )
