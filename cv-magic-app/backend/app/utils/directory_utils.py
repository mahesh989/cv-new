"""
Directory Utilities

Provides utilities for ensuring required directories exist for the CV analysis system.
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def ensure_cv_analysis_directories(additional_dirs: Optional[List[Path]] = None) -> bool:
    """
    Ensure all required cv-analysis directories exist.
    
    Args:
        additional_dirs: Optional list of additional directories to create
        
    Returns:
        True if all directories were created successfully, False otherwise
    """
    try:
        cv_analysis_base = Path("cv-analysis")
        
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


def ensure_company_directory(company_name: str) -> Path:
    """
    Ensure a company-specific directory exists under applied_companies.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Path to the company directory
    """
    try:
        # First ensure base directories exist
        ensure_cv_analysis_directories()
        
        # Create company-specific directory
        company_dir = Path("cv-analysis") / "applied_companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Company directory ensured: {company_dir}")
        return company_dir
        
    except Exception as e:
        logger.error(f"❌ Failed to create company directory for {company_name}: {e}")
        raise


def ensure_cv_directories() -> bool:
    """
    Ensure CV processing directories exist.
    
    Returns:
        True if directories were created successfully
    """
    return ensure_cv_analysis_directories([
        Path("cv-analysis") / "cvs" / "original",
        Path("cv-analysis") / "cvs" / "tailored"
    ])


def ensure_job_tracking_directories() -> bool:
    """
    Ensure job tracking directories exist.
    
    Returns:
        True if directories were created successfully
    """
    return ensure_cv_analysis_directories([
        Path("cv-analysis") / "saved_jobs"
    ])


def ensure_upload_directories() -> bool:
    """
    Ensure upload directories exist.
    
    Returns:
        True if directories were created successfully
    """
    return ensure_cv_analysis_directories([
        Path("cv-analysis") / "uploads"
    ])
