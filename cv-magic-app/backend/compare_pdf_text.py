#!/usr/bin/env python3
"""
Script to compare PDF content with JSON text content
"""

import json
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 not available, will use alternative method")

from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
from app.tailored_cv.models.cv_models import TailoredCV, ContactInfo, ExperienceEntry, SkillCategory, OptimizationStrategy


def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    if PDF_AVAILABLE:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"❌ Error extracting PDF text: {e}")
            return None
    else:
        # Alternative: Use pdfplumber if available
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except ImportError:
            print("❌ No PDF text extraction library available")
            return None
        except Exception as e:
            print(f"❌ Error extracting PDF text: {e}")
            return None


def get_json_text_content(json_path):
    """Get text content from JSON using the same conversion as the system"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
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
        
        # Convert to text using the same service
        service = CVTailoringService(user_email='mahesh@gmail.com')
        text_content = service._convert_tailored_cv_to_text(tailored_cv)
        
        return text_content
        
    except Exception as e:
        print(f"❌ Error getting JSON text content: {e}")
        return None


def compare_content():
    """Compare PDF content with JSON text content"""
    
    print("🔍 PDF vs JSON Content Comparison")
    print("=" * 50)
    
    # Paths
    json_path = "/app/user/mahesh@gmail.com/cv-analysis/cvs/tailored/Australia_for_UNHCR_tailored_cv_20251017_234250.json"
    pdf_path = "/tmp/test_pdf_export/Australia_for_UNHCR_tailored_resume_20251018_002848.pdf"
    
    # Get JSON text content
    print("📄 Getting JSON text content...")
    json_text = get_json_text_content(json_path)
    if not json_text:
        print("❌ Failed to get JSON text content")
        return False
    
    print("✅ JSON text content retrieved")
    print(f"📊 JSON text length: {len(json_text)} characters")
    
    # Get PDF text content
    print("\n📄 Extracting PDF text content...")
    pdf_text = extract_pdf_text(pdf_path)
    if not pdf_text:
        print("❌ Failed to extract PDF text content")
        print("💡 This might be due to PDF encoding or missing libraries")
        return False
    
    print("✅ PDF text content extracted")
    print(f"📊 PDF text length: {len(pdf_text)} characters")
    
    # Compare content
    print("\n🔍 Content Comparison:")
    print("-" * 30)
    
    # Show first few lines of each
    json_lines = json_text.split('\n')
    pdf_lines = pdf_text.split('\n')
    
    print("📝 JSON Text (first 10 lines):")
    for i, line in enumerate(json_lines[:10]):
        print(f"  {i+1:2d}: {line}")
    
    print("\n📄 PDF Text (first 10 lines):")
    for i, line in enumerate(pdf_lines[:10]):
        print(f"  {i+1:2d}: {line}")
    
    # Check for key content
    print("\n🎯 Key Content Check:")
    
    # Check for contact info
    contact_checks = [
        "Maheshwor Tiwari",
        "0414 032 507", 
        "maheshtwari99@gmail.com",
        "Hurstville, NSW, 2220"
    ]
    
    for check in contact_checks:
        json_has = check in json_text
        pdf_has = check in pdf_text
        status = "✅" if json_has and pdf_has else "❌"
        print(f"  {status} Contact: '{check}' - JSON: {json_has}, PDF: {pdf_has}")
    
    # Check for skills
    skills_checks = [
        "TECHNICAL SKILLS",
        "Power BI",
        "SQL", 
        "Excel",
        "Python",
        "VBA",
        "Fundraising",
        "Humanitarian Aid"
    ]
    
    for check in skills_checks:
        json_has = check in json_text
        pdf_has = check in pdf_text
        status = "✅" if json_has and pdf_has else "❌"
        print(f"  {status} Skills: '{check}' - JSON: {json_has}, PDF: {pdf_has}")
    
    # Check for experience
    experience_checks = [
        "EXPERIENCE",
        "Senior Data Analyst",
        "Jul 2024",
        "The Bitrates"
    ]
    
    for check in experience_checks:
        json_has = check in json_text
        pdf_has = check in pdf_text
        status = "✅" if json_has and pdf_has else "❌"
        print(f"  {status} Experience: '{check}' - JSON: {json_has}, PDF: {pdf_has}")
    
    # Overall assessment
    print(f"\n📊 Overall Assessment:")
    print(f"  - JSON text length: {len(json_text)} characters")
    print(f"  - PDF text length: {len(pdf_text)} characters")
    print(f"  - Length difference: {abs(len(json_text) - len(pdf_text))} characters")
    
    # Check if content is similar (allowing for formatting differences)
    json_words = set(json_text.lower().split())
    pdf_words = set(pdf_text.lower().split())
    
    common_words = json_words.intersection(pdf_words)
    total_words = json_words.union(pdf_words)
    
    similarity = len(common_words) / len(total_words) if total_words else 0
    
    print(f"  - Word similarity: {similarity:.2%}")
    
    if similarity > 0.8:
        print("✅ Content appears to match well!")
    elif similarity > 0.6:
        print("⚠️ Content is mostly similar with some differences")
    else:
        print("❌ Content appears to be significantly different")
    
    return True


if __name__ == "__main__":
    success = compare_content()
    sys.exit(0 if success else 1)
