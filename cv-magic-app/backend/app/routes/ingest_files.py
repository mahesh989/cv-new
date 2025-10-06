from pathlib import Path
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user
from app.models.auth import UserData
from app.database import get_database
from app.services.file_registry_service import FileRegistryService
from app.utils.user_path_utils import get_user_base_path

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])


@router.post("/files")
def ingest_user_files(current_user: UserData = Depends(get_current_user), db=Depends(get_database)) -> Dict:
    """Index existing user files under cv-analysis into the database."""
    try:
        base = get_user_base_path(current_user.email)
        applied = base / "applied_companies"
        if not applied.exists():
            return {"success": True, "ingested": 0}

        svc = FileRegistryService.from_email(db, current_user.email)
        total = 0

        for company_dir in applied.iterdir():
            if not company_dir.is_dir() or company_dir.name == "__pycache__":
                continue
            company_name = company_dir.name
            company_id = svc.upsert_company(company_name, display_name=company_name.replace('_', ' '))

            # Map patterns to file_type
            patterns = {
                "jd_original": ["jd_original_*.json", "jd_original.json"],
                "job_info": [f"job_info_{company_name}_*.json", "job_info.json"],
                "skills_analysis": [f"{company_name}_skills_analysis_*.json", f"{company_name}_skills_analysis.json"],
                "cv_jd_matching": [f"{company_name}_cv_jd_matching_*.json", f"{company_name}_cv_jd_matching.json"],
                "component_analysis": [f"{company_name}_component_analysis_*.json", f"{company_name}_component_analysis.json"],
                "input_recommendation": [f"{company_name}_input_recommendation_*.json", f"{company_name}_input_recommendation.json"],
                "ai_recommendation": [f"{company_name}_ai_recommendation_*.json", f"{company_name}_ai_recommendation.json"],
            }

            for file_type, globs in patterns.items():
                for pattern in globs:
                    for p in company_dir.glob(pattern):
                        ts = None
                        parts = p.stem.split('_')
                        if len(parts) >= 2 and parts[-2].isdigit() and len(parts[-2]) == 8:
                            ts = f"{parts[-2]}_{parts[-1]}" if parts[-1].isdigit() and len(parts[-1]) == 6 else None
                        svc.register_file(company_id, file_type, p, timestamp=ts)
                        total += 1

            # Tailored CVs in global cvs/tailored
            tailored_dir = base / "cvs" / "tailored"
            if tailored_dir.exists():
                for p in tailored_dir.glob(f"{company_name}_tailored_cv_*.json"):
                    ts = None
                    parts = p.stem.split('_')
                    if len(parts) >= 2:
                        ts = f"{parts[-2]}_{parts[-1]}"
                    file_id = svc.register_file(company_id, "tailored_cv", p, timestamp=ts)
                    svc.set_cv_pointer(company_id, "tailored", file_id)

        return JSONResponse(content={"success": True, "ingested": total})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


