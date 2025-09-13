#!/usr/bin/env python3
"""
Test script with the same long JD text as the mobile app
"""

import asyncio
import aiohttp
import json

async def test_long_jd():
    """Test with the same long JD text as the mobile app"""
    
    print("🔍 Testing with long JD text...")
    print("=" * 60)
    
    # Get auth token first
    login_url = "http://localhost:8000/api/quick-login"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get auth token
            async with session.post(login_url) as response:
                if response.status != 200:
                    print("❌ Failed to get auth token")
                    return
                
                auth_data = await response.json()
                token = auth_data['access_token']
                print("✅ Got auth token")
            
            # Headers with auth
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Use the same long JD text as the mobile app
            long_jd = """Data Analyst Australia for UNHCR Job Summary Australia for UNHCR Applications close: Job posted on: 14th Mar 2025 Sydney Contract , Full Time International Aid and Development , Fundraising Not For Profit (NFP) Job description Work in a high performing, values-driven organisation Competitive salary with salary packaging benefits Hybrid work arrangement with office located in Sydney CBD Full-time 15-month contract position ABOUT US Our passionate team empowers refugees to find safety and protection when they need it most. Australia for UNHCR is the UN Refugee Agency's partner in Australia, raising funds and awareness to assist people forced to flee conflict, disaster or persecution. With more than 120 million people now forcibly displaced worldwide, this work has never been more vital. At Australia for UNHCR, we harness the generosity of Australians to help UNHCR deliver life-saving aid during humanitarian emergencies. This aid includes shelter, clean water, medicine, emergency cash assistance and counselling. We also support long-term education, healthcare and employment programs to help refugees rebuild their lives and create more secure futures. As part of the UN network, we make a difference for millions of people every year. WHO WE ARE LOOKING FOR Our people are collaborative and inclusive team players, committed to finding new ways to increase support for refugees. A highly motivated, organised and detail-oriented Data Analyst to join our high performing Business Intelligence Unit, who work closely with our business stakeholders, providing data to support data-driven business decision-making across Australia for UNHCR and New Zealand for UNHCR. A data-passionate individual with strong analytical and problem-solving skills, to play a vital part in contributing to the evolving data requirements of the organisation by providing segmented data selections, data mining, analysis, and developing and maintaining reports. YOU'LL MAKE AN IMPACT BY Delivering analytics on the business-critical objective of understanding how to maximise the value from our donors, in the form of data-mining, profile analysis, building analytical models and BI report authoring in Power BI or a similar reporting suite. Addressing data extract requirements for direct marketing campaigns with a high degree of service; manipulating data in preparation for bulk communications, updating records with contact history, and working with Fundraising stakeholders to advise on segmentation strategies considering a multi-channel communication and donor-centricity approach. Producing reports and analysis for reviewing results post campaign. Building projection and segmentation models to answer key business questions. Assisting the BI Analyst and BI Manager to administer and develop A4U's data warehouse (DWH) considering current and future business requirements to strategise and implement enhancements to the platform through research, analysis, consultation and evaluation of program needs. Working with a range of internal and external stakeholders to satisfy their business intelligence requirements for analysis, report creation, data selections, and data mining within a strong project management framework, driving evidence-based decision making throughout the organisation. WE WOULD LIKE YOU TO HAVE Minimum 2 years' experience in a similar role Experience building models in spreadsheets, and comfortable writing formulas and VBA in Excel. Experience in the development, maintenance and remediation of issues relating to data models within a SQL data warehouse environment. Strong SQL coding skills and database knowledge Experience using business intelligence tools such as Power BI, Tableau, etc. Hands on experience in querying and extracting data across multiple, disparate and complex relational databases or a data warehouse Strong project management skills to deliver multiple projects and work autonomously to meet deadlines Strong stakeholder management skills. Excellent communication and customer service skills Experience extracting data for marketing campaigns with knowledge of how to best utilise data to optimise campaign outcomes An advanced understanding of how data is used for communication purposes, the process and the governing regulations / best practice guidelines. An appreciation of data issues and their solutions, particularly de-duplication and the importance of maintaining clean data. WHAT YOU'LL GET IN RETURN Working at Australia for UNHCR means that you get to make a difference for refugees every day. Our people give their best, work with compassion, and feel valued and supported. We have an inclusive and supportive culture built on a shared purpose. How do we know this? Our employees tell us! Our 2024 employee engagement survey revealed that: 100% of employees are proud to work at Australia for UNHCR 100% of employees feel trusted and valued by their Manager 89% can be successful as their authentic selves We also offer: A competitive salary commensurate with the NFP sector Access to $15,900 salary packaging Additional leave entitlements with five weeks of annual leave A flexible and hybrid work environment A focus on wellbeing, including weekly fruit box, access to a holistic Employee Assistance Program with offerings on mental health, nutrition, parenting, financial support and much more A focus on learning and development at individual, team and organisational levels We are a workplace that embraces diversity, inclusion and equal opportunity. We recognise the value of a diverse workforce and the creation of inclusive workforce cultures. We welcome applications from people with diverse experiences and cultural backgrounds, including migrants and former refugees. For further information on this position, or to discuss any requirements that will ensure you can fully participate in our recruitment process, please reach out to our HR team: [email protected] , using the subject line: Data Analyst enquiry via EthicalJobs. Please click"""
            
            # Prepare request data with the long JD
            data = {
                "cv_filename": "maheshwor_tiwari.pdf",
                "jd_text": long_jd
            }
            
            print(f"📤 Sending request to /preliminary-analysis")
            print(f"   CV: {data['cv_filename']}")
            print(f"   JD length: {len(data['jd_text'])} characters")
            
            # Make the request
            analysis_url = "http://localhost:8000/api/preliminary-analysis"
            async with session.post(analysis_url, json=data, headers=headers) as response:
                print(f"📡 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ Request successful!")
                    
                    # Check CV skills specifically
                    if "cv_skills" in result:
                        cv_skills = result["cv_skills"]
                        print(f"\n📋 CV Skills:")
                        print(f"   Technical: {len(cv_skills.get('technical_skills', []))} skills")
                        print(f"   Soft: {len(cv_skills.get('soft_skills', []))} skills")
                        print(f"   Domain: {len(cv_skills.get('domain_keywords', []))} keywords")
                        
                        if cv_skills.get('technical_skills'):
                            print(f"   Technical skills: {cv_skills['technical_skills'][:5]}")
                        if cv_skills.get('soft_skills'):
                            print(f"   Soft skills: {cv_skills['soft_skills'][:5]}")
                        if cv_skills.get('domain_keywords'):
                            print(f"   Domain keywords: {cv_skills['domain_keywords'][:5]}")
                    
                    # Check JD skills
                    if "jd_skills" in result:
                        jd_skills = result["jd_skills"]
                        print(f"\n📋 JD Skills:")
                        print(f"   Technical: {len(jd_skills.get('technical_skills', []))} skills")
                        print(f"   Soft: {len(jd_skills.get('soft_skills', []))} skills")
                        print(f"   Domain: {len(jd_skills.get('domain_keywords', []))} keywords")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed with status {response.status}")
                    print(f"Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_long_jd())
