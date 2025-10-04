"""
Enhanced CV Upload Service V2

This version saves original CVs with timestamps and maintains backward compatibility.
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, UploadFile

from ..services.cv_processor import cv_processor
from ..services.structured_cv_parser import LLMStructuredCVParser

logger = logging.getLogger(__name__)

# Constants
from app.utils.user_path_utils import get_user_uploads_path
# UPLOAD_DIR will be set per user instance
# CV_ANALYSIS_DIR will be set per user instance
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CV_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


class EnhancedCVUploadServiceV2:
    """Enhanced CV upload service with timestamped files"""
    
    def __init__(self):
        self.cv_processor = cv_processor
        self.structured_parser = LLMStructuredCVParser()
        self.original_path = CV_ANALYSIS_DIR / "cvs" / "original"
        self.original_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_cv_paths(self, include_timestamp: bool = True) -> Tuple[Path, Path]:
        """Generate paths for JSON and TXT CV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        suffix = f"_{timestamp}" if timestamp else ""
        
        return (
            self.original_path / f"original_cv{suffix}.json",
            self.original_path / f"original_cv{suffix}.txt"
        )
    
    async def upload_and_process_cv(
        self, 
        cv_file: UploadFile, 
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload and process CV with structured parsing"""
        # Validate file
        validation_result = await self._validate_cv_file(cv_file)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        try:
            # Read file content
            file_content = await cv_file.read()
            file_path = UPLOAD_DIR / cv_file.filename
            
            # Save original file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            logger.info(f"CV file saved: {cv_file.filename} ({len(file_content)} bytes)")
            
            # Extract text content
            extraction_result = self._extract_text_content(file_path)
            if not extraction_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Text extraction failed: {extraction_result['error']}"
                )
            
            # Parse into structured format
            structured_cv = await self._parse_to_structured_format(
                extraction_result["text"],
                cv_file.filename,
                title,
                description,
                user_id
            )
            
            # Validate structured CV
            validation_report = self.structured_parser.validate_cv_structure(structured_cv)
            
            # Save structured CV with timestamp
            save_result = await self._save_structured_cv(
                structured_cv=structured_cv,
                cv_text=extraction_result["text"],
                filename=cv_file.filename
            )
            
            logger.info(f"CV processed successfully: {cv_file.filename}")
            
            return {
                "success": True,
                "filename": cv_file.filename,
                "file_size": len(file_content),
                "file_type": file_path.suffix[1:].upper(),
                "text_extracted": True,
                "text_length": len(extraction_result["text"]),
                "word_count": extraction_result.get("word_count", 0),
                "structured_format": True,
                "saved_files": {
                    "json_path": save_result["json_path"],
                    "txt_path": save_result["txt_path"],
                    "timestamp": save_result["timestamp"]
                },
                "validation_report": validation_report,
                "sections_found": validation_report["sections_found"],
                "unknown_sections": list(structured_cv.get("unknown_sections", {}).keys()),
                "processing_timestamp": structured_cv["saved_at"]
            }
            
        except Exception as e:
            logger.error(f"Error processing CV: {str(e)}")
            # Clean up uploaded file if processing failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"CV processing failed: {str(e)}")
    
    async def _save_structured_cv(
        self,
        structured_cv: Dict[str, Any],
        cv_text: str,
        filename: str
    ) -> Dict[str, Any]:
        """Save structured CV with timestamp"""
        try:
            # Generate timestamped paths
            json_path, txt_path = self._generate_cv_paths(include_timestamp=True)
            
            # Also create paths without timestamp for backward compatibility
            compat_json_path, compat_txt_path = self._generate_cv_paths(include_timestamp=False)
            
            timestamp = datetime.now().isoformat()
            
            # Add metadata
            cv_with_metadata = structured_cv.copy()
            cv_with_metadata["metadata"] = {
                "source_filename": filename,
                "processed_at": timestamp,
                "processing_version": "2.0",
                "content_type": "structured_cv"
            }
            
            # Save JSON versions (both timestamped and non-timestamped)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(cv_with_metadata, f, indent=2)
            
            with open(compat_json_path, "w", encoding="utf-8") as f:
                json.dump(cv_with_metadata, f, indent=2)
            
            # Save TXT versions
            txt_path.parent.mkdir(parents=True, exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(cv_text)
            
            with open(compat_txt_path, "w", encoding="utf-8") as f:
                f.write(cv_text)
            
            logger.info(
                f"CV saved with timestamp {json_path.name} and compatibility version"
            )
            
            return {
                "success": True,
                "json_path": str(json_path),
                "txt_path": str(txt_path),
                "timestamp": timestamp,
                "compat_json_path": str(compat_json_path),
                "compat_txt_path": str(compat_txt_path)
            }
            
        except Exception as e:
            logger.error(f"Error saving structured CV: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_structured_cv(
        self,
        include_timestamp: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Load structured CV from file
        
        Args:
            include_timestamp: Whether to load latest timestamped version
        """
        try:
            if include_timestamp:
                # Find latest timestamped version
                json_files = sorted(
                    self.original_path.glob("original_cv_*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                if json_files:
                    return self.structured_parser.load_structured_cv(str(json_files[0]))
            
            # Fallback to non-timestamped version
            compat_path = self.original_path / "original_cv.json"
            if compat_path.exists():
                return self.structured_parser.load_structured_cv(str(compat_path))
            
            logger.warning("No CV file found")
            return None
            
        except Exception as e:
            logger.error(f"Error loading structured CV: {str(e)}")
            return None
    
    # Other methods remain unchanged but use self.original_path instead of
    # hardcoded paths:
    #  - _validate_cv_file
    #  - _extract_text_content
    #  - _parse_to_structured_format
    #  - get_cv_processing_status
    #  - migrate_existing_cv
    # Their implementation is identical to the original service


# Global instance
enhanced_cv_upload_service_v2 = EnhancedCVUploadServiceV2()