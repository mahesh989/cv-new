"""Test real analysis to verify path structure in practice"""

import json
from pathlib import Path
from datetime import datetime

def test_real_analysis():
    # Test company and content
    company = "Test_Analysis_Company"
    test_data = {
        "test": True,
        "timestamp": datetime.now().isoformat(),
        "content": "Test analysis content"
    }

    # 1. Get paths from utility
    from app.utils.user_path_utils import get_user_base_path, get_user_company_analysis_paths
    base_dir = get_user_base_path("test@example.com")
    paths = get_user_company_analysis_paths("test@example.com", company)

    # 2. Create test analysis files
    from app.utils.timestamp_utils import TimestampUtils
    timestamp = TimestampUtils.get_timestamp()

    # Create and verify each analysis file
    for file_type, path_fn in paths.items():
        file_path = path_fn(timestamp)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print(f"✅ Created: {file_path}")
        
        # Verify file exists and has correct structure
        assert file_path.exists(), f"File not created: {file_path}"
        assert "user_test@example.com/cv-analysis" in str(file_path), f"Wrong path structure: {file_path}"
        assert TimestampUtils.is_timestamped_filename(file_path.name), f"Not timestamped: {file_path.name}"

    print("\n✨ Real analysis test passed - all files created with correct structure!")

if __name__ == "__main__":
    try:
        test_real_analysis()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Error running tests: {e}")