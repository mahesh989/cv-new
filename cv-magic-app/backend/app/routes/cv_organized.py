"""
Organized CV Routes

This module provides clean, organized CV API endpoints using modular services.
Each endpoint uses dedicated service modules for better code organization.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import os

from ..modules.cv import cv_upload_service, cv_selection_service, cv_preview_service

router = APIRouter(prefix="/api/cv", tags=["CV Management"])


@router.post("/upload")
async def upload_cv(cv: UploadFile = File(...)):
    """Upload a CV file with validation and processing"""
    return await cv_upload_service.upload_cv(cv)


@router.get("/list")
async def list_cvs():
    """List all uploaded CVs with metadata"""
    return cv_selection_service.list_cvs()


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
    """Save selected CV as original_cv.txt in cv-analysis folder"""
    try:
        # Get CV content
        cv_content_result = cv_preview_service.get_cv_content(filename)
        
        if not cv_content_result.get('content'):
            raise HTTPException(status_code=404, detail=f"CV content not found for: {filename}")
        
        # Create cv-analysis directory if it doesn't exist
        analysis_dir = "cv-analysis"
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Save as original_cv.txt
        filepath = os.path.join(analysis_dir, "original_cv.txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ORIGINAL CV TEXT\n")
            f.write(f"CV File: {filename}\n")
            f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Length: {len(cv_content_result['content'])} characters\n")
            f.write("=" * 80 + "\n\n")
            f.write(cv_content_result['content'])
        
        return JSONResponse(content={
            "message": "CV saved for analysis successfully",
            "filename": filename,
            "saved_path": filepath,
            "content_length": len(cv_content_result['content'])
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save CV for analysis: {str(e)}")
