#!/usr/bin/env python3
"""
Debug script to test CV AI response specifically
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.skill_extraction.prompt_templates import get_prompt
from app.ai.ai_service import ai_service
from app.services.skill_extraction.response_parser import SkillExtractionParser
from app.services.cv_content_service import cv_content_service

async def debug_cv_ai():
    """Debug the CV AI response"""
    
    print("🔍 Debugging CV AI response...")
    print("=" * 60)
    
    # Get the actual CV content
    cv_result = cv_content_service.get_cv_content('maheshwor_tiwari.pdf', 1, use_fallback=False)
    if not cv_result['success']:
        print(f"❌ Failed to get CV content: {cv_result['error']}")
        return
    
    cv_text = cv_result['content']
    print(f"📄 CV Content loaded: {len(cv_text)} characters")
    print(f"📄 CV Content preview: {cv_text[:200]}...")
    print("=" * 60)
    
    # Get the prompt
    prompt = get_prompt('combined_structured', text=cv_text, document_type="CV")
    print("📝 Prompt being used:")
    print("-" * 40)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 40)
    
    # Generate AI response
    print("\n🤖 Generating AI response...")
    try:
        response = await ai_service.generate_response(
            prompt=prompt,
            temperature=0.1,
            max_tokens=2000
        )
        
        print("✅ AI Response received:")
        print("=" * 60)
        print(response.content)
        print("=" * 60)
        
        # Try to parse the response
        print("\n🔍 Attempting to parse response...")
        parser = SkillExtractionParser()
        parsed = parser.parse_response(response.content, "CV")
        
        print(f"📊 Parsing result:")
        print(f"  - Success: {parsed.get('parsing_success', False)}")
        print(f"  - Technical Skills: {len(parsed.get('technical_skills', []))}")
        print(f"  - Soft Skills: {len(parsed.get('soft_skills', []))}")
        print(f"  - Domain Keywords: {len(parsed.get('domain_keywords', []))}")
        
        if parsed.get('error'):
            print(f"  - Error: {parsed['error']}")
        
        if parsed.get('technical_skills'):
            print(f"  - Technical: {parsed['technical_skills'][:5]}")
        if parsed.get('soft_skills'):
            print(f"  - Soft: {parsed['soft_skills'][:5]}")
        if parsed.get('domain_keywords'):
            print(f"  - Domain: {parsed['domain_keywords'][:5]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_cv_ai())
