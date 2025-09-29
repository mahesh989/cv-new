"""
Directory Utilities

Provides utilities for ensuring required directories exist for the CV analysis system.
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def ensure_cv_analysis_directories(additional_dirs: Optional[List[Path]] = None, user_email: str = "admin@admin.com") -> bool:
    """
    Ensure all required cv-analysis directories exist for a user.
    
    Args:
        additional_dirs: Optional list of additional directories to create
        user_email: User email address
        
    Returns:
        True if all directories were created successfully, False otherwise
    """
    try:
        from app.utils.user_path_utils import get_user_base_path
        cv_analysis_base = get_user_base_path(user_email)
        
        # Core required directories
        required_directories = [
            cv_analysis_base,
            cv_analysis_base / "applied_companies",
            cv_analysis_base / "cvs",
            cv_analysis_base / "cvs" / "original",
            cv_analysis_base / "cvs" / "tailored",
            cv_analysis_base / "saved_jobs",
            cv_analysis_base / "uploads"
        ]
        
        # Add any additional directories if provided
        if additional_dirs:
            required_directories.extend(additional_dirs)
        
        # Create all directories
        for directory in required_directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"✅ Ensured directory exists: {directory}")
        
        logger.info(f"✅ All cv-analysis directories ensured ({len(required_directories)} directories)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create cv-analysis directories: {e}")
        return False


def ensure_company_directory(company_name: str, user_email: str = "admin@admin.com") -> Path:
    """
    Ensure a company-specific directory exists under applied_companies.
    
    Args:
        company_name: Name of the company
        user_email: User email address
        
    Returns:
        Path to the company directory
    """
    try:
        # First ensure base directories exist
        ensure_cv_analysis_directories(user_email=user_email)
        
        # Create company-specific directory
        from app.utils.user_path_utils import get_user_base_path
        company_dir = get_user_base_path(user_email) / "applied_companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Company directory ensured: {company_dir}")
        return company_dir
        
    except Exception as e:
        logger.error(f"❌ Failed to create company directory for {company_name}: {e}")
        raise


def ensure_cv_directories(user_email: str = "admin@admin.com") -> bool:
    """
    Ensure CV processing directories exist.
    
    Args:
        user_email: User email address
        
    Returns:
        True if directories were created successfully
    """
    from app.utils.user_path_utils import get_user_base_path
    base_path = get_user_base_path(user_email)
    return ensure_cv_analysis_directories([
        base_path / "cvs" / "original",
        base_path / "cvs" / "tailored"
    ], user_email=user_email)


def ensure_job_tracking_directories(user_email: str = "admin@admin.com") -> bool:
    """
    Ensure job tracking directories exist.
    
    Args:
        user_email: User email address
        
    Returns:
        True if directories were created successfully
    """
    from app.utils.user_path_utils import get_user_base_path
    base_path = get_user_base_path(user_email)
    return ensure_cv_analysis_directories([
        base_path / "saved_jobs"
    ], user_email=user_email)


def ensure_upload_directories(user_email: str = "admin@admin.com") -> bool:
    """
    Ensure upload directories exist.
    
    Args:
        user_email: User email address
        
    Returns:
        True if directories were created successfully
    """
    from app.utils.user_path_utils import get_user_base_path
    base_path = get_user_base_path(user_email)
    return ensure_cv_analysis_directories([
        base_path / "uploads"
    ], user_email=user_email)
