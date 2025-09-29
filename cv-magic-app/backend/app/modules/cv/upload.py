"""
CV Upload Module

Handles CV file upload functionality with validation and processing.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Constants
from app.utils.user_path_utils import get_user_uploads_path
UPLOAD_DIR = get_user_uploads_path("admin@admin.com")  # TODO: Get from user context
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class CVUploadService:
    """Service class for handling CV uploads"""
    
    @staticmethod
    async def upload_cv(cv: UploadFile) -> Dict[str, Any]:
        """
        Upload a CV file with validation and processing
        
        Args:
            cv: The uploaded file
            
        Returns:
            Dict containing upload result
            
        Raises:
            HTTPException: If upload fails
        """
        if not cv.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Validate file extension
        file_extension = Path(cv.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        try:
            # Read and validate file size
            file_content = await cv.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail="File too large. Maximum size is 10MB"
                )
            
            # Save file to upload directory
            file_path = UPLOAD_DIR / cv.filename
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            logger.info(f"CV uploaded successfully: {cv.filename} ({len(file_content)} bytes)")
            
            return {
                "message": "CV uploaded successfully",
                "filename": cv.filename,
                "size": len(file_content),
                "type": file_extension[1:].upper()
            }
            
        except Exception as e:
            logger.error(f"Error uploading CV: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading CV: {str(e)}")


# Global instance
cv_upload_service = CVUploadService()
