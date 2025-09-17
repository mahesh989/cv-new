#!/usr/bin/env python3

"""
Test the location extraction and project formatting fixes
"""

import sys
import os
import asyncio
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.structured_cv_parser import enhanced_cv_parser

# Your updated CV text from the raw_cv_text field
YOUR_UPDATED_CV_TEXT = """
Maheshwor Tiwari
0414 032 507 | maheshtwari99@gmail.com | Blogs on Medium | GitHub | Dashboard Portfolio

CAREER PROFILE

Dynamic Data Science Professional with over 2 years of hands-on experience in analytics, specializing in SQL, Tableau, and Python. Adept at transforming complex datasets into actionable insights to drive strategic decision-making. Enthusiastic about exploring diverse industries, gaining cross-functional expertise, and contributing impactful solutions to data-driven projects. Skilled in leveraging data to inform business strategies and deliver measurable outcomes.

KEY SKILLS 

Advanced SQL skills, proficient in writing and interpreting complex queries for analytics tasks.
Strong experience in Power BI for dashboard creation and data visualisation.
Proficient in Python and Excel for data analysis and automation.
Ability to uncover insights through analysis of large and diverse datasets.
Excellent interpersonal and communication skills to work effectively with stakeholders.
Strong ability to manage and prioritise multiple tasks in dynamic environments.

EDUCATION 

Master of Data Science		            Mar 2023 - Oct 2024
Charles Darwin University, Sydney, Australia, 	GPA - 6.35 /7
Thesis: Optimisation of Yolov8n Model for Real-Time Corrosion Detection (Grade: 89/100)
Reduced model size by 11.39% and improved inference time by 39.34% with pruning techniques.
Demonstrated fine-tuning strategies achieving a minimal 7.43% drop in detection precision.
Applied findings to enhance model performance using drones and edge devices.
Contributed to industrial inspection innovations by improving real-time object detection models.
Bachelor of Science in Information Technology                                                      	Jul 2014 – Aug 2018
Tribhuvan University, Kathmandu, Nepal		                                                                

PROFESSIONAL EXPERIENCE

Data Analyst                                                                           Jan 2024 – Jun 2024
iBuild Building Solutions, Victoria, Australia
Analysed datasets exceeding 100,000 records, ensuring 99% accuracy and integrity.
Developed Power BI dashboards to analyse customer text data and identify top 20 queries, enhancing response strategies and decision-making.
Conducted ad-hoc analyses to uncover actionable insights from customer datasets, improving response times.
Ensured 99% accuracy in datasets by identifying and addressing data discrepancies.

Data Insight & Analyst                                                               Mar 2023 - Nov 2023
Property Console, Sydney, Australia
Identified patterns and insights of user data through statistical analysis to inform strategic decision-making.
Created interactive dashboards using Power BI and Excel, reducing reporting time by 30%.
Delivered high-quality insights and reports to stakeholders in a clear and concise manner.

PROJECTS

Heart Attack Risk Prediction                                                                Oct 2024
Implemented logistic regression, random forests, and deep learning models to predict heart attack risks.
Addressed imbalanced datasets using undersampling techniques to enhance prediction reliability.
Presented findings through clear, data-driven visualisations to support decision-making.

CERTIFICATIONS
SQL, Linkedin Learning
Google Analytics, Skillshop, Google
"""

async def test_location_and_project_fixes():
    """Test the fixes for location extraction and project formatting"""
    print("🧪 Testing Location Extraction and Project Formatting Fixes")
    print("=" * 70)
    
    try:
        # Parse the updated CV
        print("📄 Parsing updated CV...")
        structured_cv = await enhanced_cv_parser.parse_cv_content(YOUR_UPDATED_CV_TEXT)
        
        # Check the fixes
        print("\n🔍 CHECKING FIXES:")
        print("=" * 70)
        
        issues_found = 0
        fixes_working = 0
        
        # 1. Check personal information location
        personal_info = structured_cv.get('personal_information', {})
        personal_location = personal_info.get('location', '')
        
        print(f"\n📍 PERSONAL LOCATION:")
        print("-" * 40)
        if personal_location and personal_location.strip():
            print(f"✅ Location found: '{personal_location}'")
            fixes_working += 1
        else:
            print(f"❌ Location missing: '{personal_location}'")
            print("   Expected: Should extract location from contact line")
            issues_found += 1
        
        # 2. Check education locations
        education = structured_cv.get('education', [])
        print(f"\n🎓 EDUCATION LOCATIONS:")
        print("-" * 40)
        
        expected_locations = ["Sydney, Australia", "Kathmandu, Nepal"]
        education_issues = 0
        
        for i, edu in enumerate(education):
            edu_location = edu.get('location', '')
            degree = edu.get('degree', 'Unknown')
            if edu_location and edu_location.strip():
                print(f"✅ {degree}: '{edu_location}'")
                fixes_working += 1
            else:
                print(f"❌ {degree}: Location missing - '{edu_location}'")
                if i < len(expected_locations):
                    print(f"   Expected: '{expected_locations[i]}'")
                education_issues += 1
        
        issues_found += education_issues
        
        # 3. Check projects formatting
        projects = structured_cv.get('projects', [])
        print(f"\n📋 PROJECT FORMATTING:")
        print("-" * 40)
        
        if projects and len(projects) > 0:
            project = projects[0]
            project_desc = project.get('description', '')
            project_name = project.get('name', 'Unknown Project')
            
            print(f"Project: {project_name}")
            print(f"Description format:")
            
            # Check if description is properly formatted (not broken into multiple lines)
            if '\n' in project_desc:
                # If there are line breaks, they should be intentional (preserving original format)
                lines = project_desc.split('\n')
                print(f"  Description has {len(lines)} lines:")
                for j, line in enumerate(lines[:3], 1):  # Show first 3 lines
                    print(f"    {j}. {line.strip()}")
                if len(lines) > 3:
                    print(f"    ... and {len(lines) - 3} more lines")
                
                # This could be correct if original had multiple lines
                print("✅ Format preserved (multi-line)")
                fixes_working += 1
            else:
                # Single description - check if it's comprehensive
                if len(project_desc) > 100:  # Should be a comprehensive description
                    print(f"✅ Single comprehensive description: '{project_desc[:100]}...'")
                    fixes_working += 1
                else:
                    print(f"❌ Description too short or fragmented: '{project_desc}'")
                    issues_found += 1
        else:
            print("⚠️ No projects found to check")
        
        # 4. Summary
        print(f"\n📊 FIXES SUMMARY:")
        print("=" * 70)
        print(f"Issues found: {issues_found}")
        print(f"Fixes working: {fixes_working}")
        
        # Expected fixes
        expected_fixes = 4  # personal location + 2 education locations + project formatting
        success_rate = (fixes_working / expected_fixes) * 100 if expected_fixes > 0 else 0
        
        print(f"Success rate: {success_rate:.1f}% ({fixes_working}/{expected_fixes} fixes working)")
        
        # Show what should be fixed
        print(f"\n🎯 EXPECTED RESULTS:")
        print("-" * 40)
        print("• Personal location: Should extract address from contact line")
        print("• Education locations: Sydney, Australia | Kathmandu, Nepal")  
        print("• Project format: Should preserve original multi-line bullet format")
        
        # Save results
        output_file = "new-cv/location_and_project_fixes_test.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_cv, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Test results saved to: {output_file}")
        
        return issues_found == 0
        
    except Exception as e:
        print(f"❌ Error testing fixes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_location_and_project_fixes())
    
    if success:
        print("\n✅ All fixes working correctly!")
        print("Location extraction and project formatting are now accurate.")
    else:
        print("\n⚠️ Some fixes need further refinement.")
        print("Review the issues above and continue improving the parser.")