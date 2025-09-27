"""
User-specific data management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from app.models.auth import UserData
from app.core.dependencies import get_current_user
from app.services.user_file_manager import UserFileManager
from app.services.user_api_key_service import UserAPIKeyService
from app.services.user_settings_service import UserSettingsService
from app.services.user_activity_service import UserActivityService

router = APIRouter(prefix="/user", tags=["user-data"])
security = HTTPBearer()


# File Management Routes
@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "cv",
    subdirectory: str = "original",
    current_user: UserData = Depends(get_current_user)
):
    """Upload file for user"""
    try:
        file_manager = UserFileManager(current_user.id)
        
        # Read file data
        file_data = await file.read()
        
        # Save file
        file_path = file_manager.save_file(
            file_data=file_data,
            filename=file.filename,
            file_type=file_type,
            subdirectory=subdirectory,
            mime_type=file.content_type
        )
        
        # Log activity
        activity_service = UserActivityService(current_user.id)
        activity_service.log_activity(
            activity_type="file_upload",
            activity_data={
                "filename": file.filename,
                "file_type": file_type,
                "file_size": len(file_data)
            }
        )
        
        return {
            "message": "File uploaded successfully",
            "file_path": file_path,
            "filename": file.filename,
            "file_size": len(file_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/files")
async def list_user_files(
    file_type: Optional[str] = None,
    current_user: UserData = Depends(get_current_user)
):
    """List user files"""
    try:
        file_manager = UserFileManager(current_user.id)
        files = file_manager.list_user_files(file_type)
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.get("/files/storage-stats")
async def get_storage_stats(current_user: UserData = Depends(get_current_user)):
    """Get user storage statistics"""
    try:
        file_manager = UserFileManager(current_user.id)
        stats = file_manager.get_user_storage_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage stats: {str(e)}"
        )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    current_user: UserData = Depends(get_current_user)
):
    """Delete user file"""
    try:
        # This would need to be implemented with proper file ID lookup
        return {"message": "File deletion endpoint - to be implemented"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


# API Key Management Routes
@router.post("/api-keys")
async def set_api_key(
    request: dict,
    current_user: UserData = Depends(get_current_user)
):
    """Set API key for user"""
    try:
        provider = request.get("provider")
        api_key = request.get("api_key")
        
        if not provider or not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider and api_key are required"
            )
        
        api_key_service = UserAPIKeyService(current_user.id)
        success = api_key_service.set_api_key(provider, api_key)
        
        if success:
            # Log activity
            activity_service = UserActivityService(current_user.id)
            activity_service.log_activity(
                activity_type="api_key_set",
                activity_data={"provider": provider}
            )
            
            return {"message": f"API key set for {provider}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to set API key"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set API key: {str(e)}"
        )


@router.get("/api-keys")
async def get_api_keys(current_user: UserData = Depends(get_current_user)):
    """Get user API keys (without actual key values)"""
    try:
        api_key_service = UserAPIKeyService(current_user.id)
        keys = api_key_service.get_all_api_keys()
        return {"api_keys": keys}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API keys: {str(e)}"
        )


@router.post("/api-keys/{provider}/validate")
async def validate_api_key(
    provider: str,
    current_user: UserData = Depends(get_current_user)
):
    """Validate API key for provider"""
    try:
        api_key_service = UserAPIKeyService(current_user.id)
        is_valid = api_key_service.validate_api_key(provider)
        
        return {"provider": provider, "is_valid": is_valid}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate API key: {str(e)}"
        )


@router.delete("/api-keys/{provider}")
async def delete_api_key(
    provider: str,
    current_user: UserData = Depends(get_current_user)
):
    """Delete API key for provider"""
    try:
        api_key_service = UserAPIKeyService(current_user.id)
        success = api_key_service.delete_api_key(provider)
        
        if success:
            # Log activity
            activity_service = UserActivityService(current_user.id)
            activity_service.log_activity(
                activity_type="api_key_deleted",
                activity_data={"provider": provider}
            )
            
            return {"message": f"API key deleted for {provider}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete API key: {str(e)}"
        )


# Settings Routes
@router.get("/settings")
async def get_user_settings(current_user: UserData = Depends(get_current_user)):
    """Get user settings"""
    try:
        settings_service = UserSettingsService(current_user.id)
        settings = settings_service.get_settings()
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}"
        )


@router.put("/settings")
async def update_user_settings(
    settings_data: Dict[str, Any],
    current_user: UserData = Depends(get_current_user)
):
    """Update user settings"""
    try:
        settings_service = UserSettingsService(current_user.id)
        updated_settings = settings_service.update_settings(settings_data)
        
        # Log activity
        activity_service = UserActivityService(current_user.id)
        activity_service.log_activity(
            activity_type="settings_updated",
            activity_data={"updated_fields": list(settings_data.keys())}
        )
        
        return updated_settings
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.put("/settings/preferred-model")
async def update_preferred_model(
    model: str,
    current_user: UserData = Depends(get_current_user)
):
    """Update preferred AI model"""
    try:
        settings_service = UserSettingsService(current_user.id)
        success = settings_service.update_preferred_model(model)
        
        if success:
            return {"message": f"Preferred model updated to {model}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update preferred model"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferred model: {str(e)}"
        )


# Activity Routes
@router.get("/activities")
async def get_user_activities(
    limit: int = 100,
    offset: int = 0,
    current_user: UserData = Depends(get_current_user)
):
    """Get user activities"""
    try:
        activity_service = UserActivityService(current_user.id)
        activities = activity_service.get_user_activities(limit, offset)
        return {"activities": activities}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activities: {str(e)}"
        )


@router.get("/activities/stats")
async def get_activity_stats(current_user: UserData = Depends(get_current_user)):
    """Get user activity statistics"""
    try:
        activity_service = UserActivityService(current_user.id)
        stats = activity_service.get_activity_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity stats: {str(e)}"
        )
