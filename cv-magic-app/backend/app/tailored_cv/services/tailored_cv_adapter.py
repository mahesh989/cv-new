import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def adapt_tailored_cv_to_pdf_format(tailored_cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert your tailored CV JSON format to the PDF generator's expected format
    PRESERVE original structure and only include what exists in the JSON
    """
    pdf_data: Dict[str, Any] = {
        "personal_information": {},
        "career_profile": {},
        "experience": [],
        "education": [],
        "skills": {"technical_skills": []},
        "projects": [],
        "certifications": []
    }

    # Personal information from contact
    contact_section = tailored_cv_data.get('contact', {})
    if contact_section:
        pdf_data["personal_information"] = {
            "name": contact_section.get('name', ''),
            "location": contact_section.get('location', ''),
            "phone": contact_section.get('phone', ''),
            "email": contact_section.get('email', ''),
            "linkedin": contact_section.get('linkedin', ''),
            "github": contact_section.get('website', ''),  # Map website to github field for PDF
            "portfolio_links": {
                "blogs": contact_section.get('website', ''),  # Use website for portfolio
                "website": contact_section.get('website', '')
            }
        }

    # Profile Summary (NEW FRAMEWORK) - Critical field mapping
    # Maps profile_summary from tailored CV to both new and legacy formats
    profile_summary = tailored_cv_data.get('profile_summary', '')
    if profile_summary:
        logger.info("[ADAPTER] Mapping profile_summary to PDF format")
        pdf_data["profile_summary"] = profile_summary
        # Also populate career_profile for backward compatibility
        pdf_data["career_profile"] = {"summary": profile_summary}
    else:
        logger.warning("[ADAPTER] ⚠️ No profile_summary found in tailored CV data")

    # Experience
    for exp in tailored_cv_data.get('experience', []) or []:
        duration = f"{exp.get('start_date', '')} - {exp.get('end_date', '')}".strip()
        pdf_experience = {
            "title": exp.get('title', ''),
            "company": exp.get('company', ''),
            "location": exp.get('location', ''),
            "duration": duration,
            "responsibilities": exp.get('bullets', [])
        }
        pdf_data["experience"].append(pdf_experience)

    # Education
    for edu in tailored_cv_data.get('education', []) or []:
        pdf_education = {
            "degree": edu.get('degree', ''),
            "institution": edu.get('institution', ''),
            "location": edu.get('location', ''),
            "year": edu.get('graduation_date', '')
        }
        pdf_data["education"].append(pdf_education)

    # Skills (handle both simple list and grouped format)
    skills_data = tailored_cv_data.get('skills', []) or []
    if skills_data:
        # Check if skills is a list of strings (simple format)
        if isinstance(skills_data[0], str):
            # Simple list format - add all skills as technical skills (single line)
            pdf_data["skills"]["technical_skills"] = skills_data
            pdf_data["skills"]["is_categorized"] = False
        else:
            # Grouped format - preserve category structure (bullets)
            pdf_data["skills"]["is_categorized"] = True
            for skill_category in skills_data:
                if isinstance(skill_category, dict):
                    category_name = skill_category.get('category', '')
                    skills_list = skill_category.get('skills', [])
                    if category_name and skills_list:
                        # Store category and skills separately for proper PDF rendering
                        if category_name not in pdf_data["skills"]:
                            pdf_data["skills"][category_name] = []
                        pdf_data["skills"][category_name] = skills_list

    # Projects
    for project in tailored_cv_data.get('projects', []) or []:
        pdf_project = {
            "name": project.get('name', ''),
            "date": project.get('date', ''),
            "duration": project.get('duration', ''),  # Add duration field
            "context": project.get('context', ''),    # Add context field
            "description": project.get('description', ''),
            "bullets": project.get('bullets', []),  # Add bullets mapping
            "technologies": project.get('technologies', [])
        }
        pdf_data["projects"].append(pdf_project)

    # Certifications
    for cert in tailored_cv_data.get('certifications', []) or []:
        if isinstance(cert, dict):
            pdf_data["certifications"].append(cert)
        else:
            pdf_data["certifications"].append({"name": cert})

    # Remove empty sections not present in source
    if not pdf_data.get("career_profile"):
        pdf_data.pop("career_profile", None)
    if not pdf_data["projects"]:
        pdf_data.pop("projects")
    if not pdf_data["certifications"]:
        pdf_data.pop("certifications")

    # VALIDATION LAYER: Ensure important fields are mapped
    _validate_field_mappings(tailored_cv_data, pdf_data)

    return pdf_data


def _validate_field_mappings(source_data: Dict[str, Any], pdf_data: Dict[str, Any]) -> None:
    """
    Validation layer to ensure all important fields from source are mapped to PDF format.
    Logs warnings for any missing mappings to help maintain consistency.
    """
    # Define important fields and their possible mapped names in PDF
    field_mappings = {
        'profile_summary': ['profile_summary', 'career_profile'],
        'contact': ['personal_information'],
        'experience': ['experience'],
        'education': ['education'],
        'skills': ['skills'],
        'projects': ['projects'],
        'certifications': ['certifications']
    }
    
    missing_mappings: List[str] = []
    
    for source_field, possible_pdf_fields in field_mappings.items():
        # Check if field exists in source and has content
        source_value = source_data.get(source_field)
        
        # Skip empty/None values
        if not source_value:
            continue
        
        # For lists, skip if empty
        if isinstance(source_value, list) and len(source_value) == 0:
            continue
        
        # For dicts, skip if empty
        if isinstance(source_value, dict) and len(source_value) == 0:
            continue
        
        # Check if at least one of the possible PDF fields has the content
        is_mapped = False
        for pdf_field in possible_pdf_fields:
            pdf_value = pdf_data.get(pdf_field)
            if pdf_value:
                # Check if it has actual content
                if isinstance(pdf_value, (str, list, dict)):
                    if pdf_value:  # Non-empty string, list, or dict
                        is_mapped = True
                        break
                else:
                    is_mapped = True
                    break
        
        if not is_mapped:
            missing_mappings.append(f"{source_field} -> {possible_pdf_fields}")
            logger.warning(
                f"⚠️ [ADAPTER_VALIDATION] Field '{source_field}' exists in source but not found in PDF data. "
                f"Expected in: {possible_pdf_fields}"
            )
    
    if missing_mappings:
        logger.warning(
            f"⚠️ [ADAPTER_VALIDATION] {len(missing_mappings)} field(s) may not be properly mapped: "
            f"{', '.join(missing_mappings)}"
        )
    else:
        logger.info("✅ [ADAPTER_VALIDATION] All important fields are properly mapped to PDF format")


def load_tailored_cv_and_convert(json_file_path: str) -> Dict[str, Any]:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        tailored_data = json.load(f)
    return adapt_tailored_cv_to_pdf_format(tailored_data)


