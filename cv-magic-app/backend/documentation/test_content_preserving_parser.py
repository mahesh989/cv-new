#!/usr/bin/env python3

"""
Test cases for content-preserving CV parser with different CV formats
"""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.structured_cv_parser import enhanced_cv_parser

# Test Case 1: Bullet-point heavy CV
TEST_CV_1_BULLETS = """
John Doe
Software Engineer
Email: john@example.com | Phone: (555) 123-4567

TECHNICAL SKILLS
• Specialized in Python programming, including data analysis, automation, and machine learning using libraries such as Pandas, NumPy, and scikit-learn.
• Proficient in SQL for querying, modeling, and managing complex relational databases like PostgreSQL and MySQL.
• Skilled in creating interactive dashboards and visualizations using Tableau, Power BI, and Matplotlib.

EXPERIENCE
Senior Developer | TechCorp | 2020-2023
• Developed scalable web applications using React and Node.js, serving 100,000+ users
• Led a team of 5 developers, implementing agile methodologies and improving delivery time by 40%
• Optimized database queries reducing response time from 500ms to 50ms
"""

# Test Case 2: Paragraph-style CV
TEST_CV_2_PARAGRAPHS = """
Jane Smith
Data Scientist
jane.smith@email.com | (555) 987-6543

PROFILE
Dynamic data scientist with extensive experience in machine learning, statistical analysis, and data visualization. Proven track record of transforming complex datasets into actionable business insights through advanced analytics and modeling techniques.

CORE COMPETENCIES
Python, R, SQL, Machine Learning, Deep Learning, Statistical Modeling, Data Visualization, Tableau, Power BI, AWS, Azure, Docker, Kubernetes

PROFESSIONAL EXPERIENCE
Senior Data Scientist, DataCorp (2021-Present)
Spearheaded the development of predictive models that increased customer retention by 25%. Collaborated with cross-functional teams to implement machine learning solutions across multiple business units. Managed large-scale data processing pipelines handling 10TB+ of daily data.
"""

# Test Case 3: Mixed format CV
TEST_CV_3_MIXED = """
Alex Johnson
Product Manager & Developer
alex.johnson@example.com | LinkedIn: linkedin.com/in/alexjohnson

SUMMARY
Results-driven product manager with 8+ years of experience bridging technical and business requirements.

KEY SKILLS:
- Product Strategy & Roadmap Planning
- Agile/Scrum Methodologies  
- User Experience (UX) Design
- Market Research & Analysis

TECHNICAL PROFICIENCIES:
JavaScript, Python, SQL, Git, JIRA, Confluence, Figma, Adobe Creative Suite

WORK HISTORY:
Product Manager @ InnovateTech (2020-Present)
  ★ Launched 3 major product features resulting in 30% user growth
  ★ Reduced customer churn by 15% through data-driven product improvements
  ★ Managed $2M product budget and cross-functional team of 12 members
"""

async def test_content_preservation():
    """Test that the parser preserves different CV formats"""
    test_cases = [
        ("Bullet-point CV", TEST_CV_1_BULLETS),
        ("Paragraph CV", TEST_CV_2_PARAGRAPHS),
        ("Mixed format CV", TEST_CV_3_MIXED)
    ]
    
    results = []
    
    for test_name, cv_text in test_cases:
        print(f"\n🧪 Testing {test_name}...")
        
        try:
            # Parse the CV
            structured_cv = await enhanced_cv_parser.parse_cv_content(cv_text)
            
            # Check content preservation
            technical_skills = structured_cv.get('skills', {}).get('technical_skills', [])
            experience = structured_cv.get('experience', [])
            
            preservation_score = 0
            total_checks = 4
            
            # Check 1: Are technical skills preserved as complete descriptions?
            if technical_skills and len(technical_skills) > 0:
                first_skill = str(technical_skills[0])
                if len(first_skill) > 50:  # Should be a complete description, not just "Python"
                    preservation_score += 1
                    print(f"  ✅ Technical skills preserved as complete descriptions")
                else:
                    print(f"  ❌ Technical skills fragmented: '{first_skill[:50]}...'")
            else:
                print(f"  ⚠️ No technical skills found")
            
            # Check 2: Are experience responsibilities preserved as complete bullet points?
            if experience and len(experience) > 0:
                first_job = experience[0]
                responsibilities = first_job.get('responsibilities', [])
                if responsibilities and len(str(responsibilities[0])) > 30:
                    preservation_score += 1
                    print(f"  ✅ Experience responsibilities preserved as complete descriptions")
                else:
                    print(f"  ❌ Experience responsibilities fragmented")
            else:
                print(f"  ⚠️ No experience found")
            
            # Check 3: Is original content stored?
            original_sections = structured_cv.get('original_sections', {})
            if original_sections.get('raw_cv_text'):
                preservation_score += 1
                print(f"  ✅ Original CV text stored for reference")
            else:
                print(f"  ❌ Original CV text not stored")
            
            # Check 4: Are section headers detected?
            headers_found = original_sections.get('section_headers_found', [])
            if len(headers_found) > 0:
                preservation_score += 1
                print(f"  ✅ Section headers detected: {headers_found}")
            else:
                print(f"  ❌ No section headers detected")
            
            # Calculate success rate
            success_rate = (preservation_score / total_checks) * 100
            print(f"  📊 Content preservation: {success_rate:.1f}% ({preservation_score}/{total_checks})")
            
            results.append({
                'test_name': test_name,
                'success_rate': success_rate,
                'preservation_score': preservation_score,
                'total_checks': total_checks
            })
            
        except Exception as e:
            print(f"  ❌ Error testing {test_name}: {e}")
            results.append({
                'test_name': test_name,
                'success_rate': 0,
                'error': str(e)
            })
    
    return results

async def main():
    """Run all tests and show summary"""
    print("🚀 Testing Content-Preserving CV Parser")
    print("=" * 50)
    
    results = await test_content_preservation()
    
    # Show summary
    print(f"\n📋 SUMMARY:")
    print("=" * 50)
    
    total_success = 0
    successful_tests = 0
    
    for result in results:
        if 'error' in result:
            print(f"❌ {result['test_name']}: FAILED - {result['error']}")
        else:
            print(f"{'✅' if result['success_rate'] >= 75 else '⚠️'} {result['test_name']}: {result['success_rate']:.1f}%")
            total_success += result['success_rate']
            if result['success_rate'] >= 75:
                successful_tests += 1
    
    if len(results) > 0:
        avg_success = total_success / len([r for r in results if 'error' not in r])
        print(f"\n🎯 Overall Success Rate: {avg_success:.1f}%")
        print(f"🎯 Tests Passing (≥75%): {successful_tests}/{len(results)}")
        
        if avg_success >= 75:
            print("✅ Content-preserving parser is working well!")
        else:
            print("⚠️ Parser needs improvement for better content preservation")
    else:
        print("❌ No valid test results")

if __name__ == "__main__":
    asyncio.run(main())