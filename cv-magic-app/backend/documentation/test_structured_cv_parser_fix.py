#!/usr/bin/env python3

"""
Test script to verify the structured CV parser fix
"""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.structured_cv_parser import enhanced_cv_parser

async def test_cv_parser_fix():
    """Test the structured CV parser with the current_model fix"""
    try:
        # Simple CV content for testing
        cv_content = """
        John Doe
        Software Engineer
        Email: john.doe@example.com
        Phone: (555) 123-4567
        
        EXPERIENCE:
        Senior Software Engineer at TechCorp (2020-2023)
        - Developed web applications using Python and JavaScript
        - Led a team of 5 developers
        - Improved system performance by 30%
        
        SKILLS:
        - Python, JavaScript, React, Django
        - Project Management, Leadership
        
        EDUCATION:
        Bachelor of Computer Science, University of Tech (2018)
        """
        
        print("Testing structured CV parser...")
        
        # Test the parsing
        structured_cv = await enhanced_cv_parser.parse_cv_content(cv_content)
        
        print("✅ CV parsing completed successfully")
        print(f"✅ AI Model used: {structured_cv.get('metadata', {}).get('ai_model_used', 'Not found')}")
        print(f"✅ Personal info name: {structured_cv.get('personal_information', {}).get('name', 'Not found')}")
        print(f"✅ Skills count: {len(structured_cv.get('skills', {}).get('technical_skills', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing structured CV parser: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing structured CV parser fix...")
    success = asyncio.run(test_cv_parser_fix())
    
    if success:
        print("\n🎉 Structured CV parser fix is working!")
    else:
        print("\n❌ Structured CV parser fix failed!")
        sys.exit(1)