"""
Simplified Job Description extraction routes with intelligent scraping
"""
import logging
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from ..services.jd_extractor import jd_extractor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jd", tags=["Job Description"])


class JDExtractionRequest(BaseModel):
    """Request model for JD extraction from URL"""
    url: str = Field(..., description="Job posting URL")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate and normalize URL format"""
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        parsed = urlparse(v)
        if not parsed.netloc:
            raise ValueError('Invalid URL format')
        
        return v


class JDTextRequest(BaseModel):
    """Request model for direct JD text processing"""
    text: str = Field(..., min_length=50, description="Job description text content")
    title: Optional[str] = Field(None, description="Optional job title")
    company: Optional[str] = Field(None, description="Optional company name")


@router.post("/extract")
async def extract_jd_from_url(request: JDExtractionRequest):
    """Extract job description from URL with intelligent scraping"""
    
    try:
        logger.info(f"Extracting JD from URL: {request.url}")
        
        # Extract content from URL
        result = jd_extractor.extract_from_url(request.url)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract JD: {result['error']}"
            )
        
        content = result['content']
        
        # Get extraction metadata
        metadata = {
            "url": request.url,
            "domain": urlparse(request.url).netloc,
            "extraction_method": result.get('method', 'generic'),
            "content_length": len(content),
            "word_count": len(content.split()),
            "title": result.get('title'),
            "company": result.get('company'),
            "location": result.get('location')
        }
        
        # Generate preview
        preview = jd_extractor.get_text_preview(content, 300)
        
        # Extract key information
        key_info = jd_extractor.extract_key_information(content)
        
        logger.info(f"JD extracted successfully: {len(content)} characters from {metadata['domain']}")
        
        return JSONResponse(content={
            "success": True,
            "content": content,
            "preview": preview,
            "metadata": metadata,
            "key_info": key_info,
            "extraction_stats": {
                "characters": len(content),
                "words": len(content.split()),
                "paragraphs": len([p for p in content.split('\n\n') if p.strip()]),
                "estimated_reading_time": max(1, len(content.split()) // 200)  # minutes
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting JD from URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting JD: {str(e)}")


@router.post("/process-text")
async def process_jd_text(request: JDTextRequest):
    """Process job description from direct text input"""
    
    try:
        logger.info(f"Processing JD text: {len(request.text)} characters")
        
        # Validate text length
        if len(request.text) > 50000:  # 50KB limit
            raise HTTPException(
                status_code=400, 
                detail="Job description text too long (max 50KB)"
            )
        
        # Process text content
        processed_content = jd_extractor.clean_and_structure_text(request.text)
        
        # Extract key information
        key_info = jd_extractor.extract_key_information(processed_content)
        
        # Generate preview
        preview = jd_extractor.get_text_preview(processed_content, 300)
        
        metadata = {
            "source": "direct_text",
            "original_length": len(request.text),
            "processed_length": len(processed_content),
            "word_count": len(processed_content.split()),
            "title": request.title,
            "company": request.company
        }
        
        logger.info(f"JD text processed successfully: {len(processed_content)} characters")
        
        return JSONResponse(content={
            "success": True,
            "content": processed_content,
            "preview": preview,
            "metadata": metadata,
            "key_info": key_info,
            "processing_stats": {
                "original_characters": len(request.text),
                "processed_characters": len(processed_content),
                "reduction_percentage": round((1 - len(processed_content) / len(request.text)) * 100, 2) if len(request.text) > 0 else 0,
                "words": len(processed_content.split()),
                "estimated_reading_time": max(1, len(processed_content.split()) // 200)
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing JD text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing JD text: {str(e)}")


@router.post("/test-url")
async def test_url_extraction(url: str):
    """Test URL extraction without full processing - for validation"""
    
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        if not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        logger.info(f"Testing URL extraction: {url}")
        
        # Test extraction with limited processing
        result = jd_extractor.extract_from_url(url, preview_only=True)
        
        if result['success']:
            content = result['content']
            preview = jd_extractor.get_text_preview(content, 500)
            
            return JSONResponse(content={
                "success": True,
                "url": url,
                "domain": parsed.netloc,
                "preview": preview,
                "content_length": len(content),
                "word_count": len(content.split()),
                "extraction_method": result.get('method', 'generic'),
                "estimated_full_length": len(content),
                "test_timestamp": result.get('timestamp')
            })
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract from URL: {result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing URL extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing URL: {str(e)}")


@router.get("/supported-sites")
async def get_supported_sites():
    """Get list of supported job posting sites with extraction confidence"""
    
    try:
        supported_sites = jd_extractor.get_supported_sites()
        
        return JSONResponse(content={
            "supported_sites": supported_sites,
            "total_sites": len(supported_sites),
            "extraction_methods": {
                "site_specific": len([s for s in supported_sites if s.get("confidence") == "high"]),
                "generic_fallback": len([s for s in supported_sites if s.get("confidence") == "medium"]),
                "experimental": len([s for s in supported_sites if s.get("confidence") == "low"])
            },
            "note": "Sites not listed may still work using generic extraction methods"
        })
        
    except Exception as e:
        logger.error(f"Error getting supported sites: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting supported sites: {str(e)}")


@router.get("/extraction-stats")
async def get_extraction_stats():
    """Get extraction statistics and performance metrics"""
    
    try:
        stats = jd_extractor.get_extraction_stats()
        
        return JSONResponse(content={
            "extraction_stats": stats,
            "performance_metrics": {
                "average_extraction_time": stats.get("avg_extraction_time", 0),
                "success_rate": stats.get("success_rate", 0),
                "total_extractions": stats.get("total_extractions", 0)
            },
            "popular_domains": stats.get("popular_domains", []),
            "common_errors": stats.get("common_errors", [])
        })
        
    except Exception as e:
        logger.error(f"Error getting extraction stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting extraction stats: {str(e)}")


@router.post("/analyze-content")
async def analyze_jd_content(text: str):
    """Analyze JD content for quality and completeness"""
    
    try:
        if not text or len(text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Text too short for analysis")
        
        logger.info(f"Analyzing JD content: {len(text)} characters")
        
        # Extract key information
        key_info = jd_extractor.extract_key_information(text)
        
        # Analyze content quality
        analysis = {
            "content_length": len(text),
            "word_count": len(text.split()),
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
            "readability_score": jd_extractor.calculate_readability_score(text),
            "completeness_score": jd_extractor.calculate_completeness_score(key_info),
            "structure_score": jd_extractor.calculate_structure_score(text)
        }
        
        # Generate recommendations
        recommendations = jd_extractor.generate_content_recommendations(analysis, key_info)
        
        return JSONResponse(content={
            "analysis": analysis,
            "key_information": key_info,
            "recommendations": recommendations,
            "overall_quality": jd_extractor.calculate_overall_quality(analysis),
            "missing_elements": jd_extractor.identify_missing_elements(key_info)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing JD content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing JD content: {str(e)}")
