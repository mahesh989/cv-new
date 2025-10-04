"""Legacy Path Migration Script

This script migrates files from the old flat directory structure to the new user-scoped structure.
It also ensures all files use the timestamped naming convention.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_legacy_paths(legacy_base: str = "cv-analysis", user_email: str = "test@example.com"):
    """
    Migrate files from legacy path structure to new user-scoped structure.
    
    Args:
        legacy_base: Base directory of legacy files
        user_email: User email for new path structure
    """
    try:
        from app.utils.user_path_utils import get_user_base_path
        from app.utils.timestamp_utils import TimestampUtils
        
        legacy_path = Path(legacy_base)
        if not legacy_path.exists():
            logger.info("✅ No legacy path found - nothing to migrate")
            return
            
        # Get new base path
        new_base = get_user_base_path(user_email)
        
        # Create required directories
        required_dirs = [
            new_base / "applied_companies",
            new_base / "cvs" / "original",
            new_base / "cvs" / "tailored",
            new_base / "saved_jobs",
            new_base / "uploads"
        ]
        
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Find all JSON files in legacy structure
        legacy_files = list(legacy_path.rglob("*.json"))
        legacy_files.extend(legacy_path.rglob("*.txt"))
        
        for old_file in legacy_files:
            try:
                # Determine new path based on file type
                if "skills_analysis" in old_file.name:
                    # Get company name
                    company = old_file.parent.name
                    new_dir = new_base / "applied_companies" / company
                    new_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create timestamped name if needed
                    if not TimestampUtils.is_timestamped_filename(old_file.name):
                        timestamp = datetime.fromtimestamp(old_file.stat().st_mtime).strftime("%Y%m%d_%H%M%S")
                        new_name = f"{company}_skills_analysis_{timestamp}.json"
                    else:
                        new_name = old_file.name
                        
                    new_path = new_dir / new_name
                
                elif old_file.name in ["original_cv.json", "original_cv.txt"]:
                    new_path = new_base / "cvs" / "original" / old_file.name
                    
                elif "_tailored_cv" in old_file.name:
                    new_path = new_base / "cvs" / "tailored" / old_file.name
                    
                elif old_file.name == "saved_jobs.json":
                    new_path = new_base / "saved_jobs" / old_file.name
                    
                else:
                    # Handle other analysis files
                    company = old_file.parent.name
                    new_dir = new_base / "applied_companies" / company
                    new_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create timestamped name if needed
                    if not TimestampUtils.is_timestamped_filename(old_file.name):
                        timestamp = datetime.fromtimestamp(old_file.stat().st_mtime).strftime("%Y%m%d_%H%M%S")
                        base_name = old_file.stem
                        new_name = f"{base_name}_{timestamp}{old_file.suffix}"
                    else:
                        new_name = old_file.name
                        
                    new_path = new_dir / new_name
                
                # Copy file to new location
                new_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old_file, new_path)
                logger.info(f"✅ Migrated: {old_file} -> {new_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to migrate {old_file}: {e}")
                continue
        
        # Verify migration
        from app.utils.path_validator import validate_required_structure
        if validate_required_structure(new_base, user_email):
            logger.info("✅ Migration completed and verified")
            
            # Optionally remove legacy directory
            response = input("Remove legacy directory? [y/N]: ").lower()
            if response == 'y':
                shutil.rmtree(legacy_path)
                logger.info(f"✅ Removed legacy directory: {legacy_path}")
        else:
            logger.error("❌ Migration verification failed")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_legacy_paths()