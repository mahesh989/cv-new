#!/usr/bin/env python3
"""
Manual test script for Australia for UNHCR Data Analyst job
Tests company folder creation and analysis flow
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://cvagent.duckdns.org/api"
# Test user credentials
TEST_EMAIL = "rashmi@gmail.com"
TEST_PASSWORD = "rashmi"

# Job Description from the URL
JD_URL = "https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst"
JD_TEXT = """
Data Analyst

Australia for UNHCR

Work in a high performing, values-driven organisation
Competitive salary with salary packaging benefits
Hybrid work arrangement with office located in Sydney CBD
Full-time 15-month contract position

ABOUT US

Our passionate team empowers refugees to find safety and protection when they need it most.

Australia for UNHCR is the UN Refugee Agency's partner in Australia, raising funds and awareness to assist people forced to flee conflict, disaster or persecution. With more than 120 million people now forcibly displaced worldwide, this work has never been more vital.

At Australia for UNHCR, we harness the generosity of Australians to help UNHCR deliver life-saving aid during humanitarian emergencies. This aid includes shelter, clean water, medicine, emergency cash assistance and counselling. We also support long-term education, healthcare and employment programs to help refugees rebuild their lives and create more secure futures. As part of the UN network, we make a difference for millions of people every year.

WHO WE ARE LOOKING FOR

Our people are collaborative and inclusive team players, committed to finding new ways to increase support for refugees.

A highly motivated, organised and detail-oriented Data Analyst to join our high performing Business Intelligence Unit, who work closely with our business stakeholders, providing data to support data-driven business decision-making across Australia for UNHCR and New Zealand for UNHCR.
A data-passionate individual with strong analytical and problem-solving skills, to play a vital part in contributing to the evolving data requirements of the organisation by providing segmented data selections, data mining, analysis, and developing and maintaining reports.

YOU'LL MAKE AN IMPACT BY

Delivering analytics on the business-critical objective of understanding how to maximise the value from our donors, in the form of data-mining, profile analysis, building analytical models and BI report authoring in Power BI or a similar reporting suite.
Addressing data extract requirements for direct marketing campaigns with a high degree of service; manipulating data in preparation for bulk communications, updating records with contact history, and working with Fundraising stakeholders to advise on segmentation strategies considering a multi-channel communication and donor-centricity approach.
Producing reports and analysis for reviewing results post campaign.
Building projection and segmentation models to answer key business questions.
Assisting the BI Analyst and BI Manager to administer and develop A4U's data warehouse (DWH) considering current and future business requirements to strategise and implement enhancements to the platform through research, analysis, consultation and evaluation of program needs.
Working with a range of internal and external stakeholders to satisfy their business intelligence requirements for analysis, report creation, data selections, and data mining within a strong project management framework, driving evidence-based decision making throughout the organisation.

WE WOULD LIKE YOU TO HAVE

Minimum 2 years' experience in a similar role
Experience building models in spreadsheets, and comfortable writing formulas and VBA in Excel.
Experience in the development, maintenance and remediation of issues relating to data models within a SQL data warehouse environment.
Strong SQL coding skills and database knowledge
Experience using business intelligence tools such as Power BI, Tableau, etc.
Hands on experience in querying and extracting data across multiple, disparate and complex relational databases or a data warehouse
Strong project management skills to deliver multiple projects and work autonomously to meet deadlines
Strong stakeholder management skills. Excellent communication and customer service skills
Experience extracting data for marketing campaigns with knowledge of how to best utilise data to optimise campaign outcomes
An advanced understanding of how data is used for communication purposes, the process and the governing regulations / best practice guidelines.
An appreciation of data issues and their solutions, particularly de-duplication and the importance of maintaining clean data.
"""

def get_auth_token():
    """Get authentication token by logging in"""
    print("\n" + "="*80)
    print("STEP 0: Getting Authentication Token")
    print("="*80)
    
    login_url = f"{BASE_URL}/auth/login"
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    print(f"\n📤 Logging in as: {TEST_EMAIL}")
    
    try:
        response = requests.post(
            login_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            if token:
                print(f"✅ Login successful!")
                print(f"   Token: {token[:50]}...")
                return token
            else:
                print(f"❌ No token in response: {result}")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Exception during login: {e}")
        return None

def test_preliminary_analysis(auth_token):
    """Test preliminary analysis endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Preliminary Analysis (Company Folder Creation)")
    print("="*80)
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Get latest CV filename (you may need to adjust this)
    cv_filename = "original_cv.json"  # Adjust based on your CV files
    
    payload = {
        "cv_filename": cv_filename,
        "jd_text": JD_TEXT,
        "jd_url": JD_URL,
        "config_name": "default"
    }
    
    print(f"\n📤 Sending request to: {BASE_URL}/preliminary-analysis")
    print(f"   Company: Australia for UNHCR")
    print(f"   JD URL: {JD_URL}")
    print(f"   JD Text Length: {len(JD_TEXT)} characters")
    
    try:
        response = requests.post(
            f"{BASE_URL}/preliminary-analysis",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis completed successfully!")
            print(f"   Company: {result.get('company', 'Unknown')}")
            print(f"   CV Skills: {len(result.get('cv_skills', {}).get('technical_skills', []))}")
            print(f"   JD Skills: {len(result.get('jd_skills', {}).get('technical_skills', []))}")
            
            if 'saved_file_path' in result:
                print(f"   Saved to: {result['saved_file_path']}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_logs():
    """Check Docker logs for folder creation"""
    print("\n" + "="*80)
    print("TEST 2: Checking Docker Logs for Folder Creation")
    print("="*80)
    
    import subprocess
    
    try:
        # Check for folder creation logs
        cmd = [
            "ssh", "ubuntu@cvagent.duckdns.org",
            "cd ~/cv-new/cv-magic-app && tail -100 logs/backend_logs.txt | grep -E '\\[FOLDER\\]|\\[JD_ANALYSIS\\].*folder|Extracted company name|Australia.*UNHCR' | tail -20"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            print("\n📋 Recent folder creation logs:")
            print(result.stdout)
        else:
            print("\n⚠️ No folder creation logs found (or command failed)")
            if result.stderr:
                print(f"   Error: {result.stderr}")
                
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def check_folder_exists():
    """Check if company folder exists in Docker"""
    print("\n" + "="*80)
    print("TEST 3: Verifying Company Folder in Docker")
    print("="*80)
    
    import subprocess
    
    try:
        # Check folder exists
        cmd = [
            "ssh", "ubuntu@cvagent.duckdns.org",
            "cd ~/cv-new/cv-magic-app && docker compose exec -T backend ls -la /app/user/chunem@gmail.com/cv-analysis/applied_companies/ | grep -i 'australia\\|unhcr'"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            print("\n✅ Company folder found:")
            print(result.stdout)
            
            # List files in folder
            cmd2 = [
                "ssh", "ubuntu@cvagent.duckdns.org",
                "cd ~/cv-new/cv-magic-app && docker compose exec -T backend ls -la /app/user/chunem@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/ 2>/dev/null | head -20"
            ]
            
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=10)
            if result2.returncode == 0 and result2.stdout:
                print("\n📁 Files in company folder:")
                print(result2.stdout)
        else:
            print("\n❌ Company folder not found")
            if result.stderr:
                print(f"   Error: {result.stderr}")
                
    except Exception as e:
        print(f"❌ Error checking folder: {e}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MANUAL TEST: Australia for UNHCR Data Analyst Job")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"JD URL: {JD_URL}")
    
    # Get auth token first
    token = get_auth_token()
    if not token:
        print("\n❌ Failed to get authentication token. Exiting.")
        exit(1)
    
    # Run tests
    success = test_preliminary_analysis(token)
    
    # Wait a bit for logs to be written
    print("\n⏳ Waiting 5 seconds for logs to be written...")
    time.sleep(5)
    
    # Check logs
    check_logs()
    
    # Check folder
    check_folder_exists()
    
    print("\n" + "="*80)
    if success:
        print("✅ TEST COMPLETED - Check results above")
    else:
        print("❌ TEST FAILED - Check errors above")
    print("="*80)

