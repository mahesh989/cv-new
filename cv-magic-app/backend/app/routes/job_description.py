from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio
from datetime import datetime

from ..services.job_scraper import scrape_job_description_async, is_valid_job_url
from ..services.job_extractor import extract_job_metadata, validate_job_description

router = APIRouter(prefix="/api/job", tags=["Job Description"])


@router.post("/scrape")
async def scrape_job_description(request: Request):
    """
    Scrape job description from a URL.
    
    Request body:
    {
        "url": "https://example.com/job-posting"
    }
    
    Returns:
    {
        "job_description": "extracted text",
        "url": "original url",
        "scraped_at": "timestamp"
    }
    """
    try:
        data = await request.json()
        url = data.get("url")
        
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")
        
        if not is_valid_job_url(url):
            raise HTTPException(status_code=400, detail="Invalid job URL format")
        
        # Scrape the job description
        job_description = await scrape_job_description_async(url)
        
        if job_description.startswith("Error:"):
            raise HTTPException(status_code=422, detail=job_description)
        
        if not job_description or len(job_description.strip()) < 10:
            raise HTTPException(status_code=422, detail="No job description found at the provided URL")
        
        return JSONResponse(content={
            "job_description": job_description,
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "length": len(job_description)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping job description: {str(e)}")


@router.post("/extract-metadata")
async def extract_job_info(request: Request):
    """
    Extract job title and company name from job description using AI.
    
    Request body:
    {
        "job_description": "job description text"
    }
    
    Returns:
    {
        "job_title": "extracted job title",
        "company": "extracted company name"
    }
    """
    try:
        data = await request.json()
        job_description = data.get("job_description", "")
        
        if not job_description:
            raise HTTPException(status_code=400, detail="No job description provided")
        
        # Validate the job description
        validation = validate_job_description(job_description)
        if not validation.get("valid", False):
            raise HTTPException(status_code=400, detail=validation.get("error", "Invalid job description"))
        
        # Extract metadata using AI
        result = await extract_job_metadata(job_description)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting job metadata: {str(e)}")


