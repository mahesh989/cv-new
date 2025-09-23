#!/usr/bin/env python3
"""
Test script to verify AI analysis consistency improvements.

This script tests the standardized configuration and consistency validation
to ensure all analyzers interpret CV content consistently.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.services.ats.components.consistency_validator import ConsistencyValidator
from app.services.ats.components.standardized_config import STANDARD_AI_PARAMS, validate_analysis_result

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_standardized_config():
    """Test standardized configuration."""
    print("🧪 Testing Standardized Configuration...")
    
    # Test AI parameters
    assert STANDARD_AI_PARAMS["temperature"] == 0.1, "Temperature should be 0.1"
    assert STANDARD_AI_PARAMS["max_tokens"] == 1500, "Max tokens should be 1500"
    assert "system_prompt" in STANDARD_AI_PARAMS, "System prompt should be defined"
    
    print("✅ Standardized configuration is correct")
    return True


def test_validation_rules():
    """Test validation rules."""
    print("🧪 Testing Validation Rules...")
    
    # Test valid result
    valid_result = {
        "cv_experience_years": 5,
        "cv_role_level": "Senior",
        "alignment_score": 85
    }
    assert validate_analysis_result(valid_result, "experience"), "Valid result should pass validation"
    
    # Test invalid result (missing field)
    invalid_result = {
        "cv_experience_years": 5,
        "alignment_score": 85
        # Missing cv_role_level
    }
    assert not validate_analysis_result(invalid_result, "experience"), "Invalid result should fail validation"
    
    # Test invalid result (score out of range)
    invalid_score_result = {
        "cv_experience_years": 5,
        "cv_role_level": "Senior",
        "alignment_score": 150  # Out of range
    }
    assert not validate_analysis_result(invalid_score_result, "experience"), "Invalid score should fail validation"
    
    print("✅ Validation rules are working correctly")
    return True


def test_consistency_validator():
    """Test consistency validator."""
    print("🧪 Testing Consistency Validator...")
    
    validator = ConsistencyValidator()
    
    # Test consistent results
    consistent_results = {
        "experience": {
            "experience_analysis": {
                "cv_experience_years": 5,
                "cv_role_level": "Senior",
                "alignment_score": 85
            }
        },
        "seniority": {
            "seniority_analysis": {
                "cv_experience_years": 5,
                "cv_responsibility_scope": "Senior Individual Contributor",
                "seniority_score": 80
            }
        },
        "skills": {
            "overall_skills_score": 75
        },
        "industry": {
            "industry_analysis": {
                "industry_alignment_score": 70
            }
        },
        "technical": {
            "technical_analysis": {
                "technical_depth_score": 80
            }
        }
    }
    
    validation_result = validator.validate_cross_analyzer_consistency(consistent_results)
    assert validation_result["is_consistent"], "Consistent results should pass validation"
    assert validation_result["confidence_score"] > 70, "Confidence score should be high for consistent results"
    
    # Test inconsistent results
    inconsistent_results = {
        "experience": {
            "experience_analysis": {
                "cv_experience_years": 0,  # Inconsistent with seniority
                "cv_role_level": "Entry-Level",
                "alignment_score": 85
            }
        },
        "seniority": {
            "seniority_analysis": {
                "cv_experience_years": 6,  # Inconsistent with experience
                "cv_responsibility_scope": "Senior Individual Contributor",
                "seniority_score": 80
            }
        },
        "skills": {
            "overall_skills_score": 75
        },
        "industry": {
            "industry_analysis": {
                "industry_alignment_score": 70
            }
        },
        "technical": {
            "technical_analysis": {
                "technical_depth_score": 80
            }
        }
    }
    
    validation_result = validator.validate_cross_analyzer_consistency(inconsistent_results)
    assert not validation_result["is_consistent"], "Inconsistent results should fail validation"
    assert len(validation_result["inconsistencies"]) > 0, "Should detect inconsistencies"
    assert len(validation_result["recommendations"]) > 0, "Should provide recommendations"
    
    print("✅ Consistency validator is working correctly")
    return True


def test_consistency_report():
    """Test consistency report generation."""
    print("🧪 Testing Consistency Report Generation...")
    
    validator = ConsistencyValidator()
    
    # Test with inconsistent results
    inconsistent_results = {
        "experience": {
            "experience_analysis": {
                "cv_experience_years": 0,
                "cv_role_level": "Entry-Level",
                "alignment_score": 85
            }
        },
        "seniority": {
            "seniority_analysis": {
                "cv_experience_years": 6,
                "cv_responsibility_scope": "Senior Individual Contributor",
                "seniority_score": 80
            }
        }
    }
    
    validation_result = validator.validate_cross_analyzer_consistency(inconsistent_results)
    report = validator.get_consistency_report(validation_result)
    
    assert "❌ Analysis results show inconsistencies" in report, "Report should indicate inconsistencies"
    assert "🚨 Inconsistencies Found:" in report, "Report should list inconsistencies"
    assert "💡 Recommendations:" in report, "Report should provide recommendations"
    
    print("✅ Consistency report generation is working correctly")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting AI Analysis Consistency Tests...\n")
    
    tests = [
        test_standardized_config,
        test_validation_rules,
        test_consistency_validator,
        test_consistency_report
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {str(e)}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! AI analysis consistency improvements are working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
