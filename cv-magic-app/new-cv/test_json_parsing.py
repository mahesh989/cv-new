#!/usr/bin/env python3
"""
Test script for JSON parsing improvements in CV tailoring service
"""
import json
import sys
import os

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.tailored_cv.services.cv_tailoring_service import CVTailoringService

def test_json_extraction():
    """Test the JSON extraction method with various AI response formats"""
    service = CVTailoringService()
    
    # Test cases for different AI response formats
    test_cases = [
        {
            "name": "Clean JSON",
            "content": '{"contact": {"name": "John Doe"}, "experience": [{"bullets": ["test"]}], "skills": []}',
            "should_pass": True
        },
        {
            "name": "JSON in markdown code block",
            "content": '''```json
{
  "contact": {"name": "John Doe"},
  "experience": [{"bullets": ["test"]}],
  "skills": []
}
```''',
            "should_pass": True
        },
        {
            "name": "JSON with extra text before",
            "content": '''Here is the optimized CV:
{
  "contact": {"name": "John Doe"},
  "experience": [{"bullets": ["test"]}], 
  "skills": []
}''',
            "should_pass": True
        },
        {
            "name": "JSON with generic code block",
            "content": '''```
{
  "contact": {"name": "John Doe"},
  "experience": [{"bullets": ["test"]}],
  "skills": []
}
```''',
            "should_pass": True
        },
        {
            "name": "Invalid JSON",
            "content": '{"invalid": json, "missing": quotes}',
            "should_pass": False
        },
        {
            "name": "Missing required fields",
            "content": '{"contact": {"name": "John Doe"}}',
            "should_pass": False
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"Content preview: {test_case['content'][:100]}...")
        
        try:
            # Test JSON extraction
            extracted_data = service._extract_and_parse_json(test_case['content'])
            print(f"✅ JSON extraction successful")
            
            # Test validation
            service._validate_tailored_json(extracted_data)
            print(f"✅ JSON validation successful")
            
            success = True
            error = None
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            success = False
            error = str(e)
        
        # Check if result matches expectation
        expected = test_case['should_pass']
        actual = success
        
        if expected == actual:
            print(f"✅ Test result matches expectation ({expected})")
            result_status = "PASS"
        else:
            print(f"❌ Test result mismatch - Expected: {expected}, Got: {actual}")
            result_status = "FAIL"
        
        results.append({
            'name': test_case['name'],
            'expected': expected,
            'actual': actual,
            'status': result_status,
            'error': error
        })
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"================")
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_icon} {result['name']}: {result['status']}")
        if result['error']:
            print(f"   Error: {result['error']}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    print("🚀 Testing JSON parsing improvements...")
    success = test_json_extraction()
    
    if success:
        print("\n🎉 All tests passed! JSON parsing improvements are working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the implementation.")
        sys.exit(1)