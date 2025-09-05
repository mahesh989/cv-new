from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from ..services.job_extraction_service import job_extraction_service
from ..core.dependencies import get_current_user
from ..models.auth import UserData

router = APIRouter(prefix="/api/job-analysis", tags=["Job Analysis"])


@router.post("/extract-and-save")
async def extract_and_save_job(request: Request, current_user: UserData = Depends(get_current_user)):
    """
    Extract job information and save to organized folder structure.
    
    Request body:
    {
        "job_description": "job description text",
        "job_url": "optional job posting URL"
    }
    
    Returns:
    {
        "success": true,
        "company_slug": "company_folder_name",
        "company_name": "extracted company name",
        "job_title": "extracted job title",
        "job_info_file": "path to job_info JSON file",
        "jd_original_file": "path to jd_original.txt file",
        "extracted_info": {...}
    }
    """
    try:
        data = await request.json()
        job_description = data.get("job_description", "")
        job_url = data.get("job_url", "")
        
        if not job_description:
            raise HTTPException(status_code=400, detail="No job description provided")
        
        # Extract auth token from request headers
        auth_token = request.headers.get("authorization", "").replace("Bearer ", "")
        
        # Extract and save job information with LLM
        result = await job_extraction_service.save_job_analysis(
            job_description=job_description,
            job_url=job_url if job_url else None,
            auth_token=auth_token if auth_token else None
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing job analysis: {str(e)}")


@router.get("/list")
async def list_analyzed_jobs():
    """
    List all analyzed jobs in the cv-analysis directory.
    
    Returns:
    {
        "jobs": [
            {
                "company_slug": "company_folder_name",
                "company_name": "company name",
                "job_title": "job title",
                "location": "location",
                "industry": "industry",
                "extracted_at": "timestamp",
                "job_info_file": "path to job_info JSON file",
                "jd_original_file": "path to jd_original.txt file",
                "has_jd_original": true/false
            }
        ]
    }
    """
    try:
        result = job_extraction_service.list_analyzed_jobs()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing analyzed jobs: {str(e)}")


@router.get("/job-info/{company_slug}")
async def get_job_info(company_slug: str):
    """
    Get job information for a specific company.
    
    Returns:
    {
        "company_slug": "company_folder_name",
        "job_info": {...},
        "jd_original_content": "original job description text"
    }
    """
    try:
        from pathlib import Path
        import json
        
        # Look for the company directory
        company_dir = Path("cv-analysis") / company_slug
        
        if not company_dir.exists():
            raise HTTPException(status_code=404, detail="Company analysis not found")
        
        # Load job_info JSON
        job_info_files = list(company_dir.glob("job_info_*.json"))
        if not job_info_files:
            raise HTTPException(status_code=404, detail="Job info file not found")
        
        with open(job_info_files[0], 'r', encoding='utf-8') as f:
            job_info = json.load(f)
        
        # Load original job description
        jd_original_file = company_dir / "jd_original.txt"
        jd_original_content = ""
        if jd_original_file.exists():
            with open(jd_original_file, 'r', encoding='utf-8') as f:
                jd_original_content = f.read()
        
        return JSONResponse(content={
            "company_slug": company_slug,
            "job_info": job_info,
            "jd_original_content": jd_original_content
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving job info: {str(e)}")


@router.delete("/delete/{company_slug}")
async def delete_job_analysis(company_slug: str):
    """
    Delete job analysis for a specific company.
    
    Returns:
    {
        "message": "Job analysis deleted successfully"
    }
    """
    try:
        import shutil
        from pathlib import Path
        
        # Look for the company directory
        company_dir = Path("cv-analysis") / company_slug
        
        if not company_dir.exists():
            raise HTTPException(status_code=404, detail="Company analysis not found")
        
        # Remove the entire company directory
        shutil.rmtree(company_dir)
        
        return JSONResponse(content={
            "message": f"Job analysis for {company_slug} deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting job analysis: {str(e)}")
