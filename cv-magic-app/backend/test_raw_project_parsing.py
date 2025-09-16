#!/usr/bin/env python3
"""
Test script to verify bullet point extraction from raw CV project section
"""

import json
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.structured_cv_parser import structured_cv_parser

def test_with_raw_cv_text():
    """Test with the actual raw CV project section"""
    
    # Raw project text from the CV (as it appears in original_cv.txt)
    raw_project_section = """Heart Attack Risk Prediction (Grade of 37/40) 	Oct 2024
Implemented logistic regression, random forests, and deep learning models to predict heart attack risks.
Addressed imbalanced datasets using undersampling techniques to enhance prediction reliability.
Presented findings through clear, data-driven visualisations to support decision-making."""

    print("=== Testing Raw Project Section ===")
    print(f"Raw project text:\n{raw_project_section}\n")
    
    # Test the bullet point extraction method on individual lines
    lines = raw_project_section.split('\n')[1:]  # Skip project title line
    combined_description = "\n".join(lines)
    
    print(f"Description lines:\n{combined_description}\n")
    
    bullet_points = structured_cv_parser._extract_bullet_points_from_text(combined_description)
    
    print(f"Extracted bullet points ({len(bullet_points)}):")
    for i, bullet in enumerate(bullet_points, 1):
        print(f"  {i}. {bullet}")
    
    return bullet_points

def test_individual_lines():
    """Test bullet extraction on individual project description lines"""
    
    project_lines = [
        "Implemented logistic regression, random forests, and deep learning models to predict heart attack risks.",
        "Addressed imbalanced datasets using undersampling techniques to enhance prediction reliability.", 
        "Presented findings through clear, data-driven visualisations to support decision-making."
    ]
    
    print("\n=== Testing Individual Lines ===")
    
    all_bullets = []
    for i, line in enumerate(project_lines, 1):
        print(f"\nLine {i}: {line}")
        bullets = structured_cv_parser._extract_bullet_points_from_text(line)
        print(f"  Bullets extracted: {bullets}")
        all_bullets.extend(bullets)
    
    print(f"\nTotal bullets from all lines: {len(all_bullets)}")
    for i, bullet in enumerate(all_bullets, 1):
        print(f"  {i}. {bullet}")
    
    return all_bullets

def simulate_correct_project_parsing():
    """Simulate how project parsing should work with the updated logic"""
    
    print("\n=== Simulating Correct Project Parsing ===")
    
    # Simulate the project data structure that should be created
    project_entry = {
        "name": "Heart Attack Risk Prediction",
        "duration": "Oct 2024",
        "company": "Charles Darwin University",
        "description": "",
        "bullet_points": [],
        "technologies": ["Deep Learning", "Logistic Regression", "Random Forest"],
        "achievements": ["Grade: 37/40"],
        "url": ""
    }
    
    # Description parts (as they would appear in the parsing process)
    description_parts = [
        "Implemented logistic regression, random forests, and deep learning models to predict heart attack risks.",
        "Addressed imbalanced datasets using undersampling techniques to enhance prediction reliability.",
        "Presented findings through clear, data-driven visualisations to support decision-making."
    ]
    
    print(f"Description parts ({len(description_parts)}):")
    for i, part in enumerate(description_parts, 1):
        print(f"  {i}. {part}")
    
    # Extract bullet points from combined description parts
    combined_text = "\n".join(description_parts)
    bullet_points = structured_cv_parser._extract_bullet_points_from_text(combined_text)
    
    project_entry["bullet_points"] = bullet_points
    
    # For description, we could use a summary or first bullet
    if bullet_points:
        project_entry["description"] = bullet_points[0][:100] + "..." if len(bullet_points[0]) > 100 else bullet_points[0]
    
    print(f"\nFinal project structure:")
    print(json.dumps(project_entry, indent=2))
    
    return project_entry

if __name__ == "__main__":
    print("🚀 Testing Raw Project Parsing for Bullet Points")
    print("=" * 60)
    
    # Test with raw CV text
    test_with_raw_cv_text()
    
    # Test individual lines
    test_individual_lines() 
    
    # Simulate correct parsing
    simulate_correct_project_parsing()
    
    print(f"\n🎉 All tests completed!")