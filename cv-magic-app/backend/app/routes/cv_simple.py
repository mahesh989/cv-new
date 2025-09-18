"""
Simplified CV processing routes with improved structure
"""
import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from ..services.cv_processor import cv_processor
from ..services.enhanced_cv_upload_service import enhanced_cv_upload_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv", tags=["CV Processing"])

# Constants
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_cv(cv: UploadFile = File(...), auto_structure: bool = True):
    """Upload a CV file with automatic structured processing"""
    
    if not cv.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    try:
        # Use the enhanced upload service for automatic structured processing
        if auto_structure:
            logger.info(f"Uploading {cv.filename} with structured processing...")
            result = await enhanced_cv_upload_service.upload_and_process_cv(
                cv_file=cv
                # Always saves as original_cv.json (replaces existing)
            )
            
            logger.info(f"✅ {cv.filename} uploaded and processed into structured format")
            
            return JSONResponse(content={
                "message": "CV uploaded and processed successfully",
                "filename": result['filename'],
                "size": result['file_size'],
                "type": result['file_type'],
                "structured_processing": True,
                "structured_cv_path": result['structured_cv_path'],
                "sections_found": result['sections_found'],
                "unknown_sections": result['unknown_sections'],
                "validation_report": result['validation_report'],
                "processing_timestamp": result['processing_timestamp']
            })
        else:
            # Fallback to basic upload without structured processing
            file_extension = Path(cv.filename).suffix.lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Read and validate file size
            file_content = await cv.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail="File too large. Maximum size is 10MB"
                )
            
            # Save file to upload directory
            file_path = UPLOAD_DIR / cv.filename
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            logger.info(f"CV uploaded successfully: {cv.filename} ({len(file_content)} bytes)")
            
            return JSONResponse(content={
                "message": "CV uploaded successfully",
                "filename": cv.filename,
                "size": len(file_content),
                "type": file_extension[1:].upper(),
                "structured_processing": False
            })
        
    except Exception as e:
        logger.error(f"Error uploading CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading CV: {str(e)}")


@router.get("/list")
async def list_cvs():
    """List all uploaded CVs with metadata"""
    
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
        
        return JSONResponse(content={
            "uploaded_cvs": [cv["filename"] for cv in cvs],  # Keep compatibility
            "cv_details": cvs,
            "total_count": len(cvs)
        })
        
    except Exception as e:
        logger.error(f"Error listing CVs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing CVs: {str(e)}")


@router.get("/content/{filename}")
async def get_cv_content(filename: str, auto_structure: bool = False):
    """Get CV content with optional structured processing"""
    
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")
        
        # Extract text using improved processor (fast operation)
        result = cv_processor.extract_text_from_file(file_path)
        
        if not result['success']:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to extract text: {result['error']}"
            )
        
        # Get file metadata
        stat = file_path.stat()
        
        logger.info(f"CV content extracted: {filename} ({len(result['text'])} characters)")
        
        response_content = {
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
        
        # Only do structured processing if explicitly requested
        if auto_structure:
            try:
                logger.info(f"Auto-processing {filename} into structured format...")
                processing_result = await enhanced_cv_upload_service.process_existing_cv(
                    filename=filename
                )
                
                if processing_result['success']:
                    structured_cv = enhanced_cv_upload_service.load_structured_cv()
                    
                    response_content["processing_info"] = {
                        "structured_processing": True,
                        "structured_cv_path": processing_result['structured_cv_path'],
                        "validation_report": processing_result['validation_report'],
                        "sections_found": processing_result['sections_found'],
                        "unknown_sections": processing_result.get('unknown_sections', []),
                        "processing_timestamp": processing_result['processing_timestamp']
                    }
                    
                    if structured_cv:
                        response_content["structured_cv"] = structured_cv
                        
                    logger.info(f"✅ {filename} processed into structured format successfully")
                else:
                    response_content["processing_info"] = {
                        "structured_processing": False,
                        "error": "Failed to process into structured format"
                    }
                    
            except Exception as e:
                logger.error(f"Error during structured processing {filename}: {str(e)}")
                response_content["processing_info"] = {
                    "structured_processing": False,
                    "error": str(e)
                }
        
        return JSONResponse(content=response_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting CV content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting CV content: {str(e)}")


@router.post("/process-structured/{filename}")
async def process_cv_structured(filename: str):
    """Process CV into structured format and save as original_cv.json"""
    
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")
        
        logger.info(f"Processing {filename} into structured format...")
        
        # Process into structured format
        processing_result = await enhanced_cv_upload_service.process_existing_cv(
            filename=filename
        )
        
        if processing_result['success']:
            logger.info(f"✅ {filename} processed and saved as original_cv.json")
            
            return JSONResponse(content={
                "success": True,
                "message": "CV processed into structured format successfully",
                "filename": filename,
                "structured_cv_path": processing_result['structured_cv_path'],
                "sections_found": processing_result['sections_found'],
                "validation_report": processing_result['validation_report'],
                "processing_timestamp": processing_result['processing_timestamp']
            })
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to process CV into structured format"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing structured CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing structured CV: {str(e)}")


@router.get("/preview/{filename}")
async def get_cv_preview(filename: str, max_length: int = 500):
    """Get CV content preview with customizable length"""
    
    try:
        file_path = UPLOAD_DIR / filename
        
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
        
        return JSONResponse(content={
            "filename": filename,
            "preview": preview,
            "full_length": len(full_text),
            "preview_length": len(preview),
            "is_truncated": len(full_text) > max_length,
            "basic_info": basic_info,
            "extraction_method": result.get('method', 'unknown')
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating CV preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating CV preview: {str(e)}")


@router.get("/read-tailored-cv/{company_name}")
async def read_tailored_cv(company_name: str):
    """
    Read tailored CV content for frontend preview
    
    This endpoint serves the most recent tailored CV text content for a company,
    compatible with the frontend CV preview functionality.
    """
    try:
        logger.info(f"📄 Tailored CV content request for {company_name}")
        
        # Path to cv-analysis folder
        cv_analysis_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        company_folder = cv_analysis_path / company_name
        
        if not company_folder.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Company folder not found: {company_name}"
            )
        
        # Find the most recent tailored CV text file
        tailored_txt_files = list(company_folder.glob("tailored_cv_*.txt"))
        if not tailored_txt_files:
            raise HTTPException(
                status_code=404,
                detail=f"No tailored CV text file found for company: {company_name}"
            )
        
        latest_txt_file = max(tailored_txt_files, key=lambda p: p.stat().st_mtime)
        
        # Read the text content
        with open(latest_txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Served tailored CV content: {latest_txt_file.name} ({len(content)} characters)")
        
        return JSONResponse(content={
            "success": True,
            "content": content,
            "filename": latest_txt_file.name,
            "company": company_name,
            "metadata": {
                "file_size": len(content),
                "last_modified": latest_txt_file.stat().st_mtime
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get tailored CV content: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tailored CV content: {str(e)}"
        )


@router.delete("/{filename}")
async def delete_cv(filename: str):
    """Delete a CV file"""
    
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")
        
        # Delete the file
        file_path.unlink()
        
        logger.info(f"CV deleted successfully: {filename}")
        
        return JSONResponse(content={
            "message": "CV deleted successfully",
            "filename": filename
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting CV: {str(e)}")



@router.get("/stats")
async def get_upload_stats():
    """Get upload directory statistics"""
    
    try:
        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "upload_directory": str(UPLOAD_DIR.absolute())
        }
        
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    stats["total_files"] += 1
                    file_size = file_path.stat().st_size
                    stats["total_size"] += file_size
                    
                    file_type = file_path.suffix[1:].upper()
                    if file_type not in stats["file_types"]:
                        stats["file_types"][file_type] = {"count": 0, "size": 0}
                    
                    stats["file_types"][file_type]["count"] += 1
                    stats["file_types"][file_type]["size"] += file_size
        
        # Convert total size to MB for readability
        stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
        
        logger.info(f"Upload stats retrieved: {stats['total_files']} files")
        
        return JSONResponse(content=stats)
        
    except Exception as e:
        logger.error(f"Error getting upload stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting upload stats: {str(e)}")
