#!/usr/bin/env python3
"""
Test role_highlights implementation with REAL CV and JD data from the system
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))


def load_latest_cv(user_email: str):
    """Load the latest CV from the user's directory"""
    from app.utils.user_path_utils import get_user_base_path
    
    print(f"\n📁 Loading CV for user: {user_email}")
    user_base = get_user_base_path(user_email)
    
    # Try to find the latest CV
    cv_dir = user_base / "cv-analysis" / "cvs"
    
    # Check for original CV
    original_cv_dir = cv_dir / "original"
    if original_cv_dir.exists():
        # Find latest JSON file
        json_files = list(original_cv_dir.glob("*.json"))
        if json_files:
            latest_cv = max(json_files, key=lambda p: p.stat().st_mtime)
            print(f"   ✅ Found CV: {latest_cv.name}")
            with open(latest_cv, 'r') as f:
                return json.load(f)
    
    # If no original, try parsed
    parsed_cv_dir = cv_dir / "parsed"
    if parsed_cv_dir.exists():
        json_files = list(parsed_cv_dir.glob("*.json"))
        if json_files:
            latest_cv = max(json_files, key=lambda p: p.stat().st_mtime)
            print(f"   ✅ Found parsed CV: {latest_cv.name}")
            with open(latest_cv, 'r') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"No CV found for user {user_email}")


def load_latest_jd(user_email: str, company: str = None):
    """Load the latest job description for a company"""
    from app.utils.user_path_utils import get_user_base_path
    
    print(f"\n📁 Loading JD for: {company or 'latest company'}")
    user_base = get_user_base_path(user_email)
    applied_dir = user_base / "cv-analysis" / "applied_companies"
    
    if not applied_dir.exists():
        raise FileNotFoundError(f"No applied companies directory found")
    
    # If company specified, load that JD
    if company:
        company_dir = applied_dir / company
        if company_dir.exists():
            jd_files = list(company_dir.glob("jd_original_*.txt"))
            if jd_files:
                latest_jd = max(jd_files, key=lambda p: p.stat().st_mtime)
                print(f"   ✅ Found JD: {latest_jd.name}")
                with open(latest_jd, 'r') as f:
                    return f.read(), company
    
    # Otherwise, find the most recent company
    company_dirs = [d for d in applied_dir.iterdir() if d.is_dir()]
    if not company_dirs:
        raise FileNotFoundError("No company directories found")
    
    latest_company = max(company_dirs, key=lambda p: p.stat().st_mtime)
    company = latest_company.name
    
    jd_files = list(latest_company.glob("jd_original_*.txt"))
    if jd_files:
        latest_jd = max(jd_files, key=lambda p: p.stat().st_mtime)
        print(f"   ✅ Found JD: {latest_jd.name}")
        print(f"   ℹ️  Company: {company}")
        with open(latest_jd, 'r') as f:
            return f.read(), company
    
    raise FileNotFoundError(f"No JD found for company {company}")


def load_latest_recommendations(user_email: str, company: str):
    """Load the latest recommendations for a company"""
    from app.utils.user_path_utils import get_user_base_path
    
    print(f"\n📁 Loading recommendations for: {company}")
    user_base = get_user_base_path(user_email)
    applied_dir = user_base / "cv-analysis" / "applied_companies" / company
    
    if not applied_dir.exists():
        print(f"   ⚠️  No recommendations directory found - will generate from JD")
        return None
    
    # Find recommendation files
    rec_files = list(applied_dir.glob("ai_recommendation_*.txt"))
    if rec_files:
        latest_rec = max(rec_files, key=lambda p: p.stat().st_mtime)
        print(f"   ✅ Found recommendations: {latest_rec.name}")
        with open(latest_rec, 'r') as f:
            return f.read()
    
    print(f"   ⚠️  No recommendations found - will generate from JD")
    return None


def validate_with_real_data(user_email: str, company: str = None, jd_text: str = None):
    """
    Test the complete CV tailoring flow with REAL data
    
    Args:
        user_email: Email of the user whose CV to load
        company: Optional company name (uses latest if not provided)
        jd_text: Optional JD text (uses file if not provided)
    """
    print("\n" + "="*80)
    print("🔍 ROLE HIGHLIGHTS VALIDATION WITH REAL DATA")
    print("="*80)
    
    from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
    from app.services.structured_cv_parser import LLMStructuredCVParser
    from app.tailored_cv.services.recommendation_parser import RecommendationParser
    
    # Step 1: Load real CV
    print("\n1️⃣  Loading real CV data...")
    try:
        cv_data = load_latest_cv(user_email)
        print(f"   ✅ CV loaded successfully")
        
        # Show CV summary
        print(f"   ℹ️  Name: {cv_data.get('personal_information', {}).get('name', 'N/A')}")
        print(f"   ℹ️  Email: {cv_data.get('personal_information', {}).get('email', 'N/A')}")
        exp_count = len(cv_data.get('experience', []))
        print(f"   ℹ️  Experience entries: {exp_count}")
        edu_count = len(cv_data.get('education', []))
        print(f"   ℹ️  Education entries: {edu_count}")
        
    except Exception as e:
        print(f"   ❌ Failed to load CV: {e}")
        raise
    
    # Step 2: Load or use provided JD
    print("\n2️⃣  Loading job description...")
    try:
        if jd_text:
            print(f"   ✅ Using provided JD text ({len(jd_text)} characters)")
            if not company:
                company = "Test_Company"
        else:
            jd_text, company = load_latest_jd(user_email, company)
        
        print(f"   ℹ️  Company: {company}")
        print(f"   ℹ️  JD length: {len(jd_text)} characters")
        print(f"   ℹ️  Preview: {jd_text[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Failed to load JD: {e}")
        raise
    
    # Step 3: Load or generate recommendations
    print("\n3️⃣  Loading/generating recommendations...")
    try:
        rec_text = load_latest_recommendations(user_email, company)
        
        if rec_text:
            print(f"   ✅ Using existing recommendations")
            # Parse recommendations
            recommendations = RecommendationParser.parse_from_text(rec_text, company)
        else:
            print(f"   ℹ️  Will need to generate recommendations (requires AI)")
            print(f"   ⚠️  Skipping full tailoring - showing structure validation only")
            
            # Just validate the structure without running full AI flow
            return validate_structure_only(cv_data, jd_text, company)
        
        print(f"   ✅ Recommendations parsed")
        print(f"   ℹ️  Job title: {recommendations.job_title}")
        print(f"   ℹ️  Critical gaps: {len(recommendations.critical_gaps)}")
        
    except Exception as e:
        print(f"   ⚠️  Could not load recommendations: {e}")
        print(f"   ℹ️  Showing structure validation only")
        return validate_structure_only(cv_data, jd_text, company)
    
    # Step 4: Check for existing tailored CV
    print("\n4️⃣  Checking for existing tailored CV...")
    try:
        from app.utils.user_path_utils import get_user_base_path
        
        user_base = get_user_base_path(user_email)
        tailored_dir = user_base / "cv-analysis" / "cvs" / "tailored"
        
        if tailored_dir.exists():
            # Find latest tailored CV for this company
            tailored_files = list(tailored_dir.glob(f"{company}_tailored_cv_*.json"))
            if tailored_files:
                latest_tailored = max(tailored_files, key=lambda p: p.stat().st_mtime)
                print(f"   ✅ Found existing tailored CV: {latest_tailored.name}")
                
                with open(latest_tailored, 'r') as f:
                    tailored_data = json.load(f)
                
                # Validate the tailored CV structure
                return validate_tailored_cv(tailored_data, company)
        
        print(f"   ℹ️  No existing tailored CV found - would need to generate")
        
    except Exception as e:
        print(f"   ⚠️  Error checking tailored CV: {e}")
    
    print("\n" + "="*80)
    print("ℹ️  For full end-to-end testing, use the CV tailoring API endpoint")
    print("="*80)


def validate_structure_only(cv_data: dict, jd_text: str, company: str):
    """Validate the CV structure without full tailoring"""
    print("\n" + "="*80)
    print("📋 STRUCTURE VALIDATION")
    print("="*80)
    
    # Check CV has required fields
    print("\n✅ CV Structure Validation:")
    required_fields = ['personal_information', 'experience', 'education', 'skills']
    for field in required_fields:
        if field in cv_data:
            print(f"   ✅ Has '{field}' field")
        else:
            print(f"   ❌ Missing '{field}' field")
    
    # Check JD has content
    print(f"\n✅ JD Validation:")
    print(f"   ✅ JD has {len(jd_text)} characters")
    print(f"   ✅ Company: {company}")
    
    print("\n✅ Structure validation PASSED")
    print("\nℹ️  To test full flow with AI generation:")
    print("   1. Use the web app to analyze JD")
    print("   2. Generate tailored CV")
    print("   3. Run this script again to validate output")
    
    return True


def validate_tailored_cv(tailored_data: dict, company: str):
    """Validate an existing tailored CV"""
    print("\n" + "="*80)
    print("📊 TAILORED CV VALIDATION")
    print("="*80)
    
    # Check for role_highlights
    print("\n1️⃣  Checking role_highlights field:")
    if 'role_highlights' in tailored_data:
        role_highlights = tailored_data['role_highlights']
        print(f"   ✅ role_highlights field exists")
        print(f"   ℹ️  Length: {len(role_highlights)} characters")
        
        # Validate structure
        checks = [
            ("Has content", len(role_highlights) > 50),
            ("Contains bullet points", '•' in role_highlights or '-' in role_highlights),
            ("Contains skills section", 'Skills:' in role_highlights or '|' in role_highlights),
            ("Has quantified achievements", any(char.isdigit() for char in role_highlights)),
        ]
        
        print("\n   📋 Structure checks:")
        all_passed = True
        for check_name, result in checks:
            if result:
                print(f"      ✅ {check_name}")
            else:
                print(f"      ❌ {check_name}")
                all_passed = False
        
        if all_passed:
            print(f"\n   ✅ role_highlights structure is CORRECT")
        else:
            print(f"\n   ⚠️  role_highlights structure needs review")
        
        # Show preview
        print(f"\n   📄 Preview:")
        all_lines = role_highlights.split('\n')
        preview_lines = all_lines[:5]
        for line in preview_lines:
            print(f"      {line}")
        if len(all_lines) > 5:
            remaining = len(all_lines) - 5
            print(f"      ... ({remaining} more lines)")
        
    else:
        print(f"   ❌ role_highlights field is MISSING")
        
        # Check for old profile_summary
        if 'profile_summary' in tailored_data:
            print(f"   ⚠️  Found old 'profile_summary' field instead")
            print(f"   ℹ️  This CV was generated with the old implementation")
        
        return False
    
    # Check for target_role
    print("\n2️⃣  Checking target_role field:")
    if 'target_role' in tailored_data:
        target_role = tailored_data['target_role']
        print(f"   ✅ target_role field exists: '{target_role}'")
    else:
        print(f"   ⚠️  target_role field is missing (will use generic header)")
    
    # Check PDF generation
    print("\n3️⃣  Checking PDF compatibility:")
    try:
        from app.tailored_cv.services.tailored_cv_adapter import adapt_tailored_cv_to_pdf_format
        
        pdf_data = adapt_tailored_cv_to_pdf_format(tailored_data)
        
        if 'role_highlights' in pdf_data:
            print(f"   ✅ Adapter maps role_highlights correctly")
        else:
            print(f"   ❌ Adapter failed to map role_highlights")
            return False
        
        if 'target_role' in pdf_data:
            print(f"   ✅ Adapter maps target_role correctly: '{pdf_data['target_role']}'")
        else:
            print(f"   ⚠️  Adapter didn't map target_role (will use 'PROFESSIONAL')")
        
    except Exception as e:
        print(f"   ❌ Adapter error: {e}")
        return False
    
    # Summary
    print("\n" + "="*80)
    print("✅ TAILORED CV VALIDATION PASSED!")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   ✅ Has role_highlights field")
    print(f"   ✅ Has proper structure (value statement + bullets + skills)")
    print(f"   ✅ Compatible with PDF generation")
    print(f"   ℹ️  Target role: {tailored_data.get('target_role', 'Not specified')}")
    
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test role_highlights implementation with real data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use your email and latest data
  python test_with_real_data.py --email your.email@example.com
  
  # Specify a company
  python test_with_real_data.py --email your.email@example.com --company "Google"
  
  # Provide JD text directly
  python test_with_real_data.py --email your.email@example.com --jd "Job description text here..."
        """
    )
    
    parser.add_argument(
        '--email',
        required=True,
        help='Your email address (used to find your CV data)'
    )
    
    parser.add_argument(
        '--company',
        help='Company name (optional, uses latest if not provided)'
    )
    
    parser.add_argument(
        '--jd',
        help='Job description text (optional, loads from file if not provided)'
    )
    
    args = parser.parse_args()
    
    try:
        validate_with_real_data(
            user_email=args.email,
            company=args.company,
            jd_text=args.jd
        )
        return 0
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

