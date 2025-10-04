"""
CV Selection Module

Handles CV listing and selection functionality.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Constants
from app.utils.user_path_utils import get_user_uploads_path
from app.core.dependencies import get_current_user
from app.models.auth import UserData
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


class CVSelectionService:
    """Service class for handling CV selection and listing"""
    
    def __init__(self, user_email: str = "admin@admin.com"):
        self.user_email = user_email
    
    def list_cvs(self, current_user: UserData = None) -> Dict[str, Any]:
        """
        List all uploaded CVs with metadata
        
        Returns:
            Dict containing CV list and metadata
            
        Raises:
            HTTPException: If listing fails
        """
        try:
            cvs = []
            
            # Resolve user-specific uploads directory
            upload_dir = get_user_uploads_path(current_user.email) if current_user else get_user_uploads_path(self.user_email)
            if upload_dir.exists():
                for file_path in upload_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                        try:
                            stat = file_path.stat()
                            cvs.append({
                                "filename": file_path.name,
                                "size": stat.st_size,
                                "type": file_path.suffix[1:].upper(),
                                "uploaded_date": stat.st_mtime
                            })
                        except Exception as e:
                            logger.warning(f"Error reading file metadata for {file_path.name}: {e}")
                            continue
            
            # Sort by filename for consistency
            cvs.sort(key=lambda x: x['filename'])
            
            logger.info(f"Listed {len(cvs)} CV files")
            
            return {
                "uploaded_cvs": [cv["filename"] for cv in cvs],
                "cv_details": cvs,
                "total_count": len(cvs)
            }
            
        except Exception as e:
            logger.error(f"Error listing CVs: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing CVs: {str(e)}")
    
    def get_cv_info(self, filename: str) -> Dict[str, Any]:
        """
        Get information about a specific CV file
        
        Args:
            filename: Name of the CV file
            
        Returns:
            Dict containing CV file information
            
        Raises:
            HTTPException: If file not found
        """
        try:
            # Use user-specific path
            file_path = get_user_uploads_path(self.user_email) / filename
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="CV file not found")
            
            stat = file_path.stat()
            
            return {
                "filename": filename,
                "size": stat.st_size,
                "type": file_path.suffix[1:].upper(),
                "uploaded_date": stat.st_mtime,
                "exists": True
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting CV info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting CV info: {str(e)}")


# Global instance - will be initialized with proper user email when needed
cv_selection_service = None
