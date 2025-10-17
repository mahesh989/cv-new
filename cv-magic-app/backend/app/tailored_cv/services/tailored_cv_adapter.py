import json
from pathlib import Path
from typing import Dict, Any


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
            "github": contact_section.get('github', ''),
            "portfolio_links": {
                "blogs": contact_section.get('blogs', ''),
                "dashboard_portfolio": contact_section.get('portfolio', '')
            }
        }

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

    # Skills (preserve grouped format)
    for skill_category in tailored_cv_data.get('skills', []) or []:
        category_name = skill_category.get('category', '')
        skills_list = skill_category.get('skills', [])
        if category_name and skills_list:
            skills_text = f"{category_name}: {', '.join(skills_list)}"
            pdf_data["skills"]["technical_skills"].append(skills_text)

    # Projects
    for project in tailored_cv_data.get('projects', []) or []:
        pdf_project = {
            "name": project.get('name', ''),
            "date": project.get('date', ''),
            "description": project.get('description', ''),
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
    if not pdf_data["career_profile"]:
        pdf_data.pop("career_profile")
    if not pdf_data["projects"]:
        pdf_data.pop("projects")
    if not pdf_data["certifications"]:
        pdf_data.pop("certifications")

    return pdf_data


def load_tailored_cv_and_convert(json_file_path: str) -> Dict[str, Any]:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        tailored_data = json.load(f)
    return adapt_tailored_cv_to_pdf_format(tailored_data)


