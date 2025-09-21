#!/usr/bin/env python3
"""
Test script for the tailored CV save API endpoint
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/cv/tailored-cv/save"

def test_api_save():
    """Test the tailored CV save API"""
    
    print("🔍 Testing Tailored CV Save API")
    print(f"📡 Endpoint: {API_ENDPOINT}")
    
    # Test data - modify this to match your actual data structure
    test_data = {
        "company_name": "Australia_for_UNHCR",
        "cv_content": "This is updated CV content from API test!",
        "filename": "Australia_for_UNHCR_tailored_cv_20250921_111415.json"  # Optional
    }
    
    print(f"📤 Sending test data:")
    print(json.dumps(test_data, indent=2))
    
    try:
        # Make the API call
        response = requests.put(
            API_ENDPOINT,
            json=test_data,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success Response:")
            print(json.dumps(result, indent=2))
            
            # Verify the file was actually updated
            if "file_path" in result:
                file_path = Path(result["file_path"])
                if file_path.exists():
                    print(f"✅ File exists: {file_path}")
                    with open(file_path, 'r') as f:
                        saved_data = json.load(f)
                    print(f"📄 Saved file content (first 200 chars):")
                    print(str(saved_data)[:200] + "...")
                    
                    # Check if our test content is in the file
                    if "This is updated CV content from API test!" in str(saved_data):
                        print("✅ Test content found in saved file!")
                    else:
                        print("❌ Test content NOT found in saved file")
                else:
                    print(f"❌ File does not exist: {file_path}")
        else:
            print(f"❌ Error Response:")
            try:
                error = response.json()
                print(json.dumps(error, indent=2))
            except:
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the server running on localhost:8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def inspect_existing_file():
    """Inspect the existing tailored CV file structure"""
    
    print("\n🔍 Inspecting existing tailored CV file structure")
    
    file_path = Path("cv-analysis/Australia_for_UNHCR/Australia_for_UNHCR_tailored_cv_20250921_111415.json")
    
    if file_path.exists():
        print(f"📄 File exists: {file_path}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        print(f"📊 File structure:")
        print(f"  - Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"  - Keys: {list(data.keys())}")
            for key, value in data.items():
                print(f"    - {key}: {type(value)} (length: {len(str(value)) if value else 0})")
                
        print(f"📄 First 300 characters of content:")
        print(str(data)[:300] + "...")
    else:
        print(f"❌ File not found: {file_path}")
        
        # Look for any tailored CV files
        company_dir = Path("cv-analysis/Australia_for_UNHCR")
        if company_dir.exists():
            tailored_files = list(company_dir.glob("*tailored_cv*.json"))
            print(f"📁 Found {len(tailored_files)} tailored CV files:")
            for file in tailored_files:
                print(f"  - {file.name}")
        else:
            print(f"❌ Company directory not found: {company_dir}")

def main():
    """Main test function"""
    
    print("=" * 60)
    print("🧪 TAILORED CV SAVE API TEST")
    print("=" * 60)
    
    # First inspect the existing file
    inspect_existing_file()
    
    # Then test the API
    test_api_save()
    
    print("\n" + "=" * 60)
    print("✅ Test completed")
    print("=" * 60)
    
    print("\n📝 Next steps:")
    print("1. Check the server logs for detailed debug information")
    print("2. Verify the file content was actually updated")
    print("3. Test from your Flutter frontend with the same data structure")

if __name__ == "__main__":
    main()
