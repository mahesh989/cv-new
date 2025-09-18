"""
CV Tailoring API Routes

FastAPI routes for CV tailoring functionality including CV optimization, 
company recommendations management, and tailored CV generation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile, Query
from fastapi.responses import JSONResponse, FileResponse

from app.core.dependencies import get_current_user
from app.models.user import User
from app.tailored_cv.models.cv_models import (
    OriginalCV, RecommendationAnalysis, TailoredCV,
    CVTailoringRequest, CVTailoringResponse,
    AvailableCompanies, CompanyRecommendation,
    ProcessingStatus, CVValidationResult
)
from app.tailored_cv.services.cv_tailoring_service import cv_tailoring_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/tailored-cv", tags=["CV Tailoring"])


@router.post("/tailor", response_model=CVTailoringResponse)
async def tailor_cv(
    request: CVTailoringRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Tailor a CV based on job recommendations and optimization framework
    
    This endpoint takes an original CV and recommendation analysis to generate
    an optimized, tailored CV using the AI-powered optimization framework.
    """
    try:
        logger.info(f"🎯 CV tailoring request for user {current_user.id} - {request.recommendations.company}")
        
        # Process the CV tailoring
        response = await cv_tailoring_service.tailor_cv(request)
        
        # Save tailored CV if successful and company folder is provided
        if response.success and request.company_folder:
            try:
                file_path = cv_tailoring_service.save_tailored_cv(
                    response.tailored_cv, 
                    request.company_folder
                )
                response.processing_summary["saved_to"] = file_path
            except Exception as e:
                logger.warning(f"Failed to save tailored CV: {e}")
                response.warnings = response.warnings or []
                response.warnings.append(f"Failed to save CV: {e}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ CV tailoring endpoint failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CV tailoring failed: {str(e)}"
        )


@router.post("/validate-cv", response_model=CVValidationResult)
async def validate_cv(
    cv: OriginalCV,
    current_user: User = Depends(get_current_user)
):
    """
    Validate CV data structure and content quality
    
    Performs comprehensive validation of CV data including required fields,
    content quality checks, and improvement suggestions.
    """
    try:
        logger.info(f"📋 CV validation request for user {current_user.id}")
        
        validation_result = cv_tailoring_service._validate_cv_data(cv)
        return validation_result
        
    except Exception as e:
        logger.error(f"❌ CV validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CV validation failed: {str(e)}"
        )


@router.get("/companies", response_model=AvailableCompanies)
async def get_available_companies(
    data_folder: str = Query(..., description="Path to data folder containing company recommendations"),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available companies with recommendation files
    
    Scans the specified data folder for company-specific recommendation files
    and returns a list of available companies for CV tailoring.
    """
    try:
        logger.info(f"📁 Fetching available companies from {data_folder} for user {current_user.id}")
        
        data_path = Path(data_folder)
        if not data_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Data folder not found: {data_folder}"
            )
        
        companies = []
        
        # Scan for company folders with recommendation files
        for company_dir in data_path.iterdir():
            if company_dir.is_dir():
                # Look for recommendation files in this company folder
                recommendation_files = list(company_dir.glob("*recommendation*.json"))
                
                if recommendation_files:
                    # Use the most recent recommendation file
                    latest_file = max(recommendation_files, key=lambda p: p.stat().st_mtime)
                    
                    try:
                        # Load recommendation to get company info
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            rec_data = json.load(f)
                        
                        recommendation = RecommendationAnalysis(**rec_data)
                        
                        company_rec = CompanyRecommendation(
                            company=recommendation.company,
                            job_title=recommendation.job_title,
                            recommendations=recommendation,
                            file_path=str(latest_file),
                            last_updated=datetime.fromtimestamp(latest_file.stat().st_mtime)
                        )
                        
                        companies.append(company_rec)
                        
                    except Exception as e:
                        logger.warning(f"Failed to process recommendation file {latest_file}: {e}")
                        continue
        
        return AvailableCompanies(
            companies=companies,
            total_count=len(companies)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get available companies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve companies: {str(e)}"
        )


@router.post("/tailor-with-real-data/{company}")
async def tailor_cv_with_real_data(
    company: str,
    custom_instructions: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Tailor CV using real data from cv-analysis folder
    
    This endpoint loads the original CV and AI recommendation from the cv-analysis folder
    for the specified company and generates a tailored CV, saving it as tailored_cv.json.
    
    Args:
        company: Company name (e.g., "Australia_for_UNHCR", "Google")
        custom_instructions: Optional custom instructions for tailoring
    """
    try:
        logger.info(f"🎯 CV tailoring with real data for user {current_user.id} - {company}")
        
        # First, check what companies are available
        available_companies = cv_tailoring_service.list_available_companies()
        logger.info(f"Available companies: {available_companies}")
        
        if company not in available_companies:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company}' not found. Available companies: {available_companies}"
            )
        
        try:
            # Load real CV and recommendation data
            original_cv, recommendation = cv_tailoring_service.load_real_cv_and_recommendation(company)
            logger.info(f"✅ Loaded real data for {company}")
            
            # Create tailoring request
            request = CVTailoringRequest(
                original_cv=original_cv,
                recommendations=recommendation,
                custom_instructions=custom_instructions,
                company_folder=None  # We'll save manually
            )
            
            # Process the CV tailoring
            response = await cv_tailoring_service.tailor_cv(request)
            
            # Save tailored CV to cv-analysis folder - no fallback, fail if saving fails
            if response.success:
                file_path = cv_tailoring_service.save_tailored_cv_to_analysis_folder(response.tailored_cv, company)
                response.processing_summary["saved_to"] = file_path
                logger.info(f"✅ Tailored CV saved to {file_path}")
            
            return response
            
        except FileNotFoundError as e:
            logger.error(f"❌ File not found for {company}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Required files not found for company '{company}': {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CV tailoring with real data failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CV tailoring failed: {str(e)}"
        )


@router.get("/available-companies")
async def get_available_companies_list(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of companies that have AI recommendation files available for CV tailoring
    """
    try:
        logger.info(f"📋 Fetching available companies for user {current_user.id}")
        
        companies = cv_tailoring_service.list_available_companies()
        
        return {
            "success": True,
            "companies": companies,
            "total_count": len(companies),
            "message": f"Found {len(companies)} companies with AI recommendations"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get available companies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve available companies: {str(e)}"
        )


@router.get("/recommendations/{company_name}")
async def get_company_recommendation(
    company_name: str,
    data_folder: str = Query(..., description="Path to data folder"),
    current_user: User = Depends(get_current_user)
):
    """
    Get recommendation analysis for a specific company
    
    Loads and returns the recommendation analysis file for the specified company.
    """
    try:
        logger.info(f"📋 Fetching recommendation for {company_name} from {data_folder}")
        
        company_folder = Path(data_folder) / company_name
        if not company_folder.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Company folder not found: {company_name}"
            )
        
        try:
            recommendation = cv_tailoring_service.load_recommendation_file(str(company_folder))
            return recommendation
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"No recommendation file found for company: {company_name}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get company recommendation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve recommendation: {str(e)}"
        )


@router.post("/upload-original-cv")
async def upload_original_cv(
    file: UploadFile = File(..., description="Original CV JSON file"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse an original CV file
    
    Accepts a JSON file containing the original CV data and validates its structure.
    """
    try:
        logger.info(f"📤 CV upload for user {current_user.id}, file: {file.filename}")
        
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Only JSON files are accepted"
            )
        
        # Read and parse the file
        content = await file.read()
        try:
            cv_data = json.loads(content)
            original_cv = OriginalCV(**cv_data)
            
            # Validate the CV
            validation_result = cv_tailoring_service._validate_cv_data(original_cv)
            
            return {
                "success": True,
                "cv": original_cv,
                "validation": validation_result,
                "message": "CV uploaded and validated successfully"
            }
            
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CV structure: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CV upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/download-tailored-cv/{company_name}")
async def download_tailored_cv(
    company_name: str,
    data_folder: str = Query(..., description="Path to data folder"),
    current_user: User = Depends(get_current_user)
):
    """
    Download the most recent tailored CV for a company
    
    Returns the latest tailored CV file for the specified company as a downloadable JSON.
    """
    try:
        logger.info(f"📥 Download tailored CV for {company_name} from {data_folder}")
        
        company_folder = Path(data_folder) / company_name
        if not company_folder.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Company folder not found: {company_name}"
            )
        
        # Find the most recent tailored CV file
        tailored_files = list(company_folder.glob("tailored_cv_*.json"))
        if not tailored_files:
            raise HTTPException(
                status_code=404,
                detail=f"No tailored CV found for company: {company_name}"
            )
        
        latest_file = max(tailored_files, key=lambda p: p.stat().st_mtime)
        
        return FileResponse(
            path=str(latest_file),
            media_type='application/json',
            filename=f"{company_name}_tailored_cv.json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )


@router.post("/batch-tailor")
async def batch_tailor_cv(
    original_cv: OriginalCV,
    company_names: List[str],
    background_tasks: BackgroundTasks,
    data_folder: str = Query(..., description="Path to data folder"),
    current_user: User = Depends(get_current_user)
):
    """
    Batch tailor CV for multiple companies
    
    Processes the same CV against multiple company recommendations in the background.
    Returns immediately with a task ID for tracking progress.
    """
    try:
        logger.info(f"🔄 Batch tailoring for user {current_user.id}, companies: {company_names}")
        
        # Validate that all companies exist
        data_path = Path(data_folder)
        missing_companies = []
        
        for company_name in company_names:
            company_folder = data_path / company_name
            if not company_folder.exists():
                missing_companies.append(company_name)
        
        if missing_companies:
            raise HTTPException(
                status_code=404,
                detail=f"Company folders not found: {missing_companies}"
            )
        
        # Generate task ID
        task_id = f"batch_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add background task
        background_tasks.add_task(
            _process_batch_tailoring,
            task_id,
            original_cv,
            company_names,
            data_folder
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "companies": company_names,
            "message": f"Batch tailoring started for {len(company_names)} companies"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Batch tailoring failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch tailoring failed: {str(e)}"
        )


@router.get("/batch-status/{task_id}", response_model=ProcessingStatus)
async def get_batch_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a batch tailoring task
    
    Returns the current status and progress of a batch tailoring operation.
    """
    try:
        # In a real implementation, you'd track this in a database or cache
        # For now, return a placeholder response
        return ProcessingStatus(
            status="processing",
            progress=50,
            current_step="Tailoring CV for company 2 of 4",
            message="Batch processing in progress"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get batch status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )


@router.post("/tailor-real")
async def tailor_cv_with_real_data(
    company: str,
    custom_instructions: str = None,
    target_ats_score: int = 85,
    current_user: User = Depends(get_current_user)
):
    """
    Tailor CV using real CV and recommendation data for a specific company
    
    This endpoint uses the actual CV and recommendation files from cv-analysis folder.
    """
    try:
        logger.info(f"🎯 Real CV tailoring request for company: {company}")
        
        # Load real CV and recommendation data
        original_cv, recommendations = cv_tailoring_service.load_real_cv_and_recommendation(company)
        
        # Create tailoring request
        request = CVTailoringRequest(
            original_cv=original_cv,
            recommendations=recommendations,
            custom_instructions=custom_instructions,
            target_ats_score=target_ats_score
        )
        
        # Process the CV tailoring
        response = await cv_tailoring_service.tailor_cv(request)
        
        return response
        
    except FileNotFoundError as e:
        logger.error(f"❌ Files not found for {company}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"CV or recommendation data not found for company: {company}. Error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Real CV tailoring failed for {company}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CV tailoring failed: {str(e)}"
        )


@router.get("/available-companies-real")
async def get_available_companies_real(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of companies with real recommendation data available
    """
    try:
        cv_analysis_path = Path(__file__).parent.parent.parent.parent.parent / "cv-analysis"
        
        companies = []
        if cv_analysis_path.exists():
            for company_dir in cv_analysis_path.iterdir():
                if company_dir.is_dir() and company_dir.name != "__pycache__":
                    # Check if it has a recommendation file
                    rec_files = list(company_dir.glob("*_ai_recommendation.json"))
                    if rec_files:
                        companies.append({
                            "company": company_dir.name,
                            "display_name": company_dir.name.replace('_', ' '),
                            "recommendation_file": str(rec_files[0]),
                            "last_updated": datetime.fromtimestamp(rec_files[0].stat().st_mtime).isoformat()
                        })
        
        return {
            "companies": companies,
            "total_count": len(companies)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get available companies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve companies: {str(e)}"
        )


@router.get("/framework")
async def get_framework(
    current_user: User = Depends(get_current_user)
):
    """
    Get the CV optimization framework content
    
    Returns the current version of the CV optimization framework for reference.
    """
    try:
        framework_path = Path(__file__).parent.parent / "prompts" / "framework.md"
        
        with framework_path.open('r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "framework_content": content,
            "version": "1.0",
            "last_updated": datetime.fromtimestamp(framework_path.stat().st_mtime).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get framework: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve framework: {str(e)}"
        )


@router.get("/content/{company_name}")
async def get_tailored_cv_content(
    company_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get tailored CV content for frontend preview
    
    This endpoint serves the most recent tailored CV text content for a company,
    compatible with the frontend CV preview functionality.
    """
    try:
        logger.info(f"📄 Tailored CV content request for {company_name} from user {current_user.id}")
        
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


# Background task function
async def _process_batch_tailoring(
    task_id: str,
    original_cv: OriginalCV,
    company_names: List[str],
    data_folder: str
):
    """
    Background task to process batch CV tailoring
    
    This would typically update a database or cache with progress information.
    """
    try:
        logger.info(f"🔄 Starting batch processing for task {task_id}")
        
        results = {}
        data_path = Path(data_folder)
        
        for i, company_name in enumerate(company_names):
            try:
                company_folder = data_path / company_name
                
                # Load recommendation
                recommendation = cv_tailoring_service.load_recommendation_file(str(company_folder))
                
                # Create tailoring request
                request = CVTailoringRequest(
                    original_cv=original_cv,
                    recommendations=recommendation,
                    company_folder=str(company_folder)
                )
                
                # Process tailoring
                response = await cv_tailoring_service.tailor_cv(request)
                
                # Save result
                if response.success:
                    file_path = cv_tailoring_service.save_tailored_cv(
                        response.tailored_cv,
                        str(company_folder)
                    )
                    results[company_name] = {
                        "success": True,
                        "file_path": file_path,
                        "ats_score": response.tailored_cv.estimated_ats_score
                    }
                else:
                    results[company_name] = {
                        "success": False,
                        "error": response.processing_summary.get("error", "Unknown error")
                    }
                
                logger.info(f"✅ Completed tailoring for {company_name} ({i+1}/{len(company_names)})")
                
            except Exception as e:
                logger.error(f"❌ Failed to process {company_name}: {e}")
                results[company_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        logger.info(f"🎉 Batch processing completed for task {task_id}")
        # In a real implementation, you'd save results to database/cache here
        
    except Exception as e:
        logger.error(f"❌ Batch processing failed for task {task_id}: {e}")


# Export router
__all__ = ["router"]