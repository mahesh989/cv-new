#!/usr/bin/env python3

import requests
import json
import time

def test_ats_comprehensive():
    base_url = "http://localhost:8000"
    
    # Test data with job description
    test_payload = {
        "cv_filename": "maheshwor_tiwari.pdf",
        "job_description": """
        Senior Data Analyst Position
        
        We are seeking a skilled Data Analyst to join our team. The ideal candidate will have:
        
        Required Skills:
        - Python programming (3+ years)
        - SQL and database management (PostgreSQL, MySQL)
        - Data visualization tools (Tableau, Power BI)
        - Statistical analysis and machine learning
        - Experience with pandas, numpy, scikit-learn
        - Data pipeline development
        - Dashboard creation and maintenance
        
        Preferred Skills:
        - Docker containerization
        - Cloud platforms (AWS, Azure)
        - Snowflake data warehouse
        - Advanced Excel skills
        - Git version control
        
        Qualifications:
        - Master's degree in Data Science, Statistics, or related field
        - 3+ years of professional data analysis experience
        - Strong communication and presentation skills
        - Experience with agile methodologies
        
        Responsibilities:
        - Analyze large datasets to identify trends and insights
        - Create and maintain interactive dashboards
        - Collaborate with cross-functional teams
        - Present findings to stakeholders
        - Develop and optimize data pipelines
        """
    }
    
    print("🚀 Testing Comprehensive ATS System...")
    print(f"📄 CV File: {test_payload['cv_filename']}")
    print(f"📋 Job Description: {len(test_payload['job_description'])} characters")
    print("=" * 60)
    
    try:
        # Test the ATS matching endpoint
        print("🔍 Running ATS Analysis...")
        response = requests.post(
            f"{base_url}/test-unified-extractor/",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ ATS Analysis Complete!")
            print("=" * 60)
            
            # Overall results
            print(f"📊 Overall Score: {result.get('overall_score', 'N/A')}/100")
            print(f"🎯 Status: {result.get('status', 'N/A').upper()}")
            print(f"📈 Compatibility: {result.get('compatibility_level', 'N/A')}")
            
            # Skill breakdown
            skills = result.get('skills', {})
            if skills:
                print("\n🔧 Skills Analysis:")
                for category, data in skills.items():
                    if isinstance(data, list):
                        print(f"  {category.replace('_', ' ').title()}: {len(data)} skills found")
                        # Show first few skills
                        if data:
                            sample_skills = data[:5]
                            print(f"    Sample: {', '.join(sample_skills)}")
                    else:
                        print(f"  {category.replace('_', ' ').title()}: {data}")
            
            # Detailed scores
            detailed_scores = result.get('detailed_scores', {})
            if detailed_scores:
                print("\n📈 Detailed Scores:")
                for category, score in detailed_scores.items():
                    print(f"  {category.replace('_', ' ').title()}: {score}")
            
            # Recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print("\n💡 Top Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"  {i}. {rec}")
            
            # Missing skills
            missing_skills = result.get('missing_skills', [])
            if missing_skills:
                print(f"\n⚠️  Missing Skills ({len(missing_skills)}):")
                for skill in missing_skills[:10]:  # Show first 10
                    print(f"  • {skill}")
            
            # Matched skills
            matched_skills = result.get('matched_skills', [])
            if matched_skills:
                print(f"\n✅ Matched Skills ({len(matched_skills)}):")
                for skill in matched_skills[:10]:  # Show first 10
                    print(f"  • {skill}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out. The analysis might be taking longer than expected.")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_ats_comprehensive() 