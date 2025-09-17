#!/usr/bin/env python3

"""
Test script to generate tailored CVs for both available companies using real data
"""

import asyncio
import json
import requests
import sys
from datetime import datetime
from pathlib import Path

# Server configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json"
}

# Global variable to store the authentication token
auth_token = None

def get_auth_token():
    """Get a valid authentication token for API calls"""
    global auth_token
    try:
        print("🔐 Getting authentication token...")
        response = requests.post(
            f"{BASE_URL}/api/auth/refresh-session",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            if auth_token:
                print("✅ Authentication token obtained successfully")
                # Update headers with the token
                HEADERS["Authorization"] = f"Bearer {auth_token}"
                return True
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Failed to get token: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        return False

def test_server_connection():
    """Test if the server is running and accessible"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
            return True  # Server is running but might need auth
    except requests.exceptions.RequestException as e:
        print(f"❌ Server connection failed: {e}")
        return False

def get_available_companies():
    """Get list of available companies for CV tailoring"""
    try:
        print("\n📋 Fetching available companies...")
        response = requests.get(
            f"{BASE_URL}/api/tailored-cv/available-companies",
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            companies = data.get('companies', [])
            print(f"✅ Found {len(companies)} companies:")
            for company in companies:
                print(f"   • {company}")
            return companies
        else:
            print(f"❌ Failed to get companies: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting companies: {e}")
        return []

def test_tailored_cv_generation(company):
    """Test tailored CV generation for a specific company"""
    try:
        print(f"\n🎯 Generating tailored CV for {company}...")
        print("-" * 60)
        
        # Use the endpoint that works with real data from cv-analysis folder
        response = requests.post(
            f"{BASE_URL}/api/tailored-cv/tailor-with-real-data/{company}",
            headers=HEADERS,
            params={
                "custom_instructions": f"Optimize for {company.replace('_', ' ')} company culture and requirements"
            },
            timeout=60  # Increased timeout for AI processing
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            success = data.get('success', False)
            print(f"✅ Success: {success}")
            
            if success:
                tailored_cv = data.get('tailored_cv', {})
                processing_summary = data.get('processing_summary', {})
                
                # Show key results
                print(f"🎯 ATS Score: {tailored_cv.get('estimated_ats_score', 'N/A')}")
                print(f"📊 Match Score: {tailored_cv.get('match_score', 'N/A')}")
                print(f"📝 Sections Modified: {len(tailored_cv.get('optimizations', {}))}")
                
                # Show where it was saved
                saved_to = processing_summary.get('saved_to', 'Not saved')
                print(f"💾 Saved to: {saved_to}")
                
                # Show optimization summary
                optimizations = tailored_cv.get('optimizations', {})
                if optimizations:
                    print(f"\n🔧 OPTIMIZATIONS APPLIED:")
                    for section, changes in optimizations.items():
                        if isinstance(changes, dict):
                            change_count = len(changes.get('modifications', []))
                        elif isinstance(changes, list):
                            change_count = len(changes)
                        else:
                            change_count = 1
                        print(f"   • {section}: {change_count} changes")
                
                # Show warnings if any
                warnings = data.get('warnings', [])
                if warnings:
                    print(f"\n⚠️ WARNINGS:")
                    for warning in warnings:
                        print(f"   • {warning}")
                
                return True
                
            else:
                error = data.get('error', 'Unknown error')
                print(f"❌ Failed: {error}")
                return False
                
        elif response.status_code == 404:
            print(f"❌ Company not found: {company}")
            print("Available companies might not include this one")
            return False
            
        elif response.status_code == 401:
            print("❌ Authentication failed - might need proper token")
            return False
            
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error generating tailored CV for {company}: {e}")
        return False

def verify_generated_files():
    """Verify that tailored CV files were generated"""
    print("\n📁 Verifying generated files...")
    print("-" * 60)
    
    cv_analysis_path = Path("cv-analysis")
    companies = ["Australia_for_UNHCR", "Nine_Entertainment"]
    
    for company in companies:
        company_path = cv_analysis_path / company
        if company_path.exists():
            # Look for tailored CV files
            tailored_files = list(company_path.glob("tailored_cv_*.json"))
            
            if tailored_files:
                latest_file = max(tailored_files, key=lambda p: p.stat().st_mtime)
                file_size = latest_file.stat().st_size
                mod_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                
                print(f"✅ {company}:")
                print(f"   📄 File: {latest_file.name}")
                print(f"   📊 Size: {file_size:,} bytes")
                print(f"   🕐 Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check if it's recent (within last 10 minutes)
                if (datetime.now() - mod_time).total_seconds() < 600:
                    print(f"   ✅ Recently generated!")
                else:
                    print(f"   ⚠️ File is older")
            else:
                print(f"❌ {company}: No tailored CV files found")
        else:
            print(f"❌ {company}: Company folder not found")

def main():
    """Main test function"""
    print("🚀 Testing Tailored CV Generation")
    print("=" * 60)
    
    # Test server connection
    if not test_server_connection():
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        sys.exit(1)
    
    # Get authentication token
    if not get_auth_token():
        print("❌ Cannot get authentication token. Server might not support dev tokens.")
        sys.exit(1)
    
    # Get available companies
    companies = get_available_companies()
    
    # If API doesn't work, use the known companies
    if not companies:
        print("⚠️ API call failed, using known companies from file system")
        companies = ["Australia_for_UNHCR", "Nine_Entertainment"]
    
    # Test tailored CV generation for each company
    success_count = 0
    total_companies = len(companies)
    
    for company in companies:
        success = test_tailored_cv_generation(company)
        if success:
            success_count += 1
    
    # Verify generated files
    verify_generated_files()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print("=" * 60)
    print(f"Companies tested: {total_companies}")
    print(f"Successful generations: {success_count}")
    print(f"Success rate: {success_count/total_companies*100 if total_companies > 0 else 0:.1f}%")
    
    if success_count == total_companies:
        print("🎉 All tailored CV generations successful!")
    elif success_count > 0:
        print("⚠️ Some tailored CV generations succeeded")
    else:
        print("❌ No tailored CV generations succeeded")
    
    return success_count == total_companies

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)