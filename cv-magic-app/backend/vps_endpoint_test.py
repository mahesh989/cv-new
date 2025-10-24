#!/usr/bin/env python3
"""
VPS Endpoint Test Script

Run this on the VPS to test job tracking endpoints and find 404 causes.
"""
import sys
import os
import json
import requests
from pathlib import Path

# Add the app to the path
sys.path.append('/app')

def test_endpoints():
    """Test job tracking endpoints"""
    print("🔍 VPS Endpoint Test")
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
    
    print("\n" + "=" * 50)
    print("🔧 Endpoint Test Complete!")

if __name__ == "__main__":
    test_endpoints()
