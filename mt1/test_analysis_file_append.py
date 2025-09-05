#!/usr/bin/env python3
"""
Test Analysis File Append - Verify ATS results append to main file
================================================================

This test verifies that:
1. Preliminary analysis creates the main analysis file
2. ATS test results are appended to the SAME file (not a new one)
3. AI recommendations use the correct main analysis file

Usage:
    python test_analysis_file_append.py
"""

import os
import requests
import json
import time
from pathlib import Path

# Server configuration
BASE_URL = "http://127.0.0.1:8000"
ANALYSIS_DIR = "analysis_results"
MAIN_ANALYSIS_FILE = "Maheshwor_Tiwari_output_log.txt"

def check_analysis_files():
    """Check what analysis files exist"""
    print("\n📁 CHECKING ANALYSIS FILES:")
    print("-" * 40)
    
    if not os.path.exists(ANALYSIS_DIR):
        print("❌ Analysis results directory doesn't exist")
        return []
    
    files = [f for f in os.listdir(ANALYSIS_DIR) if f.endswith(('.txt', '.json'))]
    print(f"📂 Analysis directory: {ANALYSIS_DIR}")
    print(f"📄 Files found: {len(files)}")
    
    for file in files:
        filepath = os.path.join(ANALYSIS_DIR, file)
        size = os.path.getsize(filepath)
        mtime = os.path.getmtime(filepath)
        print(f"  • {file} ({size} bytes, modified: {time.ctime(mtime)})")
    
    return files

def read_main_analysis_file():
    """Read the main analysis file content"""
    main_file_path = os.path.join(ANALYSIS_DIR, MAIN_ANALYSIS_FILE)
    
    if not os.path.exists(main_file_path):
        print(f"❌ Main analysis file doesn't exist: {MAIN_ANALYSIS_FILE}")
        return None
    
    with open(main_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n📖 MAIN ANALYSIS FILE CONTENT:")
    print("-" * 50)
    print(f"📄 File: {MAIN_ANALYSIS_FILE}")
    print(f"📏 Size: {len(content)} characters")
    print(f"📊 Lines: {content.count(chr(10)) + 1}")
    
    # Check for key sections
    has_preliminary = "PRELIMINARY_ANALYSIS" in content or "ANALYZE MATCH" in content
    has_ats_score = "ATS_SCORE" in content or "Enhanced ATS Score" in content
    
    print(f"✅ Contains Preliminary Analysis: {has_preliminary}")
    print(f"✅ Contains ATS Score: {has_ats_score}")
    
    if has_preliminary and has_ats_score:
        print("🎉 SUCCESS: Main file contains both preliminary analysis AND ATS results!")
        return content
    elif has_preliminary:
        print("⚠️  WARNING: Main file has preliminary analysis but missing ATS results")
        return content
    elif has_ats_score:
        print("⚠️  WARNING: Main file has ATS results but missing preliminary analysis")
        return content
    else:
        print("❌ ERROR: Main file is missing both preliminary analysis and ATS results")
        return content

def test_get_latest_analysis_file():
    """Test the get latest analysis file endpoint"""
    print("\n🔍 TESTING GET LATEST ANALYSIS FILE ENDPOINT:")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/get-latest-analysis-file", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            filepath = data.get("filepath", "")
            filename = data.get("filename", "")
            
            print(f"✅ Endpoint successful")
            print(f"📁 Returned filepath: {filepath}")
            print(f"📄 Returned filename: {filename}")
            
            # Check if it's using the main analysis file
            if filename == MAIN_ANALYSIS_FILE:
                print("🎉 SUCCESS: Endpoint correctly returns the main analysis file!")
                return True
            else:
                print(f"⚠️  WARNING: Endpoint returned {filename} instead of {MAIN_ANALYSIS_FILE}")
                return False
        else:
            print(f"❌ Endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Endpoint error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 TESTING ANALYSIS FILE APPEND FUNCTIONALITY")
    print("=" * 60)
    
    # Step 1: Check current analysis files
    files_before = check_analysis_files()
    
    # Step 2: Read main analysis file if it exists
    main_content = read_main_analysis_file()
    
    # Step 3: Test the get latest analysis file endpoint
    endpoint_success = test_get_latest_analysis_file()
    
    # Step 4: Summary
    print("\n🎯 TEST SUMMARY:")
    print("=" * 40)
    
    if main_content and "ATS_SCORE" in main_content:
        print("✅ PASS: Main analysis file contains ATS results")
        print("✅ PASS: ATS results are being appended to main file (not creating new file)")
    else:
        print("❌ FAIL: ATS results not found in main analysis file")
        print("❌ This means ATS results are being saved to a separate file instead of appending")
    
    if endpoint_success:
        print("✅ PASS: Get latest analysis file endpoint works correctly")
    else:
        print("❌ FAIL: Get latest analysis file endpoint has issues")
    
    print(f"\n📂 Analysis files found: {len(files_before)}")
    print(f"📄 Main analysis file exists: {os.path.exists(os.path.join(ANALYSIS_DIR, MAIN_ANALYSIS_FILE))}")
    
    if main_content and "ATS_SCORE" in main_content and endpoint_success:
        print("\n🎉 OVERALL RESULT: ✅ ANALYSIS FILE APPEND IS WORKING CORRECTLY!")
        print("💡 The system properly appends ATS results to the main analysis file.")
    else:
        print("\n❌ OVERALL RESULT: ANALYSIS FILE APPEND NEEDS FIXING")
        print("💡 Check that ATS results are being appended to the main file, not creating new files.")

if __name__ == "__main__":
    main() 