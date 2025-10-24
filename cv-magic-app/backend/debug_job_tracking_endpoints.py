#!/usr/bin/env python3
"""
Job Tracking Endpoints Debug Script

Test the specific endpoints that the job tracking tab uses.
"""
import sys
import os
import json
import requests
from pathlib import Path

# Add the app to the path
sys.path.append('/app')

def test_job_tracking_endpoints():
    """Test job tracking endpoints to find 404 causes"""
    print("🔍 Job Tracking Endpoints Debug")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints that the job tracking tab uses
    endpoints_to_test = [
        "/api/saved-jobs/saved",
        "/api/job-analysis/list", 
        "/api/cv-simple/latest-cv-content",
        "/api/cv-simple/latest-cv-content-fixed"
    ]
    
    print("🧪 Testing Job Tracking Endpoints:")
    
    for endpoint in endpoints_to_test:
        url = base_url + endpoint
        print(f"\n📡 Testing: {endpoint}")
        
        try:
            # Try without authentication first
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✅ Success: {len(str(data))} characters")
                    if isinstance(data, dict) and 'jobs' in data:
                        print(f"  📄 Jobs count: {len(data.get('jobs', []))}")
                except:
                    print(f"  ✅ Success: {len(response.text)} characters")
            elif response.status_code == 404:
                print(f"  ❌ 404 Not Found")
            elif response.status_code == 401:
                print(f"  🔐 401 Unauthorized (needs auth)")
            elif response.status_code == 500:
                print(f"  💥 500 Internal Server Error")
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"  Error: {response.text[:200]}")
            else:
                print(f"  ⚠️  Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection Error - Server not running")
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout - Server slow to respond")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test with authentication (if we have a test user)
    print(f"\n🔐 Testing with Authentication:")
    print("  (This requires a valid JWT token)")
    
    # Check if we can get a token
    try:
        # Try to get a token (this might fail if no users exist)
        auth_response = requests.post(
            base_url + "/api/auth/login",
            json={"email": "test@example.com", "password": "testpassword"},
            timeout=10
        )
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            token = token_data.get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"  ✅ Got authentication token")
            
            # Test endpoints with auth
            for endpoint in endpoints_to_test:
                url = base_url + endpoint
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    print(f"  📡 {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if isinstance(data, dict) and 'jobs' in data:
                                print(f"    📄 Jobs: {len(data.get('jobs', []))}")
                        except:
                            pass
                    elif response.status_code == 404:
                        print(f"    ❌ 404 - No data found")
                    elif response.status_code == 500:
                        print(f"    💥 500 - Server error")
                        try:
                            error_data = response.json()
                            print(f"    Error: {error_data.get('detail', 'Unknown')}")
                        except:
                            pass
                            
                except Exception as e:
                    print(f"    ❌ Error: {e}")
        else:
            print(f"  ❌ Authentication failed: {auth_response.status_code}")
            print(f"  💡 This might be because no users exist after database reset")
            
    except Exception as e:
        print(f"  ❌ Auth test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Debug Complete!")
    print("\n💡 Common 404 Causes:")
    print("  1. No users registered → Auth fails")
    print("  2. No saved jobs → /api/saved-jobs/saved returns 404")
    print("  3. No analyzed jobs → /api/job-analysis/list returns 404")
    print("  4. No tailored CVs → /api/cv-simple/latest-cv-content returns 404")
    print("\n🔧 To Fix:")
    print("  1. Register a new user")
    print("  2. Upload a CV")
    print("  3. Add a job and run analysis")
    print("  4. Generate a tailored CV")

if __name__ == "__main__":
    test_job_tracking_endpoints()
