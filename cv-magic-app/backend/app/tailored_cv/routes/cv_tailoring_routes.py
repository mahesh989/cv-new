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
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile, Query, Request
from fastapi.responses import JSONResponse, FileResponse

from app.core.dependencies import get_current_user
from app.models.user import User
from app.tailored_cv.models.cv_models import (
    OriginalCV, RecommendationAnalysis, TailoredCV,
    CVTailoringRequest, CVTailoringResponse,
    AvailableCompanies, CompanyRecommendation,
    ProcessingStatus, CVValidationResult
)
from app.tailored_cv.services.cv_tailoring_service import CVTailoringService

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
        
        # Create user-specific service instance
        cv_service = CVTailoringService(user_email=current_user.email)
        
        # Process the CV tailoring
        response = await cv_service.tailor_cv(request)
        
        # Save tailored CV if successful - ONLY to tailored folder
        if response.success:
            try:
                # Extract company name from recommendations
                company = request.recommendations.company if hasattr(request.recommendations, 'company') else "Unknown"
                file_path = cv_service.save_tailored_cv_to_analysis_folder(
                    response.tailored_cv, 
                    company
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
        
        # Create user-specific service instance
        cv_tailoring_service = CVTailoringService(user_email=current_user.email)
        
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
    Tailor CV using real CV and recommendation data for a specific company (requires auth)
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


@router.post("/tailor-real-test")
async def tailor_cv_with_real_data_test(
    company: str,
    custom_instructions: str = None,
    target_ats_score: int = 85
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


@router.post("/save-edited")
async def save_edited_cv(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Save edited CV content to both JSON and TXT files
    Updates existing JSON structure with new content while preserving metadata
    """
    try:
        data = await request.json()
        
        # 🔍 DEBUG: Log the incoming request data
        logger.info(f"🔍 [SAVE_EDITED] Received request data keys: {list(data.keys())}")
        logger.info(f"🔍 [SAVE_EDITED] Request data: {json.dumps(data, indent=2)[:500]}...")
        
        company = data.get('company')
        content = data.get('content')
        
        # 🔍 DEBUG: Log extracted parameters
        logger.info(f"🔍 [SAVE_EDITED] Extracted - Company: {company}")
        logger.info(f"🔍 [SAVE_EDITED] Extracted - Content type: {type(content)}")
        logger.info(f"🔍 [SAVE_EDITED] Extracted - Content length: {len(str(content)) if content else 0}")
        
        if not company or not content:
            raise HTTPException(status_code=400, detail="Company and content are required")
        
        # 🔍 DEBUG: Log the save process
        logger.info(f"🔍 [SAVE_EDITED] Starting save process for {company}")
        
        # Save to global tailored folder under the authenticated user's base path
        from app.utils.user_path_utils import get_user_base_path
        user_base = get_user_base_path(current_user.email)
        tailored_path = user_base / "cvs" / "tailored"
        
        logger.info(f"🔍 [SAVE_EDITED] Tailored path: {tailored_path}")
        
        # Find existing TXT files ONLY in tailored folder (company-scoped)
        existing_txt_files = []
        if tailored_path.exists():
            existing_txt_files = list(tailored_path.glob(f"{company}_tailored_cv_*.txt"))
        
        logger.info(f"🔍 [SAVE_EDITED] Found {len(existing_txt_files)} existing TXT files in tailored folder")
        for file in existing_txt_files:
            logger.info(f"🔍 [SAVE_EDITED] - {file}")
        
        files_updated = []
        
        # Create tailored directory if it doesn't exist
        tailored_path.mkdir(parents=True, exist_ok=True)
        
        # Update existing files (all matches) instead of only the latest
        if existing_txt_files:
            for txt_file in existing_txt_files:
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_updated.append(str(txt_file))
                logger.info(f"✅ [SAVE_EDITED] Updated TXT: {txt_file}")

                # Update paired JSON synchronously using local parser (no AI)
                json_file = txt_file.with_suffix('.json')
                if json_file.exists():
                    try:
                        with open(json_file, 'r', encoding='utf-8') as jf:
                            existing_json = json.load(jf)
                        # Deterministic header sync is handled inside parser if needed
                        updated_json = _parse_cv_content_to_json(content, existing_json)
                        updated_json['last_edited'] = datetime.now().isoformat()
                        updated_json['manually_edited'] = True
                        with open(json_file, 'w', encoding='utf-8') as jf:
                            json.dump(updated_json, jf, indent=2, ensure_ascii=False)
                        files_updated.append(str(json_file))
                        logger.info(f"✅ [SAVE_EDITED] Updated JSON: {json_file}")
                    except Exception as je:
                        logger.warning(f"⚠️ [SAVE_EDITED] Failed to update JSON {json_file}: {je}")
        else:
            # Create new file if no existing files found
            logger.info(f"🔍 [SAVE_EDITED] No existing files found, creating new file")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            tailored_txt_file = tailored_path / f"{company}_tailored_cv_{timestamp}.txt"
            with open(tailored_txt_file, 'w', encoding='utf-8') as f:
                f.write(content)
            files_updated.append(str(tailored_txt_file))
            logger.info(f"✅ [SAVE_EDITED] Created new file: {tailored_txt_file}")
        
            # Create new JSON file with same timestamp when creating new TXT
            if not existing_txt_files:
                try:
                    seed_json = {
                        'contact': {},
                        'education': [],
                        'experience': [],
                        'projects': [],
                        'skills': []
                    }
                    updated_json = _parse_cv_content_to_json(content, seed_json)
                    updated_json['last_edited'] = datetime.now().isoformat()
                    updated_json['manually_edited'] = True
                    tailored_json_file = tailored_path / f"{company}_tailored_cv_{timestamp}.json"
                    with open(tailored_json_file, 'w', encoding='utf-8') as jf:
                        json.dump(updated_json, jf, indent=2, ensure_ascii=False)
                    files_updated.append(str(tailored_json_file))
                    logger.info(f"✅ [SAVE_EDITED] Created new JSON: {tailored_json_file}")
                except Exception as json_error:
                    logger.warning(f"⚠️ [SAVE_EDITED] Failed to create JSON file: {json_error}")

        logger.info(f"✅ [SAVE_EDITED] Completed saving for {company}")
        
        return {
            "success": True,
            "message": f"CV saved successfully - updated {len(files_updated)} files",
            "files_updated": files_updated
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to save edited CV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save CV: {str(e)}")


async def _update_json_with_edited_content(existing_json: dict, edited_content: str, company: str) -> dict:
    """
    Update existing JSON structure with edited content using AI parsing
    Preserves metadata and structure while updating the content
    """
    try:
        from app.ai.ai_service import ai_service
        
        # 0) Heuristic fast-path: parse common contact line formats like
        #    "Name | PHONE | EMAIL | LOCATION" and update contact fields deterministically
        try:
            lines = [l.strip() for l in edited_content.splitlines() if l.strip()]
            if lines:
                first = lines[0]
                parts = [p.strip() for p in first.split('|')]
                if len(parts) >= 3:
                    contact = existing_json.get('contact', {}) or {}
                    # Name (part 0)
                    if parts[0] and (not contact.get('name') or parts[0] != contact.get('name')):
                        contact['name'] = parts[0]
                    # Phone (part 1)
                    if len(parts) > 1 and parts[1]:
                        contact['phone'] = parts[1]
                    # Email (part 2)
                    if len(parts) > 2 and parts[2]:
                        contact['email'] = parts[2]
                    # Location (part 3)
                    if len(parts) > 3 and parts[3]:
                        contact['location'] = parts[3]
                    existing_json['contact'] = contact
        except Exception:
            # Heuristic is best-effort; ignore failures
            pass
        
        # Create a prompt to parse the edited content back into JSON structure
        parsing_prompt = f"""
You are a CV parser. I need you to update an existing CV JSON structure with new edited content.

EXISTING JSON STRUCTURE (preserve this format exactly):
{json.dumps(existing_json, indent=2)}

EDITED CONTENT TO PARSE:
{edited_content}

INSTRUCTIONS:
1. Parse the edited content and map it back to the existing JSON structure
2. PRESERVE ALL METADATA: created_at, framework_version, estimated_ats_score, etc.
3. UPDATE ONLY THE CONTENT FIELDS: contact, education, experience, skills, projects, etc.
4. Maintain the exact same JSON structure and field names
5. If edited content is missing some sections, keep the original values
6. Return ONLY the updated JSON, no explanations

Updated JSON:"""

        # 1) Generate response using AI to fully map free text back to structure
        response = await ai_service.generate_response(
            prompt=parsing_prompt,
            user=current_user,
            temperature=0.0,  # Zero temperature for maximum consistency
            max_tokens=4000
        )
        
        # Parse the AI response
        try:
            updated_json = json.loads(response.content.strip())
            
            # Ensure metadata is preserved
            metadata_fields = ['created_at', 'framework_version', 'estimated_ats_score', 'keyword_density', 
                             'impact_statement_compliance', 'quantifications_added']
            
            for field in metadata_fields:
                if field in existing_json and field not in updated_json:
                    updated_json[field] = existing_json[field]
            
            # Update the created_at to show when it was last edited
            updated_json['last_edited'] = datetime.now().isoformat()
            
            return updated_json
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response as JSON: {e}")
            # Return original with updated timestamp
            existing_json['last_edited'] = datetime.now().isoformat()
            existing_json['edit_note'] = "Content was edited but could not be parsed back to JSON structure"
            return existing_json
            
    except Exception as e:
        logger.error(f"❌ Failed to update JSON with AI: {e}")
        # Return original with updated timestamp
        existing_json['last_edited'] = datetime.now().isoformat()
        existing_json['edit_note'] = f"Content was edited but update failed: {str(e)}"
        return existing_json


@router.post("/save-additional-prompt")
async def save_additional_prompt(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Save additional prompt instructions for CV improvement
    """
    try:
        data = await request.json()
        company = data.get('company')
        prompt = data.get('prompt')
        
        if not company or not prompt:
            raise HTTPException(status_code=400, detail="Company and prompt are required")
        
        # Save to analysis folder
        analysis_path = get_user_base_path(current_user.email) / "applied_companies" / company
        analysis_path.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save prompt file
        prompt_file = analysis_path / f"{company}_additional_prompt_{timestamp}.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(f"Additional Prompt for {company}\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            f.write(prompt)
        
        logger.info(f"✅ Saved additional prompt for {company}")
        
        return {
            "success": True,
            "message": "Additional prompt saved successfully",
            "file_saved": str(prompt_file)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to save additional prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {str(e)}")


@router.get("/available-companies-real")
async def get_available_companies_real(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of companies that have tailored CVs available in the global tailored folder
    """
    try:
        # Use user-specific path
        from app.utils.user_path_utils import get_user_base_path
        cv_analysis_path = get_user_base_path(current_user.email).resolve()
        
        companies = []
        if cv_analysis_path.exists():
            # Look in global tailored CV folder
            tailored_cv_dir = cv_analysis_path / "cvs" / "tailored"
            if tailored_cv_dir.exists():
                # Find all tailored CV files
                tailored_cv_files = list(tailored_cv_dir.glob("*_tailored_cv_*.txt"))
                
                for cv_file in tailored_cv_files:
                    # Extract company name from filename (e.g., "Company_tailored_cv_timestamp.txt")
                    filename = cv_file.stem  # Remove .txt extension
                    parts = filename.split('_tailored_cv_')
                    if len(parts) >= 2:
                        company_name = parts[0]
                        
                        # Get the corresponding JSON file for metadata
                        json_file = cv_file.with_suffix('.json')
                        
                        companies.append({
                            "company": company_name,
                            "display_name": company_name.replace('_', ' '),
                            "tailored_cv_file": str(cv_file),
                            "last_updated": datetime.fromtimestamp(cv_file.stat().st_mtime).isoformat()
                        })
                
                # Sort by last_updated (most recent first)
                companies.sort(key=lambda x: x['last_updated'], reverse=True)
        
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
    Get tailored CV content for frontend preview - STRICT MODE
    
    This endpoint serves the most recent tailored CV text content for a company.
    It ONLY looks in the tailored folder and raises an error if no tailored CV is found.
    NO FALLBACK to original CV.
    """
    try:
        logger.info(f"📄 Tailored CV content request for {company_name} from user {current_user.id}")
        
        # Use user-specific unified selector to get the latest TAILORED CV ONLY
        from app.unified_latest_file_selector import get_selector_for_user
        
        user_selector = get_selector_for_user(current_user.email)
        
        # Use the strict method that only looks in tailored folder
        cv_context = user_selector.get_latest_tailored_cv_only(company_name)
        
        if not cv_context.exists or not cv_context.txt_path:
            raise HTTPException(
                status_code=404,
                detail=f"No tailored CV found for company: {company_name}. Please generate a tailored CV first."
            )
        
        latest_json_file = cv_context.json_path
        
        # Check if JSON file exists
        if not latest_json_file or not latest_json_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Tailored CV JSON file not found: {latest_json_file}"
            )
        
        # Read the JSON content and convert to text format
        with open(latest_json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convert JSON to text format using the service
        from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
        service = CVTailoringService(user_email=current_user.email)
        
        # Create a minimal TailoredCV object for text conversion
        from app.tailored_cv.models.cv_models import TailoredCV, ContactInfo, ExperienceEntry, SkillCategory, OptimizationStrategy
        
        # Create minimal required fields
        optimization_strategy = OptimizationStrategy(
            section_order={},
            education_strategy={},
            keyword_placement={},
            quantification_targets={},
            enhancements={},
            impact_enhancements={}
        )
        
        tailored_cv = TailoredCV(
            contact=ContactInfo(**json_data['contact']),
            education=json_data.get('education', []),
            experience=[ExperienceEntry(**exp) for exp in json_data.get('experience', [])],
            skills=[SkillCategory(**skill) for skill in json_data.get('skills', [])],
            target_company=company_name,
            target_role='Data Analyst',
            optimization_strategy=optimization_strategy,
            enhancements_applied={},
            keywords_integrated=[],
            quantifications_added=[]
        )
        
        # Convert to text with current format
        content = service._convert_tailored_cv_to_text(tailored_cv)
        
        logger.info(f"✅ Served TAILORED CV content: {latest_json_file.name} from {cv_context.file_type} folder ({len(content)} characters)")
        
        return JSONResponse(content={
            "success": True,
            "content": content,
            "filename": latest_json_file.name,
            "company": company_name,
            "source_folder": cv_context.file_type,
            "metadata": {
                "file_size": len(content),
                "last_modified": latest_json_file.stat().st_mtime,
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


@router.get("/export-pdf/{company}")
async def export_pdf(
    company: str,
    current_user: User = Depends(get_current_user)
):
    """Generate and return a PDF for the latest tailored CV for the given company."""
    try:
        from app.tailored_cv.services.pdf_export_service import export_tailored_cv_pdf
        from app.utils.user_path_utils import get_user_base_path

        user_base = get_user_base_path(current_user.email)
        export_dir = user_base / "cvs" / "pdf_cvs"

        pdf_path = export_tailored_cv_pdf(current_user.email, company, export_dir)

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_path.name,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ PDF export failed for {company}: {e}")
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")


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


def _parse_cv_content_to_json(content: str, existing_json: dict) -> dict:
    """
    Parse edited CV content back into structured JSON format while preserving minimal metadata.
    
    This function maintains the JSON structure and handles:
    - Adding new content to existing sections
    - Modifying existing content
    - Deleting sections (keeps structure but empties content)
    - Preserving only essential metadata (no optimization data)
    """
    try:
        logger.info(f"🔍 [CV_PARSER] Starting CV content parsing")
        logger.info(f"🔍 [CV_PARSER] Content length: {len(content)}")
        logger.info(f"🔍 [CV_PARSER] Existing JSON keys: {list(existing_json.keys())}")
        
        # Create clean structure with only CV content and minimal metadata
        updated_json = {
            'contact': existing_json.get('contact', {}),
            'education': [],
            'experience': [],
            'projects': [],
            'skills': [],
            'created_at': existing_json.get('created_at'),
            'last_edited': None,  # Will be set later
            'manually_edited': False  # Will be set later
        }
        
        # Parse the content line by line
        lines = content.strip().split('\n')
        logger.info(f"🔍 [CV_PARSER] Processing {len(lines)} lines")
        
        # Track current section and content
        current_section = None
        current_company = None
        current_bullets = []
        section_content = {}
        
        # Extract contact info from first line if present
        if lines and ('|' in lines[0] or '@' in lines[0]):
            contact_line = lines[0]
            logger.info(f"🔍 [CV_PARSER] Parsing contact line: {contact_line}")
            
            # Parse contact information
            contact_parts = [part.strip() for part in contact_line.split('|')]
            if len(contact_parts) >= 3:
                updated_json['contact'] = {
                    "name": contact_parts[0].strip(),
                    "phone": contact_parts[1].strip() if len(contact_parts) > 1 else updated_json.get('contact', {}).get('phone'),
                    "email": contact_parts[2].strip() if len(contact_parts) > 2 else updated_json.get('contact', {}).get('email'),
                    "linkedin": updated_json.get('contact', {}).get('linkedin'),
                    "location": contact_parts[3].strip() if len(contact_parts) > 3 else updated_json.get('contact', {}).get('location'),
                    "website": updated_json.get('contact', {}).get('website')
                }
            lines = lines[1:]  # Remove processed contact line
        
        # Process remaining lines
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Detect section headers (ALL CAPS or specific patterns)
            if line.isupper() or line in ['TECHNICAL SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS', 'SKILLS']:
                current_section = line.lower().replace(' ', '_')
                logger.info(f"🔍 [CV_PARSER] Found section: {current_section}")
                section_content[current_section] = []
                i += 1
                continue
            
            # Process content based on current section
            if current_section == 'technical_skills' or current_section == 'skills':
                if line.startswith('•') or line.startswith('-'):
                    skills_text = line.replace('•', '').replace('-', '').strip()
                    # Split skills by comma and clean them
                    skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                    updated_json['skills'] = skills_list
                    logger.info(f"🔍 [CV_PARSER] Parsed {len(skills_list)} skills")
            
            elif current_section == 'experience':
                # Look for job title with date pattern (e.g., "Data Analyst         Jul 2024 – Present")
                if ('20' in line or 'Present' in line) and ('–' in line or '-' in line):
                    # This line contains job title and dates
                    parts = line.split()
                    
                    # Find the date part (contains numbers or "Present")
                    date_start_idx = -1
                    for idx, part in enumerate(parts):
                        if '20' in part or 'Present' in part or part in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                            date_start_idx = idx
                            break
                    
                    if date_start_idx > 0:
                        job_title = ' '.join(parts[:date_start_idx]).strip()
                        date_range = ' '.join(parts[date_start_idx:]).strip()
                        
                        # Get company from next line
                        i += 1
                        company_location = ""
                        if i < len(lines):
                            company_location = lines[i].strip()
                        
                        # Skip empty line if present
                        if i + 1 < len(lines) and not lines[i+1].strip():
                            i += 1
                        
                        # Collect bullets for this job
                        job_bullets = []
                        i += 1
                        while i < len(lines) and (lines[i].strip().startswith('•') or lines[i].strip().startswith('-')):
                            bullet = lines[i].strip().replace('•', '').replace('-', '').strip()
                            if bullet:
                                job_bullets.append(bullet)
                            i += 1
                        i -= 1  # Back up one since we'll increment at the end of the loop
                        
                        # Parse dates
                        start_date = "Unknown"
                        end_date = "Unknown"
                        if '–' in date_range or '-' in date_range:
                            date_parts = date_range.replace('–', '-').split('-')
                            if len(date_parts) >= 2:
                                start_date = date_parts[0].strip()
                                end_date = date_parts[1].strip()
                        
                        # Create experience entry
                        exp_entry = {
                            "company": company_location.split(',')[0].strip(),
                            "title": job_title,
                            "location": company_location,
                            "start_date": start_date,
                            "end_date": end_date,
                            "duration": None,
                            "bullets": job_bullets
                        }
                        
                        if 'experience' not in updated_json:
                            updated_json['experience'] = []
                        
                        updated_json['experience'].append(exp_entry)
                        logger.info(f"🔍 [CV_PARSER] Added experience: {job_title} at {company_location.split(',')[0]} ({len(job_bullets)} bullets)")
            
            elif current_section == 'education':
                # Similar logic for education - simplified for now
                if not line.startswith('•') and not line.startswith('-'):
                    # This might be an education entry
                    education_info = line
                    logger.info(f"🔍 [CV_PARSER] Found education: {education_info}")
            
            elif current_section == 'projects':
                # Handle projects section
                if not line.startswith('•') and not line.startswith('-'):
                    project_name = line
                    logger.info(f"🔍 [CV_PARSER] Found project: {project_name}")
            
            i += 1
        
        # Sections are already cleared at the beginning, so if they weren't populated during parsing,
        # they remain empty (which is what we want for deleted sections)
        
        # Note: parsed_text is not saved to keep the output clean
        # The original content is processed but not stored in the final JSON
        
        logger.info(f"🔍 [CV_PARSER] Parsing completed successfully")
        logger.info(f"🔍 [CV_PARSER] Updated JSON keys: {list(updated_json.keys())}")
        
        return updated_json
        
    except Exception as e:
        logger.error(f"❌ [CV_PARSER] Error parsing CV content: {e}")
        # Fallback: preserve structure but update text field
        fallback_json = existing_json.copy()
        fallback_json['text'] = content
        fallback_json['parsing_error'] = str(e)
        return fallback_json


# Export router
__all__ = ["router"]