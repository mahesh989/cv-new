#!/usr/bin/env python3
"""
Direct test of updated extraction logic with provided JD
"""

import asyncio
import time
from fastapi import Request

# Mock request class for testing
class MockRequest:
    def __init__(self, data):
        self._data = data
    async def json(self):
        return self._data

async def test_extraction_direct():
    print("🧪 Testing Updated Extraction Logic with Provided JD")
    print("=" * 60)
    try:
        from src.main import extract_skills_dynamic
        print("✅ Successfully imported extraction function")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return

    # Provided JD
    jd_text = '''Data Analyst No To Violence Job Summary No To Violence Applications close: Job posted on: 1st Aug 2022 Melbourne > CBD & Inner Suburbs Melbourne Contract , Full Time Information Technology & Digital , Policy and Research Not For Profit (NFP) Job description Work for an organisation genuinely making a difference in the community Leading organisation in ending family violence Melbourne CBD Office, close to public transport with hybrid working About us No to Violence is Australia’s largest peak body for services and individuals that work with men who use family violence. No to Violence operates the national Men’s Referral Service, the national Brief Intervention Services and the Victorian based Perpetrator Accommodation Support Service, free, confidential counselling, referral and support services. We have strong values of Change, Leadership, Gender Equity and Accountability. About the role The Data Analyst will be responsible for analysing data sets and reporting using different methodologies and business analytical tools. The role will also communicate analysis findings to management, funding bodies and other key stakeholders. The role will: Fulfil reporting requirements to meet regulatory and governance requirements Develop reports using the Business Intelligence (BI) tools Performing analysis to assess data quality and meaning of data Be responsible for all Systems Administration on the Business Intelligence platforms Ensure data collection, storage and usage is in line with contractual obligations Manage the Workforce Planner’s performance This role is Full-Time, Fixed Term until 30 June 2024. To be successful, you will have: Tertiary qualification in IT, Management Information Systems or Data Analytics Demonstrated knowledge of Business Intelligence tools Technical proficiency with databases Advanced Microsoft Excel skills Experience troubleshooting as a Systems Administrator or Super User Strong reporting capability, particularly regarding reporting against set KPIs Further details relating to the key result areas of this role can be found in the position description on our website - https://ntv. au/about-us/work-with-us/ What we offer We provide a positive work culture and a diverse and inclusive environment. Our people matter to us, and we are committed to supporting them and their wellbeing. We also play an active role in the professional development of our staff. Some other benefits we offer include Salary Packaging – tax free salary benefits of up to $15,900 per year plus up to $2,650 per year for entertainment benefits Additional leave including bonus leave, career break and paid parental leave Purchased leave options available Generous paid study leave Portable Long Service Leave EAP for employees and family An office that is always stocked with snacks. How to Apply To apply please submit an up-to-date resume and cover letter (no longer than 1 page) outlining your relevant experience aligned to the Key Role Responsibilities and Mandatory Requirements. Applications will be reviewed as received until the position is filled however do not delay in applying if you believe this role is for you. Please be advised that only applicants successful in progressing to interview will be contacted. Any questions please contact [email protected] using the subject line: Data Analyst enquiry via EthicalJobs. NTV values diversity and encourages applications from candidates of all backgrounds, including Aboriginal and Torres Strait Islander peoples and people of colour. We value people of all abilities and diversity of culture, faith, gender identity and sexual orientation. We welcome unique contributions and perspectives of all people to ensure our workforce is representative of the communities we work with and live in. How to apply This job ad has now expired, and applications are no longer being accepted. Job Summary No To Violence Applications close: Job posted on: 1st Aug 2022 Melbourne > CBD & Inner Suburbs Melbourne Contract , Full Time Information Technology & Digital , Policy and Research Not For Profit (NFP) More from this Employer.'''

    mock_request = MockRequest({"mode": "jd", "jd_text": jd_text})
    start_time = time.time()
    result = await extract_skills_dynamic(mock_request)
    end_time = time.time()
    print(f"\n⏱️ Extraction completed in {end_time - start_time:.2f} seconds\n")
    print("--- Extracted Skills ---")
    print("Soft Skills:", result.get("soft_skills"))
    print("Technical Skills:", result.get("technical_skills"))
    print("Domain Keywords:", result.get("domain_keywords"))
    print("\nRaw Claude Output:\n", result.get("raw_response")[:1200], "...\n...")

if __name__ == "__main__":
    asyncio.run(test_extraction_direct()) 