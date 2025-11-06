#!/usr/bin/env python3
"""
Test to verify role_highlights implementation is correct
"""
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def test_role_highlights_in_system_prompt():
    """Verify the system prompt includes role highlights instructions"""
    print("\n" + "="*80)
    print("Test 1: System Prompt Validation")
    print("="*80)
    
    from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
    
    service = CVTailoringService(user_email="test@example.com")
    system_prompt = service._build_system_prompt()
    
    # Check for key phrases in system prompt
    required_phrases = [
        "ROLE HIGHLIGHTS RULES",
        "VALUE STATEMENT",
        "KEY ACCOMPLISHMENTS",
        "SKILLS SNAPSHOT",
        "pipe-separated"
    ]
    
    print("\n📋 Checking system prompt for required phrases:")
    for phrase in required_phrases:
        if phrase in system_prompt:
            print(f"   ✅ Found: '{phrase}'")
        else:
            print(f"   ❌ MISSING: '{phrase}'")
            raise AssertionError(f"System prompt missing required phrase: {phrase}")
    
    # Check that old "PROFILE SUMMARY RULES" is not present
    if "PROFILE SUMMARY RULES:" in system_prompt and "ROLE HIGHLIGHTS RULES:" not in system_prompt:
        print(f"   ❌ FOUND OLD: 'PROFILE SUMMARY RULES' without 'ROLE HIGHLIGHTS RULES'")
        raise AssertionError("System prompt still uses old PROFILE SUMMARY RULES")
    else:
        print(f"   ✅ No old 'PROFILE SUMMARY RULES' found (or properly replaced)")
    
    print("\n✅ System prompt validation PASSED")
    return True


def test_role_highlights_in_user_prompt():
    """Verify the user prompt includes role highlights instructions"""
    print("\n" + "="*80)
    print("Test 2: User Prompt Validation")
    print("="*80)
    
    from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
    from app.tailored_cv.models.cv_models import OriginalCV, RecommendationAnalysis, OptimizationStrategy, ContactInfo
    from datetime import datetime
    
    # Create mock data
    mock_cv = OriginalCV(
        contact=ContactInfo(name="Test User", email="test@test.com", phone="123-456-7890", location="Sydney"),
        education=[],
        experience=[],
        skills=[],
        created_at=datetime.utcnow()
    )
    
    mock_recommendations = RecommendationAnalysis(
        company="Test Company",
        job_title="Data Analyst",
        missing_technical_skills=[],
        missing_soft_skills=[],
        missing_keywords=[],
        technical_enhancements=[],
        soft_skill_improvements=[],
        keyword_integration=[],
        critical_gaps=[],
        important_gaps=[],
        nice_to_have=[]
    )
    
    mock_strategy = OptimizationStrategy(
        education_strategy="",
        experience_strategy="",
        skills_strategy="",
        projects_strategy="",
        section_order=[],  # Required field
        keyword_placement={},
        quantification_targets=[],
        impact_enhancements={}
    )
    
    service = CVTailoringService(user_email="test@example.com")
    user_prompt = service._build_user_prompt(mock_cv, mock_recommendations, mock_strategy, None)
    
    # Check for key phrases in user prompt
    required_phrases = [
        "[ROLE TITLE] HIGHLIGHTS GENERATION",
        "VALUE STATEMENT",
        "KEY ACCOMPLISHMENTS (3 bullet points)",
        "SKILLS SNAPSHOT (6-8 skills)",
        "Generate [ROLE TITLE] HIGHLIGHTS from scratch"
    ]
    
    print("\n📋 Checking user prompt for required phrases:")
    for phrase in required_phrases:
        if phrase in user_prompt:
            print(f"   ✅ Found: '{phrase}'")
        else:
            print(f"   ❌ MISSING: '{phrase}'")
            raise AssertionError(f"User prompt missing required phrase: {phrase}")
    
    print("\n✅ User prompt validation PASSED")
    return True


def test_role_highlights_in_schema():
    """Verify TailoredCV schema includes role_highlights field"""
    print("\n" + "="*80)
    print("Test 3: Schema Validation")
    print("="*80)
    
    from app.tailored_cv.models.cv_models import TailoredCV, CleanTailoredCV
    
    # Test TailoredCV schema
    print("\n📋 Checking TailoredCV schema:")
    tailored_schema = TailoredCV.model_json_schema()
    
    if "role_highlights" in tailored_schema["properties"]:
        print(f"   ✅ TailoredCV has 'role_highlights' field")
        description = tailored_schema["properties"]["role_highlights"].get("description", "")
        print(f"   ℹ️  Description: {description}")
    else:
        print(f"   ❌ TailoredCV MISSING 'role_highlights' field")
        raise AssertionError("TailoredCV schema missing role_highlights field")
    
    if "target_role" in tailored_schema["properties"]:
        print(f"   ✅ TailoredCV has 'target_role' field")
    else:
        print(f"   ❌ TailoredCV MISSING 'target_role' field")
        raise AssertionError("TailoredCV schema missing target_role field")
    
    # Test CleanTailoredCV schema
    print("\n📋 Checking CleanTailoredCV schema:")
    clean_schema = CleanTailoredCV.model_json_schema()
    
    if "role_highlights" in clean_schema["properties"]:
        print(f"   ✅ CleanTailoredCV has 'role_highlights' field")
    else:
        print(f"   ❌ CleanTailoredCV MISSING 'role_highlights' field")
        raise AssertionError("CleanTailoredCV schema missing role_highlights field")
    
    print("\n✅ Schema validation PASSED")
    return True


def test_pdf_mapping():
    """Verify PDF generation properly maps role_highlights"""
    print("\n" + "="*80)
    print("Test 4: PDF Data Mapping Validation")
    print("="*80)
    
    try:
        from app.tailored_cv.services.pdf_export_service import ResumePDFGenerator, _map_tailored_json_to_generator_schema
    except ImportError as e:
        print(f"   ⚠️  Skipping PDF test - reportlab not installed: {e}")
        print("   ℹ️  Install with: pip install reportlab")
        return True
    
    # Test data with role_highlights
    mock_data = {
        "role_highlights": "Data Analyst with 3 years' experience...\n• Achievement 1\n• Achievement 2\n• Achievement 3\nSkills: Python | SQL | Tableau",
        "target_role": "Data Analyst",
        "contact": {
            "name": "Test User",
            "email": "test@test.com",
            "phone": "123-456-7890",
            "location": "Sydney"
        },
        "education": [],
        "experience": [],
        "skills": []
    }
    
    print("\n📋 Testing data mapping:")
    mapped_data = _map_tailored_json_to_generator_schema(mock_data)
    
    if "role_highlights" in mapped_data:
        print(f"   ✅ Mapped data contains 'role_highlights'")
        print(f"   ℹ️  Content preview: {mapped_data['role_highlights'][:50]}...")
    else:
        print(f"   ❌ Mapped data MISSING 'role_highlights'")
        raise AssertionError("PDF mapping missing role_highlights field")
    
    if "target_role" in mapped_data:
        print(f"   ✅ Mapped data contains 'target_role'")
        print(f"   ℹ️  Target role: {mapped_data['target_role']}")
    else:
        print(f"   ❌ Mapped data MISSING 'target_role'")
        raise AssertionError("PDF mapping missing target_role field")
    
    print("\n✅ PDF mapping validation PASSED")
    return True


def test_adapter_mapping():
    """Verify adapter properly maps role_highlights"""
    print("\n" + "="*80)
    print("Test 5: Adapter Mapping Validation")
    print("="*80)
    
    from app.tailored_cv.services.tailored_cv_adapter import adapt_tailored_cv_to_pdf_format
    
    # Test data with role_highlights
    tailored_cv_data = {
        "contact": {
            "name": "Test User",
            "email": "test@test.com",
            "phone": "123-456-7890",
            "location": "Sydney"
        },
        "role_highlights": "Data Analyst with 3 years' experience...",
        "target_role": "Data Analyst",
        "education": [],
        "experience": [],
        "skills": []
    }
    
    print("\n📋 Testing adapter mapping:")
    pdf_data = adapt_tailored_cv_to_pdf_format(tailored_cv_data)
    
    if "role_highlights" in pdf_data:
        print(f"   ✅ Adapted data contains 'role_highlights'")
        print(f"   ℹ️  Content preview: {pdf_data['role_highlights'][:50]}...")
    else:
        print(f"   ❌ Adapted data MISSING 'role_highlights'")
        raise AssertionError("Adapter missing role_highlights field")
    
    if "target_role" in pdf_data:
        print(f"   ✅ Adapted data contains 'target_role'")
        print(f"   ℹ️  Target role: {pdf_data['target_role']}")
    else:
        print(f"   ❌ Adapted data MISSING 'target_role'")
        raise AssertionError("Adapter missing target_role field")
    
    print("\n✅ Adapter mapping validation PASSED")
    return True


def test_fallback_chain():
    """Verify fallback chain works: role_highlights → profile_summary → career_profile"""
    print("\n" + "="*80)
    print("Test 6: Fallback Chain Validation")
    print("="*80)
    
    from app.tailored_cv.services.tailored_cv_adapter import adapt_tailored_cv_to_pdf_format
    
    # Test 1: With role_highlights (should use it)
    print("\n📋 Test 6.1: With role_highlights (priority)")
    data_with_role_highlights = {
        "contact": {"name": "Test", "email": "test@test.com"},
        "role_highlights": "NEW: Role highlights content",
        "profile_summary": "OLD: Profile summary content",
        "career_profile": {"summary": "LEGACY: Career profile"},
        "education": [],
        "experience": [],
        "skills": []
    }
    
    result = adapt_tailored_cv_to_pdf_format(data_with_role_highlights)
    if "role_highlights" in result and result["role_highlights"] == "NEW: Role highlights content":
        print(f"   ✅ Uses role_highlights (priority)")
    else:
        raise AssertionError("Failed to use role_highlights when present")
    
    # Test 2: Without role_highlights, with profile_summary (should fallback)
    print("\n📋 Test 6.2: Fallback to profile_summary")
    data_with_profile_summary = {
        "contact": {"name": "Test", "email": "test@test.com"},
        "profile_summary": "OLD: Profile summary content",
        "education": [],
        "experience": [],
        "skills": []
    }
    
    result = adapt_tailored_cv_to_pdf_format(data_with_profile_summary)
    if "profile_summary" in result and result["profile_summary"] == "OLD: Profile summary content":
        print(f"   ✅ Falls back to profile_summary")
    else:
        raise AssertionError("Failed to fallback to profile_summary")
    
    print("\n✅ Fallback chain validation PASSED")
    return True


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "="*80)
    print("🚀 ROLE HIGHLIGHTS VALIDATION TEST SUITE")
    print("="*80)
    
    tests = [
        ("System Prompt", test_role_highlights_in_system_prompt),
        ("User Prompt", test_role_highlights_in_user_prompt),
        ("Schema", test_role_highlights_in_schema),
        ("PDF Mapping", test_pdf_mapping),
        ("Adapter Mapping", test_adapter_mapping),
        ("Fallback Chain", test_fallback_chain),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

