#!/usr/bin/env python3
"""
Test script to verify bullet point extraction from project descriptions
"""

import json
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.structured_cv_parser import structured_cv_parser

def test_bullet_point_extraction():
    """Test bullet point extraction with sample project text"""
    
    # Sample project description text (similar to what's in the CV)
    project_text = """Implemented logistic regression, random forests, and deep learning models to predict heart attack risks.
Addressed imbalanced datasets using undersampling techniques to enhance prediction reliability.
Presented findings through clear, data-driven visualisations to support decision-making."""
    
    print("=== Testing Bullet Point Extraction ===")
    print(f"Input text:\n{project_text}\n")
    
    # Test the bullet point extraction method
    bullet_points = structured_cv_parser._extract_bullet_points_from_text(project_text)
    
    print(f"Extracted bullet points ({len(bullet_points)}):")
    for i, bullet in enumerate(bullet_points, 1):
        print(f"  {i}. {bullet}")
    
    return bullet_points

def reprocess_existing_cv():
    """Reprocess existing CV to add bullet points to projects"""
    
    print("\n=== Reprocessing Existing CV ===")
    
    # Load current CV
    cv_path = Path("cv-analysis/original_cv.json")
    if not cv_path.exists():
        print(f"❌ CV file not found: {cv_path}")
        return
    
    print(f"📖 Loading CV from: {cv_path}")
    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_data = json.load(f)
    
    # Process projects to add bullet points
    if 'projects' in cv_data and cv_data['projects']:
        print(f"📋 Processing {len(cv_data['projects'])} project(s)...")
        
        for i, project in enumerate(cv_data['projects']):
            project_name = project.get('name', f'Project {i+1}')
            print(f"\n🔧 Processing: {project_name}")
            
            description = project.get('description', '')
            if description:
                # Extract bullet points from description
                bullet_points = structured_cv_parser._extract_bullet_points_from_text(description)
                
                print(f"  📝 Original description: {description[:80]}...")
                print(f"  📃 Extracted {len(bullet_points)} bullet point(s):")
                
                for j, bullet in enumerate(bullet_points, 1):
                    print(f"     {j}. {bullet}")
                
                # Add bullet_points field if not exists
                if 'bullet_points' not in project:
                    project['bullet_points'] = []
                
                # Update with extracted bullet points
                project['bullet_points'] = bullet_points
                
                print(f"  ✅ Updated project with {len(bullet_points)} bullet points")
            else:
                print(f"  ⚠️  No description found for {project_name}")
    
    # Save updated CV
    backup_path = cv_path.with_suffix('.backup.json')
    print(f"\n💾 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(cv_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saving updated CV: {cv_path}")
    with open(cv_path, 'w', encoding='utf-8') as f:
        json.dump(cv_data, f, indent=2, ensure_ascii=False)
    
    print("✅ CV processing completed!")

def verify_updated_projects():
    """Verify the updated projects have bullet points"""
    
    print("\n=== Verifying Updated Projects ===")
    
    cv_path = Path("cv-analysis/original_cv.json")
    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_data = json.load(f)
    
    if 'projects' in cv_data:
        for i, project in enumerate(cv_data['projects']):
            name = project.get('name', f'Project {i+1}')
            bullet_points = project.get('bullet_points', [])
            
            print(f"\n📋 {name}:")
            print(f"   Company: {project.get('company', 'N/A')}")
            print(f"   Duration: {project.get('duration', 'N/A')}")
            print(f"   Description: {project.get('description', 'N/A')}")
            print(f"   Bullet Points ({len(bullet_points)}):")
            
            if bullet_points:
                for j, bullet in enumerate(bullet_points, 1):
                    print(f"     • {bullet}")
            else:
                print("     (No bullet points)")
            
            technologies = project.get('technologies', [])
            if technologies:
                print(f"   Technologies: {', '.join(technologies)}")
    
    print(f"\n✅ Verification completed!")

if __name__ == "__main__":
    print("🚀 Testing Bullet Point Extraction for CV Projects")
    print("=" * 60)
    
    # Test the bullet extraction method
    test_bullet_point_extraction()
    
    # Reprocess existing CV
    reprocess_existing_cv()
    
    # Verify results
    verify_updated_projects()
    
    print(f"\n🎉 All tests completed!")