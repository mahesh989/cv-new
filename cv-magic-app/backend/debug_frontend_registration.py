#!/usr/bin/env python3
"""
Debug frontend registration issues
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_registration_with_different_data():
    """Test registration with various data combinations to identify the issue"""
    print("🔍 DEBUGGING FRONTEND REGISTRATION ISSUES")
    print("="*60)
    
    # Test with timestamp to avoid conflicts
    timestamp = str(int(time.time()))
    
    test_cases = [
        {
            "name": "Complete Valid Data",
            "data": {
                "username": f"testuser{timestamp}",
                "email": f"test{timestamp}@example.com",
                "password": "password123",
                "full_name": "Test User"
            },
            "description": "All fields filled correctly"
        },
        {
            "name": "Minimal Valid Data",
            "data": {
                "username": f"user{timestamp}",
                "email": f"minimal{timestamp}@test.com",
                "password": "pass1234",
                "full_name": ""
            },
            "description": "Only required fields, empty full_name"
        },
        {
            "name": "Auto-generated Username",
            "data": {
                "username": f"john{timestamp}",
                "email": f"john.doe{timestamp}@example.com",
                "password": "password123",
                "full_name": "John Doe"
            },
            "description": "Username that could be auto-generated from email"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   📝 Description: {test_case['description']}")
        print(f"   📊 Data: {test_case['data']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   📤 Status: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: Registration working!")
                print(f"   👤 User ID: {data.get('id')}")
                print(f"   ✅ Auto-verified: {data.get('is_verified', False)}")
                
                # Test immediate login
                print(f"\n   🔑 Testing immediate login...")
                login_response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json={
                        "email": test_case['data']['email'],
                        "password": test_case['data']['password']
                    },
                    headers={'Content-Type': 'application/json'}
                )
                
                if login_response.status_code == 200:
                    print(f"   ✅ LOGIN SUCCESS: Complete workflow working!")
                else:
                    print(f"   ❌ LOGIN FAILED: {login_response.text}")
                    
            elif response.status_code == 400:
                error_data = json.loads(response.text)
                print(f"   ⚠️ USER EXISTS: {error_data.get('detail', '')}")
                
            elif response.status_code == 422:
                error_data = json.loads(response.text)
                print(f"   ❌ VALIDATION ERROR: {error_data.get('detail', '')}")
                
            else:
                print(f"   ❌ UNEXPECTED ERROR: {response.text}")
                
        except Exception as e:
            print(f"   💥 REQUEST ERROR: {e}")

def test_frontend_form_validation_scenarios():
    """Test scenarios that might cause frontend form validation failures"""
    print(f"\n🧪 TESTING FRONTEND FORM VALIDATION SCENARIOS")
    print("="*60)
    
    # These are the exact scenarios that might cause "Form validation failed"
    validation_scenarios = [
        {
            "name": "Empty Username",
            "data": {"email": "test@example.com", "password": "password123"},
            "expected": "Username required error"
        },
        {
            "name": "Empty Email",
            "data": {"username": "testuser", "password": "password123"},
            "expected": "Email required error"
        },
        {
            "name": "Empty Password",
            "data": {"username": "testuser", "email": "test@example.com"},
            "expected": "Password required error"
        },
        {
            "name": "Invalid Email Format",
            "data": {"username": "testuser", "email": "invalid-email", "password": "password123"},
            "expected": "Invalid email format error"
        },
        {
            "name": "Short Username",
            "data": {"username": "ab", "email": "test@example.com", "password": "password123"},
            "expected": "Username too short error"
        },
        {
            "name": "Weak Password",
            "data": {"username": "testuser", "email": "test@example.com", "password": "pass"},
            "expected": "Password too short error"
        }
    ]
    
    for scenario in validation_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print(f"   📊 Data: {scenario['data']}")
        print(f"   🎯 Expected: {scenario['expected']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=scenario['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   📤 Status: {response.status_code}")
            
            if response.status_code == 422:
                error_data = json.loads(response.text)
                print(f"   ✅ VALIDATION WORKING: {error_data.get('detail', '')}")
            else:
                print(f"   ❌ UNEXPECTED: Expected validation error, got {response.status_code}")
                print(f"   📄 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")

def show_frontend_debugging_steps():
    """Show steps to debug frontend form validation issues"""
    print(f"\n🔧 FRONTEND DEBUGGING STEPS")
    print("="*60)
    
    print(f"\n📱 FLUTTER APP DEBUGGING:")
    print(f"   1. 🔍 Check Flutter console logs for 'Form validation failed'")
    print(f"   2. 🔍 Look for specific field validation errors")
    print(f"   3. 🔍 Check if username auto-generation is working")
    print(f"   4. 🔍 Verify all form fields are properly filled")
    print(f"   5. 🔍 Check network connectivity to backend")
    
    print(f"\n🔍 SPECIFIC DEBUGGING COMMANDS:")
    print(f"   • Check Flutter console: Look for '❌ Form validation failed'")
    print(f"   • Check form field values: Look for field value logs")
    print(f"   • Test backend connection: Use 'Test Backend Connection' button")
    print(f"   • Check network: Ensure backend is running on localhost:8000")
    
    print(f"\n🎯 COMMON FRONTEND ISSUES:")
    print(f"   1. ❌ Username field empty (auto-generation not working)")
    print(f"   2. ❌ Invalid email format")
    print(f"   3. ❌ Weak password (less than 8 chars, no numbers)")
    print(f"   4. ❌ Network connectivity issues")
    print(f"   5. ❌ Form state not properly initialized")
    
    print(f"\n✅ SOLUTIONS:")
    print(f"   1. ✅ Ensure username auto-generation is working")
    print(f"   2. ✅ Use valid email format (user@domain.com)")
    print(f"   3. ✅ Use strong password (8+ chars, letters + numbers)")
    print(f"   4. ✅ Check network connectivity")
    print(f"   5. ✅ Verify form validation logic")

def test_backend_connectivity():
    """Test if backend is accessible"""
    print(f"\n🌐 TESTING BACKEND CONNECTIVITY")
    print("="*60)
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   📤 Backend Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Backend is accessible")
        else:
            print(f"   ⚠️ Backend responded with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ CONNECTION ERROR: Backend not accessible")
        print(f"   🔧 SOLUTION: Start backend server with 'python -m uvicorn app.main:app --reload'")
        
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT ERROR: Backend not responding")
        print(f"   🔧 SOLUTION: Check if backend server is running")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    # Test backend connectivity first
    test_backend_connectivity()
    
    # Test registration with different data
    test_registration_with_different_data()
    
    # Test form validation scenarios
    test_frontend_form_validation_scenarios()
    
    # Show debugging steps
    show_frontend_debugging_steps()
    
    print(f"\n" + "="*60)
    print(f"🎯 FRONTEND REGISTRATION DEBUGGING COMPLETE")
    print(f"✅ Backend connectivity tested")
    print(f"✅ Registration scenarios tested")
    print(f"✅ Form validation scenarios tested")
    print(f"✅ Debugging steps provided")
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Check Flutter console for specific validation errors")
    print(f"   2. Verify username auto-generation is working")
    print(f"   3. Test with valid data combinations")
    print(f"   4. Use 'Test Backend Connection' button in Flutter app")
