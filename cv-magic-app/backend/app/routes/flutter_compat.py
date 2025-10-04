"""
Flutter-compatible API routes
Provides endpoints that match the Flutter app's expectations
"""
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse

from .cv_simple import (
    upload_cv,
    list_cvs,
    get_cv_content,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    get_user_upload_dir
)
from ..services.cv_processor import cv_processor
from ..services.jd_extractor import jd_extractor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Flutter Compatible"])


@router.post("/upload-cv")
async def upload_cv_flutter(file: UploadFile = File(...)):
    """Upload CV endpoint compatible with Flutter app"""
    
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "No filename provided"
            }
        )
    
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            }
        )
    
    try:
        # Read and validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "File too large. Maximum size is 10MB"
                }
            )
        
        # Save file to upload directory
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"CV uploaded successfully: {file.filename} ({len(file_content)} bytes)")
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "message": "CV uploaded successfully",
            "size": len(file_content),
            "type": file_extension[1:].upper()  # Remove dot and uppercase
        })
        
    except Exception as e:
        logger.error(f"Error uploading CV: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Upload failed: {str(e)}"
            }
        )


@router.get("/cv-list")
async def list_cvs_flutter():
    """List CVs endpoint compatible with Flutter app"""
    
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
        
        # Sort by upload date (newest first)
        cvs.sort(key=lambda x: x['uploaded_date'], reverse=True)
        
        logger.info(f"Listed {len(cvs)} CV files")
        
        return JSONResponse(content={
            "success": True,
            "cvs": cvs,
            "total_count": len(cvs)
        })
        
    except Exception as e:
        logger.error(f"Error listing CVs: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to list CVs: {str(e)}",
                "cvs": []
            }
        )


@router.get("/cv/{filename}/content")
async def get_cv_content_flutter(filename: str):
    """Get CV content endpoint compatible with Flutter app"""
    
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "CV file not found"
                }
            )
        
        # Extract text using improved processor
        result = cv_processor.extract_text_from_file(file_path)
        
        if not result['success']:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Failed to extract text: {result['error']}"
                }
            )
        
        logger.info(f"CV content extracted: {filename} ({len(result['text'])} characters)")
        
        return JSONResponse(content={
            "success": True,
            "content": result['text'],
            "filename": filename,
            "metadata": result.get('metadata', {}),
            "extraction_info": {
                "method": result.get('method', 'unknown'),
                "character_count": len(result['text']),
                "word_count": len(result['text'].split())
            }
        })
        
    except Exception as e:
        logger.error(f"Error extracting CV content: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to get CV content: {str(e)}"
            }
        )


@router.get("/cv/{filename}/preview")
async def get_cv_preview_flutter(filename: str, limit: int = 500):
    """Get CV preview endpoint compatible with Flutter app"""
    
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "CV file not found"
                }
            )
        
        # Extract text
        result = cv_processor.extract_text_from_file(file_path)
        
        if not result['success']:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Failed to extract text: {result['error']}"
                }
            )
        
        # Generate preview
        full_text = result['text']
        preview = cv_processor.get_text_preview(full_text, limit)
        
        logger.info(f"CV preview generated: {filename} ({len(preview)} characters)")
        
        return JSONResponse(content={
            "success": True,
            "preview": preview,
            "filename": filename,
            "full_length": len(full_text),
            "preview_length": len(preview),
            "is_truncated": len(full_text) > limit
        })
        
    except Exception as e:
        logger.error(f"Error generating CV preview: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to generate preview: {str(e)}"
            }
        )


@router.post("/extract-jd")
async def extract_jd_flutter(request: Request):
    """Extract Job Description from URL - Flutter compatibility endpoint.

    Expects JSON: { "url": "https://..." }
    Returns: { success: bool, content: str, metadata?: {}, message?: str }
    """

    try:
        body = await request.json()
        url = (body or {}).get("url", "").strip()

        if not url:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Missing 'url' in request body"
            })

        result = jd_extractor.extract_from_url(url)
        if not result.get("success"):
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": result.get("error", "Failed to extract job description")
            })

        return JSONResponse(content={
            "success": True,
            "content": result.get("content") or result.get("text") or "",
            "metadata": result.get("metadata", {}),
        })

    except Exception as e:
        logger.error(f"Error extracting JD (compat): {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Error extracting job description: {str(e)}"
        })


@router.get("/upload-stats")
async def get_upload_stats_flutter():
    """Get upload statistics endpoint compatible with Flutter app"""
    
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
        
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting upload stats: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to get upload stats: {str(e)}"
            }
        )
