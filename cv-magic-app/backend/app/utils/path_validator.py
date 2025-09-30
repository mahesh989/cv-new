"""Path Validation Utility

This module provides utilities for validating paths conform to the new user-scoped structure.
"""

from pathlib import Path
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

def validate_file_path(path: Path, user_email: Optional[str] = None) -> bool:
    """
    Validate that a file path follows the new user-scoped structure.
    
    Args:
        path: Path to validate
        user_email: Optional user email to check against
        
    Returns:
        True if path is valid, False otherwise
    """
    try:
        # Path must be absolute
        if not path.is_absolute():
            logger.warning(f"❌ Path must be absolute: {path}")
            return False
            
        # Check basic structure: must be under user/{user_email}/cv-analysis/
        parts = path.parts
        if len(parts) < 4:  # Need at least: /base/user/user_email/cv-analysis
            logger.warning(f"❌ Path too short (not in user directory): {path}")
            return False
            
        # Find user directory index
        try:
            user_idx = parts.index("user")
        except ValueError:
            logger.warning(f"❌ Path not under user directory: {path}")
            return False
            
        # Verify user email directory format
        if not parts[user_idx + 1].startswith("user_"):
            logger.warning(f"❌ Invalid user directory format: {parts[user_idx + 1]}")
            return False
            
        # Check specific user if provided
        if user_email:
            expected_dir = f"user_{user_email}"
            if parts[user_idx + 1] != expected_dir:
                logger.warning(f"❌ Wrong user directory. Expected: {expected_dir}, got: {parts[user_idx + 1]}")
                return False
        
        # Verify cv-analysis
        if parts[user_idx + 2] != "cv-analysis":
            logger.warning(f"❌ Not in cv-analysis directory: {path}")
            return False
            
        # For files, verify they use timestamped format
        if path.is_file() or path.suffix:  # Has extension = intended to be file
            from app.utils.timestamp_utils import TimestampUtils
            filename = path.name
            if not TimestampUtils.is_timestamped_filename(filename):
                # Allow some non-timestamped files
                allowed_non_timestamped = [
                    "original_cv.json",
                    "original_cv.txt",
                    "saved_jobs.json"
                ]
                if filename not in allowed_non_timestamped:
                    logger.warning(f"❌ File does not use timestamp format: {filename}")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Path validation error: {str(e)}")
        return False

def validate_required_structure(base_dir: Path, user_email: str) -> bool:
    """
    Validate that a directory has all required subdirectories in the correct structure.
    
    Args:
        base_dir: Base directory to validate
        user_email: User email
        
    Returns:
        True if structure is valid, False otherwise
    """
    try:
        # Check base directory exists and is under user-scoped path
        if not validate_file_path(base_dir, user_email):
            return False
            
        # Required subdirectories
        required_dirs = [
            base_dir / "applied_companies",
            base_dir / "cvs" / "original",
            base_dir / "cvs" / "tailored",
            base_dir / "saved_jobs",
            base_dir / "uploads"
        ]
        
        # Check all required directories exist
        for directory in required_dirs:
            if not directory.exists() or not directory.is_dir():
                logger.warning(f"❌ Missing required directory: {directory}")
                return False
                
        # Check no legacy directories exist
        legacy_dirs = [
            base_dir.parent.parent / "cv-analysis"  # Old flat structure
        ]
        
        for legacy_dir in legacy_dirs:
            if legacy_dir.exists():
                logger.warning(f"❌ Legacy directory exists: {legacy_dir}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Structure validation error: {str(e)}")
        return False