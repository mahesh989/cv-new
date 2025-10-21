"""
Profile Service

Handles user profile operations: save, load, update, delete
Manages profile files at user/{email}/profile.json
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.profile import (
    UserProfile, 
    ProfileCreateRequest, 
    ProfileUpdateRequest,
    ProfileResponse
)
from app.utils.user_path_utils import get_user_base_path

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profiles"""
    
    def __init__(self):
        self.profile_filename = "profile.json"
    
    def _get_profile_path(self, user_email: str) -> Path:
        """Get the profile file path for a user"""
        user_base_path = get_user_base_path(user_email)
        return user_base_path / self.profile_filename
    
    def _ensure_user_directory(self, user_email: str) -> Path:
        """Ensure user directory exists"""
        user_base_path = get_user_base_path(user_email)
        user_base_path.mkdir(parents=True, exist_ok=True)
        return user_base_path
    
    def profile_exists(self, user_email: str) -> bool:
        """Check if profile exists for user"""
        try:
            profile_path = self._get_profile_path(user_email)
            return profile_path.exists() and profile_path.is_file()
        except Exception as e:
            logger.error(f"Error checking profile existence for {user_email}: {e}")
            return False
    
    def load_profile(self, user_email: str) -> Optional[UserProfile]:
        """Load user profile from file"""
        try:
            profile_path = self._get_profile_path(user_email)
            
            if not profile_path.exists():
                logger.info(f"Profile not found for user: {user_email}")
                return None
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            if 'created_at' in profile_data and isinstance(profile_data['created_at'], str):
                profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
            if 'updated_at' in profile_data and isinstance(profile_data['updated_at'], str):
                profile_data['updated_at'] = datetime.fromisoformat(profile_data['updated_at'])
            
            profile = UserProfile(**profile_data)
            logger.info(f"✅ Loaded profile for user: {user_email}")
            return profile
            
        except Exception as e:
            logger.error(f"Error loading profile for {user_email}: {e}")
            return None
    
    def save_profile(self, profile: UserProfile) -> bool:
        """Save user profile to file"""
        try:
            # Ensure user directory exists
            self._ensure_user_directory(profile.user_email)
            
            profile_path = self._get_profile_path(profile.user_email)
            
            # Convert to dict and handle datetime serialization
            profile_data = profile.dict()
            profile_data['created_at'] = profile.created_at.isoformat()
            profile_data['updated_at'] = profile.updated_at.isoformat()
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved profile for user: {profile.user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile for {profile.user_email}: {e}")
            return False
    
    def create_profile(self, request: ProfileCreateRequest) -> ProfileResponse:
        """Create a new user profile (overwrites existing if any)"""
        try:
            # Allow overwriting existing profiles
            if self.profile_exists(request.user_email):
                logger.info(f"Profile exists for {request.user_email}, overwriting...")
            
            # Create new profile
            now = datetime.now()
            profile = UserProfile(
                user_email=request.user_email,
                full_name=request.full_name,
                email=request.email,
                phone=request.phone,
                location=request.location,
                linkedin_url=request.linkedin_url,
                github_url=request.github_url,
                portfolio_url=request.portfolio_url,
                website_url=request.website_url,
                created_at=now,
                updated_at=now
            )
            
            # Save profile
            if self.save_profile(profile):
                return ProfileResponse(
                    success=True,
                    message="Profile created successfully",
                    profile=profile
                )
            else:
                return ProfileResponse(
                    success=False,
                    message="Failed to save profile"
                )
                
        except Exception as e:
            logger.error(f"Error creating profile for {request.user_email}: {e}")
            return ProfileResponse(
                success=False,
                message=f"Error creating profile: {str(e)}"
            )
    
    def update_profile(self, user_email: str, request: ProfileUpdateRequest) -> ProfileResponse:
        """Update existing user profile"""
        try:
            # Load existing profile
            existing_profile = self.load_profile(user_email)
            if not existing_profile:
                return ProfileResponse(
                    success=False,
                    message=f"Profile not found for user: {user_email}"
                )
            
            # Update fields that are provided
            update_data = request.dict(exclude_unset=True)
            
            # Create updated profile
            updated_profile_data = existing_profile.dict()
            updated_profile_data.update(update_data)
            updated_profile_data['updated_at'] = datetime.now()
            
            # Ensure user_email doesn't change
            updated_profile_data['user_email'] = user_email
            
            updated_profile = UserProfile(**updated_profile_data)
            
            # Save updated profile
            if self.save_profile(updated_profile):
                return ProfileResponse(
                    success=True,
                    message="Profile updated successfully",
                    profile=updated_profile
                )
            else:
                return ProfileResponse(
                    success=False,
                    message="Failed to save updated profile"
                )
                
        except Exception as e:
            logger.error(f"Error updating profile for {user_email}: {e}")
            return ProfileResponse(
                success=False,
                message=f"Error updating profile: {str(e)}"
            )
    
    def delete_profile(self, user_email: str) -> ProfileResponse:
        """Delete user profile"""
        try:
            profile_path = self._get_profile_path(user_email)
            
            if not profile_path.exists():
                return ProfileResponse(
                    success=False,
                    message=f"Profile not found for user: {user_email}"
                )
            
            profile_path.unlink()
            logger.info(f"✅ Deleted profile for user: {user_email}")
            
            return ProfileResponse(
                success=True,
                message="Profile deleted successfully"
            )
            
        except Exception as e:
            logger.error(f"Error deleting profile for {user_email}: {e}")
            return ProfileResponse(
                success=False,
                message=f"Error deleting profile: {str(e)}"
            )
    
    def get_profile_for_cv_generation(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Get profile data formatted for CV generation"""
        try:
            profile = self.load_profile(user_email)
            if not profile:
                logger.warning(f"No profile found for CV generation: {user_email}")
                return None
            
            if not profile.is_complete():
                missing_fields = profile.get_missing_fields()
                logger.warning(f"Profile incomplete for CV generation: {user_email}, missing: {missing_fields}")
                return None
            
            return profile.to_cv_header_data()
            
        except Exception as e:
            logger.error(f"Error getting profile for CV generation {user_email}: {e}")
            return None
    
    def validate_profile_for_cv(self, user_email: str) -> ProfileResponse:
        """Validate if profile is ready for CV generation"""
        try:
            profile = self.load_profile(user_email)
            if not profile:
                return ProfileResponse(
                    success=False,
                    message="Profile not found. Please create your profile first.",
                    missing_fields=["profile"]
                )
            
            if not profile.is_complete():
                missing_fields = profile.get_missing_fields()
                return ProfileResponse(
                    success=False,
                    message=f"Profile incomplete. Please complete: {', '.join(missing_fields)}",
                    missing_fields=missing_fields
                )
            
            return ProfileResponse(
                success=True,
                message="Profile is complete and ready for CV generation",
                profile=profile
            )
            
        except Exception as e:
            logger.error(f"Error validating profile for CV {user_email}: {e}")
            return ProfileResponse(
                success=False,
                message=f"Error validating profile: {str(e)}"
            )


# Global instance
profile_service = ProfileService()
