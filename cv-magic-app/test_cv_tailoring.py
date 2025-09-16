#!/usr/bin/env python3
"""
Test script for CV tailoring endpoint
"""

import requests
import json

# Test data (same as in the Flutter app and backend examples)
SAMPLE_ORIGINAL_CV = {
    "contact": {
        "name": "John Doe",
        "phone": "+1-555-0123",
        "email": "john.doe@email.com",
        "linkedin": "https://linkedin.com/in/johndoe",
        "location": "San Francisco, CA"
    },
    "education": [
        {
            "institution": "University of California, Berkeley",
            "degree": "Bachelor of Science in Computer Science",
            "location": "Berkeley, CA",
            "graduation_date": "May 2020",
            "gpa": "3.7"
        }
    ],
    "experience": [
        {
            "company": "Tech Startup Inc.",
            "title": "Software Engineer",
            "location": "San Francisco, CA",
            "start_date": "June 2020",
            "end_date": "Present",
            "bullets": [
                "Developed web applications using React and Node.js",
                "Worked on database optimization projects",
                "Collaborated with team members on various projects"
            ]
        }
    ],
    "projects": [
        {
            "name": "E-commerce Platform",
            "context": "Personal project to learn full-stack development",
            "technologies": ["React", "Node.js", "MongoDB"],
            "bullets": [
                "Created online shopping platform with user authentication",
                "Implemented payment processing and order management"
            ]
        }
    ],
    "skills": [
        {
            "category": "Programming Languages",
            "skills": ["JavaScript", "Python", "Java", "SQL"]
        },
        {
            "category": "Frameworks & Libraries",
            "skills": ["React", "Node.js", "Express", "MongoDB"]
        }
    ],
    "total_years_experience": 3
}

SAMPLE_RECOMMENDATIONS = {
    "company": "Google",
    "job_title": "Senior Software Engineer",
    "missing_technical_skills": [
        "Kubernetes", "microservices", "system design", 
        "distributed systems", "machine learning"
    ],
    "missing_soft_skills": [
        "leadership", "mentoring", "cross-functional collaboration"
    ],
    "missing_keywords": [
        "scalability", "performance optimization", "cloud architecture"
    ],
    "technical_enhancements": [
        "Kubernetes orchestration", "microservices architecture",
        "system design patterns", "performance tuning"
    ],
    "soft_skill_improvements": [
        "technical leadership", "team mentoring", 
        "stakeholder communication"
    ],
    "keyword_integration": [
        "scalable systems", "high-performance applications",
        "cloud-native solutions"
    ],
    "critical_gaps": [
        "system design experience", "scalability expertise",
        "distributed systems knowledge"
    ],
    "important_gaps": [
        "leadership experience", "mentoring skills"
    ],
    "nice_to_have": [
        "machine learning experience", "open source contributions"
    ],
    "match_score": 65,
    "target_score": 85
}

def test_cv_tailoring():
    """Test the CV tailoring endpoint"""
    
    url = "http://localhost:8000/api/tailored-cv/tailor"
    
    # For demo purposes, we'll skip authentication
    # In a real app, you'd need a valid JWT token
    payload = {
        "original_cv": SAMPLE_ORIGINAL_CV,
        "recommendations": SAMPLE_RECOMMENDATIONS,
        "custom_instructions": "Focus on scalability and system design experience",
        "target_ats_score": 85
    }
    
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_JWT_TOKEN"  # Would need this in real usage
    }
    
    try:
        print("🎯 Testing CV Tailoring Endpoint...")
        print(f"URL: {url}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! CV Tailoring Response:")
            
            if result.get("success"):
                tailored_cv = result.get("tailored_cv", {})
                print(f"  Target Company: {tailored_cv.get('target_company')}")
                print(f"  Target Role: {tailored_cv.get('target_role')}")
                print(f"  Estimated ATS Score: {tailored_cv.get('estimated_ats_score')}")
                print(f"  Keywords Integrated: {len(tailored_cv.get('keywords_integrated', []))}")
                
                # Show enhanced experience example
                experience = tailored_cv.get("experience", [])
                if experience:
                    print(f"\n📝 Enhanced Experience Example:")
                    first_exp = experience[0]
                    print(f"  {first_exp.get('title')} at {first_exp.get('company')}")
                    for bullet in first_exp.get("bullets", [])[:2]:
                        print(f"    • {bullet}")
                
                # Save result to file for inspection
                with open("tailored_cv_test_result.json", "w") as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"\n💾 Full result saved to: tailored_cv_test_result.json")
                
            else:
                print("❌ CV Tailoring failed:")
                print(f"  Error: {result.get('processing_summary', {}).get('error')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to server. Is it running on localhost:8000?")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. CV generation might take longer.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cv_tailoring()