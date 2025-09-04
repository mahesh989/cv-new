#!/usr/bin/env python3
"""
Simple script to scrape and print JD text only
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"

def print_jd_text():
    """Scrape and print JD text from the specific URL"""
    print("🔍 Scraping JD from: https://www.ethicaljobs.com.au/members/notoviolence/data-analyst-1")
    print("=" * 80)
    
    # The specific URL
    test_url = "https://www.ethicaljobs.com.au/members/notoviolence/data-analyst-1"
    
    try:
        print("🚀 Sending request to /scrape-job-description/ endpoint...")
        response = requests.post(
            f"{BASE_URL}/scrape-job-description/",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            jd_text = result.get("job_description", "")
            
            print("✅ JD scraping successful!")
            print(f"📄 JD Text Length: {len(jd_text)} characters")
            print("\n" + "="*80)
            print("📄 JD TEXT CONTENT:")
            print("="*80)
            print(jd_text)
            print("="*80)
                
        else:
            print(f"❌ JD scraping failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Simple JD Text Scraping")
    print("=" * 80)
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Run the test
    print_jd_text()
    
    print("\n✅ JD text scraping completed!") 