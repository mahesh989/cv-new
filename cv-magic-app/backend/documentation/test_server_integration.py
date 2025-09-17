#!/usr/bin/env python3

"""
Quick integration test to verify the fix works in server context
"""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.ai.ai_service import ai_service
from app.services.structured_cv_parser import enhanced_cv_parser

async def test_integration():
    """Test that the AI service and CV parser work together"""
    try:
        print("Testing AI Service and CV Parser integration...")
        
        # Test 1: Check ai_service current_model property
        print(f"✅ Current AI model: {ai_service.current_model}")
        
        # Test 2: Simple CV parsing like the server does
        cv_text = """
        Jane Smith
        Data Scientist
        Email: jane.smith@email.com
        
        EXPERIENCE:
        Data Scientist at DataCorp (2021-2023)
        - Built machine learning models with Python
        - Analyzed large datasets using SQL
        
        SKILLS:
        Python, SQL, Machine Learning, Statistics
        """
        
        print("Parsing CV content...")
        structured_cv = await enhanced_cv_parser.parse_cv_content(cv_text)
        
        # Check that the AI model was recorded properly
        ai_model_used = structured_cv.get('metadata', {}).get('ai_model_used', 'NOT_FOUND')
        print(f"✅ AI model recorded in CV metadata: {ai_model_used}")
        
        # Verify the parsing worked
        name = structured_cv.get('personal_information', {}).get('name', 'NOT_FOUND')
        print(f"✅ Parsed name: {name}")
        
        if ai_model_used != 'NOT_FOUND' and name != 'NOT_FOUND':
            print("\n🎉 Integration test passed! The fix resolves the original error.")
            return True
        else:
            print("\n❌ Integration test failed - some data missing")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    
    if success:
        print("\n✅ The LLM parsing error has been successfully fixed!")
        print("The server should now work without the 'current_model' attribute error.")
    else:
        print("\n❌ Integration test failed!")
        sys.exit(1)