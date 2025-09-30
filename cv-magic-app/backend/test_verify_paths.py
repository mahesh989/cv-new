"""Test the path verifier during analysis"""

from pathlib import Path
from app.services.path_verifier import path_verifier

def test_verify_paths():
    # Test company and paths
    company = "Test_Company_XYZ"
    user_email = "admin@admin.com"

    print("\n🔍 Testing path verification during analysis\n")

    # 1. First verify the overall structure
    path_verifier.verify_analysis_paths(company, user_email)

    # 2. Verify specific file content
    from app.utils.user_path_utils import get_user_base_path
    base_dir = get_user_base_path(user_email)

    # Check CV file content
    cv_file = base_dir / "cvs/original/original_cv.json"
    print("\n📄 Verifying CV file content:")
    path_verifier.verify_file_content(cv_file, ["text", "sections", "saved_at"])

    # Check skills analysis file content
    skills_file = next((base_dir / "applied_companies" / company).glob("*skills_analysis*.json"), None)
    if skills_file:
        print("\n📄 Verifying skills analysis content:")
        path_verifier.verify_file_content(skills_file, ["matched_skills", "missing_skills", "score"])

    print("\n✨ Path verification complete!")

if __name__ == "__main__":
    test_verify_paths()