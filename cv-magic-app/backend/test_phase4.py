#!/usr/bin/env python3
"""
Test script for Phase 4: Email Verification & Password Reset
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

def test_verification_status(token):
    """Test email verification status"""
    print_test_header("Email Verification Status")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/auth/verification-status",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Verification status: {data['is_verified']}")
            return True
        else:
            print_result(False, f"Verification status failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Verification status error: {e}")
        return False

def test_send_verification_email(token):
    """Test sending verification email"""
    print_test_header("Send Verification Email")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/send-verification",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Verification email: {data['message']}")
            return True
        else:
            print_result(False, f"Send verification failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Send verification error: {e}")
        return False

def test_resend_verification_email(token):
    """Test resending verification email"""
    print_test_header("Resend Verification Email")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/resend-verification",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Resend verification: {data['message']}")
            return True
        else:
            print_result(False, f"Resend verification failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Resend verification error: {e}")
        return False

def test_forgot_password():
    """Test forgot password functionality"""
    print_test_header("Forgot Password")
    
    try:
        # Test with existing email
        forgot_data = {
            "email": "test@example.com"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/forgot-password",
            json=forgot_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Forgot password: {data['message']}")
        else:
            print_result(False, f"Forgot password failed: {response.status_code} - {response.text}")
            return False
        
        # Test with non-existing email (should still return success for security)
        forgot_data = {
            "email": "nonexistent@example.com"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/forgot-password",
            json=forgot_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Non-existent email: {data['message']}")
            return True
        else:
            print_result(False, f"Non-existent email failed: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print_result(False, f"Forgot password error: {e}")
        return False

def test_password_reset():
    """Test password reset functionality"""
    print_test_header("Password Reset")
    
    try:
        # Test with invalid token
        reset_data = {
            "token": "invalid_token_123",
            "new_password": "newpassword123"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/reset-password",
            json=reset_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            data = response.json()
            print_result(True, f"Invalid token rejected: {data['detail']}")
            return True
        else:
            print_result(False, f"Invalid token not rejected: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print_result(False, f"Password reset error: {e}")
        return False

def test_email_verification_endpoint():
    """Test email verification endpoint"""
    print_test_header("Email Verification Endpoint")
    
    try:
        # Test with invalid token
        verification_data = {
            "token": "invalid_token_123"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/verify-email",
            json=verification_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            data = response.json()
            print_result(True, f"Invalid verification token rejected: {data['detail']}")
            return True
        else:
            print_result(False, f"Invalid verification token not rejected: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print_result(False, f"Email verification error: {e}")
        return False

def test_email_service_configuration():
    """Test email service configuration"""
    print_test_header("Email Service Configuration")
    
    try:
        # Test if email service can be instantiated
        from app.services.email_service import EmailService
        email_service = EmailService()
        
        # Check if configuration is loaded
        if hasattr(email_service, 'smtp_server') and hasattr(email_service, 'from_email'):
            print_result(True, "Email service configuration loaded")
            return True
        else:
            print_result(False, "Email service configuration missing")
            return False
        
    except Exception as e:
        print_result(False, f"Email service configuration error: {e}")
        return False

def test_token_service_configuration():
    """Test token service configuration"""
    print_test_header("Token Service Configuration")
    
    try:
        # Test if token service can be instantiated
        from app.services.token_service import TokenService
        token_service = TokenService()
        
        # Check if configuration is loaded
        if hasattr(token_service, 'verification_token_expiry') and hasattr(token_service, 'reset_token_expiry'):
            print_result(True, "Token service configuration loaded")
            return True
        else:
            print_result(False, "Token service configuration missing")
            return False
        
    except Exception as e:
        print_result(False, f"Token service configuration error: {e}")
        return False

def test_database_schema_update():
    """Test if database schema includes new fields"""
    print_test_header("Database Schema Update")
    
    try:
        # Test if we can query the user table with new fields
        from app.database import get_database
        from app.models.user import User
        
        db = next(get_database())
        
        # Try to query a user to see if new fields exist
        user = db.query(User).first()
        if user:
            # Check if new fields exist
            if hasattr(user, 'verification_token') and hasattr(user, 'reset_token'):
                print_result(True, "Database schema updated with new fields")
                return True
            else:
                print_result(False, "Database schema missing new fields")
                return False
        else:
            print_result(True, "Database schema updated (no users to test)")
            return True
        
    except Exception as e:
        print_result(False, f"Database schema update error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PHASE 4 TESTING: Email Verification & Password Reset")
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
    
    # 3. Test database schema update
    db_schema_result = test_database_schema_update()
    results.append(("Database Schema Update", db_schema_result))
    
    # 4. Test email service configuration
    email_config_result = test_email_service_configuration()
    results.append(("Email Service Configuration", email_config_result))
    
    # 5. Test token service configuration
    token_config_result = test_token_service_configuration()
    results.append(("Token Service Configuration", token_config_result))
    
    # 6. Test verification status
    verification_status_result = test_verification_status(token)
    results.append(("Email Verification Status", verification_status_result))
    
    # 7. Test send verification email
    send_verification_result = test_send_verification_email(token)
    results.append(("Send Verification Email", send_verification_result))
    
    # 8. Test resend verification email
    resend_verification_result = test_resend_verification_email(token)
    results.append(("Resend Verification Email", resend_verification_result))
    
    # 9. Test forgot password
    forgot_password_result = test_forgot_password()
    results.append(("Forgot Password", forgot_password_result))
    
    # 10. Test password reset
    password_reset_result = test_password_reset()
    results.append(("Password Reset", password_reset_result))
    
    # 11. Test email verification endpoint
    email_verification_result = test_email_verification_endpoint()
    results.append(("Email Verification Endpoint", email_verification_result))
    
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
        print("🎉 ALL TESTS PASSED! Phase 4 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
