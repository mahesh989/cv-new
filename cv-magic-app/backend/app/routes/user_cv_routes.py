"""
User-aware CV routes for file system restructuring
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from app.models.auth import UserData
from app.core.dependencies import get_current_user
from app.services.user_cv_service import UserCVService

router = APIRouter(prefix="/user/cv", tags=["user-cv"])
security = HTTPBearer()


@router.get("/stats")
async def get_cv_stats(current_user: UserData = Depends(get_current_user)):
    """Get CV statistics for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        stats = cv_service.get_user_cv_stats()
        
        return {"stats": stats}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get CV stats: {str(e)}"
        )


@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    current_user: UserData = Depends(get_current_user)
):
    """Upload CV for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        result = await cv_service.upload_cv(file, title, description)
        
        return {
            "message": "CV uploaded successfully",
            "cv": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload CV: {str(e)}"
        )


@router.get("/list")
async def list_user_cvs(current_user: UserData = Depends(get_current_user)):
    """List all CVs for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        cvs = cv_service.get_user_cvs()
        
        return {"cvs": cvs}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list CVs: {str(e)}"
        )


@router.get("/{cv_id}")
async def get_cv(
    cv_id: int,
    current_user: UserData = Depends(get_current_user)
):
    """Get specific CV for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        cv = cv_service.get_cv_by_id(cv_id)
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return {"cv": cv}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get CV: {str(e)}"
        )


@router.delete("/{cv_id}")
async def delete_cv(
    cv_id: int,
    current_user: UserData = Depends(get_current_user)
):
    """Delete CV for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        success = cv_service.delete_cv(cv_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return {"message": "CV deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete CV: {str(e)}"
        )


@router.get("/{cv_id}/download")
async def download_cv(
    cv_id: int,
    current_user: UserData = Depends(get_current_user)
):
    """Download CV file for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        file_content = cv_service.get_cv_file_content(cv_id)
        
        # Get CV info for filename
        cv = cv_service.get_cv_by_id(cv_id)
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        from fastapi.responses import Response
        return Response(
            content=file_content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={cv['original_filename']}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download CV: {str(e)}"
        )


@router.post("/{cv_id}/tailored")
async def save_tailored_cv(
    cv_id: int,
    tailored_content: str,
    filename: Optional[str] = None,
    current_user: UserData = Depends(get_current_user)
):
    """Save tailored CV for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        file_path = cv_service.save_tailored_cv(cv_id, tailored_content, filename)
        
        return {
            "message": "Tailored CV saved successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save tailored CV: {str(e)}"
        )


@router.put("/{cv_id}/analysis")
async def update_cv_analysis(
    cv_id: int,
    analysis_data: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Update CV with analysis results for authenticated user"""
    try:
        cv_service = UserCVService(current_user.id)
        success = cv_service.update_cv_analysis(cv_id, analysis_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return {"message": "CV analysis updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update CV analysis: {str(e)}"
        )


