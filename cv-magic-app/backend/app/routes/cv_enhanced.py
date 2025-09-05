"""
Enhanced CV processing routes with improved functionality
"""
import logging
import time
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse

from ..enhanced_database import enhanced_db
from ..models.enhanced import (
    CVUploadResponse, CVListResponse, CVContentResponse,
    SuccessResponse, ErrorResponse
)
from ..services.cv_processor import cv_processor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cv-enhanced", tags=["CV Enhanced"])


async def process_cv_content(cv_id: str):
    """Background task to process CV content"""
    try:
        # Get CV file path
        file_path = enhanced_db.get_cv_file_path(cv_id)
        if not file_path:
            logger.error(f"CV file not found: {cv_id}")
            return
        
        # Extract text
        result = cv_processor.extract_text_from_file(file_path)
        
        if result['success']:
            # Update CV with extracted content
            enhanced_db.update_cv_content(cv_id, result['text'])
            logger.info(f"CV processed successfully: {cv_id}")
        else:
            logger.error(f"CV processing failed: {cv_id} - {result['error']}")
            
    except Exception as e:
        logger.error(f"Error processing CV {cv_id}: {str(e)}")


@router.post("/upload", response_model=CVUploadResponse)
async def upload_cv(
    background_tasks: BackgroundTasks,
    cv_file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Upload CV file and extract text content"""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    if not cv_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = Path(cv_file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        file_content = await cv_file.read()
        
        # Validate file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
        
        # Save to database
        cv_response = enhanced_db.save_cv(
            filename=cv_file.filename,
            file_content=file_content,
            title=title,
            description=description
        )
        
        # Process CV in background
        background_tasks.add_task(process_cv_content, cv_response.id)
        
        logger.info(f"CV uploaded: {cv_response.filename} (ID: {cv_response.id})")
        
        return cv_response
        
    except Exception as e:
        logger.error(f"Error uploading CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading CV: {str(e)}")


@router.get("/list", response_model=CVListResponse)
async def list_cvs(page: int = 1, limit: int = 10):
    """List uploaded CVs with pagination"""
    
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
            
        cvs = enhanced_db.list_cvs(page=page, limit=limit)
        total = enhanced_db.count_cvs()
        
        return CVListResponse(
            cvs=cvs,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing CVs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing CVs: {str(e)}")


@router.get("/{cv_id}", response_model=CVContentResponse)
async def get_cv_content(cv_id: str):
    """Get CV content by ID"""
    
    try:
        # Get CV info
        cv_info = enhanced_db.get_cv(cv_id)
        if not cv_info:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Get CV text content
        text_content = enhanced_db.get_cv_content(cv_id)
        if not text_content:
            # Check if CV is still being processed
            if cv_info.processing_status.value == 'pending':
                raise HTTPException(status_code=202, detail="CV is still being processed")
            else:
                raise HTTPException(status_code=404, detail="CV content not available")
        
        return CVContentResponse(
            id=cv_info.id,
            filename=cv_info.filename,
            title=cv_info.title,
            text_content=text_content,
            file_type=cv_info.file_type,
            processing_status=cv_info.processing_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting CV content: {str(e)}")


@router.get("/{cv_id}/preview")
async def get_cv_preview(cv_id: str, max_length: int = 500):
    """Get CV content preview"""
    
    try:
        # Get CV text content
        text_content = enhanced_db.get_cv_content(cv_id)
        if not text_content:
            raise HTTPException(status_code=404, detail="CV content not available")
        
        # Generate preview
        preview = cv_processor.get_text_preview(text_content, max_length)
        
        # Extract basic info
        basic_info = cv_processor.extract_basic_info(text_content)
        
        return {
            "cv_id": cv_id,
            "preview": preview,
            "full_length": len(text_content),
            "preview_length": len(preview),
            "basic_info": basic_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting CV preview: {str(e)}")


@router.get("/{cv_id}/download")
async def download_cv(cv_id: str):
    """Download CV file"""
    
    try:
        # Get CV info and file path
        cv_info = enhanced_db.get_cv(cv_id)
        if not cv_info:
            raise HTTPException(status_code=404, detail="CV not found")
        
        file_path = enhanced_db.get_cv_file_path(cv_id)
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")
        
        # Determine media type
        media_type_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        
        media_type = media_type_map.get(cv_info.file_type.value, 'application/octet-stream')
        
        return FileResponse(
            path=file_path,
            filename=cv_info.filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading CV: {str(e)}")


@router.delete("/{cv_id}", response_model=SuccessResponse)
async def delete_cv(cv_id: str):
    """Delete CV"""
    
    try:
        deleted = enhanced_db.delete_cv(cv_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="CV not found")
        
        logger.info(f"CV deleted: {cv_id}")
        return SuccessResponse(message="CV deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting CV: {str(e)}")


@router.post("/{cv_id}/reprocess", response_model=SuccessResponse)
async def reprocess_cv(cv_id: str, background_tasks: BackgroundTasks):
    """Reprocess CV text extraction"""
    
    try:
        # Check if CV exists
        cv_info = enhanced_db.get_cv(cv_id)
        if not cv_info:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Reprocess CV in background
        background_tasks.add_task(process_cv_content, cv_id)
        
        logger.info(f"CV reprocessing started: {cv_id}")
        return SuccessResponse(message="CV reprocessing started")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reprocessing CV: {str(e)}")


@router.get("/{cv_id}/stats")
async def get_cv_stats(cv_id: str):
    """Get CV processing statistics"""
    
    try:
        # Get CV info
        cv_info = enhanced_db.get_cv(cv_id)
        if not cv_info:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Get text content for analysis
        text_content = enhanced_db.get_cv_content(cv_id)
        
        stats = {
            "cv_id": cv_id,
            "filename": cv_info.filename,
            "file_size_bytes": cv_info.file_size,
            "file_size_mb": round(cv_info.file_size / (1024 * 1024), 2),
            "file_type": cv_info.file_type,
            "processing_status": cv_info.processing_status,
            "upload_date": cv_info.upload_date,
        }
        
        if text_content:
            basic_info = cv_processor.extract_basic_info(text_content)
            stats.update({
                "text_length": len(text_content),
                "word_count": len(text_content.split()),
                "has_email": len(basic_info['emails']) > 0,
                "email_count": len(basic_info['emails']),
                "has_phone": len(basic_info['phones']) > 0,
                "has_skills_section": basic_info['has_skills_section'],
                "has_experience_section": basic_info['has_experience_section'],
                "has_education_section": basic_info['has_education_section'],
            })
        else:
            stats.update({
                "text_length": 0,
                "word_count": 0,
                "content_available": False
            })
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting CV stats: {str(e)}")
