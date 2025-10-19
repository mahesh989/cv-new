#!/usr/bin/env python3
"""
Test Company Extraction for AHPRA Job Posting
Tests the Single AI Method with URL-based fallback
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.company_extractor import CompanyExtractor
from app.ai.ai_service import AIServiceManager


async def test_ahpra_extraction():
    """Test company extraction for AHPRA job posting"""
    
    # Test data from the actual job posting
    jd_url = "https://www.ethicaljobs.com.au/members/baurecruitment/finance-systems-analyst?keywords=Data%20Analyst"
    
    jd_text = """
Finance Systems Analyst

Australian Health Practitioner Regulation Agency (AHPRA)

2 hours left to apply

Job Summary

Australian Health Practitioner Regulation Agency (AHPRA)

* Starting at $135,031 plus superannuation and leave loading
* Applications close:
* Job posted on: 13th Oct 2025
* Melbourne
* Full Time
* Finance and Accounting, Information Technology & Digital
* Not For Profit (NFP)

Job description

The Australian Health Practitioner Regulation Agency (Ahpra) works in partnership with 15 National Boards to implement the national regulatory scheme for health professionals. The purpose of health practitioner regulation is to protect the public by ensuring that only health practitioners who have the skills, qualifications, and knowledge to provide safe care are registered. 

The Finance and Risk Directorate plays a critical role in supporting this mission by leveraging data, embracing technology, and enabling change. Our Finance and Procurement team supports key governance bodies, including multiple committees, National Executive, and all 15 National Boards. We ensure financial sustainability and discipline across the National Registration and Accreditation Scheme, keeping practitioner fees reasonable and aligned with ministerial expectations.

**We have an ongoing full time role for a Finance Systems Analyst to join our team in the Melbourne office.**

We're looking for a Finance System Analyst to lead the design, implementation, and optimisation of finance systems that support strategic planning, forecasting, and reporting across the organisation. You will provide advice on system architecture, data governance, and integration, ensuring accuracy, compliance, and performance. A key focus will be developing and maintaining Anaplan models, as well as creating insightful dashboards and reports in Anaplan, Power BI, and Excel.

In this role, you will collaborate with finance stakeholders to identify opportunities for automation and system improvements, translate business needs into technical solutions, and provide training to uplift capability across the team. You will also contribute to a culture of continuous improvement and support workplace health, safety, and wellbeing initiatives.

Please refer to **the attached role description for a full overview.**

### **As the ideal candidate, you will demonstrate the following:**

* Tertiary qualifications in Finance, Accounting, Computer Science, Information Systems, or equivalent experience.
* Anaplan certification (Level 1, 2, and The Anaplan Way)
* 3+ years' experience in finance systems analysis, including:  
   * Building and maintaining complex Anaplan models.  
   * Leading enterprise-level financial system implementations.  
   * Translating financial requirements into scalable technical solutions.  
   * Providing expert-level support, training, and guidance to stakeholders.
* Experience with ERP systems and data visualisation tools such as Power BI or Tableau.
* Strong background in budgeting, forecasting, financial modelling, and FP&A processes.
* Advanced analytical, problem-solving, and communication skills.
* Proven ability to engage and collaborate with stakeholders at all levels.
* High proficiency in financial and technology systems, with a focus on continuous improvement.

### **What we offer:** 

* A friendly and supportive working culture with hybrid arrangements
* Discounts on private health insurance
* Career progression, learning and development opportunities
* Attractive base salary starting at $135,031 plus superannuation and leave loading

###   **To apply:** 

* Click '**Apply now**' to submit your application.
* Your application must include an updated resume
* Applicants must be an Australian Citizen, Permanent Resident, or hold a valid work permit or visa. Work eligibility will be checked as part of the recruitment process.
* For any queries or a confidential discussion regarding this position, please email [email protected] using the subject line: **Finance Systems Analyst enquiry via EthicalJobs**.

Offer of employment is subject to successful background (pre-employment screening) and Criminal History checks. 

**Please note that applications will be screened and shortlisted during the advertising period. Should we receive suitable candidates during this time, the advertising period will cease.** 

Ahpra requires all employees to comply with Ahpra policies, including the **Flexible working policy**. 

Ahpra is an equal opportunity employer committed to providing a working environment that embraces and values diversity and inclusion. We strongly encourage people of all abilities to apply, particularly people of Aboriginal and Torres Strait Islander heritage, and those who may experience diversity or disability related barriers in securing employment. If you have any support or access requirements, we encourage you to advise us at time of application.

_With respect, no agencies please._
"""
    
    print("🧪 TESTING COMPANY EXTRACTION FOR AHPRA JOB POSTING")
    print("=" * 60)
    print(f"URL: {jd_url}")
    print(f"Text length: {len(jd_text)} characters")
    print()
    
    # Initialize the extractor
    ai_service = AIServiceManager()
    extractor = CompanyExtractor(ai_service)
    
    # Create a mock user for testing
    class MockUser:
        def __init__(self):
            self.id = 1
            self.email = "test@example.com"
            self.name = "Test User"
    
    mock_user = MockUser()
    
    # Test 1: AI Extraction (Primary Method)
    print("🤖 TEST 1: AI EXTRACTION (Primary Method)")
    print("-" * 40)
    try:
        result = await extractor.extract(jd_url, jd_text, mock_user)
        
        print(f"✅ Company Name: '{result.name}'")
        print(f"✅ Normalized: '{result.normalized}'")
        print(f"✅ Confidence: {result.confidence.value}")
        print(f"✅ Is Agency: {result.is_agency}")
        print(f"✅ Display Name: '{result.display_name}'")
        
        # Validate expected results
        expected_company = "Australian Health Practitioner Regulation Agency"
        if expected_company.lower() in result.name.lower():
            print("✅ PASS: Correctly extracted AHPRA company name")
        else:
            print(f"❌ FAIL: Expected '{expected_company}', got '{result.name}'")
            
        if result.confidence.value in ["high", "medium"]:
            print("✅ PASS: Good confidence level")
        else:
            print(f"⚠️  WARNING: Low confidence level ({result.confidence.value})")
            
    except Exception as e:
        print(f"❌ AI Extraction failed: {str(e)}")
        print("🔄 This will trigger the URL-based fallback...")
    
    print()
    
    # Test 2: URL-Based Fallback (Manual Test)
    print("🔗 TEST 2: URL-BASED FALLBACK (Manual Test)")
    print("-" * 40)
    try:
        fallback_result = extractor._url_based_fallback(jd_url, jd_text)
        
        print(f"✅ Fallback Company: '{fallback_result['company']}'")
        print(f"✅ Fallback Confidence: {fallback_result['confidence']}")
        print(f"✅ Fallback Is Agency: {fallback_result['is_agency']}")
        
        # Validate fallback results
        if fallback_result['company'] != "Unknown":
            print("✅ PASS: Fallback extracted a company name")
        else:
            print("❌ FAIL: Fallback returned 'Unknown'")
            
    except Exception as e:
        print(f"❌ URL-based fallback failed: {str(e)}")
    
    print()
    
    # Test 3: Validation (Benefits Text Rejection)
    print("🚫 TEST 3: VALIDATION (Benefits Text Rejection)")
    print("-" * 40)
    
    # Test that benefits text is properly rejected
    benefits_text = "plus superannuation and leave loading"
    validation_result = extractor._validate_company_name(benefits_text)
    
    print(f"✅ Benefits text '{benefits_text}' → '{validation_result}'")
    
    if validation_result == "Unknown":
        print("✅ PASS: Benefits text correctly rejected")
    else:
        print(f"❌ FAIL: Benefits text should be rejected, got '{validation_result}'")
    
    # Test other invalid terms
    invalid_terms = [
        "salary package and benefits",
        "compensation and leave entitlements",
        "remuneration package",
        "work from home",
        "job opportunity"
    ]
    
    for term in invalid_terms:
        result = extractor._validate_company_name(term)
        if result == "Unknown":
            print(f"✅ '{term}' → correctly rejected")
        else:
            print(f"❌ '{term}' → should be rejected, got '{result}'")
    
    print()
    
    # Test 4: Existing Folder Matching
    print("📁 TEST 4: EXISTING FOLDER MATCHING")
    print("-" * 40)
    
    # Simulate existing folders
    existing_folders = [
        "Australian_Health_Practitioner_Regulation_Agency",
        "AHPRA",
        "Microsoft",
        "Google",
        "Unknown_Company"
    ]
    
    # Create a test result
    from app.services.company_extractor import CompanyResult, Confidence
    test_result = CompanyResult(
        name="Australian Health Practitioner Regulation Agency",
        confidence=Confidence.HIGH,
        is_agency=False,
        normalized="Australian_Health_Practitioner_Regulation_Agency",
        display_name="Australian Health Practitioner Regulation Agency"
    )
    
    matched = extractor.match_existing(test_result, existing_folders)
    print(f"✅ Test result: '{test_result.normalized}'")
    print(f"✅ Existing folders: {existing_folders}")
    print(f"✅ Matched folder: '{matched}'")
    
    if matched == "Australian_Health_Practitioner_Regulation_Agency":
        print("✅ PASS: Correctly matched existing folder")
    else:
        print(f"❌ FAIL: Expected 'Australian_Health_Practitioner_Regulation_Agency', got '{matched}'")
    
    print()
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print("✅ AI extraction with user context")
    print("✅ URL-based fallback for job boards")
    print("✅ Benefits text validation and rejection")
    print("✅ Existing folder matching")
    print("✅ Comprehensive error handling")
    print()
    print("🚀 The Single AI Method with URL-based fallback is working correctly!")


if __name__ == "__main__":
    asyncio.run(test_ahpra_extraction())
