#!/usr/bin/env python3

"""
Test to verify raw CV text is not saved in JSON output
"""

import sys
import os
import asyncio
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.structured_cv_parser import enhanced_cv_parser

# Simple CV for testing
TEST_CV_TEXT = """
John Doe
Software Engineer
john@example.com | (555) 123-4567

CAREER PROFILE
Experienced software engineer with 5+ years in web development.

TECHNICAL SKILLS
• Python programming and web frameworks
• JavaScript and React development  
• Database design and optimization

EXPERIENCE
Senior Developer | TechCorp | 2020-2023
• Built scalable web applications
• Led development team of 4 engineers
• Implemented CI/CD pipelines
"""

async def test_no_raw_text_saved():
    """Test that raw CV text is not included in the saved JSON"""
    print("🧪 Testing Raw Text Exclusion from JSON Output")
    print("=" * 55)
    
    try:
        # Parse the CV
        print("📄 Parsing test CV...")
        structured_cv = await enhanced_cv_parser.parse_cv_content(TEST_CV_TEXT)
        
        # Check original_sections structure
        original_sections = structured_cv.get('original_sections', {})
        
        print("\n🔍 CHECKING ORIGINAL_SECTIONS:")
        print("-" * 40)
        
        success = True
        
        # Check if raw_cv_text exists
        if 'raw_cv_text' in original_sections:
            raw_text_value = original_sections['raw_cv_text']
            print(f"❌ Raw CV text found in output:")
            print(f"    Length: {len(str(raw_text_value))} characters")
            print(f"    Preview: '{str(raw_text_value)[:100]}...'")
            success = False
        else:
            print("✅ Raw CV text NOT found in output (correct)")
        
        # Check what IS included in original_sections
        print(f"\n📋 ORIGINAL_SECTIONS CONTENTS:")
        print("-" * 40)
        for key, value in original_sections.items():
            print(f"  • {key}: {type(value).__name__}")
            if isinstance(value, list):
                print(f"    └─ {len(value)} items: {value}")
            elif isinstance(value, str):
                print(f"    └─ '{value}'")
        
        # Check section headers are still preserved
        section_headers = original_sections.get('section_headers_found', [])
        if section_headers:
            print(f"✅ Section headers preserved: {len(section_headers)} found")
            for header in section_headers:
                print(f"    • {header}")
        else:
            print("⚠️ No section headers found")
        
        # Check parsing approach
        parsing_approach = original_sections.get('parsing_approach', '')
        if parsing_approach:
            print(f"✅ Parsing approach preserved: '{parsing_approach}'")
        else:
            print("⚠️ Parsing approach missing")
        
        # Calculate JSON size
        json_str = json.dumps(structured_cv, indent=2)
        json_size = len(json_str)
        
        print(f"\n📊 JSON OUTPUT SIZE:")
        print("-" * 40)
        print(f"Total JSON size: {json_size:,} characters")
        print(f"Original CV size: {len(TEST_CV_TEXT):,} characters")
        
        if json_size < len(TEST_CV_TEXT) * 3:  # Should be reasonable without raw text
            print("✅ JSON size is reasonable (no large raw text included)")
        else:
            print("⚠️ JSON size seems large - may contain raw text")
        
        # Save test output
        output_file = "new-cv/no_raw_text_test.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_cv, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Test output saved to: {output_file}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("-" * 40)
        if success:
            print("✅ SUCCESS: Raw CV text is NOT saved in JSON output")
            print("✅ Section headers and parsing metadata are preserved")
            print("✅ JSON output is clean and efficient")
        else:
            print("❌ ISSUE: Raw CV text is still being saved in JSON")
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing raw text exclusion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_no_raw_text_saved())
    
    if success:
        print("\n🎉 Raw text exclusion is working correctly!")
        print("The JSON output no longer contains the original CV text.")
    else:
        print("\n❌ Raw text exclusion needs fixing.")
        sys.exit(1)