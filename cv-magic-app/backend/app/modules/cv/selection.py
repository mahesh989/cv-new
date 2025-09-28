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
UPLOAD_DIR = Path("cv-analysis/uploads")
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


class CVSelectionService:
    """Service class for handling CV selection and listing"""
    
    @staticmethod
    def list_cvs() -> Dict[str, Any]:
        """
        List all uploaded CVs with metadata
        
        Returns:
            Dict containing CV list and metadata
            
        Raises:
            HTTPException: If listing fails
        """
        try:
            cvs = []
            
            if UPLOAD_DIR.exists():
                for file_path in UPLOAD_DIR.iterdir():
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
    
    @staticmethod
    def get_cv_info(filename: str) -> Dict[str, Any]:
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
            file_path = UPLOAD_DIR / filename
            
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


# Global instance
cv_selection_service = CVSelectionService()
