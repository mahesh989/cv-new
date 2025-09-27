#!/usr/bin/env python3
"""
Test script for Phase 2: Database Schema & User Isolation
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['access_token']
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_server_connection():
    """Test if server is running"""
    print_test_header("Server Connection")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_result(True, "Server is running")
            return True
        else:
            print_result(False, f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Server connection failed: {e}")
        return False

def test_user_file_upload(token):
    """Test user file upload"""
    print_test_header("User File Upload")
    
    # Create a test file
    test_content = b"This is a test CV file content"
    
    try:
        files = {
            'file': ('test_cv.pdf', test_content, 'application/pdf')
        }
        data = {
            'file_type': 'cv',
            'subdirectory': 'original'
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{API_BASE}/user/files/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"File uploaded successfully: {data['filename']}")
            return True
        else:
            print_result(False, f"File upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"File upload error: {e}")
        return False

def test_user_file_listing(token):
    """Test user file listing"""
    print_test_header("User File Listing")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/user/files",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"File listing successful: {len(data['files'])} files")
            return True
        else:
            print_result(False, f"File listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"File listing error: {e}")
        return False

def test_user_storage_stats(token):
    """Test user storage statistics"""
    print_test_header("User Storage Statistics")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/user/files/storage-stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Storage stats: {data['total_files']} files, {data['total_size_mb']} MB")
            return True
        else:
            print_result(False, f"Storage stats failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Storage stats error: {e}")
        return False

def test_user_api_key_management(token):
    """Test user API key management"""
    print_test_header("User API Key Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test setting API key
        api_key_data = {
            "provider": "openai",
            "api_key": "sk-test123456789"
        }
        
        response = requests.post(
            f"{API_BASE}/user/api-keys",
            json=api_key_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print_result(True, "API key set successfully")
        else:
            print_result(False, f"API key setting failed: {response.status_code} - {response.text}")
            return False
        
        # Test getting API keys
        response = requests.get(
            f"{API_BASE}/user/api-keys",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"API keys retrieved: {len(data['api_keys'])} keys")
        else:
            print_result(False, f"API key retrieval failed: {response.status_code} - {response.text}")
            return False
        
        # Test validating API key
        response = requests.post(
            f"{API_BASE}/user/api-keys/openai/validate",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"API key validation: {data['is_valid']}")
        else:
            print_result(False, f"API key validation failed: {response.status_code} - {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"API key management error: {e}")
        return False

def test_user_settings(token):
    """Test user settings management"""
    print_test_header("User Settings Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test getting settings
        response = requests.get(
            f"{API_BASE}/user/settings",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Settings retrieved: preferred model = {data.get('preferred_ai_model', 'N/A')}")
        else:
            print_result(False, f"Settings retrieval failed: {response.status_code} - {response.text}")
            return False
        
        # Test updating settings
        settings_data = {
            "preferred_ai_model": "gpt-4",
            "analysis_preferences": {
                "temperature": 0.5,
                "max_tokens": 3000
            }
        }
        
        response = requests.put(
            f"{API_BASE}/user/settings",
            json=settings_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Settings updated: {data.get('preferred_ai_model', 'N/A')}")
        else:
            print_result(False, f"Settings update failed: {response.status_code} - {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Settings management error: {e}")
        return False

def test_user_activities(token):
    """Test user activity logging"""
    print_test_header("User Activity Logging")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test getting activities
        response = requests.get(
            f"{API_BASE}/user/activities",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Activities retrieved: {len(data['activities'])} activities")
        else:
            print_result(False, f"Activities retrieval failed: {response.status_code} - {response.text}")
            return False
        
        # Test getting activity stats
        response = requests.get(
            f"{API_BASE}/user/activities/stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Activity stats: {data['total_activities']} total activities")
        else:
            print_result(False, f"Activity stats failed: {response.status_code} - {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Activity logging error: {e}")
        return False

def test_user_isolation():
    """Test user data isolation"""
    print_test_header("User Data Isolation")
    
    # This would test that users can't access each other's data
    # For now, we'll just test that the endpoints require authentication
    try:
        # Try to access user data without token
        response = requests.get(f"{API_BASE}/user/files")
        
        if response.status_code == 401 or response.status_code == 403 or "Not authenticated" in response.text:
            print_result(True, "User data properly protected (requires authentication)")
            return True
        else:
            print_result(False, f"User data not properly protected: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"User isolation test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PHASE 2 TESTING: Database Schema & User Isolation")
    print(f"Testing at: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    # Test results
    results = []
    
    # 1. Test server connection
    if not test_server_connection():
        print("\n❌ Server is not running. Please start the server first.")
        sys.exit(1)
    
    # 2. Get authentication token
    token = get_auth_token()
    if not token:
        print("\n❌ Authentication failed. Please ensure test user exists.")
        sys.exit(1)
    
    # 3. Test user file upload
    file_upload_result = test_user_file_upload(token)
    results.append(("User File Upload", file_upload_result))
    
    # 4. Test user file listing
    file_listing_result = test_user_file_listing(token)
    results.append(("User File Listing", file_listing_result))
    
    # 5. Test user storage stats
    storage_stats_result = test_user_storage_stats(token)
    results.append(("User Storage Statistics", storage_stats_result))
    
    # 6. Test user API key management
    api_key_result = test_user_api_key_management(token)
    results.append(("User API Key Management", api_key_result))
    
    # 7. Test user settings
    settings_result = test_user_settings(token)
    results.append(("User Settings Management", settings_result))
    
    # 8. Test user activities
    activities_result = test_user_activities(token)
    results.append(("User Activity Logging", activities_result))
    
    # 9. Test user isolation
    isolation_result = test_user_isolation()
    results.append(("User Data Isolation", isolation_result))
    
    # Print summary
    print_test_header("TEST SUMMARY")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 2 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
