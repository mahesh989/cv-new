# job_tracker.py
import os
import json
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from dotenv import load_dotenv
from .hybrid_ai_service import hybrid_ai
import re

# Load environment variables
load_dotenv()
ai_service = hybrid_ai

router = APIRouter()

JOB_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "job_db.json"))
TAILORED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tailored_cvs"))

os.makedirs(os.path.dirname(JOB_DB), exist_ok=True)
os.makedirs(TAILORED_DIR, exist_ok=True)

def normalize_location(location_text: str) -> str:
    """Clean and normalize location strings to be concise and readable"""
    if not location_text or location_text.lower() in ['unknown', 'not specified', 'not found']:
        return "Not specified"
    
    # Remove common verbose patterns
    location = location_text.strip()
    
    # Handle multiple locations - pick the first main city
    if ' ; OR ' in location or ' OR ' in location:
        # Split on OR and take the first location
        location = re.split(r'\s*;\s*OR\s*|\s*OR\s*', location)[0].strip()
    
    # Remove directional suburbs and detailed area descriptions
    location = re.sub(r'\s*>\s*[^,]*', '', location)  # Remove "> CBD, Inner West..." parts
    
    # Clean up common patterns - more aggressive cleaning
    patterns_to_remove = [
        r',\s*CBD\s*&\s*Inner\s*Suburbs',
        r',\s*Inner\s*Suburbs',
        r',\s*CBD',
        r'\s*&\s*Inner\s*Suburbs',
        r'\s*&\s*surrounding\s*areas?',
        r'\s*and\s*surrounding\s*areas?',
        r'\s*metro\s*area',
        r'\s*metropolitan\s*area',
        r'\s*region',
        r',\s*Inner\s*West\s*&\s*Eastern\s*Suburbs\s*\w+',  # Remove "Inner West & Eastern Suburbs Sydney"
        r',\s*[A-Z][a-z]+\s*&\s*[A-Z][a-z]+\s*[A-Z][a-z]+\s*\w+',  # Generic pattern for "Area & Area City"
    ]
    
    for pattern in patterns_to_remove:
        location = re.sub(pattern, '', location, flags=re.IGNORECASE)
    
    # Extract just the main city name if Australian
    australian_cities = ['sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'darwin', 'hobart', 'canberra']
    location_lower = location.lower()
    
    # Find the main Australian city and simplify to "City, Australia"
    for city in australian_cities:
        if city in location_lower:
            return f"{city.title()}, Australia"
    
    # If not Australian, clean up and return
    # Clean up extra commas and spaces
    location = re.sub(r',\s*,', ',', location)  # Remove double commas
    location = re.sub(r',\s*$', '', location)   # Remove trailing comma
    location = re.sub(r'^\s*,', '', location)   # Remove leading comma
    location = re.sub(r'\s+', ' ', location)    # Normalize spaces
    
    # Capitalize properly
    parts = [part.strip().title() for part in location.split(',')]
    location = ', '.join(filter(None, parts))  # Filter out empty parts
    
    return location.strip() if location.strip() else "Not specified"

def extract_metadata_gpt(jd_text: str) -> dict:
    """Extract company name, phone, and location using GPT"""
    prompt = f"""
Extract the following details from this job description:

- Company Name: Just the organization name, no extra words
- Location: ONLY the main city and country (e.g., "Sydney, Australia" or "Melbourne, Australia"). 
  If multiple cities are mentioned, pick the PRIMARY/FIRST one. 
  Do NOT include suburbs, regions, or detailed area descriptions.
- Contact Phone Number: If available

Rules for Location:
- Keep it SHORT and clean: "City, Country" format
- Examples: "Sydney, Australia", "Melbourne, Australia", "Brisbane, Australia"
- Do NOT include: suburbs, CBD, inner suburbs, metro areas, regional descriptions
- If multiple locations, pick the first/main one

If something is missing, return "Unknown" or "Not specified".

Job Description:
{jd_text}

Return in this exact JSON format:
{{
  "company": "...",
  "location": "...",
  "phone": "..."
}}
"""
    try:
        response = ai_service.generate_response(
            prompt=prompt,
            model="gpt-3.5-turbo",
            temperature=0
        )
        content = response.strip()
        
        # Parse the JSON response
        import json
        if content.startswith("{") and content.endswith("}"):
            metadata = json.loads(content)
        else:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                metadata = json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found")
        
        # Apply location normalization
        if 'location' in metadata:
            metadata['location'] = normalize_location(metadata['location'])
        
        return metadata
    except Exception as e:
        print("[GPT Metadata Error]", e)
        return {
            "company": "Unknown",
            "location": "Not specified",
            "phone": "Not found"
        }

@router.post("/save-job/")
async def save_job(request: Request):
    # Ensure job_db.json exists as an empty list if missing
    if not os.path.exists(JOB_DB):
        with open(JOB_DB, "w") as f:
            json.dump([], f)
    data = await request.json()
    job_link = data.get("job_link")
    jd_text = data.get("jd_text")
    tailored_cv = data.get("tailored_cv")
    applied = bool(data.get("applied", False))

    # New comprehensive metadata
    cv_metadata = data.get("cv_metadata", {})
    original_cv = data.get("original_cv", "")
    ats_score = data.get("ats_score", 0)
    generation_source = data.get("generation_source", "manual")

    if not job_link or not jd_text or not tailored_cv:
        raise HTTPException(status_code=400, detail="Missing required fields.")

    # 🧠 Extract metadata from JD (legacy support)
    legacy_metadata = extract_metadata_gpt(jd_text)

    # Create comprehensive job data
    new_job_data = {
        "sn": str(uuid4())[:8],
        "company": cv_metadata.get("company", legacy_metadata.get("company", "Unknown")),
        "role": cv_metadata.get("role", "Unknown Role"),
        "level": cv_metadata.get("level", "Not specified"),
        "industry": cv_metadata.get("industry", "Not specified"),
        "work_type": cv_metadata.get("work_type", "Not specified"),
        "location": legacy_metadata.get("location", "Not specified"),
        "phone": legacy_metadata.get("phone", "Not found"),
        "date_applied": datetime.now().strftime("%Y-%m-%d"),
        "job_link": job_link,
        "tailored_cv": tailored_cv,
        "original_cv": original_cv,
        "applied": applied,
        "ats_score": ats_score,
        "generation_source": generation_source,
        "key_skills": cv_metadata.get("key_skills", []),
        "cv_display_name": generate_cv_display_name(cv_metadata, tailored_cv),
        "generation_details": {
            "matched_hard_skills": cv_metadata.get("matched_hard_skills", []),
            "matched_soft_skills": cv_metadata.get("matched_soft_skills", []),
            "missed_hard_skills": cv_metadata.get("missed_hard_skills", []),
            "missed_soft_skills": cv_metadata.get("missed_soft_skills", []),
            "cv_length": cv_metadata.get("length", 0)
        }
    }

    existing = []
    if os.path.exists(JOB_DB):
        with open(JOB_DB, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    # 🛡 Check for duplicate (same company + same job_link)
    duplicate_index = next(
        (i for i, job in enumerate(existing) if job.get("company") == new_job_data["company"] and job.get("job_link") == job_link),
        None
    )

    if duplicate_index is not None:
        # 🔥 If duplicate found — overwrite but preserve some fields
        old_job = existing[duplicate_index]
        new_job_data["date_applied"] = old_job.get("date_applied", new_job_data["date_applied"])
        existing[duplicate_index] = new_job_data
    else:
        # 🚀 Otherwise, just add new
        existing.append(new_job_data)

    # ✅ Save back to DB
    with open(JOB_DB, "w") as f:
        json.dump(existing, f, indent=2)

    return {"message": "Job saved successfully with comprehensive metadata."}

def generate_cv_display_name(metadata: dict, filename: str) -> str:
    """Generate a user-friendly display name for the CV"""
    company = metadata.get("company", "Unknown")
    role = metadata.get("role", "Unknown Role")
    level = metadata.get("level", "")
    work_type = metadata.get("work_type", "")
    
    # Create a comprehensive display name
    display_parts = []
    
    if level and level != "Not specified":
        display_parts.append(level)
    
    display_parts.append(role)
    display_parts.append(f"at {company}")
    
    if work_type and work_type != "Not specified":
        display_parts.append(f"({work_type})")
    
    display_name = " ".join(display_parts)
    
    # Add filename as fallback info
    if len(display_name) > 80:
        display_name = f"{role} at {company}"
    
    return display_name

@router.get("/jobs/")
def list_saved_jobs():
    if not os.path.exists(JOB_DB):
        return []
    with open(JOB_DB, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

@router.post("/toggle-applied/")
async def toggle_applied(request: Request):
    data = await request.json()
    sn = data.get("sn")
    if not sn:
        raise HTTPException(status_code=400, detail="Missing job serial number.")

    if not os.path.exists(JOB_DB):
        raise HTTPException(status_code=404, detail="Job DB not found.")

    with open(JOB_DB, "r") as f:
        jobs = json.load(f)

    for job in jobs:
        if job.get("sn") == sn:
            job["applied"] = "no" if job.get("applied") == "yes" else "yes"
            break
    else:
        raise HTTPException(status_code=404, detail="Job not found.")

    with open(JOB_DB, "w") as f:
        json.dump(jobs, f, indent=2)

    return {"message": "Applied status toggled."}

@router.delete("/delete-all-jobs/")
def delete_all_jobs():
    """Delete all saved jobs and clean up orphaned CV files"""
    # Clear the database
    with open(JOB_DB, "w") as f:
        json.dump([], f)
    
    # Clean up all CV files in the tailored directory
    cleanup_result = cleanup_orphaned_cv_files()
    
    return {
        "message": "All saved jobs deleted successfully.",
        "cleanup_result": cleanup_result
    }

@router.post("/cleanup-orphaned-cvs/")
def cleanup_orphaned_cv_files():
    """Clean up CV files that are no longer referenced in the database"""
    try:
        # Get all CV filenames referenced in the database
        referenced_cvs = set()
        if os.path.exists(JOB_DB):
            with open(JOB_DB, "r") as f:
                try:
                    jobs = json.load(f)
                    for job in jobs:
                        tailored_cv = job.get("tailored_cv", "")
                        if tailored_cv:
                            referenced_cvs.add(tailored_cv)
                except json.JSONDecodeError:
                    pass
        
        # Get all CV files in the tailored directory
        if not os.path.exists(TAILORED_DIR):
            return {"message": "Tailored CV directory does not exist", "deleted_files": []}
        
        all_cv_files = [f for f in os.listdir(TAILORED_DIR) if f.endswith('.docx')]
        
        # Find orphaned files (files not referenced in database)
        orphaned_files = [f for f in all_cv_files if f not in referenced_cvs]
        
        # Delete orphaned files
        deleted_files = []
        for filename in orphaned_files:
            file_path = os.path.join(TAILORED_DIR, filename)
            try:
                os.remove(file_path)
                deleted_files.append(filename)
                print(f"🗑️ Deleted orphaned CV file: {filename}")
            except Exception as e:
                print(f"❌ Failed to delete {filename}: {e}")
        
        return {
            "message": f"Cleanup completed. Deleted {len(deleted_files)} orphaned CV files.",
            "deleted_files": deleted_files,
            "total_files_before": len(all_cv_files),
            "referenced_files": len(referenced_cvs),
            "orphaned_files": len(orphaned_files)
        }
    
    except Exception as e:
        print(f"❌ Error during CV cleanup: {e}")
        return {
            "message": f"Error during cleanup: {str(e)}",
            "deleted_files": []
        }
