#!/usr/bin/env python3
"""
Test script to see the actual CV AI response
"""

import asyncio
import aiohttp
import json

async def test_cv_response():
    """Test the CV response specifically"""
    
    print("🔍 Testing CV response...")
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
            
            # Prepare request data with a simple JD to focus on CV
            data = {
                "cv_filename": "maheshwor_tiwari.pdf",
                "jd_text": "Data Analyst role requiring Python, SQL, and communication skills."
            }
            
            print(f"📤 Sending request to /preliminary-analysis")
            print(f"   CV: {data['cv_filename']}")
            print(f"   JD: {data['jd_text']}")
            
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
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed with status {response.status}")
                    print(f"Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cv_response())
