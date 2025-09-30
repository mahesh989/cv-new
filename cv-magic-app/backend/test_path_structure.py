"""Test to verify future analysis will follow the correct path structure"""

import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_analysis_paths():
    # Test configuration
    user_email = "admin@admin.com"
    company = "Test_Company"
    timestamp = "20250929_211755"  # Using fixed timestamp for testing

    # Expected path structure - use relative path
    base_path = Path("user/user_admin@admin.com/cv-analysis")
    
    # 1. Test directory creation
    from app.utils.user_path_utils import get_user_base_path
    user_base = get_user_base_path(user_email)
    assert str(user_base) == str(base_path), f"Wrong base path: {user_base}"
    print(f"✅ Base path correct: {user_base}")

    # 2. Test company analysis paths
    from app.utils.user_path_utils import get_user_company_analysis_paths
    paths = get_user_company_analysis_paths(user_email, company)

    # Test each expected file path
    expected_files = [
        (paths["jd_original"](timestamp), f"jd_original_{timestamp}.json"),
        (paths["job_info"](timestamp), f"job_info_{company}_{timestamp}.json"),
        (paths["jd_analysis"](timestamp), f"jd_analysis_{timestamp}.json"),
        (paths["cv_jd_matching"](timestamp), f"cv_jd_matching_{timestamp}.json"),
        (paths["component_analysis"](timestamp), f"component_analysis_{timestamp}.json"),
        (paths["skills_analysis"](timestamp), f"{company}_skills_analysis_{timestamp}.json"),
        (paths["input_recommendation"](timestamp), f"{company}_input_recommendation_{timestamp}.json"),
        (paths["ai_recommendation"](timestamp), f"{company}_ai_recommendation_{timestamp}.json"),
        (paths["tailored_cv"](timestamp), f"{company}_tailored_cv_{timestamp}.json")
    ]

    for path, expected_name in expected_files:
        assert path.name == expected_name, f"Wrong filename: {path.name} != {expected_name}"
        assert "user_admin@admin.com/cv-analysis" in str(path), f"Wrong path structure: {path}"
        print(f"✅ File path correct: {path}")

    # 3. Test non-timestamped files
    from app.utils.user_cv_paths import get_user_cv_paths
    cv_paths = get_user_cv_paths(user_email)
    
    assert cv_paths["original"] / "original_cv.json" == base_path / "cvs/original/original_cv.json"
    assert cv_paths["original"] / "original_cv.txt" == base_path / "cvs/original/original_cv.txt"
    print("✅ CV paths correct")

    # 4. Test path validation
    from app.utils.path_validator import validate_file_path
    test_files = [
        base_path / "applied_companies/Test_Company/jd_original_20250929_211755.json",
        base_path / "cvs/original/original_cv.json",
        base_path / "cvs/tailored/Test_Company_tailored_cv_20250929_211755.json",
        base_path / "saved_jobs/saved_jobs.json"
    ]

    for file_path in test_files:
        assert validate_file_path(file_path, user_email), f"Invalid path: {file_path}"
        print(f"✅ Path validates: {file_path}")

    # 5. Test timestamp format
    from app.utils.timestamp_utils import TimestampUtils
    test_timestamp = TimestampUtils.get_timestamp()
    assert len(test_timestamp) == 15  # YYYYMMDD_HHMMSS
    assert "_" in test_timestamp
    print(f"✅ Timestamp format correct: {test_timestamp}")

    print("\n✨ All path structure tests passed!")

if __name__ == "__main__":
    try:
        test_analysis_paths()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Error running tests: {e}")