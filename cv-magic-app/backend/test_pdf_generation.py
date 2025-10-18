#!/usr/bin/env python3
"""
Test script to generate PDF from existing CV JSON and compare contents
"""

import json
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

from app.tailored_cv.services.pdf_export_service import export_tailored_cv_pdf
from app.tailored_cv.services.tailored_cv_adapter import load_tailored_cv_and_convert
from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
from app.tailored_cv.models.cv_models import TailoredCV, ContactInfo, ExperienceEntry, SkillCategory, OptimizationStrategy


def test_pdf_generation():
    """Test PDF generation from existing CV JSON"""
    
    print("🧪 PDF Generation Test")
    print("=" * 50)
    
    # Path to existing tailored CV JSON
    json_path = "/app/user/mahesh@gmail.com/cv-analysis/cvs/tailored/Australia_for_UNHCR_tailored_cv_20251017_234250.json"
    
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return False
    
    print(f"📄 Loading JSON from: {json_path}")
    
    # Load the JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print("✅ JSON loaded successfully")
    print(f"📊 JSON structure:")
    print(f"  - Contact: {json_data.get('contact', {}).get('name', 'N/A')}")
    print(f"  - Experience entries: {len(json_data.get('experience', []))}")
    print(f"  - Skills categories: {len(json_data.get('skills', []))}")
    print(f"  - Education entries: {len(json_data.get('education', []))}")
    
    # Display skills structure
    skills = json_data.get('skills', [])
    print(f"\n🎯 Skills Structure:")
    for i, skill_category in enumerate(skills):
        if isinstance(skill_category, dict):
            category = skill_category.get('category', 'Unknown')
            skills_list = skill_category.get('skills', [])
            print(f"  {i+1}. {category}: {len(skills_list)} skills")
            print(f"     Skills: {', '.join(skills_list[:3])}{'...' if len(skills_list) > 3 else ''}")
    
    # Test the adapter
    print(f"\n🔄 Testing Adapter...")
    try:
        pdf_data = load_tailored_cv_and_convert(json_path)
        print("✅ Adapter conversion successful")
        print(f"📊 Adapter output structure:")
        print(f"  - Skills keys: {list(pdf_data.get('skills', {}).keys())}")
        print(f"  - Is categorized: {pdf_data.get('skills', {}).get('is_categorized', 'NOT SET')}")
        
        # Show skills in adapter output
        skills_data = pdf_data.get('skills', {})
        if skills_data.get('is_categorized'):
            print(f"  - Categorized skills:")
            for key, value in skills_data.items():
                if key != 'is_categorized' and isinstance(value, list):
                    print(f"    {key}: {len(value)} skills")
        else:
            technical_skills = skills_data.get('technical_skills', [])
            print(f"  - Technical skills: {len(technical_skills)} skills")
            print(f"    Skills: {', '.join(technical_skills[:5])}{'...' if len(technical_skills) > 5 else ''}")
            
    except Exception as e:
        print(f"❌ Adapter conversion failed: {e}")
        return False
    
    # Test PDF generation
    print(f"\n📄 Testing PDF Generation...")
    try:
        # Create test export directory
        export_dir = Path("/tmp/test_pdf_export")
        export_dir.mkdir(exist_ok=True)
        
        # Generate PDF
        pdf_path = export_tailored_cv_pdf('mahesh@gmail.com', 'Australia_for_UNHCR', export_dir)
        
        print("✅ PDF generation successful")
        print(f"📁 PDF saved to: {pdf_path}")
        print(f"📊 PDF size: {pdf_path.stat().st_size} bytes")
        
        # Verify PDF exists and has content
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            print("✅ PDF file is valid and has content")
        else:
            print("❌ PDF file is empty or invalid")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test text conversion for comparison
    print(f"\n📝 Testing Text Conversion...")
    try:
        # Create a minimal TailoredCV object for text conversion
        optimization_strategy = OptimizationStrategy(
            section_order=[],
            education_strategy="",
            keyword_placement={},
            quantification_targets=[],
            impact_enhancements={}
        )
        
        tailored_cv = TailoredCV(
            contact=ContactInfo(**json_data['contact']),
            education=json_data.get('education', []),
            experience=[ExperienceEntry(**exp) for exp in json_data.get('experience', [])],
            skills=[SkillCategory(**skill) for skill in json_data.get('skills', [])],
            target_company='Australia_for_UNHCR',
            target_role='Data Analyst',
            optimization_strategy=optimization_strategy,
            enhancements_applied={},
            keywords_integrated=[],
            quantifications_added=[]
        )
        
        # Convert to text
        service = CVTailoringService(user_email='mahesh@gmail.com')
        text_content = service._convert_tailored_cv_to_text(tailored_cv)
        
        print("✅ Text conversion successful")
        print(f"📊 Text content length: {len(text_content)} characters")
        
        # Show first few lines of text content
        lines = text_content.split('\n')
        print(f"📝 First 10 lines of text content:")
        for i, line in enumerate(lines[:10]):
            print(f"  {i+1:2d}: {line}")
        
        # Save text content for comparison
        text_file = export_dir / "test_text_content.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"💾 Text content saved to: {text_file}")
        
    except Exception as e:
        print(f"❌ Text conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n🎉 All tests passed!")
    print(f"📁 Test files created in: {export_dir}")
    print(f"  - PDF: {pdf_path.name}")
    print(f"  - Text: test_text_content.txt")
    
    return True


if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
