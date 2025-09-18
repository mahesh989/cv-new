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


@router.get("/latest-cv-content")
async def get_latest_cv_content():
    """
    Get the latest CV content (from either original or tailored folder) for frontend preview
    This is a general endpoint that doesn't require a company name
    """
    try:
        logger.info("📄 Latest CV content request")
        
        # Use dynamic CV selector to get the latest CV
        from app.services.dynamic_cv_selector import dynamic_cv_selector
        
        # Get the latest CV files (could be from original or tailored folder)
        latest_cv_paths = dynamic_cv_selector.get_latest_cv_paths_for_services()
        
        if not latest_cv_paths['txt_path']:
            raise HTTPException(
                status_code=404,
                detail="No CV text file found in cvs folders"
            )
        
        latest_txt_file = Path(latest_cv_paths['txt_path'])
        
        # Check if it exists
        if not latest_txt_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"CV text file not found: {latest_txt_file}"
            )
        
        # Read the text content
        with open(latest_txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Served latest CV content: {latest_txt_file.name} from {latest_cv_paths['txt_source']} folder ({len(content)} characters)")
        
        return JSONResponse(content={
            "success": True,
            "content": content,
            "filename": latest_txt_file.name,
            "source_folder": latest_cv_paths['txt_source'],
            "metadata": {
                "file_size": len(content),
                "last_modified": latest_txt_file.stat().st_mtime,
                "dynamic_selection": True
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get latest CV content: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest CV content: {str(e)}"
        )


@router.get("/read-tailored-cv/{company_name}")
async def read_tailored_cv(company_name: str):
    """
    Read tailored CV content for frontend preview
    
    This endpoint serves the most recent tailored CV text content for a company,
    compatible with the frontend CV preview functionality.
    """
    try:
        logger.info(f"📄 Tailored CV content request for {company_name}")
        
        # Use dynamic CV selector to get the latest tailored CV
        from app.services.dynamic_cv_selector import dynamic_cv_selector
        
        # Get the latest CV files (could be from original or tailored folder)
        latest_cv_paths = dynamic_cv_selector.get_latest_cv_paths_for_services()
        
        if not latest_cv_paths['txt_path']:
            raise HTTPException(
                status_code=404,
                detail="No CV text file found in cvs folders"
            )
        
        latest_txt_file = Path(latest_cv_paths['txt_path'])
        
        # Check if it exists
        if not latest_txt_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"CV text file not found: {latest_txt_file}"
            )
        
        # File is already the latest from dynamic selector
        
        # Read the text content
        with open(latest_txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Served CV content: {latest_txt_file.name} from {latest_cv_paths['txt_source']} folder ({len(content)} characters)")
        
        return JSONResponse(content={
            "success": True,
            "content": content,
            "filename": latest_txt_file.name,
            "company": company_name,
            "source_folder": latest_cv_paths['txt_source'],
            "metadata": {
                "file_size": len(content),
                "last_modified": latest_txt_file.stat().st_mtime,
                "dynamic_selection": True
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


@router.get("/latest-tailored-cv")
async def get_latest_tailored_cv():
    """
    Get the most recent tailored CV across all companies
    
    This endpoint finds the latest tailored CV file across all company folders
    and returns its content for frontend preview.
    """
    try:
        logger.info("📄 Fetching latest tailored CV across all companies")
        
        # Path to cv-analysis folder
        cv_analysis_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        
        if not cv_analysis_path.exists():
            raise HTTPException(
                status_code=404,
                detail="CV analysis folder not found"
            )
        
        # Find all tailored CV text files across all company folders
        all_tailored_files = []
        for company_dir in cv_analysis_path.iterdir():
            if company_dir.is_dir() and company_dir.name != "__pycache__":
                # Look for company-specific naming pattern first
                company_files = list(company_dir.glob(f"{company_dir.name}_tailored_cv_*.txt"))
                if not company_files:
                    # Fallback to any tailored CV files
                    company_files = list(company_dir.glob("*tailored_cv_*.txt"))
                
                all_tailored_files.extend(company_files)
        
        if not all_tailored_files:
            raise HTTPException(
                status_code=404,
                detail="No tailored CV files found in any company folder"
            )
        
        # Sort by timestamp in filename first, then by modified time as fallback
        def get_timestamp(filepath):
            try:
                # Extract timestamp from filename pattern company_tailored_cv_YYYYMMDD_HHMMSS.txt
                filename = filepath.name
                timestamp_part = filename.split('_tailored_cv_')[1].replace('.txt', '')
                # Convert to datetime for proper comparison
                from datetime import datetime
                return datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
            except:
                # Fallback to file modification time if filename parsing fails
                return filepath.stat().st_mtime
        
        latest_txt_file = max(all_tailored_files, key=get_timestamp)
        
        # Extract company name from file path
        company_name = latest_txt_file.parent.name
        
        # Read the text content
        with open(latest_txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Served latest tailored CV: {latest_txt_file.name} from {company_name} ({len(content)} characters)")
        
        return JSONResponse(content={
            "success": True,
            "content": content,
            "filename": latest_txt_file.name,
            "company": company_name,
            "metadata": {
                "file_size": len(content),
                "last_modified": latest_txt_file.stat().st_mtime,
                "file_path": str(latest_txt_file)
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get latest tailored CV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest tailored CV: {str(e)}"
        )

@router.get("/available-companies")
async def get_available_companies():
    """
    Get list of available companies with tailored CVs
    
    Returns companies that have tailored CV files available for preview.
    """
    try:
        logger.info("📋 Fetching available companies")
        
        # Path to cv-analysis folder
        cv_analysis_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        companies = []
        
        if cv_analysis_path.exists():
            for company_dir in cv_analysis_path.iterdir():
                if company_dir.is_dir() and company_dir.name != "__pycache__":
                    # Check if it has tailored CV files with company-specific naming
                    company_name = company_dir.name
                    tailored_files = list(company_dir.glob(f"{company_name}_tailored_cv_*.txt"))
                    if not tailored_files:
                        # Fallback to any tailored CV files
                        tailored_files = list(company_dir.glob("*tailored_cv_*.txt"))
                    
                    if tailored_files:
                        companies.append({
                            "company": company_name,
                            "display_name": company_name.replace('_', ' '),
                            "has_tailored_cv": True,
                            "last_updated": max(tailored_files, key=lambda p: p.stat().st_mtime).stat().st_mtime
                        })
        
        logger.info(f"✅ Found {len(companies)} companies with tailored CVs")
        
        return JSONResponse(content={
            "success": True,
            "companies": companies,
            "total_count": len(companies)
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get available companies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve companies: {str(e)}"
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
