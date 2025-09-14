#!/usr/bin/env python3
"""
Debug script to check the actual CV AI response format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai.ai_service import AIServiceManager
from app.services.skill_extraction.prompt_templates import SkillExtractionPrompts
from app.services.cv_content_service import CVContentService

async def main():
    print("🔍 Debugging CV AI Response Format")
    
    # Initialize services
    ai_service = AIServiceManager()
    cv_service = CVContentService()
    
    # Get CV content
    cv_filename = "maheshwor_tiwari.pdf"
    cv_content_result = cv_service.get_cv_content(cv_filename)
    print(f"📄 CV Content result type: {type(cv_content_result)}")
    print(f"📄 CV Content result: {cv_content_result}")
    
    # Extract the actual content
    if isinstance(cv_content_result, dict):
        cv_content = cv_content_result.get('content', '')
    else:
        cv_content = str(cv_content_result)
    
    print(f"📄 CV Content length: {len(cv_content)} chars")
    
    # Get prompt template
    template = SkillExtractionPrompts.get_skill_extraction_template("CV", cv_content)
    system_prompt = SkillExtractionPrompts.get_system_prompt("CV")
    
    # Create a simple JD for testing
    jd_content = "Data Analyst role requiring Python, SQL, and data analysis skills."
    
    # Use the template directly (it's already formatted)
    prompt = template
    
    print(f"📝 Prompt length: {len(prompt)} chars")
    print(f"📝 System prompt length: {len(system_prompt)} chars")
    
    # Get AI response
    print("🤖 Calling AI service...")
    response = await ai_service.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        model="gpt-3.5-turbo"
    )
    
    print(f"📊 Response type: {type(response)}")
    print(f"📊 Response provider: {response.provider}")
    print(f"📊 Response model: {response.model}")
    print(f"📊 Response content length: {len(response.content)} chars")
    print("\n" + "="*80)
    print("FULL AI RESPONSE:")
    print("="*80)
    print(response.content)
    print("="*80)
    
    # Check for expected patterns
    print("\n🔍 Checking for expected patterns:")
    patterns = ["SOFT_SKILLS =", "TECHNICAL_SKILLS =", "DOMAIN_KEYWORDS ="]
    for pattern in patterns:
        if pattern in response.content:
            print(f"✅ Found: {pattern}")
        else:
            print(f"❌ Missing: {pattern}")
    
    # Look for any list-like structures
    import re
    list_patterns = [
        r'\[.*?\]',  # Any square brackets
        r'SOFT_SKILLS.*?=',  # SOFT_SKILLS assignment
        r'TECHNICAL_SKILLS.*?=',  # TECHNICAL_SKILLS assignment
        r'DOMAIN_KEYWORDS.*?=',  # DOMAIN_KEYWORDS assignment
    ]
    
    print("\n🔍 Looking for list patterns:")
    for pattern in list_patterns:
        matches = re.findall(pattern, response.content, re.DOTALL)
        if matches:
            print(f"✅ Pattern '{pattern}': {len(matches)} matches")
            for i, match in enumerate(matches[:2]):  # Show first 2 matches
                print(f"   Match {i+1}: {match[:100]}...")
        else:
            print(f"❌ Pattern '{pattern}': No matches")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
