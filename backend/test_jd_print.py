#!/usr/bin/env python3
"""
Script to scrape and print JD text from a specific URL
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"

def scrape_and_print_jd():
    """Scrape JD from the specific URL and print the content"""
    print("🔍 Scraping JD from: https://www.ethicaljobs.com.au/members/notoviolence/data-analyst-1")
    print("=" * 80)
    
    # The specific URL you want to test
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
            print("📄 COMPLETE JD TEXT CONTENT:")
            print("="*80)
            print(jd_text)
            print("="*80)
            
            # Also test skill extraction
            print("\n🚀 Testing JD skills extraction...")
            skills_response = requests.post(
                f"{BASE_URL}/extract-jd-skills/",
                json={"jd_text": jd_text},
                headers={"Content-Type": "application/json"}
            )
            
            if skills_response.status_code == 200:
                skills_result = skills_response.json()
                print("✅ JD skills extraction successful!")
                print(f"📊 Extracted Skills:")
                print(f"   Technical: {skills_result.get('technical_skills', [])}")
                print(f"   Soft: {skills_result.get('soft_skills', [])}")
                print(f"   Domain: {skills_result.get('domain_keywords', [])}")
                print(f"   Quality Metrics: {skills_result.get('quality_metrics', {})}")
            else:
                print(f"❌ JD skills extraction failed: {skills_response.status_code}")
                print(f"Error: {skills_response.text}")
                
        else:
            print(f"❌ JD scraping failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing JD Text Scraping and Printing")
    print("=" * 80)
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Run the test
    scrape_and_print_jd()
    
    print("\n✅ JD text scraping and printing completed!")
    print("Check the output above to see the complete JD text content.") 