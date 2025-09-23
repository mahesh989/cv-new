"""
Test CV error handling
"""

import asyncio
from pathlib import Path
from app.services.enhanced_dynamic_cv_selector_v2 import enhanced_dynamic_cv_selector_v2
from app.exceptions.cv_exceptions import (
    CVError, CVNotFoundError, EmptyContentError,
    CVFormatError, CVVersionError, CVSelectionError
)

def print_section(title: str):
    """Print a section header"""
    print(f"\n{title}")
    print("=" * len(title))

async def test_cv_error_handling():
    """Test error handling in CV selection"""
    company = "Australia_for_UNHCR"
    test_cases = []
    
    print_section("Testing CV Error Handling")
    
    # Test Case 1: Non-existent company
    print_section("Test 1: Non-existent company")
    try:
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company="NonExistentCompany",
            strict=True
        )
        print("❌ Should have raised CVNotFoundError")
    except CVNotFoundError as e:
        print(f"✅ Correctly raised CVNotFoundError: {str(e)}")
    except Exception as e:
        print(f"❌ Wrong error type: {type(e).__name__}")
    
    # Test Case 2: Missing TXT file
    print_section("Test 2: Missing text file")
    try:
        # Create JSON without TXT
test_json = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs/original/test_cv_20250922_235959.json")
        test_json.parent.mkdir(parents=True, exist_ok=True)
test_json.write_text('{"metadata": {}, "personal_information": {}, "experience": []}')
        
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            strict=True
        )
        print("❌ Should have raised CVFormatError")
    except CVFormatError as e:
        print(f"✅ Correctly raised CVFormatError: {str(e)}")
    except Exception as e:
        print(f"❌ Wrong error type: {type(e).__name__}")
    finally:
        if test_json.exists():
            test_json.unlink()
    
    # Test Case 3: Empty content
    print_section("Test 3: Empty content")
    try:
        # Create empty files
test_json = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs/original/test_cv_20250922_235959.json")
        test_txt = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs/original/test_cv_20250922_235959.txt")
        test_json.parent.mkdir(parents=True, exist_ok=True)
        test_json.write_text("{}")
        test_txt.write_text("")
        
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            strict=True
        )
        print("❌ Should have raised EmptyContentError")
    except EmptyContentError as e:
        print(f"✅ Correctly raised EmptyContentError: {str(e)}")
    except Exception as e:
        print(f"❌ Wrong error type: {type(e).__name__}")
    finally:
        if test_json.exists():
            test_json.unlink()
        if test_txt.exists():
            test_txt.unlink()
    
    # Test Case 4: Invalid JSON format
    print_section("Test 4: Invalid JSON format")
    try:
        # Create invalid JSON
test_json = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs/original/test_cv_20250922_235959.json")
        test_txt = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs/original/test_cv_20250922_235959.txt")
        test_json.parent.mkdir(parents=True, exist_ok=True)
        test_json.write_text("{ invalid json }")
        test_txt.write_text("Some CV content")
        
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            strict=True
        )
        print("❌ Should have raised CVFormatError")
    except CVFormatError as e:
        print(f"✅ Correctly raised CVFormatError: {str(e)}")
    except Exception as e:
        print(f"❌ Wrong error type: {type(e).__name__}")
    finally:
        if test_json.exists():
            test_json.unlink()
        if test_txt.exists():
            test_txt.unlink()
    
    # Test Case 5: Invalid timestamp format
    print_section("Test 5: Invalid timestamp format")
    try:
        # Create file with invalid timestamp
test_json = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs/original/test_cv.json")
        test_txt = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/cvs/original/test_cv.txt")
        test_json.parent.mkdir(parents=True, exist_ok=True)
        test_json.write_text("{}")
        test_txt.write_text("Some CV content")
        
        cv_files = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            strict=True
        )
        print("❌ Should have raised CVVersionError")
    except CVVersionError as e:
        print(f"✅ Correctly raised CVVersionError: {str(e)}")
    except Exception as e:
        print(f"❌ Wrong error type: {type(e).__name__}")
    finally:
        if test_json.exists():
            test_json.unlink()
        if test_txt.exists():
            test_txt.unlink()

if __name__ == "__main__":
    asyncio.run(test_cv_error_handling())