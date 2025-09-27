"""
User-aware job routes for file system restructuring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from app.models.auth import UserData
from app.core.dependencies import get_current_user
from app.services.user_job_service import UserJobService

router = APIRouter(prefix="/user/jobs", tags=["user-jobs"])
security = HTTPBearer()


@router.post("/description")
async def save_job_description(
    job_data: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Save job description for authenticated user"""
    try:
        job_service = UserJobService(current_user.id)
        file_path = job_service.save_job_description(job_data)
        
        return {
            "message": "Job description saved successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save job description: {str(e)}"
        )


@router.post("/application")
async def save_job_application(
    application_data: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Save job application for authenticated user"""
    try:
        job_service = UserJobService(current_user.id)
        result = job_service.save_job_application(application_data)
        
        return {
            "message": "Job application saved successfully",
            "application": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save job application: {str(e)}"
        )


@router.get("/applications")
async def list_job_applications(current_user: UserData = Depends(get_current_user)):
    """Get all job applications for authenticated user"""
    try:
        job_service = UserJobService(current_user.id)
        applications = job_service.get_user_job_applications()
        
        return {"applications": applications}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list job applications: {str(e)}"
        )


@router.put("/application/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str,
    notes: Optional[str] = None,
    current_user: UserData = Depends(get_current_user)
):
    """Update job application status for authenticated user"""
    try:
        job_service = UserJobService(current_user.id)
        success = job_service.update_job_application_status(application_id, status, notes)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        return {"message": "Application status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application status: {str(e)}"
        )


@router.post("/match/{cv_id}")
async def save_job_match(
    cv_id: int,
    job_data: Dict[str, Any],
    match_results: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Save job match results for authenticated user"""
    try:
        job_service = UserJobService(current_user.id)
        file_path = job_service.save_job_match(cv_id, job_data, match_results)
        
        return {
            "message": "Job match saved successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save job match: {str(e)}"
        )


@router.get("/stats")
async def get_job_stats(current_user: UserData = Depends(get_current_user)):
    """Get job statistics for authenticated user"""
    try:
        job_service = UserJobService(current_user.id)
        stats = job_service.get_user_job_stats()
        
        return {"stats": stats}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job stats: {str(e)}"
        )
