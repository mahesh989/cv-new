"""
User Profile Models

Defines the data structure for user profiles stored in user/{email}/profile.json
"""

from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import Optional
from datetime import datetime


class UserProfile(BaseModel):
    """User profile data structure"""
    
    # Required fields
    user_email: EmailStr
    full_name: str
    email: EmailStr
    phone: str
    location: str
    
    # Optional fields - using str to allow any format
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    @validator('phone')
    def validate_phone(cls, v):
        """Basic phone validation - should contain digits and common separators"""
        if not v or len(v.strip()) < 5:
            raise ValueError('Phone number must be at least 5 characters')
        # Remove common separators and check if remaining chars are mostly digits
        clean_phone = ''.join(c for c in v if c.isdigit())
        if len(clean_phone) < 5:
            raise ValueError('Phone number must contain at least 5 digits')
        return v.strip()
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name"""
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()
    
    @validator('location')
    def validate_location(cls, v):
        """Validate location"""
        if not v or len(v.strip()) < 2:
            raise ValueError('Location must be at least 2 characters')
        return v.strip()
    
    @validator('email')
    def validate_email_format(cls, v):
        """Validate email format"""
        if not v or len(v.strip()) < 5:
            raise ValueError('Email must be at least 5 characters')
        if '@' not in v:
            raise ValueError('Email must contain @ symbol')
        return v.strip()
    
    def is_complete(self) -> bool:
        """Check if profile has all required fields"""
        required_fields = ['user_email', 'full_name', 'email', 'phone', 'location']
        return all(getattr(self, field) for field in required_fields)
    
    def get_missing_fields(self) -> list[str]:
        """Get list of missing required fields"""
        missing = []
        required_fields = ['user_email', 'full_name', 'email', 'phone', 'location']
        for field in required_fields:
            if not getattr(self, field):
                missing.append(field)
        return missing
    
    def to_cv_header_data(self) -> dict:
        """Convert profile to CV header format with clickable links"""
        return {
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'website_url': self.website_url,
        }
    
    def _format_url(self, url: str) -> str:
        """Format URL to be clickable (add https:// if missing)"""
        if not url:
            return url
        url = url.strip()
        if not url.startswith(('http://', 'https://', 'mailto:')):
            return f'https://{url}'
        return url
    
    def get_clickable_links(self) -> list[dict]:
        """Get list of clickable links for CV"""
        links = []
        
        if self.linkedin_url:
            links.append({
                'text': 'LinkedIn',
                'url': self._format_url(self.linkedin_url),
                'type': 'linkedin'
            })
        
        if self.github_url:
            links.append({
                'text': 'GitHub',
                'url': self._format_url(self.github_url),
                'type': 'github'
            })
        
        if self.portfolio_url:
            links.append({
                'text': 'Portfolio',
                'url': self._format_url(self.portfolio_url),
                'type': 'portfolio'
            })
        
        if self.website_url:
            links.append({
                'text': 'Website',
                'url': self._format_url(self.website_url),
                'type': 'website'
            })
        
        return links


class ProfileCreateRequest(BaseModel):
    """Request model for creating a profile"""
    user_email: EmailStr
    full_name: str
    email: EmailStr
    phone: str
    location: str
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    """Request model for updating a profile"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None


class ProfileResponse(BaseModel):
    """Response model for profile operations"""
    success: bool
    message: str
    profile: Optional[UserProfile] = None
    missing_fields: Optional[list[str]] = None
