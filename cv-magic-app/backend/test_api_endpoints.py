#!/usr/bin/env python3
"""
Quick API endpoint test script for Postman verification

This script tests the JD Analysis API endpoints to ensure they're working
before testing in Postman.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
COMPANY_NAME = "Australia_for_UNHCR"

# You'll need to replace this with a valid token
# For testing, you might want to temporarily disable auth in the routes
AUTH_TOKEN = "your_bearer_token_here"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Testing {method} {endpoint}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            try:
                json_data = response.json()
                print(f"Response Keys: {list(json_data.keys())}")
                if 'data' in json_data:
                    print(f"Data Keys: {list(json_data['data'].keys())}")
            except:
                print("Response: (non-JSON)")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {response.text}")
        
        return response
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on port 8000")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all endpoint tests"""
    print("🚀 Testing JD Analysis API Endpoints")
    print("=" * 50)
    
    # Test 1: Check server status
    print("\n1️⃣ Testing server status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
    except:
        print("❌ Server is not running. Please start it with:")
        print("python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: Check analysis status
    test_endpoint("GET", f"/api/jd-analysis/{COMPANY_NAME}/status")
    
    # Test 3: Analyze JD (this will create analysis if it doesn't exist)
    test_endpoint("POST", f"/api/analyze-jd/{COMPANY_NAME}", {
        "force_refresh": False,
        "temperature": 0.3
    })
    
    # Test 4: Get saved analysis
    test_endpoint("GET", f"/api/jd-analysis/{COMPANY_NAME}")
    
    # Test 5: Get all keywords
    test_endpoint("GET", f"/api/jd-analysis/{COMPANY_NAME}/keywords", params={"keyword_type": "all"})
    
    # Test 6: Get required keywords
    test_endpoint("GET", f"/api/jd-analysis/{COMPANY_NAME}/keywords", params={"keyword_type": "required"})
    
    # Test 7: Get preferred keywords
    test_endpoint("GET", f"/api/jd-analysis/{COMPANY_NAME}/keywords", params={"keyword_type": "preferred"})
    
    # Test 8: Test error handling (non-existent company)
    test_endpoint("GET", f"/api/jd-analysis/NonExistentCompany/status")
    
    print("\n🎉 API endpoint testing completed!")
    print("=" * 50)
    print("\n📋 Next steps for Postman:")
    print("1. Import the endpoints from the POSTMAN_JD_ANALYSIS_TESTS.md file")
    print("2. Set up your authentication token")
    print("3. Run the tests in Postman")
    print("4. Check the response formats match the expected structure")

if __name__ == "__main__":
    main()
