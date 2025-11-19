"""
Organized CV Routes

This module provides clean, organized CV API endpoints using modular services.
Each endpoint uses dedicated service modules for better code organization.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
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
async def save_cv_for_analysis(
    filename: str, 
    background_tasks: BackgroundTasks,
    current_user: UserData = Depends(get_current_user)
):
    """Save selected CV as both original_cv.txt and original_cv.json in cv-analysis folder"""
    logger.info(f"🔍 [SAVE_CV] Received request to save CV: {filename} for user: {current_user.email}")
    
    try:
        # Get CV content using user-specific service instance
        logger.info(f"🔍 [SAVE_CV] Getting CV content for: {filename}")
        from app.modules.cv.preview import CVPreviewService
        user_cv_preview_service = CVPreviewService(user_email=current_user.email)
        cv_content_result = user_cv_preview_service.get_cv_content(filename)
        
        logger.info(f"🔍 [SAVE_CV] CV content result keys: {list(cv_content_result.keys())}")
        logger.info(f"🔍 [SAVE_CV] CV content length: {len(cv_content_result.get('content', ''))}")
        
        if not cv_content_result.get('content'):
            logger.error(f"❌ [SAVE_CV] CV content not found for: {filename}")
            raise HTTPException(status_code=404, detail=f"CV content not found for: {filename}")
        
        # Create user-scoped cv-analysis directory if it doesn't exist
        analysis_base: Path = get_user_base_path(current_user.email)
        logger.info(f"🔍 [SAVE_CV] Analysis base path: {analysis_base}")
        analysis_base.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ [SAVE_CV] Analysis base directory created/verified: {analysis_base.exists()}")
        
        # Save as original_cv.txt in the user-scoped cvs/original folder
        original_folder = analysis_base / "cvs" / "original"
        logger.info(f"🔍 [SAVE_CV] Original folder path: {original_folder}")
        original_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ [SAVE_CV] Original folder created/verified: {original_folder.exists()}")
        
        txt_filepath = original_folder / "original_cv.txt"
        json_filepath = original_folder / "original_cv.json"
        
        logger.info(f"🔍 [SAVE_CV] TXT file path: {txt_filepath}")
        logger.info(f"🔍 [SAVE_CV] JSON file path: {json_filepath}")
        
        # CRITICAL: Always overwrite both files when user selects CV from dropdown
        # Save original_cv.txt immediately
        logger.info(f"💾 [SAVE_CV] Writing TXT file: {txt_filepath}")
        try:
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(cv_content_result['content'])
            logger.info(f"✅ [SAVE_CV] CV saved as text (overwritten): {txt_filepath}")
            logger.info(f"✅ [SAVE_CV] TXT file exists: {txt_filepath.exists()}, size: {txt_filepath.stat().st_size if txt_filepath.exists() else 0} bytes")
        except Exception as txt_error:
            logger.error(f"❌ [SAVE_CV] Failed to write TXT file: {txt_error}")
            raise
        
        # CRITICAL: Create minimal original_cv.json immediately so it exists
        # This ensures the file exists even if background processing fails
        import json
        from datetime import datetime
        logger.info(f"💾 [SAVE_CV] Creating minimal JSON file: {json_filepath}")
        
        minimal_json = {
            "filename": filename,
            "text": cv_content_result['content'],
            "saved_at": datetime.now().isoformat(),
            "content_type": "text",  # Will be updated to "structured" after background processing
            "processing_status": "pending_structured_parsing"
        }
        
        try:
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(minimal_json, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ [SAVE_CV] CV saved as minimal JSON (overwritten): {json_filepath}")
            logger.info(f"✅ [SAVE_CV] JSON file exists: {json_filepath.exists()}, size: {json_filepath.stat().st_size if json_filepath.exists() else 0} bytes")
        except Exception as json_error:
            logger.error(f"❌ [SAVE_CV] Failed to write JSON file: {json_error}")
            raise
        
        # Start structured processing in background (non-blocking)
        # Use the same method that was working before: process_existing_cv()
        async def background_structured_processing():
            """Background task to process CV into structured format using the working method"""
            try:
                logger.info(f"🔄 [BACKGROUND] Processing {filename} for structured CV format (background)...")
                from app.services.enhanced_cv_upload_service import EnhancedCVUploadService
                user_enhanced_cv_upload_service = EnhancedCVUploadService(user_email=current_user.email)
                
                # Use the same method that was working before
                processing_result = await user_enhanced_cv_upload_service.process_existing_cv(filename=filename)
                
                if processing_result.get('success', False):
                    logger.info(f"✅ [BACKGROUND] CV saved as structured JSON: {processing_result.get('structured_cv_path')}")
                    logger.info(f"✅ [BACKGROUND] Processing result: {processing_result.get('sections_found', 'N/A')} sections found")
                else:
                    logger.warning(f"⚠️ [BACKGROUND] Failed to save structured CV: {processing_result.get('error', 'Unknown error')}")
                    # Update minimal JSON with error status
                    try:
                        minimal_json['processing_status'] = f"failed: {processing_result.get('error', 'Unknown error')}"
                        with open(json_filepath, 'w', encoding='utf-8') as f:
                            json.dump(minimal_json, f, indent=2, ensure_ascii=False)
                        logger.info(f"✅ [BACKGROUND] Updated minimal JSON with error status: {json_filepath}")
                    except Exception as save_error:
                        logger.error(f"❌ [BACKGROUND] Failed to update JSON file: {save_error}")
                    
            except Exception as e:
                logger.error(f"❌ [BACKGROUND] Error processing structured CV: {str(e)}")
                import traceback
                logger.error(f"❌ [BACKGROUND] Traceback: {traceback.format_exc()}")
                # Update status but keep the file
                try:
                    minimal_json['processing_status'] = f"error: {str(e)}"
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(minimal_json, f, indent=2, ensure_ascii=False)
                    logger.info(f"✅ [BACKGROUND] Updated JSON with error status: {json_filepath}")
                except Exception as save_error:
                    logger.error(f"❌ [BACKGROUND] Failed to update JSON file: {save_error}")
        
        # Add background task using FastAPI's BackgroundTasks (supports async functions)
        background_tasks.add_task(background_structured_processing)
        logger.info(f"✅ [SAVE_CV] Background task scheduled for structured processing")
        
        return JSONResponse(content={
            "message": "CV saved for analysis successfully",
            "filename": filename,
            "txt_path": str(txt_filepath),
            "json_path": str(json_filepath),
            "structured_success": "minimal_json_created_immediately_enhancement_in_background",
            "content_length": len(cv_content_result['content']),
            "note": "Both original_cv.txt and original_cv.json created immediately. JSON will be enhanced with structured data in background."
        })
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"❌ [SAVE_CV] Exception in save_cv_for_analysis: {str(e)}")
        import traceback
        logger.error(f"❌ [SAVE_CV] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to save CV for analysis: {str(e)}")
