#!/usr/bin/env python3
"""
Detailed test of URL scraping to debug the Advertising Industry Careers issue
"""

import requests
from bs4 import BeautifulSoup
import re

def test_detailed_scraping():
    """Test detailed scraping to understand the website structure"""
    
    print("🔍 Detailed URL Scraping Analysis")
    print("=" * 60)
    
    url = "https://advertisingindustry.careers/job/bi-engineer-data-analyst-6da0267f-f149-4aaa-a160-210f9ad61cae/?utm_source=joraau&utm_campaign=joraau&utm_medium=cpc"
    
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        }
        
        print("1️⃣ Fetching URL...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"   ✅ Status Code: {response.status_code}")
        print(f"   📊 Content Length: {len(response.text)} characters")
        print()
        
        print("2️⃣ Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"   ✅ HTML parsed successfully")
        print()
        
        print("3️⃣ Analyzing HTML Structure:")
        
        # Check for common job content selectors
        selectors_to_test = [
            'main', 'article',
            '[class*="job-description"]', '[class*="job-details"]', '[class*="job-content"]',
            '[class*="description"]', '[class*="details"]', '[class*="content"]',
            '.job-description', '.job-details', '.job-content',
            '.description', '.details', '.content',
            '#job-description', '#job-details', '#job-content',
            '#description', '#details', '#content'
        ]
        
        found_content = {}
        for selector in selectors_to_test:
            elements = soup.select(selector)
            if elements:
                text = elements[0].get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 50:  # Only show substantial content
                    found_content[selector] = len(text)
                    print(f"   ✅ {selector}: {len(text)} characters")
        
        if not found_content:
            print("   ⚠️  No substantial content found with common selectors")
        
        print()
        
        print("4️⃣ Checking for specific text patterns:")
        
        # Look for specific text that should be in the job description
        page_text = soup.get_text()
        patterns_to_find = [
            "Drive is Nine's brand",
            "Nine Entertainment",
            "Data Engineer role",
            "Power BI",
            "5+ years of experience",
            "Bachelor's degree",
            "McMahons Point, NSW"
        ]
        
        for pattern in patterns_to_find:
            if pattern in page_text:
                print(f"   ✅ Found: '{pattern}'")
            else:
                print(f"   ❌ Missing: '{pattern}'")
        
        print()
        
        print("5️⃣ Full page text analysis:")
        full_text = soup.get_text(separator=' ', strip=True)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        print(f"   📊 Full page text length: {len(full_text)} characters")
        print(f"   📊 Full page word count: {len(full_text.split())} words")
        
        if len(full_text) > 1000:
            print("   📋 First 500 characters of full text:")
            print("   " + "-" * 40)
            print("   " + full_text[:500] + "...")
            print("   " + "-" * 40)
        
        print()
        
        print("6️⃣ Checking for JavaScript/SPA content:")
        scripts = soup.find_all('script')
        print(f"   📊 Found {len(scripts)} script tags")
        
        # Check if content might be loaded via JavaScript
        if len(scripts) > 5:
            print("   ⚠️  High number of scripts detected - might be a Single Page Application")
            print("   💡 Content might be loaded dynamically via JavaScript")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Detailed Scraping Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_detailed_scraping()
