"""
User Path Utilities

Handles user-specific path generation for cv-analysis structure
"""

from pathlib import Path
from typing import Optional, Dict, Callable
import logging

logger = logging.getLogger(__name__)

def get_user_base_path(user_email: Optional[str] = None) -> Path:
    """
    Get user-specific base path for cv-analysis
    
    Args:
        user_email: User email address
        
    Returns:
        Path to user-specific cv-analysis directory
        
    Raises:
        ValueError: If no user email is provided
    """
    if not user_email:
        raise ValueError("User email must be provided")
    
    # Normalize email
    user_email = user_email.strip().lower()
    
    # Create user folder name using the actual email address
    # This is safe for modern filesystems and more readable
    user_folder = f"user_{user_email}"
    
    # Use standard user-scoped path structure: user/{user_folder}/cv-analysis
    base_path = Path("user") / user_folder / "cv-analysis"
    
    # Create the base path if it doesn't exist
    base_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"✅ User base path: {base_path} for {user_email}")
    return base_path

def ensure_user_directories(user_email: Optional[str] = None) -> Path:
    """
    Ensure user-specific directories exist
    
    Args:
        user_email: User email address
        
    Returns:
        Path to user-specific cv-analysis directory
    """
    base_path = get_user_base_path(user_email)
    
    # Create complete directory structure
    directories_to_create = [
        base_path,
        base_path / "applied_companies",
        base_path / "cvs" / "original",
        base_path / "cvs" / "tailored",
        base_path / "saved_jobs",
        base_path / "uploads"
    ]
    
    for directory in directories_to_create:
        directory.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"✅ Ensured user directories exist: {base_path}")
    return base_path

def validate_company_name(company: str) -> None:
    """Validate company name to prevent Unknown_Company and invalid names"""
    if not company:
        raise ValueError("Company name must be provided")
    if company.lower() in ["unknown_company", "unknown", "unknown_company_"]:
        raise ValueError("Invalid company name: Cannot use 'Unknown_Company' or variants")
    if any(char in company for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']):
        raise ValueError("Company name contains invalid characters")

def get_user_company_path(user_email: Optional[str], company: str) -> Path:
    """
    Get user-specific company directory path
    
    Args:
        user_email: User email address
        company: Company name
        
    Returns:
        Path to company-specific directory
    """
    validate_company_name(company)
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

def get_user_cv_paths(user_email: Optional[str] = None) -> Dict[str, Path]:
    """
    Get paths for CV-related directories
    
    Args:
        user_email: User email address
        
    Returns:
        Dictionary containing paths for original and tailored CVs
    """
    base_path = get_user_base_path(user_email)
    return {
        "original": base_path / "cvs" / "original",
        "tailored": base_path / "cvs" / "tailored"
    }

def get_user_company_analysis_paths(user_email: Optional[str], company: str) -> Dict[str, Callable[[str], Path]]:
    """
    Get all analysis-related paths for a company
    
    Args:
        user_email: User email address
        company: Company name
        
    Returns:
        Dictionary containing all analysis-related path generators
    """
    company_dir = get_user_company_path(user_email, company)
    return {
        "jd_original": lambda ts: company_dir / f"jd_original_{ts}.json",
        "job_info": lambda ts: company_dir / f"job_info_{company}_{ts}.json",
        "jd_analysis": lambda ts: company_dir / f"{company}_jd_analysis_{ts}.json",
        "cv_jd_matching": lambda ts: company_dir / f"{company}_cv_jd_matching_{ts}.json",
        "component_analysis": lambda ts: company_dir / f"{company}_component_analysis_{ts}.json",
        "skills_analysis": lambda ts: company_dir / f"{company}_skills_analysis_{ts}.json",
        "input_recommendation": lambda ts: company_dir / f"{company}_input_recommendation_{ts}.json",
        "ai_recommendation": lambda ts: company_dir / f"{company}_ai_recommendation_{ts}.json",
        "tailored_cv": lambda ts: get_user_cv_paths(user_email)["tailored"] / f"{company}_tailored_cv_{ts}.json"
    }

def verify_company_file_structure(company: str, user_email: str = "test@example.com", create_dirs: bool = True) -> Dict[str, Path]:
    """
    Verify and optionally create the complete file structure for a company
    
    Args:
        company: Company name
        user_email: User email
        create_dirs: Whether to create directories if they don't exist
        
    Returns:
        Dictionary of verified paths
    """
    # Validate company name
    validate_company_name(company)
    
    # Get all paths
    base_path = get_user_base_path(user_email)
    company_paths = get_user_company_analysis_paths(user_email, company)
    cv_paths = get_user_cv_paths(user_email)
    
    # Generate timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Verify/create directories
    required_dirs = [
        base_path / "applied_companies" / company,
        cv_paths["original"],
        cv_paths["tailored"],
        base_path / "saved_jobs",
        base_path / "uploads"
    ]
    
    if create_dirs:
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)
    
    # Generate all file paths
    paths = {
        "jd_original": company_paths["jd_original"](timestamp),
        "job_info": company_paths["job_info"](timestamp),
        "jd_analysis": company_paths["jd_analysis"](timestamp),
        "cv_jd_matching": company_paths["cv_jd_matching"](timestamp),
        "component_analysis": company_paths["component_analysis"](timestamp),
        "skills_analysis": company_paths["skills_analysis"](timestamp),
        "input_recommendation": company_paths["input_recommendation"](timestamp),
        "ai_recommendation": company_paths["ai_recommendation"](timestamp),
        "tailored_cv": company_paths["tailored_cv"](timestamp),
        "original_cv_txt": cv_paths["original"] / "original_cv.txt",
        "original_cv_json": cv_paths["original"] / "original_cv.json",
        "saved_jobs": base_path / "saved_jobs" / "saved_jobs.json"
    }
    
    return paths

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
