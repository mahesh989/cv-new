#!/usr/bin/env python3
"""
Test script for real CV tailoring endpoint with Australia_for_UNHCR data
"""

import requests
import json
import sys

def test_real_cv_tailoring():
    """Test the real CV tailoring endpoint"""
    
    url = "http://localhost:8000/api/tailored-cv/tailor-real"
    
    payload = {
        "company": "Australia_for_UNHCR",
        "custom_instructions": "Focus on data analysis skills for humanitarian work",
        "target_ats_score": 85
    }
    
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_JWT_TOKEN"  # Would need this in real usage
    }
    
    try:
        print("🎯 Testing Real CV Tailoring Endpoint...")
        print(f"URL: {url}")
        print(f"Company: {payload['company']}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Real CV Tailoring Response:")
            
            if result.get("success"):
                tailored_cv = result.get("tailored_cv", {})
                print(f"  Target Company: {tailored_cv.get('target_company')}")
                print(f"  Target Role: {tailored_cv.get('target_role')}")
                print(f"  Estimated ATS Score: {tailored_cv.get('estimated_ats_score')}")
                print(f"  Keywords Integrated: {len(tailored_cv.get('keywords_integrated', []))}")
                
                # Show enhanced experience example
                experience = tailored_cv.get("experience", [])
                if experience:
                    print(f"\n📝 Enhanced Experience Example:")
                    first_exp = experience[0]
                    print(f"  {first_exp.get('title')} at {first_exp.get('company')}")
                    for bullet in first_exp.get("bullets", [])[:2]:
                        print(f"    • {bullet}")
                
                # Show processing summary
                summary = result.get("processing_summary", {})
                print(f"\n📊 Processing Summary:")
                print(f"  Original bullets: {summary.get('original_bullet_points', 'N/A')}")
                print(f"  Tailored bullets: {summary.get('tailored_bullet_points', 'N/A')}")
                print(f"  ATS improvement: +{summary.get('estimated_ats_improvement', 0)} points")
                
                # Save result to file for inspection
                with open("real_tailored_cv_result.json", "w") as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"\n💾 Full result saved to: real_tailored_cv_result.json")
                
            else:
                print("❌ CV Tailoring failed:")
                print(f"  Error: {result.get('processing_summary', {}).get('error')}")
                
        elif response.status_code == 404:
            print("❌ Company data not found:")
            print(f"  {response.json().get('detail', 'Unknown error')}")
            print("\n💡 Available companies can be checked at: /api/tailored-cv/available-companies-real")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to server. Is it running on localhost:8000?")
        print("💡 Start server with: cd backend && python -m uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Real CV generation might take longer (60+ seconds).")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_available_companies():
    """Test the available companies endpoint"""
    
    url = "http://localhost:8000/api/tailored-cv/available-companies-real"
    
    try:
        print("\n🏢 Testing Available Companies Endpoint...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            companies = result.get("companies", [])
            print(f"✅ Found {len(companies)} companies:")
            
            for company in companies:
                print(f"  📁 {company['display_name']} ({company['company']})")
                print(f"    📄 File: {company['recommendation_file']}")
                print(f"    🕐 Updated: {company['last_updated']}")
        else:
            print(f"❌ Failed to get companies: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting companies: {e}")


if __name__ == "__main__":
    # Test available companies first
    test_available_companies()
    
    # Then test CV tailoring
    test_real_cv_tailoring()
    
    print("\n" + "="*60)
    print("📋 Next Steps:")
    print("1. Check the generated 'real_tailored_cv_result.json' file")
    print("2. Compare original vs tailored CV content")
    print("3. Verify ATS score improvements")
    print("4. Test with Flutter app: flutter run")
    print("="*60)