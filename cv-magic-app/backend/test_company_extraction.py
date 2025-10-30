#!/usr/bin/env python3
"""
Test Company Name Extraction - Verify Universal Prompt Integration

This script tests the updated CompanyExtractor with real-world job descriptions
to ensure the "NSW" bug is fixed and extraction works globally.

Usage:
    python test_company_extraction.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.company_extractor import CompanyExtractor, Confidence
from app.ai.ai_service import AIServiceManager


# Test Cases
TEST_CASES = [
    {
        "name": "Test 1: NSW Government Agency (Your Original Issue)",
        "jd_url": "https://www.seek.com.au/job/12345",
        "jd_text": """Data Analyst Energy and Water Ombudsman NSW 2 days left to apply Job Summary Energy and Water Ombudsman NSW Applications close: Job posted on: 20th Oct 2025 Sydney > CBD, Inner West & Eastern Suburbs Sydney Full Time , Contract Information Technology & Digital Not For Profit (NFP) Job description Full-time, 12-month fixed-term contract opportunity High-performing, respected organisation in convenient Sydney CBD location Flexible hybrid working environment (3 days working from home) Grow your skills with comprehensive training and development Looking for a career move where you can make a difference? At EWON, we provide consumers with independent, free, informal dispute resolution services in the energy and water sectors.""",
        "expected_company": "Energy and Water Ombudsman NSW",
        "expected_confidence": "high"
    },
    {
        "name": "Test 2: Transport for NSW",
        "jd_url": "https://jobs.nsw.gov.au/job/12345",
        "jd_text": "Senior Engineer - Transport for NSW. Join Australia's largest transport infrastructure agency. Transport for NSW is the lead agency for transport in NSW, responsible for planning, program administration, policy, regulation, procuring public transport services and infrastructure for NSW.",
        "expected_company": "Transport for NSW",
        "expected_confidence": "high"
    },
    {
        "name": "Test 3: US Government Department",
        "jd_url": "https://usajobs.gov/job/12345",
        "jd_text": "Software Developer | California Department of Education | Sacramento, CA. The California Department of Education is seeking a talented Software Developer to join our IT team. We oversee California's diverse and dynamic public school system.",
        "expected_company": "California Department of Education",
        "expected_confidence": "high"
    },
    {
        "name": "Test 4: Recruitment Agency",
        "jd_url": "https://www.seek.com.au/job/67890",
        "jd_text": "Posted by Hays Recruitment on behalf of a leading financial services company. Senior Data Analyst role in Melbourne CBD. Our client, a confidential major bank, is seeking an experienced Data Analyst. Apply through Hays today.",
        "expected_company": "Hays Recruitment",
        "expected_confidence": "medium"
    },
    {
        "name": "Test 5: International Corporation",
        "jd_url": "https://careers.deloitte.com/au/job/12345",
        "jd_text": "Senior Analyst at Deloitte Australia. Deloitte Touche Tohmatsu Limited (Australia) is hiring. Join one of the world's leading professional services firms. Deloitte Australia provides audit, consulting, financial advisory, risk advisory, and tax services.",
        "expected_company": "Deloitte Australia",
        "expected_confidence": "high"
    },
    {
        "name": "Test 6: Small Business",
        "jd_url": "",
        "jd_text": "Join Sunshine Breads! We are a family-owned artisan bakery in downtown Melbourne. Sunshine Breads has been serving our community for 20 years with fresh, locally-sourced baked goods. Now hiring: Head Baker position available.",
        "expected_company": "Sunshine Breads",
        "expected_confidence": "high"
    },
    {
        "name": "Test 7: UK Healthcare",
        "jd_url": "https://www.jobs.nhs.uk/job/12345",
        "jd_text": "Nurse Practitioner | NHS Greater Glasgow and Clyde | Glasgow, Scotland. NHS Greater Glasgow and Clyde is one of the largest healthcare systems in the UK, serving over 1.2 million patients. Join our dedicated team of healthcare professionals.",
        "expected_company": "NHS Greater Glasgow and Clyde",
        "expected_confidence": "high"
    },
    {
        "name": "Test 8: Just 'NSW' (Edge Case - Should Fail)",
        "jd_url": "",
        "jd_text": "Data Analyst NSW Sydney location great benefits salary package competitive",
        "expected_company": "Unknown",  # Should trigger fallback
        "expected_confidence": "low"
    }
]


def print_result(test_case, result, passed):
    """Print test result with formatting"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} {test_case['name']}")
    print(f"  Expected: {test_case['expected_company']} (confidence: {test_case['expected_confidence']})")
    print(f"  Got:      {result.name} (confidence: {result.confidence.value})")
    if result.confidence.value == "low" or not passed:
        print(f"  Normalized: {result.normalized}")
        print(f"  Is Agency: {result.is_agency}")


async def run_tests():
    """Run all test cases"""
    print("=" * 80)
    print("Company Name Extraction - Test Suite")
    print("Testing Universal AI Prompt Integration")
    print("=" * 80)
    
    # Initialize the extractor
    ai_service = AIServiceManager()
    extractor = CompanyExtractor(ai_service)
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 80}")
        print(f"Running Test {i}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"{'=' * 80}")
        
        try:
            # Extract company name
            result = await extractor.extract(
                jd_url=test_case["jd_url"],
                jd_text=test_case["jd_text"],
                user=None
            )
            
            # Check if result matches expectations
            company_match = (
                result.name.lower() == test_case["expected_company"].lower() or
                test_case["expected_company"].lower() in result.name.lower() or
                result.name.lower() in test_case["expected_company"].lower()
            )
            
            confidence_acceptable = (
                result.confidence.value == test_case["expected_confidence"] or
                (test_case["expected_confidence"] == "medium" and result.confidence.value in ["medium", "high"]) or
                (test_case["expected_confidence"] == "low" and result.name == "Unknown")
            )
            
            passed = company_match and confidence_acceptable
            
            if passed:
                passed_tests += 1
            else:
                failed_tests += 1
            
            print_result(test_case, result, passed)
            
        except Exception as e:
            print(f"❌ ERROR: {test_case['name']}")
            print(f"  Exception: {str(e)}")
            failed_tests += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Total Tests: {len(TEST_CASES)}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {passed_tests / len(TEST_CASES) * 100:.1f}%")
    print("=" * 80)
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! Company extraction is working correctly.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Review the results above.")
    
    return failed_tests == 0


def main():
    """Main entry point"""
    try:
        # Run async tests
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

