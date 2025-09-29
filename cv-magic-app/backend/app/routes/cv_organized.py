"""
Organized CV Routes

This module provides clean, organized CV API endpoints using modular services.
Each endpoint uses dedicated service modules for better code organization.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import logging

from ..modules.cv import cv_upload_service, cv_selection_service, cv_preview_service
from app.core.dependencies import get_current_user
from app.models.auth import UserData
from ..services.enhanced_cv_upload_service import enhanced_cv_upload_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cv", tags=["CV Management"])


@router.post("/upload")
async def upload_cv(cv: UploadFile = File(...)):
    """Upload a CV file with validation and processing"""
    return await cv_upload_service.upload_cv(cv)


@router.get("/list")
async def list_cvs(current_user: UserData = Depends(get_current_user)):
    """List all uploaded CVs with metadata"""
    return cv_selection_service.list_cvs(current_user)


@router.get("/info/{filename}")
async def get_cv_info(filename: str):
    """Get information about a specific CV file"""
    return cv_selection_service.get_cv_info(filename)


@router.get("/content/{filename}")
async def get_cv_content(filename: str):
    """Get CV text content with improved extraction"""
    return cv_preview_service.get_cv_content(filename)


@router.get("/preview/{filename}")
async def get_cv_preview(filename: str, max_length: int = 500):
    """Get CV content preview with customizable length"""
    return cv_preview_service.get_cv_preview(filename, max_length)


@router.post("/save-for-analysis/{filename}")
async def save_cv_for_analysis(filename: str):
    """Save selected CV as both original_cv.txt and original_cv.json in cv-analysis folder"""
    try:
        # Get CV content
        cv_content_result = cv_preview_service.get_cv_content(filename)
        
        if not cv_content_result.get('content'):
            raise HTTPException(status_code=404, detail=f"CV content not found for: {filename}")
        
        # Create cv-analysis directory if it doesn't exist
        analysis_dir = "cv-analysis"
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Save as original_cv.txt in the new cvs/original folder
        original_folder = os.path.join(analysis_dir, "cvs", "original")
        os.makedirs(original_folder, exist_ok=True)
        txt_filepath = os.path.join(original_folder, "original_cv.txt")
        
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ORIGINAL CV TEXT\n")
            f.write(f"CV File: {filename}\n")
            f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Length: {len(cv_content_result['content'])} characters\n")
            f.write("=" * 80 + "\n\n")
            f.write(cv_content_result['content'])
        
        logger.info(f"CV saved as text: {txt_filepath}")
        
        # Start structured processing in background (non-blocking)
        structured_success = True
        structured_path = "cv-analysis/cvs/original/original_cv.json (processing in background)"
        
        # Trigger background structured processing without blocking response
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        async def background_structured_processing():
            try:
                logger.info(f"Processing {filename} for structured CV format (background)...")
                processing_result = await enhanced_cv_upload_service.process_existing_cv(
                    filename=filename
                )
                
                if processing_result.get('success', False):
                    logger.info(f"✅ Background: CV saved as structured JSON: {processing_result.get('structured_cv_path')}")
                else:
                    logger.warning(f"⚠️ Background: Failed to save structured CV: {processing_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Background: Error saving structured CV: {str(e)}")
        
        # Start background task (fire and forget)
        asyncio.create_task(background_structured_processing())
        
        return JSONResponse(content={
            "message": "CV saved for analysis successfully",
            "filename": filename,
            "txt_path": txt_filepath,
            "structured_path": structured_path,
            "structured_success": structured_success,
            "content_length": len(cv_content_result['content']),
            "note": "Both original_cv.txt and original_cv.json have been saved for analysis and CV tailoring"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save CV for analysis: {str(e)}")
