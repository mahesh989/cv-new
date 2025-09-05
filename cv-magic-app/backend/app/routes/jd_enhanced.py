"""
Enhanced Job Description extraction routes with improved functionality
"""
import logging
from typing import Optional, List
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field, validator

from ..enhanced_database import enhanced_db
from ..models.enhanced import (
    JDExtractionResponse, JDListResponse, JDContentResponse,
    SuccessResponse, ErrorResponse, JDSource
)
from ..services.jd_extractor import jd_extractor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jd-enhanced", tags=["JD Enhanced"])


class JDExtractionRequest(BaseModel):
    """Request model for JD extraction"""
    url: str = Field(..., description="Job posting URL")
    title: Optional[str] = Field(None, description="Optional job title")
    company: Optional[str] = Field(None, description="Optional company name")
    location: Optional[str] = Field(None, description="Optional job location")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        parsed = urlparse(v)
        if not parsed.netloc:
            raise ValueError('Invalid URL format')
        
        return v


class JDDirectTextRequest(BaseModel):
    """Request model for direct text JD processing"""
    text: str = Field(..., description="Job description text content")
    title: Optional[str] = Field(None, description="Optional job title")
    company: Optional[str] = Field(None, description="Optional company name")
    location: Optional[str] = Field(None, description="Optional job location")
    source_url: Optional[str] = Field(None, description="Optional source URL")
    

async def process_jd_extraction(jd_id: str):
    """Background task to extract JD content"""
    try:
        # Get JD info
        jd_info = enhanced_db.get_jd(jd_id)
        if not jd_info:
            logger.error(f"JD not found: {jd_id}")
            return
        
        # Extract content from URL
        result = jd_extractor.extract_from_url(jd_info.source_url)
        
        if result['success']:
            # Update JD with extracted content
            enhanced_db.update_jd_content(
                jd_id=jd_id,
                content=result['content'],
                title=result.get('title'),
                company=result.get('company'),
                location=result.get('location')
            )
            logger.info(f"JD processed successfully: {jd_id}")
        else:
            logger.error(f"JD processing failed: {jd_id} - {result['error']}")
            
    except Exception as e:
        logger.error(f"Error processing JD {jd_id}: {str(e)}")


@router.post("/extract", response_model=JDExtractionResponse)
async def extract_jd(
    background_tasks: BackgroundTasks,
    request: JDExtractionRequest
):
    """Extract job description from URL"""
    
    try:
        # Save JD extraction request to database
        jd_response = enhanced_db.save_jd(
            source_url=request.url,
            source=JDSource.URL,
            title=request.title,
            company=request.company,
            location=request.location
        )
        
        # Process JD extraction in background
        background_tasks.add_task(process_jd_extraction, jd_response.id)
        
        logger.info(f"JD extraction started: {request.url} (ID: {jd_response.id})")
        
        return jd_response
        
    except Exception as e:
        logger.error(f"Error extracting JD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting JD: {str(e)}")


@router.post("/extract-text", response_model=JDExtractionResponse)
async def extract_jd_from_text(request: JDDirectTextRequest):
    """Process job description from direct text input"""
    
    try:
        # Validate text length
        if len(request.text) < 50:
            raise HTTPException(status_code=400, detail="Job description text too short")
        
        if len(request.text) > 50000:  # 50KB limit
            raise HTTPException(status_code=400, detail="Job description text too long")
        
        # Process text content
        processed_content = jd_extractor.clean_and_structure_text(request.text)
        
        # Save JD to database
        jd_response = enhanced_db.save_jd(
            source_url=request.source_url or "direct_text",
            source=JDSource.DIRECT_TEXT,
            title=request.title,
            company=request.company,
            location=request.location,
            content=processed_content
        )
        
        logger.info(f"JD processed from text: (ID: {jd_response.id})")
        
        return jd_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing JD text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing JD text: {str(e)}")


@router.get("/list", response_model=JDListResponse)
async def list_jds(
    page: int = 1, 
    limit: int = 10,
    source: Optional[JDSource] = Query(None, description="Filter by source type")
):
    """List extracted job descriptions with pagination"""
    
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
            
        jds = enhanced_db.list_jds(page=page, limit=limit, source=source)
        total = enhanced_db.count_jds(source=source)
        
        return JDListResponse(
            jds=jds,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing JDs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing JDs: {str(e)}")


@router.get("/{jd_id}", response_model=JDContentResponse)
async def get_jd_content(jd_id: str):
    """Get job description content by ID"""
    
    try:
        # Get JD info
        jd_info = enhanced_db.get_jd(jd_id)
        if not jd_info:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Get JD content
        content = enhanced_db.get_jd_content(jd_id)
        if not content:
            # Check if JD is still being processed
            if jd_info.processing_status.value == 'pending':
                raise HTTPException(status_code=202, detail="Job description is still being processed")
            else:
                raise HTTPException(status_code=404, detail="Job description content not available")
        
        return JDContentResponse(
            id=jd_info.id,
            title=jd_info.title,
            company=jd_info.company,
            location=jd_info.location,
            source_url=jd_info.source_url,
            source=jd_info.source,
            content=content,
            processing_status=jd_info.processing_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting JD content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting JD content: {str(e)}")


@router.get("/{jd_id}/preview")
async def get_jd_preview(jd_id: str, max_length: int = 500):
    """Get job description content preview"""
    
    try:
        # Get JD content
        content = enhanced_db.get_jd_content(jd_id)
        if not content:
            raise HTTPException(status_code=404, detail="Job description content not available")
        
        # Generate preview
        preview = jd_extractor.get_text_preview(content, max_length)
        
        # Extract key information
        key_info = jd_extractor.extract_key_information(content)
        
        return {
            "jd_id": jd_id,
            "preview": preview,
            "full_length": len(content),
            "preview_length": len(preview),
            "key_info": key_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting JD preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting JD preview: {str(e)}")


@router.delete("/{jd_id}", response_model=SuccessResponse)
async def delete_jd(jd_id: str):
    """Delete job description"""
    
    try:
        deleted = enhanced_db.delete_jd(jd_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        logger.info(f"JD deleted: {jd_id}")
        return SuccessResponse(message="Job description deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting JD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting JD: {str(e)}")


@router.post("/{jd_id}/reprocess", response_model=SuccessResponse)
async def reprocess_jd(jd_id: str, background_tasks: BackgroundTasks):
    """Reprocess job description extraction"""
    
    try:
        # Check if JD exists and has URL source
        jd_info = enhanced_db.get_jd(jd_id)
        if not jd_info:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        if jd_info.source != JDSource.URL:
            raise HTTPException(
                status_code=400, 
                detail="Cannot reprocess job descriptions from non-URL sources"
            )
        
        # Reprocess JD in background
        background_tasks.add_task(process_jd_extraction, jd_id)
        
        logger.info(f"JD reprocessing started: {jd_id}")
        return SuccessResponse(message="Job description reprocessing started")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing JD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reprocessing JD: {str(e)}")


@router.get("/{jd_id}/stats")
async def get_jd_stats(jd_id: str):
    """Get job description processing statistics"""
    
    try:
        # Get JD info
        jd_info = enhanced_db.get_jd(jd_id)
        if not jd_info:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Get content for analysis
        content = enhanced_db.get_jd_content(jd_id)
        
        stats = {
            "jd_id": jd_id,
            "title": jd_info.title,
            "company": jd_info.company,
            "location": jd_info.location,
            "source": jd_info.source,
            "source_url": jd_info.source_url,
            "processing_status": jd_info.processing_status,
            "extraction_date": jd_info.extraction_date,
        }
        
        if content:
            key_info = jd_extractor.extract_key_information(content)
            stats.update({
                "content_length": len(content),
                "word_count": len(content.split()),
                "has_requirements": key_info.get('has_requirements', False),
                "has_skills": key_info.get('has_skills', False),
                "has_experience": key_info.get('has_experience', False),
                "has_education": key_info.get('has_education', False),
                "has_salary": key_info.get('has_salary', False),
                "technical_skills_count": len(key_info.get('technical_skills', [])),
                "soft_skills_count": len(key_info.get('soft_skills', [])),
            })
        else:
            stats.update({
                "content_length": 0,
                "word_count": 0,
                "content_available": False
            })
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting JD stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting JD stats: {str(e)}")


@router.get("/supported-sites/list")
async def get_supported_sites():
    """Get list of supported job posting sites"""
    
    try:
        supported_sites = jd_extractor.get_supported_sites()
        
        return {
            "supported_sites": supported_sites,
            "total_sites": len(supported_sites),
            "note": "Other sites may also work using generic extraction methods"
        }
        
    except Exception as e:
        logger.error(f"Error getting supported sites: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting supported sites: {str(e)}")


@router.post("/test-url")
async def test_url_extraction(url: str):
    """Test URL extraction without saving to database"""
    
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        if not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Test extraction
        result = jd_extractor.extract_from_url(url)
        
        if result['success']:
            # Return preview of extracted content
            preview = jd_extractor.get_text_preview(result['content'], 1000)
            key_info = jd_extractor.extract_key_information(result['content'])
            
            return {
                "success": True,
                "url": url,
                "extracted_title": result.get('title'),
                "extracted_company": result.get('company'),
                "extracted_location": result.get('location'),
                "content_preview": preview,
                "content_length": len(result['content']),
                "word_count": len(result['content'].split()),
                "key_info": key_info,
                "extraction_method": result.get('method', 'unknown')
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to extract content: {result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing URL extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing URL extraction: {str(e)}")
