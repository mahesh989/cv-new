#!/usr/bin/env python3
"""
Test script to verify the enhanced response parser works with different AI model formats
"""

import logging
from app.services.skill_extraction.response_parser import SkillExtractionParser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_response_parser():
    """Test the enhanced response parser with different AI model formats"""
    
    print("🧪 Testing Enhanced Response Parser")
    print("=" * 50)
    
    # Test 1: GPT-4o Mini format (Python variables)
    gpt4o_response = """
    SOFT_SKILLS = ["Communication", "Leadership", "Problem-solving"]
    TECHNICAL_SKILLS = ["Python", "SQL", "Machine Learning"]
    DOMAIN_KEYWORDS = ["Data Analysis", "AI", "Research"]
    """
    
    print("\n1️⃣ Testing GPT-4o Mini Format (Python Variables):")
    result1 = SkillExtractionParser.parse_response(gpt4o_response, "CV")
    print(f"   Soft Skills: {result1['soft_skills']}")
    print(f"   Technical Skills: {result1['technical_skills']}")
    print(f"   Domain Keywords: {result1['domain_keywords']}")
    print(f"   Success: {result1['parsing_success']}")
    
    # Test 2: GPT-3.5 Turbo format (Markdown with **)
    gpt35_response = """
    **SOFT SKILLS:**
    - Communication
    - Leadership
    - Problem-solving
    
    **TECHNICAL SKILLS:**
    - Python
    - SQL
    - Machine Learning
    
    **DOMAIN KEYWORDS:**
    - Data Analysis
    - AI
    - Research
    """
    
    print("\n2️⃣ Testing GPT-3.5 Turbo Format (Markdown):")
    result2 = SkillExtractionParser.parse_response(gpt35_response, "CV")
    print(f"   Soft Skills: {result2['soft_skills']}")
    print(f"   Technical Skills: {result2['technical_skills']}")
    print(f"   Domain Keywords: {result2['domain_keywords']}")
    print(f"   Success: {result2['parsing_success']}")
    
    # Test 3: DeepSeek format (Section headers)
    deepseek_response = """
    Soft Skills:
    - Communication
    - Leadership
    - Problem-solving
    
    Technical Skills:
    - Python
    - SQL
    - Machine Learning
    
    Domain Keywords:
    - Data Analysis
    - AI
    - Research
    """
    
    print("\n3️⃣ Testing DeepSeek Format (Section Headers):")
    result3 = SkillExtractionParser.parse_response(deepseek_response, "CV")
    print(f"   Soft Skills: {result3['soft_skills']}")
    print(f"   Technical Skills: {result3['technical_skills']}")
    print(f"   Domain Keywords: {result3['domain_keywords']}")
    print(f"   Success: {result3['parsing_success']}")
    
    # Test 4: Claude format (Alternative bullets)
    claude_response = """
    TECHNICAL SKILLS:
    * Python
    * SQL
    * Machine Learning
    
    SOFT SKILLS:
    * Communication
    * Leadership
    * Problem-solving
    
    DOMAIN KEYWORDS:
    * Data Analysis
    * AI
    * Research
    """
    
    print("\n4️⃣ Testing Claude Format (Asterisk Bullets):")
    result4 = SkillExtractionParser.parse_response(claude_response, "CV")
    print(f"   Soft Skills: {result4['soft_skills']}")
    print(f"   Technical Skills: {result4['technical_skills']}")
    print(f"   Domain Keywords: {result4['domain_keywords']}")
    print(f"   Success: {result4['parsing_success']}")
    
    # Summary
    print(f"\n📊 Summary:")
    successful_tests = sum([
        result1['parsing_success'],
        result2['parsing_success'],
        result3['parsing_success'],
        result4['parsing_success']
    ])
    print(f"   Successful tests: {successful_tests}/4")
    print(f"   ✅ Parser is now model-agnostic!" if successful_tests == 4 else f"   ❌ Some tests failed")

if __name__ == "__main__":
    test_response_parser()
