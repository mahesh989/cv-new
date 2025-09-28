from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, AnyHttpUrl

from ..services.job_scraper import scrape_job_description_async, is_valid_job_url
from ..services.job_extractor import extract_job_metadata, validate_job_description
from ..utils.directory_utils import ensure_cv_analysis_directories

class JobScrapeRequest(BaseModel):
    url: AnyHttpUrl

router = APIRouter(prefix="/api/job", tags=["Job Description"])




@router.post("/scrape")
async def scrape_job_description(request_data: JobScrapeRequest, request: Request):
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
        # Ensure required directories exist before processing
        ensure_cv_analysis_directories()
        
        url = str(request_data.url)
        
        if not is_valid_job_url(url):
            raise HTTPException(status_code=400, detail="Invalid job URL format")
        
        # Get external context if available
        raw_body = await request.body()
        if raw_body:
            try:
                body = await request.json()
                external_context = body.get('external_context', [])
            except:
                external_context = []
        else:
            external_context = []
        
        # Scrape the job description
        job_description = await scrape_job_description_async(url, external_context)
        
        if (job_description.startswith("Error:") or 
            job_description.startswith("Error fetching") or 
            job_description.startswith("Unexpected error")):
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
        # Ensure required directories exist before processing
        ensure_cv_analysis_directories()
        
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


