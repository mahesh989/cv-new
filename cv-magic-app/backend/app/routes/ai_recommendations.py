"""
AI Recommendations API Routes

This module provides endpoints for retrieving AI recommendations
that have been generated and saved as JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.services.ai_recommendation_generator import ai_recommendation_generator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="", tags=["ai-recommendations"])

@router.get("/ai-recommendations/latest")
async def get_latest_ai_recommendations():
    """
    Get the latest AI recommendations from the most recently generated file
    
    Returns:
        JSON response with recommendation content
    """
    try:
        ai_recommendations_dir = Path("cv-analysis")
        
        if not ai_recommendations_dir.exists():
            return JSONResponse(
                status_code=404,
                content={"error": "No AI recommendations directory found"}
            )
        
        # Find all latest timestamped AI recommendation files per company
        recommendation_files = []
        from app.utils.timestamp_utils import TimestampUtils
        for company_dir in ai_recommendations_dir.iterdir():
            if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                ai_file = TimestampUtils.find_latest_timestamped_file(
                    company_dir, f"{company_dir.name}_ai_recommendation", "json"
                )
                if ai_file and ai_file.exists():
                    recommendation_files.append(ai_file)
        
        if not recommendation_files:
            return JSONResponse(
                status_code=404,
                content={"error": "No AI recommendation files found"}
            )
        
        # Sort by modification time (most recent first)
        recommendation_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_file = recommendation_files[0]
        
        # Read the latest AI recommendation file
        with open(latest_file, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)
        
        return JSONResponse(content={
            "success": True,
            "company": ai_data.get("company"),
            "generated_at": ai_data.get("generated_at"),
            "recommendation_content": ai_data.get("recommendation_content"),
            "ai_model_info": ai_data.get("ai_model_info"),
            "file_path": str(latest_file)
        })
        
    except Exception as e:
        logger.error(f"❌ [AI_RECOMMENDATIONS] Error fetching latest recommendations: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch AI recommendations: {str(e)}"}
        )


@router.get("/ai-recommendations/company/{company}")
async def get_company_ai_recommendations(company: str):
    """
    Get AI recommendations for a specific company
    
    Args:
        company: Company name
        
    Returns:
        JSON response with recommendation content
    """
    try:
        from app.utils.timestamp_utils import TimestampUtils
        # Try multiple naming patterns for AI recommendations
        ai_file_path = TimestampUtils.find_latest_timestamped_file(
            Path(f"cv-analysis/applied_companies/{company}"),
            f"{company}_ai_recommendation",
            "json",
        )
        if not ai_file_path:
            # Try input_recommendation pattern
            ai_file_path = TimestampUtils.find_latest_timestamped_file(
                Path(f"cv-analysis/applied_companies/{company}"),
                f"{company}_input_recommendation",
                "json",
            )
        if not ai_file_path:
            # Try non-timestamped files
            ai_file_path = Path(f"cv-analysis/applied_companies/{company}/{company}_ai_recommendation.json")
        if not ai_file_path.exists():
            ai_file_path = Path(f"cv-analysis/applied_companies/{company}/{company}_input_recommendation.json")
        
        if not ai_file_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": f"No AI recommendations found for company: {company}"}
            )
        
        # Read the AI recommendation file
        with open(ai_file_path, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)
        
        # Handle different file formats
        if "recommendation_content" in ai_data:
            # Standard AI recommendation format
            content = {
                "success": True,
                "company": ai_data.get("company"),
                "generated_at": ai_data.get("generated_at"),
                "recommendation_content": ai_data.get("recommendation_content"),
                "ai_model_info": ai_data.get("ai_model_info"),
                "file_path": str(ai_file_path)
            }
        else:
            # Input recommendation format - extract recommendations from analyze_match_entries
            recommendations = []
            
            # Extract from analyze_match_entries if available
            if "analyze_match_entries" in ai_data and ai_data["analyze_match_entries"]:
                for entry in ai_data["analyze_match_entries"]:
                    if "content" in entry:
                        recommendations.append(entry["content"])
            
            # Extract component analysis strategic priorities
            if "component_analysis_entries" in ai_data and ai_data["component_analysis_entries"]:
                for entry in ai_data["component_analysis_entries"]:
                    if "component_analyses" in entry and "skills" in entry["component_analyses"]:
                        skills_data = entry["component_analyses"]["skills"]
                        if "skills_analysis" in skills_data:
                            for skill in skills_data["skills_analysis"]:
                                if "jd_application" in skill:
                                    recommendations.append(f"💡 {skill['skill']}: {skill['jd_application']}")
            
            content = {
                "success": True,
                "company": ai_data.get("company", "Australia_for_UNHCR"),
                "generated_at": ai_data.get("timestamp") or (ai_data.get("analyze_match_entries", [{}])[0].get("timestamp") if ai_data.get("analyze_match_entries") else None),
                "recommendation_content": "\n\n".join(recommendations) if recommendations else "Comprehensive analysis available",
                "ai_model_info": {"model": "comprehensive_analysis", "source": "input_recommendation"},
                "file_path": str(ai_file_path)
            }
        
        return JSONResponse(content=content)
        
    except Exception as e:
        logger.error(f"❌ [AI_RECOMMENDATIONS] Error fetching recommendations for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch AI recommendations for {company}: {str(e)}"}
        )


@router.get("/ai-recommendations/list")
async def list_available_ai_recommendations():
    """
    List all companies that have AI recommendations available
    
    Returns:
        JSON response with list of companies and their recommendation info
    """
    try:
        ai_recommendations_dir = Path("cv-analysis")
        
        if not ai_recommendations_dir.exists():
            return JSONResponse(content={
                "success": True,
                "companies": [],
                "total": 0
            })
        
        companies_with_recommendations = []
        
        for company_dir in ai_recommendations_dir.iterdir():
            if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                from app.utils.timestamp_utils import TimestampUtils
                ai_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_ai_recommendation", "json")
                if ai_file and ai_file.exists():
                    try:
                        # Get file stats
                        stat_info = ai_file.stat()
                        
                        # Read basic info from file
                        with open(ai_file, 'r', encoding='utf-8') as f:
                            ai_data = json.load(f)
                        
                        companies_with_recommendations.append({
                            "company": company_dir.name,
                            "generated_at": ai_data.get("generated_at"),
                            "ai_model": ai_data.get("ai_model_info", {}).get("model"),
                            "file_size": stat_info.st_size,
                            "last_modified": stat_info.st_mtime,
                            "has_content": bool(ai_data.get("recommendation_content"))
                        })
                        
                    except Exception as e:
                        logger.warning(f"Could not read AI recommendation file for {company_dir.name}: {e}")
                        companies_with_recommendations.append({
                            "company": company_dir.name,
                            "error": "Could not read file contents"
                        })
        
        # Sort by last modified time (most recent first)
        companies_with_recommendations.sort(key=lambda x: x.get("last_modified", 0), reverse=True)
        
        return JSONResponse(content={
            "success": True,
            "companies": companies_with_recommendations,
            "total": len(companies_with_recommendations)
        })
        
    except Exception as e:
        logger.error(f"❌ [AI_RECOMMENDATIONS] Error listing AI recommendations: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list AI recommendations: {str(e)}"}
        )


@router.post("/ai-recommendations/convert-txt-to-json")
async def convert_txt_to_json():
    """
    Convert all existing TXT recommendation files to JSON format
    
    Returns:
        JSON response with conversion results
    """
    try:
        logger.info("🔄 [AI_RECOMMENDATIONS] Starting TXT to JSON conversion")
        
        # Convert all TXT files to JSON
        conversion_results = ai_recommendation_generator.batch_convert_txt_to_json()
        
        successful_count = sum(1 for success in conversion_results.values() if success)
        total_count = len(conversion_results)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Conversion completed: {successful_count}/{total_count} files converted",
            "conversion_results": conversion_results,
            "successful_count": successful_count,
            "total_count": total_count
        })
        
    except Exception as e:
        logger.error(f"❌ [AI_RECOMMENDATIONS] Error converting TXT to JSON: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to convert TXT to JSON: {str(e)}"}
        )


@router.post("/ai-recommendations/convert-txt-to-json/{company}")
async def convert_company_txt_to_json(company: str):
    """
    Convert TXT recommendation file to JSON format for a specific company
    
    Args:
        company: Company name
        
    Returns:
        JSON response with conversion result
    """
    try:
        logger.info(f"🔄 [AI_RECOMMENDATIONS] Converting TXT to JSON for: {company}")
        
        # Convert TXT file to JSON for the specific company
        success = ai_recommendation_generator.convert_txt_to_json(company)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"Successfully converted TXT to JSON for {company}",
                "company": company
            })
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Failed to convert TXT to JSON for {company}. TXT file may not exist.",
                    "company": company
                }
            )
        
    except Exception as e:
        logger.error(f"❌ [AI_RECOMMENDATIONS] Error converting TXT to JSON for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to convert TXT to JSON for {company}: {str(e)}"}
        )


@router.post("/ai-recommendations/generate-and-tailor/{company}")
async def generate_ai_recommendation_and_tailor_cv(company: str):
    """
    Generate AI recommendation for a company and automatically trigger CV tailoring
    
    This endpoint generates AI recommendations and then immediately triggers
    CV tailoring using the generated recommendations.
    
    Args:
        company: Company name
        
    Returns:
        JSON response with both AI recommendation and CV tailoring results
    """
    try:
        logger.info(f"🚀 [AI_RECOMMENDATIONS] Starting AI generation and CV tailoring for: {company}")
        
        # Step 1: Generate AI recommendation
        ai_success = await ai_recommendation_generator.generate_ai_recommendation(company, force_regenerate=True)
        
        if not ai_success:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Failed to generate AI recommendations for {company}",
                    "ai_recommendation_success": False,
                    "cv_tailoring_success": False
                }
            )
        
        logger.info(f"✅ [AI_RECOMMENDATIONS] AI recommendation generated for {company}")
        
        # Note: CV tailoring should be automatically triggered by the AI generator
        # Let's give it a moment and then check for the tailored CV file
        import asyncio
        await asyncio.sleep(2)  # Give time for CV tailoring to complete
        
        # Check if tailored CV was created
        cv_analysis_path = Path("cv-analysis")
        tailored_cv_file = cv_analysis_path / "tailored_cv.json"
        company_tailored_files = list((cv_analysis_path / company).glob("tailored_cv_*.json"))
        
        cv_tailoring_success = tailored_cv_file.exists() or len(company_tailored_files) > 0
        
        # Get the latest AI recommendation
        ai_file_path = cv_analysis_path / company / f"{company}_ai_recommendation.json"
        ai_recommendation_data = None
        if ai_file_path.exists():
            with open(ai_file_path, 'r', encoding='utf-8') as f:
                ai_recommendation_data = json.load(f)
        
        # Get tailored CV info
        tailored_cv_info = None
        if tailored_cv_file.exists():
            tailored_cv_info = {
                "file_path": str(tailored_cv_file),
                "created_at": tailored_cv_file.stat().st_mtime,
                "file_size": tailored_cv_file.stat().st_size
            }
        elif company_tailored_files:
            latest_company_file = max(company_tailored_files, key=lambda p: p.stat().st_mtime)
            tailored_cv_info = {
                "file_path": str(latest_company_file),
                "created_at": latest_company_file.stat().st_mtime,
                "file_size": latest_company_file.stat().st_size
            }
        
        return JSONResponse(content={
            "success": True,
            "message": f"AI recommendation and CV tailoring completed for {company}",
            "company": company,
            "ai_recommendation_success": ai_success,
            "cv_tailoring_success": cv_tailoring_success,
            "ai_recommendation_file": str(ai_file_path) if ai_file_path.exists() else None,
            "ai_recommendation_data": ai_recommendation_data,
            "tailored_cv_info": tailored_cv_info,
            "workflow_status": "complete" if ai_success and cv_tailoring_success else "partial"
        })
        
    except Exception as e:
        logger.error(f"❌ [AI_RECOMMENDATIONS] Error in generate and tailor workflow for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to complete AI recommendation and CV tailoring workflow: {str(e)}",
                "company": company
            }
        )
