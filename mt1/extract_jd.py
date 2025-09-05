#!/usr/bin/env python3
"""
Quick JD Skills Extractor - Interactive Version
==============================================

Paste your job description and get instant skill extraction with Claude Sonnet 4!

Usage: python extract_jd.py
"""

import requests
import json
import sys

def extract_skills(jd_text):
    """Extract skills from job description"""
    
    url = "http://127.0.0.1:8000/extract-jd-skills/"
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"jd_text": jd_text},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure the server is running: python -c \"import uvicorn; from src.main import app; uvicorn.run(app, host='127.0.0.1', port=8000)\"")
        return None

def display_results(data):
    """Display the extraction results in a nice format"""
    
    technical = data.get('technical_skills', [])
    soft = data.get('soft_skills', [])
    domain = data.get('domain_keywords', [])
    
    print("\n" + "="*60)
    print("🎯 CLAUDE SONNET 4 - JD SKILL EXTRACTION RESULTS")
    print("="*60)
    
    print(f"\n🔧 TECHNICAL SKILLS ({len(technical)}):")
    print("-" * 30)
    for i, skill in enumerate(technical, 1):
        print(f"{i:2d}. {skill}")
    
    print(f"\n🤝 SOFT SKILLS ({len(soft)}):")
    print("-" * 30)
    for i, skill in enumerate(soft, 1):
        print(f"{i:2d}. {skill}")
    
    print(f"\n🏢 DOMAIN KEYWORDS ({len(domain)}):")
    print("-" * 30)
    for i, keyword in enumerate(domain, 1):
        print(f"{i:2d}. {keyword}")
    
    total = len(technical + soft + domain)
    print(f"\n📊 TOTAL EXTRACTED: {total} items")
    print("="*60)

def main():
    """Main interactive loop"""
    
    print("🚀 QUICK JD SKILLS EXTRACTOR WITH CLAUDE SONNET 4")
    print("=" * 55)
    print("🤖 Using the latest Claude Sonnet 4 model")
    print("🔗 Server: http://127.0.0.1:8000")
    print("\n💡 Instructions:")
    print("   1. Paste your job description below")
    print("   2. Press Enter twice when done")
    print("   3. Get instant skill extraction!")
    print("   4. Type 'quit' to exit")
    print("\n" + "-" * 55)
    
    while True:
        print("\n📝 Paste your Job Description:")
        print("(Press Enter twice when finished, or type 'quit' to exit)")
        print("-" * 40)
        
        lines = []
        empty_lines = 0
        
        while True:
            try:
                line = input()
                
                if line.lower().strip() == 'quit':
                    print("\n👋 Goodbye!")
                    return
                
                if line.strip() == "":
                    empty_lines += 1
                    if empty_lines >= 2 and len(lines) > 0:
                        break
                else:
                    empty_lines = 0
                    lines.append(line)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return
        
        if not lines:
            print("❌ No job description entered. Please try again.")
            continue
        
        jd_text = "\n".join(lines).strip()
        
        print("\n🔄 Extracting skills with Claude Sonnet 4...")
        
        # Extract skills
        result = extract_skills(jd_text)
        
        if result:
            display_results(result)
            
            # Ask if user wants to see raw JSON
            try:
                show_json = input("\n💻 Show raw JSON response? (y/n): ").lower().strip()
                if show_json in ['y', 'yes']:
                    print("\n📋 RAW JSON RESPONSE:")
                    print("-" * 30)
                    print(json.dumps(result, indent=2))
            except KeyboardInterrupt:
                pass
        
        print("\n" + "="*60)
        print("✨ Ready for next job description!")

if __name__ == "__main__":
    main() 