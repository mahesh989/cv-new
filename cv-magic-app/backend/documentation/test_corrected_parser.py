#!/usr/bin/env python3

"""
Test the corrected parser to verify no false extractions
"""

import sys
import os
import asyncio
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.structured_cv_parser import enhanced_cv_parser

# Your original CV text
YOUR_CV_TEXT = """
Maheshwor Tiwari  
0414 032 507 | maheshtwari99@gmail.com | LinkedIn  | Hurstville, NSW, 2220  
Blogs on Medium  | GitHub  | Dashboard  Portfolio  
CAREER PROFIL E 
 
I hold a PhD in Physics and completed a Master's in Data Science, bringing over three years of experience in Python 
coding, AI, and machine learning. My expertise encompasses modeling and training AI models, writing efficient Python 
scripts, designing and deploying robust data pipelines, conducting innovative research, and creating advanced 
visualiz ations that convert complex data into actionable insights. I am also proficient in SQL, Tableau, and Power BI, building 
comprehensive dashboards that support data -driven decision -making.  
 
TECHNICAL SKILLS  
• Specialized in Python programming, including data analysis, automation, and machine learning using libraries such 
as Pandas, NumPy, and scikit -learn.  
• Proficient in SQL for querying, modeling, and managing complex relational databases like PostgreSQL and MySQL.  
• Skilled in creating interactive dashboards and visualizations using Tableau, Power BI, and Matplotlib.  
• Experienced with GitHub for version control, Docker for containerization, and Snowflake for cloud data warehousing.  
• Adept at leveraging tools like Visual Studio Code, Google Analytics, and Excel for data -driven solutions and reporting.  
 
EDUCATION  
Master of Data Science  
Charles Darwin University, Sydney, Australia GPA   Mar 2023 - Nov 2024  
PhD in Physics  
CY Cergy Paris University, Cergy, France  Oct 2018 - Sep 2022  
Master of Theoretical Physics  
CY Cergy Paris University, Cergy, France    Sep 2016 - Jun 2018  
 
EXPERIENCE   
Data Analyst         Jul 2024 – Present  
The Bitrates, Sydney, New South Wales, Australia  
• Designed and implemented Python scripts for data cleaning, preprocessing, and analysis, improving data pipeline 
efficiency by 30%.  
• Developed machine learning models in Python for predictive analytics, enabling data -driven business decisions.  
• Leveraged AI techniques to automate repetitive tasks, reducing manual effort and improving productivity.  
• Built dynamic dashboards and visualizations using Python libraries like Matplotlib and Seaborn to communicate 
insights effectively.  
• Integrated Google Analytics data with Python for advanced analysis, enhancing customer behavior insights.  
"""

async def test_corrected_parser():
    """Test the corrected parser with your CV"""
    print("🧪 Testing Corrected Parser - Avoiding False Extractions")
    print("=" * 60)
    
    try:
        # Parse your CV with the corrected parser
        print("📄 Parsing your CV with corrections...")
        structured_cv = await enhanced_cv_parser.parse_cv_content(YOUR_CV_TEXT)
        
        # Check for false extractions
        print("\n🔍 CHECKING FOR FALSE EXTRACTIONS:")
        print("=" * 60)
        
        # 1. Check section headers
        original_sections = structured_cv.get('original_sections', {})
        headers_found = original_sections.get('section_headers_found', [])
        print(f"\n📋 SECTION HEADERS DETECTED:")
        print("-" * 40)
        for header in headers_found:
            print(f"  • {header}")
        
        # Check for incorrect headers
        incorrect_headers = [
            "Maheshwor Tiwari", "PhD in Physics", "Research Intern",
            "Lecturer and Course Facilitator", "Master of Data Science", 
            "Master of Theoretical Physics"
        ]
        
        false_headers_found = []
        for incorrect in incorrect_headers:
            if incorrect in headers_found:
                false_headers_found.append(incorrect)
        
        if false_headers_found:
            print(f"❌ FALSE HEADERS FOUND: {false_headers_found}")
        else:
            print("✅ No false headers detected!")
        
        # 2. Check experience achievements and technologies
        experience = structured_cv.get('experience', [])
        print(f"\n💼 EXPERIENCE SECTIONS CHECK:")
        print("-" * 40)
        
        total_false_extractions = 0
        
        for i, job in enumerate(experience, 1):
            achievements = job.get('achievements', [])
            technologies = job.get('technologies', [])
            
            print(f"\nJob {i}: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            
            # Check achievements
            if achievements and len(achievements) > 0:
                non_empty_achievements = [a for a in achievements if a and a.strip()]
                if non_empty_achievements:
                    print(f"  ❌ FALSE ACHIEVEMENTS EXTRACTED: {len(non_empty_achievements)} items")
                    for ach in non_empty_achievements[:2]:  # Show first 2
                        print(f"    - {ach}")
                    total_false_extractions += len(non_empty_achievements)
                else:
                    print("  ✅ Achievements: Empty (correct)")
            else:
                print("  ✅ Achievements: Empty (correct)")
            
            # Check technologies
            if technologies and len(technologies) > 0:
                non_empty_technologies = [t for t in technologies if t and t.strip()]
                if non_empty_technologies:
                    print(f"  ❌ FALSE TECHNOLOGIES EXTRACTED: {len(non_empty_technologies)} items")
                    for tech in non_empty_technologies[:3]:  # Show first 3
                        print(f"    - {tech}")
                    total_false_extractions += len(non_empty_technologies)
                else:
                    print("  ✅ Technologies: Empty (correct)")
            else:
                print("  ✅ Technologies: Empty (correct)")
        
        # 3. Summary
        print(f"\n📊 CORRECTION SUMMARY:")
        print("=" * 60)
        print(f"False headers found: {len(false_headers_found)}")
        print(f"False extractions found: {total_false_extractions}")
        
        # Expected correct headers (only actual section headers)
        expected_headers = ["CAREER PROFIL E", "TECHNICAL SKILLS", "EDUCATION", "EXPERIENCE"]
        correct_headers = [h for h in headers_found if h in expected_headers]
        print(f"Correct headers found: {len(correct_headers)}/{len(expected_headers)}")
        print(f"Correct headers: {correct_headers}")
        
        # Calculate success score
        total_issues = len(false_headers_found) + total_false_extractions
        if total_issues == 0:
            print("\n🎉 SUCCESS: No false extractions detected!")
            success = True
        else:
            print(f"\n⚠️ ISSUES REMAINING: {total_issues} false extractions still found")
            success = False
        
        # Save corrected structure
        output_file = "new-cv/corrected_cv_no_false_extractions.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_cv, f, indent=2, ensure_ascii=False)
        print(f"📁 Corrected structure saved to: {output_file}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing corrected parser: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_corrected_parser())
    
    if success:
        print("\n✅ Parser corrections successful!")
        print("No false extractions or incorrect headers detected.")
    else:
        print("\n❌ Parser still has issues - needs further correction.")
        sys.exit(1)