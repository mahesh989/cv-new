#!/usr/bin/env python3
"""
Test that simulates the exact frontend-to-backend flow
to identify where the skill comparison is failing.
"""

import requests
import json

def test_frontend_simulation():
    """Simulate the exact CV and JD skills from the logs"""
    
    # These are the exact skills from the user's logs
    cv_skills = {
        "technical_skills": [
            "Python programming", "AI", "Machine learning", "SQL", "Tableau", 
            "Power BI", "Pandas", "NumPy", "scikit-learn", "PostgreSQL", "MySQL", 
            "Matplotlib", "GitHub", "Docker", "Snowflake", "Visual Studio Code", 
            "Google Analytics", "Excel", "Seaborn", "Version control", 
            "Containerization", "Cloud data warehousing"
        ],
        "soft_skills": [
            "Communication skills", "Teamwork", "Collaboration", "Problem-solving", 
            "Leadership", "Mentoring", "Time management", "Presentation skills"
        ],
        "domain_keywords": [
            "Data analysis", "Data pipelines", "Data visualization", "Dashboards", 
            "Data-driven decision-making", "Predictive analytics", "Data cleaning", 
            "Data preprocessing", "Computational modeling", "Data accuracy", 
            "Data integrity", "Actionable insights", "Customer behavior insights", 
            "Key metrics", "Data extraction", "ETL processes", "Business intelligence", 
            "Analytics", "Reporting", "Data modeling"
        ]
    }
    
    jd_skills = {
        "technical_skills": [
            "Business Intelligence tools", "Microsoft Excel", "Database proficiency", 
            "Systems Administration", "Troubleshooting", "Data analysis methodologies", 
            "Report development", "Data quality assessment"
        ],
        "soft_skills": [
            "Communication skills", "Leadership", "Management skills", 
            "Analytical thinking", "Problem-solving", "Stakeholder management"
        ],
        "domain_keywords": [
            "Data Analyst", "Data sets", "Reporting", "Business analytical tools", 
            "Analysis findings", "Regulatory requirements", "Governance requirements", 
            "Data quality", "Data collection", "Data storage", "Data usage", "KPIs", 
            "IT", "Management Information Systems", "Data Analytics", 
            "Performance management", "Compliance monitoring", 
            "Business intelligence reporting", "Data governance"
        ]
    }
    
    print("🧪 [SIMULATION] Testing with actual user data:")
    print(f"  CV Skills count: {sum(len(v) for v in cv_skills.values())}")
    print(f"  JD Skills count: {sum(len(v) for v in jd_skills.values())}")
    
    # Expected total from logs
    expected_total = len(jd_skills["technical_skills"]) + len(jd_skills["soft_skills"]) + len(jd_skills["domain_keywords"])
    print(f"  Expected total JD requirements: {expected_total}")
    
    try:
        url = "http://localhost:8000/api/llm/compare-skills"
        payload = {
            "cv_skills": cv_skills,
            "jd_skills": jd_skills
        }
        
        print(f"\n🚀 [SIMULATION] Sending request to {url}")
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            comparison_result = result.get('comparison_result', {})
            validation = result.get('validation', {})
            
            print(f"\n📊 [SIMULATION] Results:")
            
            # Validation info
            print(f"  Validation Valid: {validation.get('valid', 'N/A')}")
            print(f"  Processed Count: {validation.get('processed_count', 'N/A')}")
            print(f"  Expected Count: {expected_total}")
            
            # Match summary
            match_summary = comparison_result.get('match_summary', {})
            print(f"  Total JD Requirements: {match_summary.get('total_jd_requirements', 'N/A')}")
            print(f"  Total Matches: {match_summary.get('total_matches', 'N/A')}")
            print(f"  Match Percentage: {match_summary.get('match_percentage', 'N/A')}%")
            print(f"  Validation Passed: {match_summary.get('validation_passed', 'N/A')}")
            
            # Count actual results
            matched = comparison_result.get('matched', {})
            missing = comparison_result.get('missing', {})
            
            matched_count = sum(len(matched.get(cat, [])) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])
            missing_count = sum(len(missing.get(cat, [])) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])
            total_processed = matched_count + missing_count
            
            print(f"  Actual Matched: {matched_count}")
            print(f"  Actual Missing: {missing_count}")
            print(f"  Total Processed: {total_processed}")
            
            # Check for empty results (the user's issue)
            if total_processed == 0:
                print(f"\n❌ [ISSUE] EMPTY RESULTS DETECTED!")
                print(f"  This matches the user's problem - all results are 0")
                return False
            elif total_processed != expected_total:
                print(f"\n⚠️ [WARNING] Count mismatch: {total_processed} vs {expected_total}")
                return False
            else:
                print(f"\n✅ [SUCCESS] All requirements processed correctly!")
                return True
                
        else:
            print(f"❌ [ERROR] API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Frontend-Backend Simulation Test")
    print("=" * 50)
    
    success = test_frontend_simulation()
    
    if success:
        print("\n🎉 Backend is working correctly - issue must be in frontend!")
    else:
        print("\n❌ Issue reproduced - backend has problems!") 