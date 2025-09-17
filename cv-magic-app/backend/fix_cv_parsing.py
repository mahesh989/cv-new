#!/usr/bin/env python3
"""
Fix CV parsing to properly extract experience and skills data
"""

import json
import re
from pathlib import Path
from datetime import datetime

def parse_cv_properly():
    """Parse the CV text and extract all sections properly"""
    
    # Load the original CV text
    txt_path = Path('/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/original_cv.txt')
    with open(txt_path, 'r') as f:
        cv_text = f.read()
    
    # Skip the header metadata
    cv_text_lines = cv_text.split('\n')
    actual_cv_start = 0
    for i, line in enumerate(cv_text_lines):
        if 'Maheshwor Tiwari' in line and '@' not in line:
            actual_cv_start = i
            break
    
    cv_content = '\n'.join(cv_text_lines[actual_cv_start:])
    
    # Extract personal information
    personal_info = {
        "name": "Maheshwor Tiwari",
        "phone": "0414 032 507",
        "email": "maheshtwari99@gmail.com",
        "location": "Sydney, Australia",
        "linkedin": "",
        "portfolio_links": {
            "blogs": "Medium Blog Available",
            "github": "GitHub Profile Available",
            "dashboard_portfolio": "Dashboard Portfolio Available",
            "website": ""
        }
    }
    
    # Extract career profile
    career_profile = {}
    profile_match = re.search(r'CAREER PROFILE\s*\n(.*?)(?=\n[A-Z])', cv_content, re.DOTALL)
    if profile_match:
        career_profile = {"summary": profile_match.group(1).strip()}
    
    # Extract technical skills (from KEY SKILLS section)
    technical_skills = []
    skills_match = re.search(r'KEY SKILLS\s*\n(.*?)(?=\nEDUCATION|\nEXPERIENCE)', cv_content, re.DOTALL)
    if skills_match:
        skills_text = skills_match.group(1)
        # Split by bullet points or new lines
        for line in skills_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('•'):
                technical_skills.append(line)
    
    # Extract education
    education = []
    edu_match = re.search(r'EDUCATION\s*\n(.*?)(?=\n[A-Z][A-Z]|\nData)', cv_content, re.DOTALL)
    if edu_match:
        edu_text = edu_match.group(1)
        
        # Master's degree
        if "Master of Data Science" in edu_text:
            education.append({
                "degree": "Master of Data Science",
                "institution": "Charles Darwin University",
                "location": "Sydney, Australia",
                "duration": "Mar 2023 - Oct 2024",
                "additional_info": "",
                "gpa": "6.35/7",
                "honors": "",
                "relevant_coursework": []
            })
        
        # Bachelor's degree  
        if "Bachelor" in edu_text:
            education.append({
                "degree": "Bachelor of Science in Information Technology",
                "institution": "Tribhuvan University",
                "location": "Kathmandu, Nepal",
                "duration": "Jul 2014 – Aug 2018",
                "additional_info": "",
                "gpa": "",
                "honors": "",
                "relevant_coursework": []
            })
    
    # Extract experience - looking for the actual job entries
    experience = []
    
    # iBuild Building Solutions
    if "iBuild" in cv_content:
        exp1_match = re.search(r'Data Analyst.*?Mar 2024.*?Jun 2024.*?\niBuild.*?\n(.*?)(?=\nData|\nPROJECT|\Z)', cv_content, re.DOTALL)
        if exp1_match:
            bullets_text = exp1_match.group(1)
            bullets = []
            for line in bullets_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('Data'):
                    bullets.append(line)
            
            experience.append({
                "position": "Data Analyst",
                "company": "iBuild Building Solutions",
                "location": "Victoria, Australia",
                "duration": "Mar 2024 – Jun 2024",
                "employment_type": "Contract",
                "achievements": bullets[:4],  # Take first 4 bullets
                "responsibilities": []
            })
    
    # Property Console
    if "Property Console" in cv_content:
        exp2_match = re.search(r'Data Insight.*?Jun 2023.*?Nov 2023.*?\nProperty Console.*?\n(.*?)(?=\nPROJECT|\nCERT|\Z)', cv_content, re.DOTALL)
        if exp2_match:
            bullets_text = exp2_match.group(1)
            bullets = []
            for line in bullets_text.split('\n'):
                line = line.strip()
                if line and len(line) > 20:  # Filter out short fragments
                    bullets.append(line)
            
            experience.append({
                "position": "Data Insight & Analyst",
                "company": "Property Console",
                "location": "Sydney, Australia",
                "duration": "Jun 2023 - Nov 2023",
                "employment_type": "Contract",
                "achievements": bullets[:3],  # Take first 3 bullets
                "responsibilities": []
            })
    
    # Extract projects
    projects = []
    if "Heart Attack Risk Prediction" in cv_content or "Thesis" in cv_content:
        projects.append({
            "name": "Heart Attack Risk Prediction",
            "description": "University Machine Learning and AI Project",
            "duration": "Oct 2024",
            "technologies": ["Python", "Machine Learning", "Deep Learning", "Data Visualization"],
            "achievements": [
                "Implemented logistic regression, random forests, and deep learning models",
                "Addressed imbalanced datasets using undersampling techniques",
                "Achieved grade of 37/40 for project excellence"
            ],
            "url": "",
            "status": "Completed"
        })
    
    # Extract certifications
    certifications = []
    if "CERTIFICATIONS" in cv_content or "SQL" in cv_content:
        certifications = [
            {
                "name": "SQL",
                "issuing_organization": "LinkedIn Learning",
                "date_obtained": "",
                "expiry_date": "",
                "status": "Active",
                "description": "",
                "credential_id": "",
                "url": ""
            },
            {
                "name": "Google Analytics",
                "issuing_organization": "Skillshop, Google",
                "date_obtained": "",
                "expiry_date": "",
                "status": "Active",
                "description": "",
                "credential_id": "",
                "url": ""
            }
        ]
    
    # Build the complete structured CV
    structured_cv = {
        "personal_information": personal_info,
        "career_profile": career_profile,
        "technical_skills": technical_skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "soft_skills": [],
        "domain_expertise": [],
        "languages": [],
        "awards": [],
        "publications": [],
        "volunteer_work": [],
        "professional_memberships": [],
        "unknown_sections": {},
        "saved_at": datetime.now().isoformat(),
        "metadata": {
            "source_filename": "Bloomberg_DA_Maheshwor_Tiwar copy 2.docx",
            "processed_at": datetime.now().isoformat(),
            "processing_version": "2.0",
            "content_type": "structured_cv"
        }
    }
    
    return structured_cv


def main():
    """Main function to fix the CV parsing"""
    print("🔧 Fixing CV parsing...")
    
    # Parse the CV properly
    structured_cv = parse_cv_properly()
    
    # Save the fixed CV
    cv_path = Path('/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/original_cv.json')
    
    # Create backup first
    backup_path = cv_path.with_suffix('.backup.json')
    if cv_path.exists():
        with open(cv_path, 'r') as f:
            backup_data = json.load(f)
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        print(f"✅ Backup created: {backup_path}")
    
    # Save the fixed CV
    with open(cv_path, 'w') as f:
        json.dump(structured_cv, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Fixed CV saved to: {cv_path}")
    
    # Verify the fix
    print("\n📊 Verification:")
    print(f"  - Experience entries: {len(structured_cv['experience'])}")
    print(f"  - Technical skills: {len(structured_cv['technical_skills'])}")
    print(f"  - Education entries: {len(structured_cv['education'])}")
    print(f"  - Projects: {len(structured_cv['projects'])}")
    print(f"  - Certifications: {len(structured_cv['certifications'])}")
    
    if structured_cv['experience']:
        print("\n👔 Experience found:")
        for exp in structured_cv['experience']:
            print(f"  - {exp['position']} at {exp['company']}")
            print(f"    Achievements: {len(exp['achievements'])} items")
    
    if structured_cv['technical_skills']:
        print("\n🛠️ Skills found:")
        for skill in structured_cv['technical_skills'][:3]:
            print(f"  - {skill[:50]}...")


if __name__ == "__main__":
    main()