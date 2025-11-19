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
from app.utils.user_path_utils import get_user_base_path
from pathlib import Path
from ..services.enhanced_cv_upload_service import enhanced_cv_upload_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cv", tags=["CV Management"])


@router.post("/upload")
async def upload_cv(cv: UploadFile = File(...), current_user: UserData = Depends(get_current_user)):
    """Upload a CV file with validation and processing - user-specific path isolated"""
    from app.modules.cv.upload import CVUploadService
    user_cv_upload_service = CVUploadService(user_email=current_user.email)
    return await user_cv_upload_service.upload_cv(cv)


@router.get("/list")
async def list_cvs(current_user: UserData = Depends(get_current_user)):
    """List all uploaded CVs with metadata - user-specific path isolated"""
    from app.modules.cv.selection import CVSelectionService
    user_cv_selection_service = CVSelectionService(user_email=current_user.email)
    return user_cv_selection_service.list_cvs(current_user)


@router.get("/info/{filename}")
async def get_cv_info(filename: str, current_user: UserData = Depends(get_current_user)):
    """Get information about a specific CV file - user-specific path isolated"""
    from app.modules.cv.selection import CVSelectionService
    user_cv_selection_service = CVSelectionService(user_email=current_user.email)
    return user_cv_selection_service.get_cv_info(filename)


@router.get("/content/{filename}")
async def get_cv_content(filename: str, current_user: UserData = Depends(get_current_user)):
    """Get CV text content with improved extraction - user-specific path isolated"""
    from app.modules.cv.preview import CVPreviewService
    user_cv_preview_service = CVPreviewService(user_email=current_user.email)
    return user_cv_preview_service.get_cv_content(filename)


@router.get("/preview/{filename}")
async def get_cv_preview(filename: str, max_length: int = 500, current_user: UserData = Depends(get_current_user)):
    """Get CV content preview with customizable length - user-specific path isolated"""
    from app.modules.cv.preview import CVPreviewService
    user_cv_preview_service = CVPreviewService(user_email=current_user.email)
    return user_cv_preview_service.get_cv_preview(filename, max_length)


@router.post("/save-for-analysis/{filename}")
async def save_cv_for_analysis(filename: str, current_user: UserData = Depends(get_current_user)):
    """Save selected CV as both original_cv.txt and original_cv.json in cv-analysis folder"""
    try:
        # Get CV content using user-specific service instance
        from app.modules.cv.preview import CVPreviewService
        user_cv_preview_service = CVPreviewService(user_email=current_user.email)
        cv_content_result = user_cv_preview_service.get_cv_content(filename)
        
        if not cv_content_result.get('content'):
            raise HTTPException(status_code=404, detail=f"CV content not found for: {filename}")
        
        # Create user-scoped cv-analysis directory if it doesn't exist
        analysis_base: Path = get_user_base_path(current_user.email)
        analysis_base.mkdir(parents=True, exist_ok=True)
        
        # Save as original_cv.txt in the user-scoped cvs/original folder
        original_folder = analysis_base / "cvs" / "original"
        original_folder.mkdir(parents=True, exist_ok=True)
        txt_filepath = original_folder / "original_cv.txt"
        json_filepath = original_folder / "original_cv.json"
        
        # CRITICAL: Always overwrite both files when user selects CV from dropdown
        # Save original_cv.txt immediately
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(cv_content_result['content'])
        
        logger.info(f"✅ CV saved as text (overwritten): {txt_filepath}")
        
        # CRITICAL: Create minimal original_cv.json immediately so it exists
        # This ensures the file exists even if background processing fails
        import json
        from datetime import datetime
        minimal_json = {
            "filename": filename,
            "text": cv_content_result['content'],
            "saved_at": datetime.now().isoformat(),
            "content_type": "text",  # Will be updated to "structured" after background processing
            "processing_status": "pending_structured_parsing"
        }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(minimal_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ CV saved as minimal JSON (overwritten): {json_filepath}")
        
        # Start structured processing in background (non-blocking)
        # This will enhance the JSON file with structured data
        import asyncio
        
        async def background_structured_processing():
            try:
                logger.info(f"🔄 Processing {filename} for structured CV format (background)...")
                from app.services.enhanced_cv_upload_service import EnhancedCVUploadService
                user_enhanced_cv_upload_service = EnhancedCVUploadService(user_email=current_user.email)
                
                # Process the content directly instead of looking for the file in upload folder
                cv_content = cv_content_result['content']
                structured_cv = await user_enhanced_cv_upload_service._parse_to_structured_format(
                    text_content=cv_content,
                    filename=filename,
                    user=current_user
                )
                
                # Check if parsing was successful (no parsing_error field means success)
                if not structured_cv.get('parsing_error'):
                    # Save the structured CV to the original folder
                    # CRITICAL: Always overwrite when user selects CV from dropdown
                    # Ensure filename is stored in the structured CV for tracking
                    if 'filename' not in structured_cv:
                        structured_cv['filename'] = filename
                    if 'saved_at' not in structured_cv:
                        structured_cv['saved_at'] = datetime.now().isoformat()
                    structured_cv['content_type'] = "structured"
                    structured_cv['processing_status'] = "completed"
                    
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(structured_cv, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"✅ Background: CV enhanced with structured JSON (overwritten): {json_filepath} (filename: {filename})")
                else:
                    error_msg = structured_cv.get('parsing_error', 'Unknown error')
                    logger.warning(f"⚠️ Background: Failed to enhance structured CV: {error_msg}")
                    logger.warning(f"⚠️ Background: Keeping minimal JSON format. Structured CV data: {structured_cv}")
                    # Update status but keep the file
                    minimal_json['processing_status'] = f"failed: {error_msg}"
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(minimal_json, f, indent=2, ensure_ascii=False)
                    
            except Exception as e:
                logger.error(f"❌ Background: Error enhancing structured CV: {str(e)}")
                import traceback
                logger.error(f"❌ Background: Traceback: {traceback.format_exc()}")
                # Update status but keep the file
                try:
                    minimal_json['processing_status'] = f"error: {str(e)}"
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(minimal_json, f, indent=2, ensure_ascii=False)
                except:
                    pass
        
        # Start background task (fire and forget)
        asyncio.create_task(background_structured_processing())
        
        return JSONResponse(content={
            "message": "CV saved for analysis successfully",
            "filename": filename,
            "txt_path": str(txt_filepath),
            "json_path": str(json_filepath),
            "structured_success": "minimal_json_created_immediately_enhancement_in_background",
            "content_length": len(cv_content_result['content']),
            "note": "Both original_cv.txt and original_cv.json created immediately. JSON will be enhanced with structured data in background."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save CV for analysis: {str(e)}")
