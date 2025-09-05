#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from job_scraper import scrape_job_description

def test_jd_extraction():
    url = "https://www.ethicaljobs.com.au/members/notoviolence/data-analyst-1"
    
    print("🔍 Testing Job Description Extraction Directly")
    print("=" * 50)
    print(f"URL: {url}")
    print()
    
    try:
        print("⏳ Starting extraction...")
        result = scrape_job_description(url)
        
        print("✅ Extraction completed!")
        print(f"📏 Result length: {len(result)} characters")
        print()
        print("📄 Extracted content:")
        print("-" * 40)
        print(result[:1000] + "..." if len(result) > 1000 else result)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jd_extraction() 