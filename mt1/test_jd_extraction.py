#!/usr/bin/env python3

import requests
import json

def test_job_extraction():
    url = "https://www.ethicaljobs.com.au/members/notoviolence/data-analyst-1"
    
    print("🔍 Testing Job Description Extraction")
    print("=" * 50)
    print(f"URL: {url}")
    print()
    
    try:
        # Test the scrape endpoint
        response = requests.post(
            "http://localhost:8000/scrape-job-description/",
            json={"url": url},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Extracted job description:")
            print("-" * 30)
            print(data.get('job_description', 'No job description found')[:500] + "...")
            print("-" * 30)
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_job_extraction() 