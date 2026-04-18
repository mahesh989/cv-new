"""
CV processing routes — upload, list, read, delete, and tailored-CV management.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user
from app.models.auth import UserData
from app.services.cv_processor import cv_processor
from app.services.enhanced_cv_upload_service import EnhancedCVUploadService
from app.unified_latest_file_selector import get_selector_for_user
from app.utils.user_path_utils import get_user_base_path, get_user_uploads_path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv", tags=["CV Processing"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _uploads_dir(user_email: str) -> Path:
    """Return (and create) the user-specific upload directory."""
    path = get_user_uploads_path(user_email)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _tailored_timestamp(filepath: Path):
    """Extract sortable datetime from tailored-CV filename, falling back to mtime."""
    try:
        ts = filepath.name.split("_tailored_cv_")[1].replace(".txt", "")
        return datetime.strptime(ts, "%Y%m%d_%H%M%S")
    except Exception:
        return filepath.stat().st_mtime


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_cv(
    cv: UploadFile = File(...),
    current_user: UserData = Depends(get_current_user),
):
    """Upload a CV file (no structured processing)."""
    if not cv.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    try:
        svc = EnhancedCVUploadService(user_email=current_user.email)
        result = await svc.upload_cv_only(cv_file=cv)
        logger.info(f"CV uploaded: {cv.filename} for {current_user.email}")
        return JSONResponse(content={
            "message": "CV uploaded successfully.",
            "filename": result["filename"],
            "size": result["file_size"],
            "type": result["file_type"],
            "upload_path": result["upload_path"],
            "structured_processing": False,
            "user_email": current_user.email,
        })
    except Exception as e:
        logger.error(f"Error uploading CV for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading CV: {e}")


@router.get("/list")
async def list_cvs(current_user: UserData = Depends(get_current_user)):
    """List all uploaded CVs with metadata."""
    try:
        upload_dir = get_user_uploads_path(current_user.email)
        cvs = []
        if upload_dir.exists():
            for fp in upload_dir.iterdir():
                if fp.is_file() and fp.suffix.lower() in ALLOWED_EXTENSIONS:
                    try:
                        st = fp.stat()
                        cvs.append({"filename": fp.name, "size": st.st_size,
                                    "type": fp.suffix[1:].upper(), "uploaded_date": st.st_mtime})
                    except Exception as e:
                        logger.warning(f"Error reading metadata for {fp.name}: {e}")
        cvs.sort(key=lambda x: x["filename"])
        return JSONResponse(content={"uploaded_cvs": [c["filename"] for c in cvs],
                                     "cv_details": cvs, "total_count": len(cvs)})
    except Exception as e:
        logger.error(f"Error listing CVs: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing CVs: {e}")


@router.get("/content/{filename}")
async def get_cv_content(
    filename: str,
    auto_structure: bool = False,
    current_user: UserData = Depends(get_current_user),
):
    """Get CV content with optional structured processing."""
    try:
        file_path = _uploads_dir(current_user.email) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")

        result = cv_processor.extract_text_from_file(file_path)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to extract text: {result['error']}")

        st = file_path.stat()
        response: dict = {
            "filename": filename,
            "content": result["text"],
            "metadata": result.get("metadata", {}),
            "file_info": {"size": st.st_size, "type": file_path.suffix[1:].upper(), "uploaded_date": st.st_mtime},
            "extraction_info": {"method": result.get("method", "unknown"),
                                "character_count": len(result["text"]),
                                "word_count": len(result["text"].split())},
        }

        if auto_structure:
            try:
                svc = EnhancedCVUploadService(user_email=current_user.email)
                proc = await svc.process_existing_cv(filename=filename)
                if proc["success"]:
                    response["processing_info"] = {
                        "structured_processing": True,
                        "structured_cv_path": proc["structured_cv_path"],
                        "validation_report": proc["validation_report"],
                        "sections_found": proc["sections_found"],
                        "unknown_sections": proc.get("unknown_sections", []),
                        "processing_timestamp": proc["processing_timestamp"],
                    }
                    structured = svc.load_structured_cv()
                    if structured:
                        response["structured_cv"] = structured
                else:
                    response["processing_info"] = {"structured_processing": False, "error": "Processing failed"}
            except Exception as e:
                logger.error(f"Error during structured processing of {filename}: {e}")
                response["processing_info"] = {"structured_processing": False, "error": str(e)}

        return JSONResponse(content=response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting CV content: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting CV content: {e}")


@router.post("/process-structured/{filename}")
async def process_cv_structured(
    filename: str,
    current_user: UserData = Depends(get_current_user),
):
    """Process a CV into structured format (original_cv.json)."""
    try:
        file_path = _uploads_dir(current_user.email) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")

        svc = EnhancedCVUploadService(user_email=current_user.email)
        proc = await svc.process_existing_cv(filename=filename)
        if proc["success"]:
            return JSONResponse(content={
                "success": True, "message": "CV processed into structured format successfully",
                "filename": filename, "structured_cv_path": proc["structured_cv_path"],
                "sections_found": proc["sections_found"], "validation_report": proc["validation_report"],
                "processing_timestamp": proc["processing_timestamp"],
            })
        raise HTTPException(status_code=500, detail="Failed to process CV into structured format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing structured CV: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing structured CV: {e}")


@router.get("/preview/{filename}")
async def get_cv_preview(
    filename: str,
    max_length: int = 500,
    current_user: UserData = Depends(get_current_user),
):
    """Get a CV content preview."""
    try:
        file_path = _uploads_dir(current_user.email) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")

        result = cv_processor.extract_text_from_file(file_path)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to extract text: {result['error']}")

        full_text = result["text"]
        preview = cv_processor.get_text_preview(full_text, max_length)
        return JSONResponse(content={
            "filename": filename, "preview": preview, "full_length": len(full_text),
            "preview_length": len(preview), "is_truncated": len(full_text) > max_length,
            "basic_info": cv_processor.extract_basic_info(full_text),
            "extraction_method": result.get("method", "unknown"),
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating CV preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating CV preview: {e}")


@router.get("/latest-cv-content")
async def get_latest_cv_content(current_user: UserData = Depends(get_current_user)):
    """Get the latest CV content (original or tailored) for frontend preview."""
    try:
        selector = get_selector_for_user(current_user.email)
        cv_ctx = selector.get_latest_cv_across_all("__any__")

        if not cv_ctx or not cv_ctx.txt_path:
            raise HTTPException(status_code=404, detail="No CV text file found")

        txt_file = Path(str(cv_ctx.txt_path))
        if not txt_file.exists():
            raise HTTPException(status_code=404, detail=f"CV text file not found: {txt_file}")

        content = txt_file.read_text(encoding="utf-8")
        return JSONResponse(content={
            "success": True, "content": content, "filename": txt_file.name,
            "source_folder": cv_ctx.file_type,
            "metadata": {"file_size": len(content), "last_modified": txt_file.stat().st_mtime,
                         "dynamic_selection": True},
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest CV content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest CV content: {e}")


@router.get("/read-tailored-cv/{company_name}")
async def read_tailored_cv(
    company_name: str,
    current_user: UserData = Depends(get_current_user),
):
    """Read tailored CV content for frontend preview (strict — no fallback to original)."""
    try:
        selector = get_selector_for_user(current_user.email)
        ctx = selector.get_latest_tailored_cv_only(company_name)

        if not ctx.exists or not ctx.txt_path:
            raise HTTPException(status_code=404,
                                detail=f"No tailored CV found for '{company_name}'. Generate one first.")

        txt_file = ctx.txt_path
        if not txt_file.exists():
            raise HTTPException(status_code=404, detail=f"Tailored CV file not found: {txt_file}")

        content = txt_file.read_text(encoding="utf-8")
        return JSONResponse(content={
            "success": True, "content": content, "filename": txt_file.name, "company": company_name,
            "source_folder": ctx.file_type,
            "metadata": {"file_size": len(content), "last_modified": txt_file.stat().st_mtime,
                         "timestamp": ctx.timestamp, "dynamic_selection": True},
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tailored CV content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tailored CV content: {e}")


@router.get("/latest-tailored-cv")
async def get_latest_tailored_cv(current_user: UserData = Depends(get_current_user)):
    """Get the most recent tailored CV across all companies."""
    try:
        base = get_user_base_path(current_user.email)
        tailored_dir = base / "cvs" / "tailored"

        if not tailored_dir.exists():
            raise HTTPException(status_code=404, detail="No tailored CV files found")

        files = list(tailored_dir.glob("*_tailored_cv_*.txt"))
        if not files:
            raise HTTPException(status_code=404, detail="No tailored CV files found")

        latest = max(files, key=_tailored_timestamp)
        company_name = latest.name.split("_tailored_cv_")[0] if "_tailored_cv_" in latest.name else "Unknown"
        content = latest.read_text(encoding="utf-8")

        return JSONResponse(content={
            "success": True, "content": content, "filename": latest.name, "company": company_name,
            "metadata": {"file_size": len(content), "last_modified": latest.stat().st_mtime,
                         "file_path": str(latest)},
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest tailored CV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest tailored CV: {e}")


@router.get("/available-companies")
async def get_available_companies(current_user: UserData = Depends(get_current_user)):
    """List companies that have tailored CVs available."""
    try:
        base = get_user_base_path(current_user.email)
        companies = []
        applied = base / "applied_companies"
        if applied.exists():
            for company_dir in applied.iterdir():
                if not company_dir.is_dir() or company_dir.name == "__pycache__":
                    continue
                name = company_dir.name
                files = list(company_dir.glob(f"{name}_tailored_cv_*.txt")) \
                        or list(company_dir.glob("*tailored_cv_*.txt"))
                if files:
                    companies.append({
                        "company": name,
                        "display_name": name.replace("_", " "),
                        "has_tailored_cv": True,
                        "last_updated": max(files, key=lambda p: p.stat().st_mtime).stat().st_mtime,
                    })
        return JSONResponse(content={"success": True, "companies": companies, "total_count": len(companies)})
    except Exception as e:
        logger.error(f"Failed to get available companies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve companies: {e}")


@router.delete("/{filename}")
async def delete_cv(
    filename: str,
    current_user: UserData = Depends(get_current_user),
):
    """Delete a CV file."""
    try:
        file_path = _uploads_dir(current_user.email) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")
        file_path.unlink()
        logger.info(f"CV deleted: {filename}")
        return JSONResponse(content={"message": "CV deleted successfully", "filename": filename})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CV: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting CV: {e}")


@router.get("/stats")
async def get_upload_stats(current_user: UserData = Depends(get_current_user)):
    """Get upload directory statistics."""
    try:
        upload_dir = _uploads_dir(current_user.email)
        stats: dict = {"total_files": 0, "total_size": 0, "file_types": {},
                       "upload_directory": str(upload_dir.absolute()), "user_email": current_user.email}
        if upload_dir.exists():
            for fp in upload_dir.iterdir():
                if fp.is_file() and fp.suffix.lower() in ALLOWED_EXTENSIONS:
                    stats["total_files"] += 1
                    sz = fp.stat().st_size
                    stats["total_size"] += sz
                    ft = fp.suffix[1:].upper()
                    stats["file_types"].setdefault(ft, {"count": 0, "size": 0})
                    stats["file_types"][ft]["count"] += 1
                    stats["file_types"][ft]["size"] += sz
        stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting upload stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting upload stats: {e}")


@router.put("/tailored-cv/save")
async def save_tailored_cv(
    request: Request,
    current_user: UserData = Depends(get_current_user),
):
    """Save edited tailored CV content back to file."""
    try:
        data = await request.json()
        company_name = data.get("company_name")
        cv_content = data.get("cv_content")
        filename = data.get("filename")

        if not company_name:
            return JSONResponse(status_code=400, content={"error": "company_name is required"})
        if not cv_content:
            return JSONResponse(status_code=400, content={"error": "cv_content is required"})

        base = get_user_base_path(current_user.email)
        company_path = base / company_name
        if not company_path.exists():
            return JSONResponse(status_code=404, content={"error": f"Company directory not found: {company_name}"})

        if filename:
            target = company_path / filename
            if not target.exists():
                return JSONResponse(status_code=404, content={"error": f"File not found: {filename}"})
        else:
            candidates = list(company_path.glob("*tailored_cv*.json"))
            if not candidates:
                return JSONResponse(status_code=404, content={"error": f"No tailored CV files found for {company_name}"})
            target = max(candidates, key=lambda p: p.stat().st_mtime)

        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

        if isinstance(existing, dict):
            if isinstance(cv_content, dict):
                existing.update(cv_content)
            else:
                existing["text"] = cv_content
            existing["updated_at"] = datetime.now().isoformat()
            existing["manually_edited"] = True
            updated = existing
        else:
            updated = {"content": cv_content, "updated_at": datetime.now().isoformat(),
                       "manually_edited": True, "original_data": existing}

        target.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"Tailored CV saved: {target}")

        return JSONResponse(content={
            "success": True, "message": "Tailored CV saved successfully",
            "company": company_name, "filename": target.name,
            "file_path": str(target), "updated_at": updated.get("updated_at"),
        })
    except Exception as e:
        logger.error(f"Error saving tailored CV: {e}")
        return JSONResponse(status_code=500, content={"error": f"Failed to save tailored CV: {e}"})
