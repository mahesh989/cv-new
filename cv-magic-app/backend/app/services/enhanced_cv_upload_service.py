"""
Enhanced CV Upload Service

This service integrates the structured CV parser into the upload/processing flow,
ensuring all CVs are saved in the structured format going forward.
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import HTTPException, UploadFile
from ..services.cv_processor import cv_processor
from ..services.structured_cv_parser import LLMStructuredCVParser

logger = logging.getLogger(__name__)

# Constants
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def get_user_paths(user_email: str = "admin@admin.com"):
    """Get user-specific paths"""
    from app.utils.user_path_utils import get_user_base_path, get_user_uploads_path
    return {
        'upload_dir': get_user_uploads_path(user_email),
        'cv_analysis_dir': get_user_base_path(user_email)
    }


class EnhancedCVUploadService:
    """Enhanced CV upload service with structured parsing"""

    def __init__(self, user_email: str = "admin@admin.com"):
        self.user_email = user_email
        self.cv_processor = cv_processor
        self.structured_parser = LLMStructuredCVParser()
        paths = get_user_paths(user_email)
        self.upload_dir = paths['upload_dir']
        self.cv_analysis_dir = paths['cv_analysis_dir']
        self.original_cv_json_path = self.cv_analysis_dir / "cvs" / "original" / "original_cv.json"
        
        # Ensure directories exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.cv_analysis_dir.mkdir(parents=True, exist_ok=True)

    async def upload_and_process_cv(
        self, 
        cv_file: UploadFile, 
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload and process CV with structured parsing
        
        Args:
            cv_file: The uploaded CV file
            user_id: Optional user ID
            title: Optional CV title
            description: Optional CV description
            
        Returns:
            Dict containing upload and processing results
            
        Note:
            Always saves as original_cv.json (replaces existing file)
        """
        
        # Validate file
        validation_result = await self._validate_cv_file(cv_file)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        try:
            # Read file content
            file_content = await cv_file.read()
            file_path = self.upload_dir / cv_file.filename
            
            # Save original file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            logger.info(f"CV file saved: {cv_file.filename} ({len(file_content)} bytes)")
            
            # Extract text content
            extraction_result = self._extract_text_content(file_path)
            if not extraction_result["success"]:
                raise HTTPException(status_code=500, detail=f"Text extraction failed: {extraction_result['error']}")
            
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
            
            # Save structured CV as original_cv.json (always replaces existing)
            save_result = self._save_structured_cv(structured_cv, True, cv_file.filename)
            
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
                "saved_as_original_cv": True,  # Always true now
                "structured_cv_path": save_result["file_path"],
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

    async def process_existing_cv(self, filename: str) -> Dict[str, Any]:
        """
        Process an existing CV file into structured format
        
        Args:
            filename: Name of existing CV file
            
        Returns:
            Dict containing processing results
            
        Note:
            Always saves as original_cv.json (replaces existing file)
        """
        try:
            file_path = self.upload_dir / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="CV file not found")
            
            # Extract text content
            extraction_result = self._extract_text_content(file_path)
            if not extraction_result["success"]:
                raise HTTPException(status_code=500, detail=f"Text extraction failed: {extraction_result['error']}")
            
            # Parse into structured format
            structured_cv = await self._parse_to_structured_format(extraction_result["text"], filename)
            
            # Validate structured CV
            validation_report = self.structured_parser.validate_cv_structure(structured_cv)
            
            # Save structured CV as original_cv.json (always replaces existing)
            save_result = self._save_structured_cv(structured_cv, True, filename)
            
            logger.info(f"Existing CV processed successfully: {filename}")
            
            return {
                "success": True,
                "filename": filename,
                "text_length": len(extraction_result["text"]),
                "word_count": extraction_result.get("word_count", 0),
                "structured_format": True,
                "saved_as_original_cv": True,  # Always true now
                "structured_cv_path": save_result["file_path"],
                "validation_report": validation_report,
                "sections_found": validation_report["sections_found"],
                "unknown_sections": list(structured_cv.get("unknown_sections", {}).keys()),
                "processing_timestamp": structured_cv["saved_at"]
            }
            
        except Exception as e:
            logger.error(f"Error processing existing CV: {str(e)}")
            raise HTTPException(status_code=500, detail=f"CV processing failed: {str(e)}")

    def load_structured_cv(self, use_original: bool = True, filename: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load structured CV from file - always from original_cv.json
        
        Args:
            use_original: Ignored (kept for compatibility) - always loads from original_cv.json
            filename: Ignored (kept for compatibility) - always loads from original_cv.json
            
        Returns:
            Structured CV data or None if not found
        """
        try:
            # Always load from original_cv.json (same logic as original_cv.txt)
            if self.original_cv_json_path.exists():
                return self.structured_parser.load_structured_cv(str(self.original_cv_json_path))
            else:
                logger.warning("original_cv.json file not found")
                return None
            
        except Exception as e:
            logger.error(f"Error loading structured CV: {str(e)}")
            return None

    def get_cv_processing_status(self, filename: str) -> Dict[str, Any]:
        """Get processing status for a CV file"""
        try:
            file_path = self.upload_dir / filename
            structured_cv_path = self.cv_analysis_dir / f"{filename.split('.')[0]}_structured_cv.json"
            
            status = {
                "filename": filename,
                "original_file_exists": file_path.exists(),
                "structured_cv_exists": structured_cv_path.exists(),
                "is_processed": structured_cv_path.exists(),
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
                "upload_date": file_path.stat().st_mtime if file_path.exists() else None
            }
            
            if structured_cv_path.exists():
                structured_cv = self.structured_parser.load_structured_cv(str(structured_cv_path))
                if structured_cv:
                    status["processing_date"] = structured_cv.get("saved_at")
                    status["sections_count"] = len([k for k in structured_cv.keys() if k != "saved_at" and structured_cv[k]])
                    status["has_personal_info"] = bool(structured_cv.get("personal_information", {}).get("name"))
                    status["has_technical_skills"] = bool(structured_cv.get("technical_skills", []))
                    status["has_experience"] = bool(structured_cv.get("experience", []))
                    status["unknown_sections"] = list(structured_cv.get("unknown_sections", {}).keys())
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting processing status: {str(e)}")
            return {"filename": filename, "error": str(e)}

    async def _validate_cv_file(self, cv_file: UploadFile) -> Dict[str, Any]:
        """Validate CV file before processing"""
        if not cv_file.filename:
            return {"valid": False, "error": "No filename provided"}
        
        # Validate file extension
        file_extension = Path(cv_file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return {
                "valid": False, 
                "error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            }
        
        # Check file content (peek at size without fully reading)
        current_position = cv_file.file.tell()
        cv_file.file.seek(0, 2)  # Seek to end
        file_size = cv_file.file.tell()
        cv_file.file.seek(current_position)  # Restore position
        
        if file_size > MAX_FILE_SIZE:
            return {"valid": False, "error": "File too large. Maximum size is 10MB"}
        
        if file_size == 0:
            return {"valid": False, "error": "File is empty"}
        
        return {"valid": True}

    def _extract_text_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract text content from CV file"""
        try:
            result = self.cv_processor.extract_text_from_file(file_path)
            
            if result['success']:
                logger.info(f"Text extracted successfully: {len(result['text'])} characters")
                return {
                    "success": True,
                    "text": result['text'],
                    "word_count": result.get('word_count', len(result['text'].split())),
                    "method": result.get('file_type', 'unknown')
                }
            else:
                return {"success": False, "error": result.get('error', 'Unknown extraction error')}
                
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _parse_to_structured_format(
        self, 
        text_content: str, 
        filename: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse text content into structured CV format"""
        try:
            # Check if text content is already structured JSON
            try:
                existing_data = json.loads(text_content)
                if isinstance(existing_data, dict) and "personal_information" in existing_data:
                    # Already structured, just validate and clean
                    structured_cv = await self.structured_parser.parse_cv_content(existing_data)
                    logger.info("CV was already in structured format")
                else:
                    # JSON but not our structure, parse as text
                    structured_cv = await self.structured_parser.parse_cv_content(text_content)
                    logger.info("CV parsed from JSON content")
            except json.JSONDecodeError:
                # Regular text content, parse it
                structured_cv = await self.structured_parser.parse_cv_content(text_content)
                logger.info("CV parsed from raw text content")
            
            # Add metadata
            structured_cv["metadata"] = {
                "source_filename": filename,
                "processed_at": datetime.now().isoformat(),
                "processing_version": "1.0",
                "title": title or "",
                "description": description or "",
                "user_id": user_id or ""
            }
            
            return structured_cv
            
        except Exception as e:
            logger.error(f"Error parsing to structured format: {str(e)}")
            # Return basic structure with error info
            empty_structure = self.structured_parser._get_empty_structure()
            empty_structure["parsing_error"] = str(e)
            empty_structure["original_text"] = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
            return empty_structure

    def _save_structured_cv(
        self, 
        structured_cv: Dict[str, Any], 
        save_as_original: bool,
        filename: str
    ) -> Dict[str, Any]:
        """Save structured CV to file - always as original_cv.json (replaces if exists)"""
        try:
            # Always save as original_cv.json (same logic as original_cv.txt)
            file_path = self.original_cv_json_path
            
            # Add metadata similar to the txt format (modify a copy to avoid changing original)
            cv_with_metadata = structured_cv.copy()
            cv_with_metadata["metadata"] = {
                "source_filename": filename,
                "processed_at": datetime.now().isoformat(),
                "processing_version": "2.0",
                "content_type": "structured_cv"
            }
            
            # Save structured CV (replaces existing file)
            self.structured_parser.save_structured_cv(cv_with_metadata, str(file_path))
            logger.info(f"Structured CV saved as original_cv.json: {file_path} (replaced existing)")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            }
            
        except Exception as e:
            logger.error(f"Error saving structured CV: {str(e)}")
            return {"success": False, "error": str(e)}

    async def migrate_existing_cv(self, source_path: str, backup: bool = True) -> Dict[str, Any]:
        """
        Migrate an existing CV from old format to structured format
        
        Args:
            source_path: Path to existing CV file
            backup: Whether to create backup of original
            
        Returns:
            Migration result
        """
        try:
            source = Path(source_path)
            if not source.exists():
                raise FileNotFoundError(f"Source CV file not found: {source_path}")
            
            # Load existing CV data
            with open(source, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Create backup if requested
            if backup:
                backup_path = source.with_suffix('.backup.json')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Backup created: {backup_path}")
            
            # Convert to structured format
            if isinstance(existing_data, dict) and "text" in existing_data:
                # Old format with text field
                structured_cv = await self.structured_parser.parse_cv_content(existing_data["text"])
            else:
                # Try to parse as-is
                structured_cv = await self.structured_parser.parse_cv_content(existing_data)
            
            # Save in new format
            self.structured_parser.save_structured_cv(structured_cv, source_path)
            
            # Validate result
            validation_report = self.structured_parser.validate_cv_structure(structured_cv)
            
            logger.info(f"CV migrated successfully: {source_path}")
            
            return {
                "success": True,
                "source_path": source_path,
                "backup_created": backup,
                "backup_path": str(backup_path) if backup else None,
                "validation_report": validation_report,
                "sections_found": validation_report["sections_found"],
                "unknown_sections": list(structured_cv.get("unknown_sections", {}).keys())
            }
            
        except Exception as e:
            logger.error(f"Error migrating CV: {str(e)}")
            return {"success": False, "error": str(e)}


# Global instance
enhanced_cv_upload_service = EnhancedCVUploadService("admin@admin.com")