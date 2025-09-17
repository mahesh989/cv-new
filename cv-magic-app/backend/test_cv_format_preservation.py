#!/usr/bin/env python3
"""
Test script to verify that CVs are always saved in the correct structured JSON format
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def verify_cv_format(cv_path: str) -> Dict[str, Any]:
    """
    Verify that a CV file is in the correct structured JSON format
    
    Args:
        cv_path: Path to the CV JSON file
        
    Returns:
        Dictionary with validation results
    """
    results = {
        "valid_json": False,
        "has_correct_structure": False,
        "required_fields": [],
        "missing_fields": [],
        "format_version": None,
        "errors": []
    }
    
    try:
        # Check if file exists
        if not Path(cv_path).exists():
            results["errors"].append(f"File not found: {cv_path}")
            return results
            
        # Try to load as JSON
        with open(cv_path, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
        
        results["valid_json"] = True
        
        # Check for required top-level fields
        required_fields = [
            "personal_information",
            "career_profile",
            "technical_skills",
            "education",
            "experience",
            "projects",
            "certifications",
            "soft_skills",
            "domain_expertise",
            "languages",
            "awards",
            "publications",
            "volunteer_work",
            "professional_memberships",
            "unknown_sections",
            "saved_at",
            "metadata"
        ]
        
        for field in required_fields:
            if field in cv_data:
                results["required_fields"].append(field)
            else:
                results["missing_fields"].append(field)
        
        # Check if it has the correct structure (not raw text)
        if "text" in cv_data and len(cv_data) == 2:
            # This is the OLD format (raw text)
            results["has_correct_structure"] = False
            results["errors"].append("CV is in old raw text format, not structured format")
        elif "personal_information" in cv_data:
            # This is the correct structured format
            results["has_correct_structure"] = True
            
            # Check personal_information structure
            personal_info = cv_data.get("personal_information", {})
            if isinstance(personal_info, dict):
                if "name" in personal_info and "email" in personal_info:
                    results["personal_info_valid"] = True
                else:
                    results["errors"].append("personal_information missing required fields (name, email)")
            
            # Check if experience is an array
            if isinstance(cv_data.get("experience", []), list):
                results["experience_format_valid"] = True
            else:
                results["errors"].append("experience field is not an array")
            
            # Check if education is an array
            if isinstance(cv_data.get("education", []), list):
                results["education_format_valid"] = True
            else:
                results["errors"].append("education field is not an array")
            
            # Check metadata
            metadata = cv_data.get("metadata", {})
            if metadata:
                results["format_version"] = metadata.get("processing_version", "Unknown")
        
        # Calculate completeness score
        completeness = (len(results["required_fields"]) / len(required_fields)) * 100
        results["completeness_percentage"] = round(completeness, 2)
        
    except json.JSONDecodeError as e:
        results["errors"].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        results["errors"].append(f"Error reading file: {str(e)}")
    
    return results


def main():
    """Main test function"""
    print("=" * 60)
    print("CV Format Preservation Test")
    print("=" * 60)
    
    # Test the original_cv.json file
    original_cv_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/original_cv.json"
    
    print(f"\nTesting: {original_cv_path}")
    print("-" * 40)
    
    results = verify_cv_format(original_cv_path)
    
    # Display results
    print(f"✓ Valid JSON: {results['valid_json']}")
    print(f"✓ Correct Structure: {results['has_correct_structure']}")
    print(f"✓ Format Version: {results['format_version']}")
    print(f"✓ Completeness: {results.get('completeness_percentage', 0)}%")
    
    if results["required_fields"]:
        print(f"\n✓ Fields Present ({len(results['required_fields'])}):")
        for field in results["required_fields"][:5]:  # Show first 5
            print(f"  - {field}")
        if len(results["required_fields"]) > 5:
            print(f"  ... and {len(results['required_fields']) - 5} more")
    
    if results["missing_fields"]:
        print(f"\n⚠ Missing Fields ({len(results['missing_fields'])}):")
        for field in results["missing_fields"]:
            print(f"  - {field}")
    
    if results["errors"]:
        print(f"\n❌ Errors:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    # Overall verdict
    print("\n" + "=" * 60)
    if results["valid_json"] and results["has_correct_structure"]:
        print("✅ PASS: CV is in correct structured JSON format!")
    else:
        print("❌ FAIL: CV is NOT in correct format!")
    print("=" * 60)
    
    return results["valid_json"] and results["has_correct_structure"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)