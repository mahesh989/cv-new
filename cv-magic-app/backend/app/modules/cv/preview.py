"""
CV Preview Module

Handles CV content extraction and preview functionality.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from ...services.cv_processor import cv_processor

logger = logging.getLogger(__name__)

class CVPreviewService:
    """Service class for handling CV preview and content extraction"""
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        from app.utils.user_path_utils import get_user_uploads_path
        self.upload_dir = get_user_uploads_path(user_email)
    
    def get_cv_content(self, filename: str) -> Dict[str, Any]:
        """
        Get CV text content with improved extraction
        
        Args:
            filename: Name of the CV file
            
        Returns:
            Dict containing CV content and metadata
            
        Raises:
            HTTPException: If extraction fails
        """
        try:
            file_path = self.upload_dir / filename
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="CV file not found")
            
            # Extract text using improved processor
            result = cv_processor.extract_text_from_file(file_path)
            
            if not result['success']:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to extract text: {result['error']}"
                )
            
            # Get file metadata
            stat = file_path.stat()
            
            logger.info(f"CV content extracted: {filename} ({len(result['text'])} characters)")
            
            return {
                "filename": filename,
                "content": result['text'],
                "metadata": result.get('metadata', {}),
                "file_info": {
                    "size": stat.st_size,
                    "type": file_path.suffix[1:].upper(),
                    "uploaded_date": stat.st_mtime
                },
                "extraction_info": {
                    "method": result.get('method', 'unknown'),
                    "character_count": len(result['text']),
                    "word_count": len(result['text'].split())
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extracting CV content: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error extracting CV content: {str(e)}")
    
def get_cv_preview(self, filename: str, max_length: int = 500) -> Dict[str, Any]:
        """
        Get CV content preview with customizable length
        
        Args:
            filename: Name of the CV file
            max_length: Maximum length of preview text
            
        Returns:
            Dict containing CV preview and metadata
            
        Raises:
            HTTPException: If extraction fails
        """
        try:
            file_path = self.upload_dir / filename
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="CV file not found")
            
            # Extract text
            result = cv_processor.extract_text_from_file(file_path)
            
            if not result['success']:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to extract text: {result['error']}"
                )
            
            # Generate preview
            full_text = result['text']
            preview = cv_processor.get_text_preview(full_text, max_length)
            
            # Extract basic info
            basic_info = cv_processor.extract_basic_info(full_text)
            
            logger.info(f"CV preview generated: {filename} ({len(preview)} characters)")
            
            return {
                "filename": filename,
                "preview": preview,
                "full_length": len(full_text),
                "preview_length": len(preview),
                "is_truncated": len(full_text) > max_length,
                "basic_info": basic_info,
                "extraction_method": result.get('method', 'unknown')
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating CV preview: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating CV preview: {str(e)}")


# Global instance - will be initialized with proper user email when needed
cv_preview_service = None
