"""
Profile Routes

API endpoints for user profile management
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional

from app.core.auth import verify_token
from app.core.dependencies import get_current_user
from app.models.auth import UserData
from app.models.profile import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
    ProfileResponse
)
from app.services.profile_service import profile_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: UserData = Depends(get_current_user)
):
    """Get current user's profile"""
    try:
        logger.info(f"📋 [PROFILE] Getting profile for user: {current_user.email}")
        
        profile = profile_service.load_profile(current_user.email)
        if not profile:
            return ProfileResponse(
                success=False,
                message="Profile not found. Please create your profile first."
            )
        
        return ProfileResponse(
            success=True,
            message="Profile retrieved successfully",
            profile=profile
        )
        
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error getting profile for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")


@router.post("", response_model=ProfileResponse)
async def create_profile(
    request: ProfileCreateRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Create a new profile for current user"""
    try:
        logger.info(f"📋 [PROFILE] Creating profile for user: {current_user.email}")
        
        # Ensure the user_email in request matches the authenticated user
        # (This ensures the profile belongs to the authenticated user)
        # The 'email' field can be different (for creating CVs for others)
        if request.user_email != current_user.email:
            raise HTTPException(
                status_code=403, 
                detail="Cannot create profile for different user"
            )
        
        result = profile_service.create_profile(request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"✅ [PROFILE] Profile created successfully for: {current_user.email}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error creating profile for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")


@router.put("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Update current user's profile"""
    try:
        logger.info(f"📋 [PROFILE] Updating profile for user: {current_user.email}")
        
        result = profile_service.update_profile(current_user.email, request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"✅ [PROFILE] Profile updated successfully for: {current_user.email}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error updating profile for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.delete("", response_model=ProfileResponse)
async def delete_profile(
    current_user: UserData = Depends(get_current_user)
):
    """Delete current user's profile"""
    try:
        logger.info(f"📋 [PROFILE] Deleting profile for user: {current_user.email}")
        
        result = profile_service.delete_profile(current_user.email)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"✅ [PROFILE] Profile deleted successfully for: {current_user.email}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error deleting profile for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting profile: {str(e)}")


@router.get("/exists", response_model=dict)
async def check_profile_exists(
    current_user: UserData = Depends(get_current_user)
):
    """Check if profile exists for current user"""
    try:
        logger.info(f"📋 [PROFILE] Checking profile existence for user: {current_user.email}")
        
        exists = profile_service.profile_exists(current_user.email)
        
        return {
            "success": True,
            "exists": exists,
            "user_email": current_user.email
        }
        
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error checking profile existence for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking profile existence: {str(e)}")


@router.get("/validate", response_model=ProfileResponse)
async def validate_profile_for_cv(
    current_user: UserData = Depends(get_current_user)
):
    """Validate if profile is ready for CV generation"""
    try:
        logger.info(f"📋 [PROFILE] Validating profile for CV generation: {current_user.email}")
        
        result = profile_service.validate_profile_for_cv(current_user.email)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error validating profile for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating profile: {str(e)}")


@router.get("/cv-data", response_model=dict)
async def get_profile_for_cv_generation(
    current_user: UserData = Depends(get_current_user)
):
    """Get profile data formatted for CV generation"""
    try:
        logger.info(f"📋 [PROFILE] Getting profile data for CV generation: {current_user.email}")
        
        cv_data = profile_service.get_profile_for_cv_generation(current_user.email)
        
        if not cv_data:
            raise HTTPException(
                status_code=404, 
                detail="Profile not found or incomplete. Please create/complete your profile first."
            )
        
        return {
            "success": True,
            "cv_data": cv_data,
            "user_email": current_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error getting profile for CV generation {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting profile for CV generation: {str(e)}")


# Admin endpoint for debugging (requires special permissions)
@router.get("/admin/{user_email}", response_model=ProfileResponse)
async def get_profile_admin(
    user_email: str,
    current_user: UserData = Depends(get_current_user)
):
    """Admin endpoint to get any user's profile (for debugging)"""
    try:
        # Only allow admin users or the user themselves
        if current_user.email != user_email and not getattr(current_user, 'is_admin', False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"📋 [PROFILE] Admin getting profile for user: {user_email}")
        
        profile = profile_service.load_profile(user_email)
        if not profile:
            return ProfileResponse(
                success=False,
                message=f"Profile not found for user: {user_email}"
            )
        
        return ProfileResponse(
            success=True,
            message="Profile retrieved successfully",
            profile=profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [PROFILE] Error getting profile admin for {user_email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")
