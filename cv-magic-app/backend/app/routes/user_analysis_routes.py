"""
User-aware analysis routes for file system restructuring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from app.models.auth import UserData
from app.core.dependencies import get_current_user
from app.services.user_analysis_service import UserAnalysisService

router = APIRouter(prefix="/user/analysis", tags=["user-analysis"])
security = HTTPBearer()


@router.post("/skills/{cv_id}")
async def save_skills_analysis(
    cv_id: int,
    analysis_data: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Save skills analysis for authenticated user"""
    try:
        analysis_service = UserAnalysisService(current_user.id)
        file_path = analysis_service.save_skills_analysis(cv_id, analysis_data)
        
        return {
            "message": "Skills analysis saved successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save skills analysis: {str(e)}"
        )


@router.post("/recommendations/{cv_id}")
async def save_recommendations(
    cv_id: int,
    recommendations: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Save AI recommendations for authenticated user"""
    try:
        analysis_service = UserAnalysisService(current_user.id)
        file_path = analysis_service.save_recommendations(cv_id, recommendations)
        
        return {
            "message": "Recommendations saved successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recommendations: {str(e)}"
        )


@router.post("/results/{cv_id}")
async def save_analysis_results(
    cv_id: int,
    results: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Save complete analysis results for authenticated user"""
    try:
        analysis_service = UserAnalysisService(current_user.id)
        file_path = analysis_service.save_analysis_results(cv_id, results)
        
        return {
            "message": "Analysis results saved successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save analysis results: {str(e)}"
        )


@router.get("/list")
async def list_user_analyses(
    cv_id: Optional[int] = None,
    current_user: UserData = Depends(get_current_user)
):
    """Get all analyses for authenticated user"""
    try:
        analysis_service = UserAnalysisService(current_user.id)
        analyses = analysis_service.get_user_analyses(cv_id)
        
        return {"analyses": analyses}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}"
        )


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: int,
    current_user: UserData = Depends(get_current_user)
):
    """Get specific analysis for authenticated user"""
    try:
        analysis_service = UserAnalysisService(current_user.id)
        analysis = analysis_service.get_analysis_file(analysis_id)
        
        return {"analysis": analysis}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )


@router.post("/comparison/{cv_id}")
async def save_job_comparison(
    cv_id: int,
    job_data: Dict[str, Any],
    comparison_results: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Save job comparison results for authenticated user"""
    try:
        analysis_service = UserAnalysisService(current_user.id)
        file_path = analysis_service.save_job_comparison(cv_id, job_data, comparison_results)
        
        return {
            "message": "Job comparison saved successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save job comparison: {str(e)}"
        )


@router.get("/stats")
async def get_analysis_stats(current_user: UserData = Depends(get_current_user)):
    """Get analysis statistics for authenticated user"""
    try:
        analysis_service = UserAnalysisService(current_user.id)
        stats = analysis_service.get_user_analysis_stats()
        
        return {"stats": stats}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis stats: {str(e)}"
        )
