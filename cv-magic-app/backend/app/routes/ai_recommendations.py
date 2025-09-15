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
        ai_recommendations_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        
        if not ai_recommendations_dir.exists():
            return JSONResponse(
                status_code=404,
                content={"error": "No AI recommendations directory found"}
            )
        
        # Find all AI recommendation files
        recommendation_files = []
        for company_dir in ai_recommendations_dir.iterdir():
            if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                ai_file = company_dir / f"{company_dir.name}_ai_recommendation.json"
                if ai_file.exists():
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
        ai_file_path = Path(f"/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/{company}/{company}_ai_recommendation.json")
        
        if not ai_file_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": f"No AI recommendations found for company: {company}"}
            )
        
        # Read the AI recommendation file
        with open(ai_file_path, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)
        
        return JSONResponse(content={
            "success": True,
            "company": ai_data.get("company"),
            "generated_at": ai_data.get("generated_at"),
            "recommendation_content": ai_data.get("recommendation_content"),
            "ai_model_info": ai_data.get("ai_model_info"),
            "file_path": str(ai_file_path)
        })
        
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
        ai_recommendations_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        
        if not ai_recommendations_dir.exists():
            return JSONResponse(content={
                "success": True,
                "companies": [],
                "total": 0
            })
        
        companies_with_recommendations = []
        
        for company_dir in ai_recommendations_dir.iterdir():
            if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                ai_file = company_dir / f"{company_dir.name}_ai_recommendation.json"
                if ai_file.exists():
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