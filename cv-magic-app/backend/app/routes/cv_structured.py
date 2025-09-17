"""
Structured CV processing routes

These routes integrate the structured CV parser into the upload/processing flow,
ensuring all CVs are saved in the structured format going forward.
"""

import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse

from ..services.enhanced_cv_upload_service import enhanced_cv_upload_service
from ..services.structured_cv_parser import enhanced_cv_parser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv-structured", tags=["Structured CV Processing"])


@router.post("/upload")
async def upload_cv_structured(
    cv_file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    save_as_original: bool = Form(True)
):
    """
    Upload CV and process into structured format
    
    This endpoint:
    1. Validates the uploaded file
    2. Extracts text content 
    3. Parses into structured JSON format
    4. Saves in the new structured format
    5. Handles unknown sections gracefully
    """
    try:
        result = await enhanced_cv_upload_service.upload_and_process_cv(
            cv_file=cv_file,
            user_id=user_id,
            title=title,
            description=description,
            save_as_original=save_as_original
        )
        
        logger.info(f"CV uploaded and structured successfully: {result['filename']}")
        
        return JSONResponse(content={
            "status": "success",
            "message": "CV uploaded and processed successfully",
            "data": result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in structured CV upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/process-existing/{filename}")
async def process_existing_cv(
    filename: str,
    save_as_original: bool = Query(False)
):
    """
    Process an existing uploaded CV into structured format
    
    Useful for converting existing CVs to the new structured format
    """
    try:
        result = await enhanced_cv_upload_service.process_existing_cv(
            filename=filename,
            save_as_original=save_as_original
        )
        
        logger.info(f"Existing CV processed successfully: {filename}")
        
        return JSONResponse(content={
            "status": "success", 
            "message": "CV processed successfully",
            "data": result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing existing CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/load")
async def load_structured_cv(
    use_original: bool = Query(True, description="Load from original_cv.json"),
    filename: Optional[str] = Query(None, description="Specific filename to load")
):
    """
    Load structured CV data
    
    Returns the structured CV in the new format with all sections properly organized
    """
    try:
        cv_data = enhanced_cv_upload_service.load_structured_cv(
            use_original=use_original,
            filename=filename
        )
        
        if not cv_data:
            raise HTTPException(status_code=404, detail="Structured CV not found")
        
        # Get summary information
        summary = {
            "sections_count": len([k for k in cv_data.keys() if k not in ["saved_at", "unknown_sections", "metadata"] and cv_data[k]]),
            "has_personal_info": bool(cv_data.get("personal_information", {}).get("name")),
            "has_technical_skills": bool(cv_data.get("technical_skills", [])),
            "has_experience": bool(cv_data.get("experience", [])),
            "has_education": bool(cv_data.get("education", [])),
            "has_projects": bool(cv_data.get("projects", [])),
            "unknown_sections": list(cv_data.get("unknown_sections", {}).keys()),
            "last_updated": cv_data.get("saved_at"),
            "source_file": cv_data.get("metadata", {}).get("source_filename")
        }
        
        return JSONResponse(content={
            "status": "success",
            "summary": summary,
            "cv_data": cv_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading structured CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Loading failed: {str(e)}")


@router.get("/status/{filename}")
async def get_processing_status(filename: str):
    """
    Get processing status for a specific CV file
    
    Shows whether the CV has been processed into structured format
    """
    try:
        status = enhanced_cv_upload_service.get_cv_processing_status(filename)
        
        return JSONResponse(content={
            "status": "success",
            "data": status
        })
        
    except Exception as e:
        logger.error(f"Error getting processing status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/validate")
async def validate_structured_cv(
    use_original: bool = Query(True, description="Validate original_cv.json"),
    filename: Optional[str] = Query(None, description="Specific filename to validate")
):
    """
    Validate structured CV format and report any issues
    
    Returns detailed validation report including missing sections, errors, and warnings
    """
    try:
        cv_data = enhanced_cv_upload_service.load_structured_cv(
            use_original=use_original,
            filename=filename
        )
        
        if not cv_data:
            raise HTTPException(status_code=404, detail="Structured CV not found for validation")
        
        validation_report = enhanced_cv_parser.validate_cv_structure(cv_data)
        
        return JSONResponse(content={
            "status": "success",
            "validation_report": validation_report,
            "recommendations": _get_validation_recommendations(validation_report)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating structured CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/migrate")
async def migrate_existing_cv(
    source_path: str = Form(..., description="Path to existing CV file"),
    create_backup: bool = Form(True, description="Create backup of original")
):
    """
    Migrate an existing CV from old format to structured format
    
    Useful for converting existing original_cv.json to the new structured format
    """
    try:
        result = enhanced_cv_upload_service.migrate_existing_cv(
            source_path=source_path,
            backup=create_backup
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Migration failed"))
        
        logger.info(f"CV migrated successfully: {source_path}")
        
        return JSONResponse(content={
            "status": "success",
            "message": "CV migrated successfully",
            "data": result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error migrating CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.get("/sections")
async def get_cv_sections(
    use_original: bool = Query(True, description="Use original_cv.json"),
    filename: Optional[str] = Query(None, description="Specific filename"),
    section: Optional[str] = Query(None, description="Specific section to retrieve")
):
    """
    Get specific sections from structured CV
    
    Useful for retrieving only specific parts of the CV (e.g., just technical_skills)
    """
    try:
        cv_data = enhanced_cv_upload_service.load_structured_cv(
            use_original=use_original,
            filename=filename
        )
        
        if not cv_data:
            raise HTTPException(status_code=404, detail="Structured CV not found")
        
        if section:
            if section not in cv_data:
                raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
            
            return JSONResponse(content={
                "status": "success",
                "section": section,
                "data": cv_data[section]
            })
        
        # Return all available sections
        sections = {}
        for key, value in cv_data.items():
            if key not in ["saved_at", "metadata"] and value:
                sections[key] = {
                    "type": type(value).__name__,
                    "has_data": bool(value),
                    "count": len(value) if isinstance(value, (list, dict)) else None
                }
        
        return JSONResponse(content={
            "status": "success",
            "available_sections": sections,
            "total_sections": len(sections)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV sections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Section retrieval failed: {str(e)}")


@router.put("/sections/{section_name}")
async def update_cv_section(
    section_name: str,
    section_data: dict,
    use_original: bool = Query(True, description="Update original_cv.json"),
    filename: Optional[str] = Query(None, description="Specific filename to update")
):
    """
    Update a specific section in the structured CV
    
    Allows targeted updates to specific sections without affecting the rest
    """
    try:
        # Load existing CV
        cv_data = enhanced_cv_upload_service.load_structured_cv(
            use_original=use_original,
            filename=filename
        )
        
        if not cv_data:
            raise HTTPException(status_code=404, detail="Structured CV not found")
        
        # Update the specific section
        cv_data[section_name] = section_data
        cv_data["saved_at"] = datetime.now().isoformat()
        
        # Validate the updated CV
        validation_report = structured_cv_parser.validate_cv_structure(cv_data)
        
        # Save the updated CV
        if use_original:
            file_path = Path("cv-analysis/original_cv.json")
        else:
            base_name = filename.split('.')[0] if filename else "updated"
            file_path = Path(f"cv-analysis/{base_name}_structured_cv.json")
        
        success = structured_cv_parser.save_structured_cv(cv_data, str(file_path))
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save updated CV")
        
        logger.info(f"CV section updated: {section_name}")
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Section '{section_name}' updated successfully",
            "validation_report": validation_report,
            "updated_at": cv_data["saved_at"]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating CV section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Section update failed: {str(e)}")


@router.get("/export")
async def export_structured_cv(
    format_type: str = Query("json", description="Export format: json, yaml"),
    use_original: bool = Query(True, description="Export original_cv.json"),
    filename: Optional[str] = Query(None, description="Specific filename to export"),
    include_metadata: bool = Query(True, description="Include metadata in export")
):
    """
    Export structured CV in different formats
    
    Supports JSON and YAML export formats
    """
    try:
        cv_data = enhanced_cv_upload_service.load_structured_cv(
            use_original=use_original,
            filename=filename
        )
        
        if not cv_data:
            raise HTTPException(status_code=404, detail="Structured CV not found")
        
        # Remove metadata if not requested
        if not include_metadata:
            cv_data.pop("metadata", None)
            cv_data.pop("unknown_sections", None)
        
        if format_type.lower() == "yaml":
            import yaml
            exported_content = yaml.dump(cv_data, default_flow_style=False, allow_unicode=True)
            media_type = "text/yaml"
        else:
            import json
            exported_content = json.dumps(cv_data, indent=2, ensure_ascii=False)
            media_type = "application/json"
        
        return JSONResponse(
            content={
                "status": "success",
                "format": format_type,
                "content": exported_content,
                "size": len(exported_content)
            },
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


def _get_validation_recommendations(validation_report: dict) -> List[str]:
    """Generate recommendations based on validation report"""
    recommendations = []
    
    if not validation_report["valid"]:
        recommendations.append("❌ CV structure has critical issues that need to be addressed")
    
    for missing in validation_report.get("missing_required", []):
        recommendations.append(f"📝 Add {missing.replace('_', ' ').title()} section")
    
    for warning in validation_report.get("warnings", []):
        recommendations.append(f"⚠️ {warning}")
    
    if not recommendations:
        recommendations.append("✅ CV structure looks good!")
    
    return recommendations