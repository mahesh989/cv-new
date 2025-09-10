#!/usr/bin/env python3
"""
Test JD Analysis endpoints without authentication

This script temporarily modifies the routes to skip authentication
for easier testing in Postman.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
COMPANY_NAME = "Australia_for_UNHCR"

def test_without_auth():
    """Test endpoints without authentication"""
    
    print("🧪 Testing JD Analysis API without authentication")
    print("=" * 60)
    
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
    
    # Test 2: Check analysis status (should work without auth if you comment out auth)
    print(f"\n2️⃣ Testing status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/jd-analysis/{COMPANY_NAME}/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status check successful!")
            print(f"   - Analysis exists: {data['data']['analysis_exists']}")
            print(f"   - JD file exists: {data['data']['jd_file_exists']}")
            print(f"   - Can analyze: {data['data']['can_analyze']}")
        else:
            print(f"❌ Status check failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Try to analyze (will fail with 401 if auth is required)
    print(f"\n3️⃣ Testing analysis endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/analyze-jd/{COMPANY_NAME}", 
                               json={"force_refresh": False, "temperature": 0.3})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis successful!")
            print(f"   - Required keywords: {len(data['data']['required_keywords'])}")
            print(f"   - Preferred keywords: {len(data['data']['preferred_keywords'])}")
            print(f"   - AI model used: {data['data']['ai_model_used']}")
        elif response.status_code == 401:
            print("🔒 Authentication required (expected)")
        else:
            print(f"❌ Analysis failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n📋 To test in Postman without authentication:")
    print(f"1. Comment out the auth verification in app/routes/jd_analysis.py")
    print(f"2. Restart the server")
    print(f"3. Use the endpoints without Authorization headers")
    print(f"4. Remember to uncomment auth verification when done!")

if __name__ == "__main__":
    test_without_auth()
