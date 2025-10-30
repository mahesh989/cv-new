#!/usr/bin/env python3
"""
Test to verify consistency_validator type safety fix
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def test_safe_numeric_conversion():
    """Test that _safe_numeric handles all types correctly"""
    
    print("=" * 80)
    print("Testing Consistency Validator Type Safety Fix")
    print("=" * 80)
    
    from app.services.ats.components.consistency_validator import ConsistencyValidator
    
    validator = ConsistencyValidator()
    
    test_cases = [
        # (input, expected_output, description)
        (5, 5.0, "Integer"),
        (5.5, 5.5, "Float"),
        ("5", 5.0, "String number"),
        ("5.5", 5.5, "String float"),
        ("  5  ", 5.0, "String with whitespace"),
        (None, 0.0, "None value"),
        ("", 0.0, "Empty string"),
        ("invalid", 0.0, "Invalid string"),
        ([], 0.0, "List (invalid type)"),
        ({}, 0.0, "Dict (invalid type)"),
    ]
    
    print("\n📊 Testing _safe_numeric conversion:")
    all_passed = True
    
    for input_val, expected, description in test_cases:
        result = validator._safe_numeric(input_val)
        passed = result == expected
        status = "✅" if passed else "❌"
        
        print(f"  {status} {description:25} | Input: {repr(input_val):20} → {result} (expected {expected})")
        
        if not passed:
            all_passed = False
    
    return all_passed


def test_consistency_validation_with_mixed_types():
    """Test that consistency validation works with mixed string/number types"""
    
    print("\n" + "=" * 80)
    print("Testing Consistency Validation with Mixed Types")
    print("=" * 80)
    
    from app.services.ats.components.consistency_validator import ConsistencyValidator
    
    validator = ConsistencyValidator()
    
    # Mock results with MIXED types (strings and numbers)
    # This simulates what AI might return
    results = {
        "experience": {
            "experience_analysis": {
                "cv_experience_years": "5",  # STRING
                "cv_role_level": "Mid-Level",
                "alignment_score": 75  # NUMBER
            }
        },
        "seniority": {
            "seniority_analysis": {
                "cv_experience_years": 5,  # NUMBER
                "cv_responsibility_scope": "Mid-Level",
                "seniority_score": "80"  # STRING
            }
        },
        "skills": {
            "overall_skills_score": "70.5"  # STRING
        },
        "industry": {
            "industry_analysis": {
                "industry_alignment_score": 65  # NUMBER
            }
        },
        "technical": {
            "technical_analysis": {
                "technical_depth_score": "90"  # STRING
            }
        }
    }
    
    print("\n📥 Input data with mixed types:")
    print(f"   exp_years: {repr(results['experience']['experience_analysis']['cv_experience_years'])} (type: string)")
    print(f"   sen_years: {repr(results['seniority']['seniority_analysis']['cv_experience_years'])} (type: number)")
    print(f"   alignment_score: {repr(results['experience']['experience_analysis']['alignment_score'])} (type: number)")
    print(f"   seniority_score: {repr(results['seniority']['seniority_analysis']['seniority_score'])} (type: string)")
    
    try:
        validation_results = validator.validate_cross_analyzer_consistency(results)
        
        print("\n✅ SUCCESS: Validation completed without errors!")
        print(f"\n📊 Validation Results:")
        print(f"   Consistent: {validation_results['is_consistent']}")
        print(f"   Confidence Score: {validation_results['confidence_score']}%")
        print(f"   Inconsistencies: {len(validation_results['inconsistencies'])}")
        
        if validation_results['inconsistencies']:
            print(f"\n   Inconsistency Details:")
            for inconsistency in validation_results['inconsistencies']:
                print(f"      - {inconsistency.get('type', 'unknown')}")
        
        return True
        
    except TypeError as e:
        print(f"\n❌ FAILURE: TypeError occurred: {e}")
        print("   This means the fix is NOT working properly!")
        return False
    except Exception as e:
        print(f"\n❌ FAILURE: Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("\n🧪 Running Type Safety Tests...\n")
    
    test1_passed = test_safe_numeric_conversion()
    test2_passed = test_consistency_validation_with_mixed_types()
    
    print("\n" + "=" * 80)
    print("📋 Test Summary:")
    print("=" * 80)
    print(f"  Test 1 (_safe_numeric): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Test 2 (consistency validation): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests PASSED! Type safety fix is working correctly.")
        print("   The consistency validator can now handle both strings and numbers.")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED! Please review the implementation.")
        sys.exit(1)

