"""
Test script for timestamp-aware file selection
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from app.services.enhanced_cv_upload_service_v2 import enhanced_cv_upload_service_v2
from app.services.enhanced_dynamic_cv_selector_v2 import enhanced_dynamic_cv_selector_v2


async def test_cv_upload_and_selection():
    """Test CV upload with timestamps and file selection"""
    company = "Australia_for_UNHCR"
    test_results = {}
    
    print("\nTesting CV file system with timestamps:")
    print("=" * 50)
    
    try:
        # Step 1: Get initial files
        print("\n1. Getting current CV files:")
        initial_files = enhanced_dynamic_cv_selector_v2.get_cv_files(company)
        print("Initial files:")
        print(json.dumps(initial_files.to_dict(), indent=2))
        
        # Step 2: Get all available versions
        print("\n2. Getting all CV versions:")
        all_versions = enhanced_dynamic_cv_selector_v2.get_all_cv_versions(company)
        print(f"Found {len(all_versions)} versions:")
        for version in all_versions:
            print(f"- {version['type']} version {version['version']} from {version['timestamp']}")
        
        # Step 3: Test file selection with preferences
        print("\n3. Testing file selection with preferences:")
        
        # Original preferred
        original_selection = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            prefer_tailored=False
        )
        print("\nOriginal preferred:")
        print(json.dumps(original_selection.to_dict(), indent=2))
        
        # Tailored preferred
        tailored_selection = enhanced_dynamic_cv_selector_v2.get_cv_files(
            company=company,
            prefer_tailored=True
        )
        print("\nTailored preferred:")
        print(json.dumps(tailored_selection.to_dict(), indent=2))
        
        # Step 4: Verify file existence
        print("\n4. Verifying file existence:")
        files_to_check = [
            (original_selection.json_path, "Original JSON"),
            (original_selection.txt_path, "Original TXT"),
            (tailored_selection.json_path, "Tailored JSON"),
            (tailored_selection.txt_path, "Tailored TXT")
        ]
        
        for file_path, file_type in files_to_check:
            if file_path and file_path.exists():
                size = file_path.stat().st_size
                modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                print(f"{file_type}: {file_path.name}")
                print(f"  Size: {size} bytes")
                print(f"  Modified: {modified}")
            else:
                print(f"{file_type}: Not found")
        
        test_results["success"] = True
        test_results["message"] = "All tests completed"
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        test_results["success"] = False
        test_results["error"] = str(e)
    
    print("\nTest Results:")
    print("=" * 50)
    print(json.dumps(test_results, indent=2))


if __name__ == "__main__":
    asyncio.run(test_cv_upload_and_selection())