"""
Test Enhanced CV Selector

Tests the enhanced CV selector with proper timestamp handling
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from app.services.enhanced_dynamic_cv_selector_v2 import enhanced_dynamic_cv_selector_v2
from app.errors.cv_errors import CVNotFoundError, CVFormatError, CVVersionError


def print_section(title):
    """Print a test section header"""
    print(f"\n{title}\n{'=' * len(title)}\n")


def get_test_paths(company: str):
    """Get test file paths for a company"""
    base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs") / company
    return [
        base_dir / "original" / "test_cv_20250922_235959.json",
        base_dir / "original" / "test_cv_20250922_235959.txt",
        base_dir / "original" / "test_cv.json",
        base_dir / "original" / "test_cv.txt",
        base_dir / "tailored" / "test_cv.json",
        base_dir / "tailored" / "test_cv.txt"
    ]


def cleanup_test_files():
    """Remove test files"""
    company = "Australia_for_UNHCR"
    test_paths = get_test_paths(company)
    
    # Create test directories
    for path in test_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        
    # Clean up test files
    for path in test_paths:
        if path.exists():
            path.unlink()
    
    for path in test_paths:
        test_file = Path(path)
        if test_file.exists():
            test_file.unlink()


def create_test_cv(is_timestamped: bool = True, valid_timestamp: bool = True):
    """Create test CV files
    
    Args:
        is_timestamped: Whether to create timestamped files
        valid_timestamp: Whether to use valid timestamp format
    """
    company = "Australia_for_UNHCR"
    base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs") / company / "original"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp suffix
    if is_timestamped:
        if valid_timestamp:
            timestamp_suffix = "_20250922_235959"
        else:
            timestamp_suffix = "_invalid_ts"
    else:
        timestamp_suffix = ""
    
    # Create files
    base_json = base_dir / f"test_cv{timestamp_suffix}.json"
    base_txt = base_dir / f"test_cv{timestamp_suffix}.txt"
    
    # Create valid JSON structure
    json_data = {
        "metadata": {
            "version": "1.0",
            "type": "original"
        },
        "personal_information": {
            "name": "Test User",
            "email": "test@example.com"
        },
        "experience": [
            {
                "title": "Test Role",
                "company": "Test Company"
            }
        ]
    }
    
    # Add timestamp if needed
    if is_timestamped and valid_timestamp:
        json_data["metadata"]["timestamp"] = "2025-09-22T23:59:59Z"
    elif is_timestamped:
        json_data["metadata"]["timestamp"] = "invalid"
    
    base_json.write_text(json.dumps(json_data, indent=4))
    
    # Create TXT content
    base_txt.write_text('\n'.join([
        "Personal Information",
        "====================",
        "Name: Test User",
        "Email: test@example.com",
        "",
        "Experience",
        "==========",
        "Test Role at Test Company",
        "",
        "Education",
        "=========",
        "Test University",
        "",
        "Skills",
        "======",
        "- Test Skill 1",
        "- Test Skill 2"
    ]))
    company = "Australia_for_UNHCR"
    base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs") / company / "original"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped files
    base_json = base_dir / "test_cv_20250922_235959.json"
    base_txt = base_dir / "test_cv_20250922_235959.txt"
    
    # Valid JSON structure
    base_json.write_text(json.dumps({
        "metadata": {
            "version": "1.0",
            "type": "original",
            "timestamp": "2025-09-22T23:59:59Z"
        },
        "personal_information": {
            "name": "Base User",
            "email": "base@example.com"
        },
        "experience": [
            {
                "title": "Base Role",
                "company": "Base Company"
            }
        ]
    }, indent=4))
    
    # Valid TXT content
    base_txt.write_text('\n'.join([
        "Personal Information",
        "====================",
        "Name: Base User",
        "Email: base@example.com",
        "",
        "Experience",
        "==========",
        "Base Role at Base Company",
        "",
        "Education",
        "=========",
        "Base University",
        "",
        "Skills",
        "======",
        "- Base Skill 1",
        "- Base Skill 2"
    ]))


async def test_enhanced_cv_selector():
    """Test enhanced CV selector with proper timestamp handling"""
    print("\nTesting Enhanced CV Selector\n=========================\n")
    
    company = "Australia_for_UNHCR"
    
    # Test Case 1: Valid timestamped files
    print_section("Test 1: Valid timestamped files")
    try:
        # Create valid timestamped CV
        create_test_cv(is_timestamped=True, valid_timestamp=True)
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            strict=True
        )
        if cv_files.exists and cv_files.timestamp:
            print("✅ Successfully loaded timestamped CV files")
            print(f"Timestamp: {cv_files.timestamp}")
        else:
            print("❌ Failed to load timestamped CV files")
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
    
    # Test Case 2: Non-timestamped files
    print_section("Test 2: Non-timestamped files")
    try:
        # Create non-timestamped files
        create_test_cv(is_timestamped=False)
        
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            strict=True
        )
        
        if cv_files.exists:
            print("✅ Successfully handled non-timestamped files")
            print(f"Version: {cv_files.version}")
        else:
            print("❌ Failed to handle non-timestamped files")
            
    except CVVersionError as e:
        print(f"✅ Correctly raised CVVersionError: {str(e)}")
    except Exception as e:
        print(f"❌ Wrong error type: {type(e).__name__}")
        
    # Test Case 3: Invalid timestamp format
    print_section("Test 3: Invalid timestamp format")
    try:
        # Create file with invalid timestamp
        create_test_cv(is_timestamped=True, valid_timestamp=False)
        
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            strict=True
        )
        print("❌ Should have raised CVVersionError")
    except CVVersionError as e:
        print(f"✅ Correctly raised CVVersionError: {str(e)}")
    except Exception as e:
        print(f"❌ Wrong error type: {type(e).__name__}")


if __name__ == "__main__":
    try:
        # Clean up any existing test files
        cleanup_test_files()
        
        # Run tests
        asyncio.run(test_enhanced_cv_selector())
    finally:
        # Clean up after tests
        cleanup_test_files()