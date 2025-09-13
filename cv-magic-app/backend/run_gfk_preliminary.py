#!/usr/bin/env python3
"""
Run Preliminary Analysis for GfK

This script runs the preliminary analysis to create all necessary files for GfK.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# GfK Job Description
GFK_JD = """
About Us
GfK.  Growth from Knowledge.
For over 89 years, we have earned the trust of our clients around the world by solving critical business questions in their decision-making process around consumers, markets, brands and media. Our reliable data and insights, together with advanced AI capabilities, have shaped the decisions of the world's largest companies. With our innovations, we're enabling our clients to be ahead of what's next.
We are proud to be on a transformational journey from a traditional market research company to a prescriptive data analytics and consulting partner for our clients. As part of the world leading media company Bertelsmann, our goal is to accelerate the impact of brave decisions that successfully drive commerce in the Technical Consumer Goods industry and beyond.

The Role:
The Analyst TCG AU is responsible for the quality and accuracy of our retailer data to ensure we provide the highest standard of data and insights to the Technical Consumer Goods industry in Australia.
This role is a great opportunity for an enthusiastic and self-motivated junior data analyst to learn and develop their analytics skills. You will be working with large data sets and performing data cleansing, analysing and interpreting market data at brand and model level, resolving data queries and be responsible for meeting weekly and monthly deadlines.
 
Responsibilities include:
• Working with large data sets and performing data cleansing
• Analysing and interpreting market data at brand and model level
• Assisting with the development of reporting processes
• Taking ownership of data quality and timeliness
• Resolving data queries internally and with external clients
• Meeting weekly and monthly deadlines
• Managing multiple tasks

We are looking for people who have:
Essential
• 1–3 years' experience in analytics, data modelling, or data visualisation.
• Intermediate/Advanced Excel skills
• Basic/Intermediate programming skills (SQL, Python)
• Excellent communication skills
• Proven analytical ability with high attention to detail
• 1–2 years' experience managing a small team, contributing as a team player, and demonstrate the ability to adapt quickly to changing business needs
 
Desirable but not essential:
• Power BI
• Tableau
"""

async def run_preliminary_analysis():
    """Run preliminary analysis via API"""
    
    print("🚀 Running preliminary analysis for GfK...")
    print("=" * 60)
    
    # Get a quick login token first
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
            
            # Prepare request data
            data = {
                "cv_filename": "Maheshwor Tiwari CV.pdf",
                "jd_text": GFK_JD,
                "config_name": None
            }
            
            # Run preliminary analysis
            analysis_url = "http://localhost:8000/api/preliminary-analysis"
            async with session.post(analysis_url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Preliminary analysis completed successfully!")
                    
                    # Print results summary
                    if "cv_skills" in result:
                        cv_skills = result["cv_skills"]
                        print(f"\nCV Skills Extracted:")
                        print(f"  - Technical: {len(cv_skills.get('technical_skills', []))} skills")
                        print(f"  - Soft: {len(cv_skills.get('soft_skills', []))} skills")
                        print(f"  - Domain: {len(cv_skills.get('domain_keywords', []))} keywords")
                    
                    if "jd_skills" in result:
                        jd_skills = result["jd_skills"]
                        print(f"\nJD Requirements Extracted:")
                        print(f"  - Technical: {len(jd_skills.get('technical_skills', []))} skills")
                        print(f"  - Soft: {len(jd_skills.get('soft_skills', []))} skills")
                        print(f"  - Domain: {len(jd_skills.get('domain_keywords', []))} keywords")
                    
                    if "saved_file_path" in result:
                        print(f"\nAnalysis saved to: {result['saved_file_path']}")
                    
                    print("\n✅ Preliminary analysis complete. The pipeline will now run in the background.")
                    print("   This includes: JD Analysis → CV-JD Matching → Component Analysis → ATS Calculation")
                    print("\n⏳ Please wait a few seconds for the pipeline to complete...")
                    
                else:
                    error = await response.text()
                    print(f"❌ Preliminary analysis failed with status {response.status}")
                    print(f"Error: {error}")
                    
    except Exception as e:
        print(f"❌ Failed to run preliminary analysis: {e}")


async def main():
    """Main function"""
    await run_preliminary_analysis()
    
    # Wait a bit for the async pipeline to complete
    print("\nWaiting 10 seconds for background pipeline to complete...")
    await asyncio.sleep(10)
    
    print("\n" + "=" * 60)
    print("Now you can run the test script to check if component analysis completed:")
    print("  python test_gfk_pipeline.py")
    print("\nOr manually trigger the complete pipeline:")
    print("  python test_gfk_pipeline.py")


if __name__ == "__main__":
    asyncio.run(main())
