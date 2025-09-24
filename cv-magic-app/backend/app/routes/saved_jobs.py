"""
Saved Jobs API Routes

Endpoints for managing saved job data.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from datetime import datetime

from ..services.saved_jobs_service import saved_jobs_service

router = APIRouter(prefix="/api/jobs", tags=["Saved Jobs"])

@router.get("/saved")
async def get_saved_jobs():
    """Get all saved jobs."""
    try:
        jobs = saved_jobs_service.get_all_jobs()
        return JSONResponse(content={
            "success": True,
            "jobs": jobs,
            "total": len(jobs),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved/{job_url:path}")
async def get_job_by_url(job_url: str):
    """Get a specific job by its URL."""
    try:
        job = saved_jobs_service.get_job_by_url(job_url)
        if job:
            return JSONResponse(content={
                "success": True,
                "job": job
            })
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "Job not found"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_job(job_data: Dict):
    """Save a new job."""
    try:
        if not job_data.get("job_url"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "job_url is required"
                }
            )

        success = saved_jobs_service.save_new_job(job_data)
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "Job saved successfully",
                "job": job_data
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Failed to save job"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/saved/{job_url:path}")
async def delete_job(job_url: str):
    """Delete a saved job."""
    try:
        success = saved_jobs_service.delete_job(job_url)
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "Job deleted successfully"
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Failed to delete job"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/saved")
async def clear_all_jobs():
    """Clear all saved jobs."""
    try:
        success = saved_jobs_service.clear_all_jobs()
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "All jobs cleared successfully"
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Failed to clear jobs"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))