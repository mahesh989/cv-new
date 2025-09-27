#!/usr/bin/env python3
"""
Test script for Phase 1: Core Authentication & User Management
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

def test_user_registration():
    """Test user registration"""
    print_test_header("User Registration")
    
    # Test data
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"User registered successfully: {data['username']}")
            return data
        else:
            print_result(False, f"Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_result(False, f"Registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print_test_header("User Login")
    
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
            print_result(True, f"User login successful: {data['user']['email']}")
            return data['access_token']
        else:
            print_result(False, f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_result(False, f"Login error: {e}")
        return None

def test_admin_login():
    """Test admin login"""
    print_test_header("Admin Login")
    
    admin_data = {
        "email": "admin@cvapp.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/admin/login",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Admin login successful: {data['user']['email']}")
            return data['access_token']
        else:
            print_result(False, f"Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_result(False, f"Admin login error: {e}")
        return None

def test_user_profile(token):
    """Test user profile access"""
    print_test_header("User Profile Access")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/auth/profile",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Profile access successful: {data['email']}")
            return True
        else:
            print_result(False, f"Profile access failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Profile access error: {e}")
        return False

def test_admin_functions(admin_token):
    """Test admin functions"""
    print_test_header("Admin Functions")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test system stats
        response = requests.get(
            f"{API_BASE}/admin/system-stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"System stats: {data}")
        else:
            print_result(False, f"System stats failed: {response.status_code} - {response.text}")
            return False
        
        # Test list users
        response = requests.get(
            f"{API_BASE}/admin/users",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"User list retrieved: {len(data)} users")
            return True
        else:
            print_result(False, f"User list failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Admin functions error: {e}")
        return False

def test_invalid_credentials():
    """Test invalid credentials"""
    print_test_header("Invalid Credentials")
    
    invalid_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 401:
            print_result(True, "Invalid credentials properly rejected")
            return True
        else:
            print_result(False, f"Invalid credentials not rejected: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Invalid credentials test error: {e}")
        return False

def test_duplicate_registration():
    """Test duplicate registration"""
    print_test_header("Duplicate Registration")
    
    duplicate_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=duplicate_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print_result(True, "Duplicate registration properly rejected")
            return True
        else:
            print_result(False, f"Duplicate registration not rejected: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Duplicate registration test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PHASE 1 TESTING: Core Authentication & User Management")
    print(f"Testing at: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    # Test results
    results = []
    
    # 1. Test server connection
    if not test_server_connection():
        print("\n❌ Server is not running. Please start the server first.")
        sys.exit(1)
    
    # 2. Test user registration
    user_data = test_user_registration()
    results.append(("User Registration", user_data is not None))
    
    # 3. Test duplicate registration
    duplicate_result = test_duplicate_registration()
    results.append(("Duplicate Registration Rejection", duplicate_result))
    
    # 4. Test user login
    user_token = test_user_login()
    results.append(("User Login", user_token is not None))
    
    # 5. Test user profile
    if user_token:
        profile_result = test_user_profile(user_token)
        results.append(("User Profile Access", profile_result))
    
    # 6. Test admin login
    admin_token = test_admin_login()
    results.append(("Admin Login", admin_token is not None))
    
    # 7. Test admin functions
    if admin_token:
        admin_result = test_admin_functions(admin_token)
        results.append(("Admin Functions", admin_result))
    
    # 8. Test invalid credentials
    invalid_result = test_invalid_credentials()
    results.append(("Invalid Credentials Rejection", invalid_result))
    
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
        print("🎉 ALL TESTS PASSED! Phase 1 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
