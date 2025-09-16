#!/usr/bin/env python3
"""
Script to reprocess CV from original text to extract proper bullet points
"""

import json
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.structured_cv_parser import structured_cv_parser

def reprocess_cv_from_original_text():
    """Reprocess the entire CV from original text to get proper bullet points"""
    
    print("=== Reprocessing CV from Original Text ===")
    
    # Load the original CV text
    original_txt_path = Path("cv-analysis/original_cv.txt")
    if not original_txt_path.exists():
        print(f"❌ Original CV text file not found: {original_txt_path}")
        return
    
    print(f"📖 Loading original CV text: {original_txt_path}")
    with open(original_txt_path, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    # Parse the entire CV from scratch with updated logic
    print("🔧 Parsing CV with updated bullet point extraction...")
    structured_cv = structured_cv_parser.parse_cv_content(original_text)
    
    # Save the newly parsed CV
    new_cv_path = Path("cv-analysis/original_cv.json")
    backup_path = Path("cv-analysis/original_cv.pre-bullet-update.backup.json")
    
    # Create backup of existing CV
    if new_cv_path.exists():
        print(f"💾 Creating backup of existing CV: {backup_path}")
        with open(new_cv_path, 'r', encoding='utf-8') as f:
            existing_cv = json.load(f)
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(existing_cv, f, indent=2, ensure_ascii=False)
    
    # Save the newly parsed CV
    print(f"💾 Saving newly parsed CV: {new_cv_path}")
    with open(new_cv_path, 'w', encoding='utf-8') as f:
        json.dump(structured_cv, f, indent=2, ensure_ascii=False)
    
    print("✅ CV reprocessing completed!")
    return structured_cv

def analyze_projects_improvements(cv_data):
    """Analyze the improvements in project parsing"""
    
    print(f"\n=== Project Parsing Analysis ===")
    
    projects = cv_data.get('projects', [])
    print(f"📋 Found {len(projects)} project(s):")
    
    for i, project in enumerate(projects, 1):
        name = project.get('name', f'Project {i}')
        bullet_points = project.get('bullet_points', [])
        technologies = project.get('technologies', [])
        
        print(f"\n{i}. {name}:")
        print(f"   Company: {project.get('company', 'N/A')}")
        print(f"   Duration: {project.get('duration', 'N/A')}")
        print(f"   Technologies: {', '.join(technologies) if technologies else 'None'}")
        print(f"   Bullet Points ({len(bullet_points)}):")
        
        if bullet_points:
            for j, bullet in enumerate(bullet_points, 1):
                print(f"     • {bullet}")
        else:
            print("     (No bullet points found)")
        
        # Show original description for comparison
        description = project.get('description', '')
        if description:
            print(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")

def verify_all_sections(cv_data):
    """Verify all sections of the CV"""
    
    print(f"\n=== Complete CV Structure Verification ===")
    
    sections = [
        'personal_information', 'career_profile', 'technical_skills', 
        'education', 'experience', 'projects', 'certifications'
    ]
    
    for section in sections:
        if section in cv_data and cv_data[section]:
            data = cv_data[section]
            if isinstance(data, list):
                count = len(data)
                print(f"✅ {section}: {count} items")
            elif isinstance(data, dict):
                if section == 'personal_information':
                    name = data.get('name', 'N/A')
                    email = data.get('email', 'N/A')
                    print(f"✅ {section}: {name} ({email})")
                elif section == 'career_profile':
                    summary_length = len(data.get('summary', ''))
                    print(f"✅ {section}: {summary_length} characters")
                else:
                    print(f"✅ {section}: Available")
            else:
                print(f"✅ {section}: Available")
        else:
            print(f"❌ {section}: Missing or empty")

if __name__ == "__main__":
    print("🚀 Reprocessing CV with Bullet Point Extraction")
    print("=" * 60)
    
    # Reprocess CV from original text
    structured_cv = reprocess_cv_from_original_text()
    
    if structured_cv:
        # Analyze project improvements
        analyze_projects_improvements(structured_cv)
        
        # Verify all sections
        verify_all_sections(structured_cv)
    
    print(f"\n🎉 CV reprocessing completed!")