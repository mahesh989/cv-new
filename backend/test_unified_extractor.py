#!/usr/bin/env python3
"""
Test script for unified skill extractor
"""

import sys
import os
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv()

from src.unified_skill_extractor import extract_skills_unified
from src.cv_parser import extract_text_from_pdf, extract_text_from_docx

def test_cv_extraction(cv_filename):
    """Test skill extraction on a CV file"""
    print(f"\n=== TESTING UNIFIED SKILL EXTRACTOR ===")
    print(f"CV File: {cv_filename}")
    
    # Load CV text
    upload_dir = "uploads"
    file_path = os.path.join(upload_dir, cv_filename)
    
    if not os.path.exists(file_path):
        print(f"❌ CV file not found: {file_path}")
        return
    
    ext = os.path.splitext(cv_filename)[1].lower()
    if ext == ".pdf":
        cv_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        cv_text = extract_text_from_docx(file_path)
    else:
        print(f"❌ Unsupported file format: {ext}")
        return
    
    print(f"✅ CV text loaded: {len(cv_text)} characters")
    
    # Extract skills
    try:
        print("🔄 Starting skill extraction...")
        skills = extract_skills_unified(cv_text)
        
        print(f"\n🎯 EXTRACTION RESULTS:")
        print(f"📋 Technical Skills ({len(skills['technical_skills'])}): {skills['technical_skills']}")
        print(f"🤝 Soft Skills ({len(skills['soft_skills'])}): {skills['soft_skills']}")
        print(f"🏢 Domain Skills ({len(skills['domain_skills'])}): {skills['domain_skills']}")
        
        return skills
        
    except Exception as e:
        print(f"❌ Error extracting skills: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_jd_extraction():
    """Test skill extraction on a sample JD"""
    sample_jd = """
    Data Analyst Position
    
    We are seeking a skilled Data Analyst to join our team. The ideal candidate will have:
    
    Required Skills:
    - Proficiency in Python and SQL
    - Experience with Tableau and Power BI
    - Strong analytical and problem-solving skills
    - Excellent communication abilities
    - Knowledge of statistical analysis
    
    Preferred Skills:
    - AWS or Azure cloud experience
    - Machine learning knowledge
    - Agile methodology experience
    - Financial services domain knowledge
    
    Responsibilities:
    - Analyze large datasets to identify trends
    - Create dashboards and reports
    - Collaborate with cross-functional teams
    - Present findings to stakeholders
    """
    
    print(f"\n=== TESTING JD SKILL EXTRACTION ===")
    
    try:
        skills = extract_skills_unified(sample_jd)
        
        print(f"\n🎯 JD EXTRACTION RESULTS:")
        print(f"📋 Technical Skills ({len(skills['technical_skills'])}): {skills['technical_skills']}")
        print(f"🤝 Soft Skills ({len(skills['soft_skills'])}): {skills['soft_skills']}")
        print(f"🏢 Domain Skills ({len(skills['domain_skills'])}): {skills['domain_skills']}")
        
        return skills
        
    except Exception as e:
        print(f"❌ Error extracting JD skills: {e}")
        return None

if __name__ == "__main__":
    # Test CV extraction
    cv_skills = test_cv_extraction("maheshwor_tiwari.pdf")
    
    # Test JD extraction
    jd_skills = test_jd_extraction()
    
    # Compare results
    if cv_skills and jd_skills:
        print(f"\n📊 COMPARISON SUMMARY:")
        print(f"CV Technical Skills: {len(cv_skills['technical_skills'])}")
        print(f"JD Technical Skills: {len(jd_skills['technical_skills'])}")
        print(f"CV Soft Skills: {len(cv_skills['soft_skills'])}")
        print(f"JD Soft Skills: {len(jd_skills['soft_skills'])}")
        print(f"CV Domain Skills: {len(cv_skills['domain_skills'])}")
        print(f"JD Domain Skills: {len(jd_skills['domain_skills'])}") 