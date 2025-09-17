"""
Async CV Processing Service

This service handles background processing of CV files for analysis,
including the creation of original_cv.json using LLM parsing.
It uses FastAPI's BackgroundTasks to avoid blocking the main thread.
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Constants
CV_ANALYSIS_DIR = Path("cv-analysis")
UPLOAD_DIR = Path("uploads")

# Ensure directories exist
CV_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Thread pool for background processing
executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cv_processor")

# Track processing status
processing_status: Dict[str, Dict[str, Any]] = {}
processing_lock = threading.Lock()


class AsyncCVProcessor:
    """Handles async CV processing operations"""
    
    @staticmethod
    async def save_cv_for_analysis_async(
        filename: str,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """
        Initiate background CV analysis processing.
        Returns immediately while processing continues in background.
        
        Args:
            filename: Name of the CV file to process
            background_tasks: FastAPI BackgroundTasks instance
            
        Returns:
            Dict with status information
        """
        try:
            # Check if file exists
            file_path = UPLOAD_DIR / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail=f"CV file not found: {filename}")
            
            # Check if already processing
            with processing_lock:
                if filename in processing_status and processing_status[filename].get("status") == "processing":
                    return {
                        "status": "already_processing",
                        "message": "CV is already being processed",
                        "filename": filename
                    }
                
                # Mark as processing
                processing_status[filename] = {
                    "status": "processing",
                    "started_at": datetime.now().isoformat(),
                    "progress": "Initializing..."
                }
            
            # Add background task for processing
            background_tasks.add_task(
                process_cv_in_background,
                filename
            )
            
            return {
                "status": "accepted",
                "message": "CV analysis initiated in background",
                "filename": filename,
                "note": "Processing will continue in background"
            }
            
        except Exception as e:
            logger.error(f"Error initiating async CV processing: {str(e)}")
            with processing_lock:
                processing_status[filename] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def get_processing_status(filename: str) -> Dict[str, Any]:
        """Get the current processing status for a CV file"""
        with processing_lock:
            if filename in processing_status:
                return processing_status[filename].copy()
            else:
                # Check if files already exist
                txt_path = CV_ANALYSIS_DIR / "original_cv.txt"
                json_path = CV_ANALYSIS_DIR / "original_cv.json"
                
                if txt_path.exists() and json_path.exists():
                    return {
                        "status": "completed",
                        "txt_exists": True,
                        "json_exists": True,
                        "message": "CV analysis files available"
                    }
                elif txt_path.exists():
                    return {
                        "status": "partial",
                        "txt_exists": True,
                        "json_exists": False,
                        "message": "Text file saved, JSON processing may be needed"
                    }
                else:
                    return {
                        "status": "not_started",
                        "message": "CV has not been processed for analysis"
                    }


async def process_cv_in_background(filename: str):
    """
    Background task to process CV for analysis.
    Creates both original_cv.txt and original_cv.json.
    
    Args:
        filename: Name of the CV file to process
    """
    try:
        logger.info(f"Starting background processing for {filename}")
        
        # Update status
        with processing_lock:
            processing_status[filename] = {
                "status": "processing",
                "progress": "Extracting text content...",
                "started_at": datetime.now().isoformat()
            }
        
        # Step 1: Extract text content (quick operation)
        from app.services.cv_processor import cv_processor
        
        file_path = UPLOAD_DIR / filename
        extraction_result = cv_processor.extract_text_from_file(file_path)
        
        if not extraction_result['success']:
            raise Exception(f"Text extraction failed: {extraction_result.get('error', 'Unknown error')}")
        
        cv_content = extraction_result['text']
        
        # Step 2: Save as original_cv.txt (quick operation)
        with processing_lock:
            processing_status[filename]["progress"] = "Saving text file..."
        
        txt_filepath = CV_ANALYSIS_DIR / "original_cv.txt"
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ORIGINAL CV TEXT\n")
            f.write(f"CV File: {filename}\n")
            f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Length: {len(cv_content)} characters\n")
            f.write("=" * 80 + "\n\n")
            f.write(cv_content)
        
        logger.info(f"CV text saved: {txt_filepath}")
        
        # Step 3: Process to structured JSON (may take time due to LLM)
        with processing_lock:
            processing_status[filename]["progress"] = "Creating structured JSON (this may take a moment)..."
        
        # Import here to avoid circular dependencies
        from app.services.structured_cv_parser import LLMStructuredCVParser
        
        parser = LLMStructuredCVParser()
        
        # Parse CV content using LLM (async operation)
        structured_cv = await parser.parse_cv_content(cv_content)
        
        # Add metadata
        structured_cv["metadata"]["source_filename"] = filename
        structured_cv["metadata"]["processed_at"] = datetime.now().isoformat()
        structured_cv["metadata"]["processing_version"] = "2.0_async"
        
        # Save as original_cv.json
        json_filepath = CV_ANALYSIS_DIR / "original_cv.json"
        parser.save_structured_cv(structured_cv, str(json_filepath))
        
        logger.info(f"Structured CV saved: {json_filepath}")
        
        # Step 4: Validate the results
        validation_report = parser.validate_cv_structure(structured_cv)
        
        # Update status to completed
        with processing_lock:
            processing_status[filename] = {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "txt_path": str(txt_filepath),
                "json_path": str(json_filepath),
                "validation": validation_report,
                "sections_found": validation_report.get("sections_found", []),
                "content_length": len(cv_content)
            }
        
        logger.info(f"✅ Background processing completed for {filename}")
        
    except Exception as e:
        logger.error(f"Error in background CV processing: {str(e)}")
        with processing_lock:
            processing_status[filename] = {
                "status": "error",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }


class QuickCVContentExtractor:
    """Fast CV content extraction without LLM processing"""
    
    @staticmethod
    def get_cv_content_fast(filename: str) -> Dict[str, Any]:
        """
        Get CV content quickly without any processing.
        This is used for immediate preview display.
        
        Args:
            filename: Name of the CV file
            
        Returns:
            Dict containing CV content and metadata
        """
        try:
            from app.services.cv_processor import cv_processor
            
            file_path = UPLOAD_DIR / filename
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="CV file not found")
            
            # Extract text using simple processor (no LLM)
            result = cv_processor.extract_text_from_file(file_path)
            
            if not result['success']:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to extract text: {result['error']}"
                )
            
            # Get file metadata
            stat = file_path.stat()
            
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
                    "method": result.get('method', 'simple'),
                    "character_count": len(result['text']),
                    "word_count": len(result['text'].split()),
                    "processing_type": "fast_extraction"
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extracting CV content: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error extracting CV content: {str(e)}")


# Global instances
async_cv_processor = AsyncCVProcessor()
quick_extractor = QuickCVContentExtractor()


# Cleanup function for graceful shutdown
def cleanup_executor():
    """Cleanup thread pool executor on shutdown"""
    executor.shutdown(wait=False)
    processing_status.clear()