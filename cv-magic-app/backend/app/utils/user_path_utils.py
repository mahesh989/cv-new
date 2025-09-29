"""
User Path Utilities

Handles user-specific path generation for cv-analysis structure
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_user_base_path(user_email: Optional[str] = None) -> Path:
    """
    Get user-specific base path for cv-analysis
    
    Args:
        user_email: User email address (defaults to admin@admin.com)
        
    Returns:
        Path to user-specific cv-analysis directory
    """
    if not user_email:
        user_email = "admin@admin.com"
    
    # Create user folder name using raw email
    user_folder = f"user_{user_email}"
    
    # Return path: user/{user_folder}/cv-analysis
    base_path = Path("user") / user_folder / "cv-analysis"
    
    logger.debug(f"Generated user base path: {base_path} for email: {user_email}")
    return base_path

def ensure_user_directories(user_email: Optional[str] = None) -> Path:
    """
    Ensure user-specific directories exist
    
    Args:
        user_email: User email address (defaults to admin@admin.com)
        
    Returns:
        Path to user-specific cv-analysis directory
    """
    base_path = get_user_base_path(user_email)
    
    # Create all required subdirectories
    directories_to_create = [
        base_path,
        base_path / "applied_companies",
        base_path / "saved_jobs",
        base_path / "uploads"
    ]
    
    for directory in directories_to_create:
        directory.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"✅ Ensured user directories exist: {base_path}")
    return base_path

def get_user_company_path(user_email: Optional[str], company: str) -> Path:
    """
    Get user-specific company directory path
    
    Args:
        user_email: User email address
        company: Company name
        
    Returns:
        Path to company-specific directory
    """
    base_path = get_user_base_path(user_email)
    return base_path / "applied_companies" / company

def get_user_saved_jobs_path(user_email: Optional[str] = None) -> Path:
    """
    Get user-specific saved_jobs.json path
    
    Args:
        user_email: User email address
        
    Returns:
        Path to saved_jobs.json file
    """
    base_path = get_user_base_path(user_email)
    return base_path / "saved_jobs" / "saved_jobs.json"

def get_user_uploads_path(user_email: Optional[str] = None) -> Path:
    """
    Get user-specific uploads directory path
    
    Args:
        user_email: User email address
        
    Returns:
        Path to uploads directory
    """
    base_path = get_user_base_path(user_email)
    return base_path / "uploads"
