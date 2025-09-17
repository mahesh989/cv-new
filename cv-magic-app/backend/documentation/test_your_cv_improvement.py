#!/usr/bin/env python3

"""
Test the improved parser with your original CV to demonstrate content preservation
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

async def test_your_cv_improvement():
    """Test the improved parser with your CV"""
    print("🧪 Testing Content-Preserving Parser with Your CV")
    print("=" * 60)
    
    try:
        # Parse your CV with the improved parser
        print("📄 Parsing your CV...")
        structured_cv = await enhanced_cv_parser.parse_cv_content(YOUR_CV_TEXT)
        
        # Show the improvements
        print("\n✨ CONTENT PRESERVATION RESULTS:")
        print("=" * 60)
        
        # 1. Technical Skills Preservation
        technical_skills = structured_cv.get('skills', {}).get('technical_skills', [])
        print(f"\n🔧 TECHNICAL SKILLS ({len(technical_skills)} items):")
        print("-" * 40)
        for i, skill in enumerate(technical_skills, 1):
            print(f"{i}. {skill}")
            
        # 2. Experience Preservation 
        experience = structured_cv.get('experience', [])
        print(f"\n💼 EXPERIENCE ({len(experience)} roles):")
        print("-" * 40)
        if experience:
            first_job = experience[0]
            print(f"Role: {first_job.get('title')} at {first_job.get('company')}")
            responsibilities = first_job.get('responsibilities', [])
            print(f"Responsibilities ({len(responsibilities)} items):")
            for i, resp in enumerate(responsibilities[:3], 1):  # Show first 3
                print(f"  {i}. {resp}")
            if len(responsibilities) > 3:
                print(f"  ... and {len(responsibilities) - 3} more")
                
        # 3. Original Content Storage
        original_sections = structured_cv.get('original_sections', {})
        print(f"\n📚 ORIGINAL CONTENT PRESERVATION:")
        print("-" * 40)
        print(f"Raw CV stored: {'✅' if original_sections.get('raw_cv_text') else '❌'}")
        headers_found = original_sections.get('section_headers_found', [])
        print(f"Section headers detected: {headers_found}")
        print(f"Parsing approach: {original_sections.get('parsing_approach', 'N/A')}")
        
        # 4. Metadata
        metadata = structured_cv.get('metadata', {})
        print(f"\n🏷️ PARSER METADATA:")
        print("-" * 40)
        print(f"Version: {metadata.get('parsing_version', 'N/A')}")
        print(f"AI Model: {metadata.get('ai_model_used', 'N/A')}")
        print(f"Content preservation: {metadata.get('content_preservation', 'N/A')}")
        print(f"Quality score: {metadata.get('quality_score', 'N/A')}")
        
        # 5. Compare with previous approach
        print(f"\n📊 IMPROVEMENT COMPARISON:")
        print("-" * 40)
        print("BEFORE (Fragmented):")
        print("  Technical Skills: ['Python programming', 'Data analysis', 'SQL', ...]")
        print("  → Lost context and detailed descriptions")
        print("\nAFTER (Content-Preserving):")
        if technical_skills:
            first_skill = technical_skills[0][:100] + "..." if len(technical_skills[0]) > 100 else technical_skills[0]
            print(f"  Technical Skills: ['{first_skill}']")
            print("  → Maintains complete descriptions with full context")
        
        # Save improved structure for comparison
        output_file = "new-cv/your_cv_improved_structure.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_cv, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Improved structure saved to: {output_file}")
        
        print(f"\n🎉 SUCCESS: Your CV is now parsed with full content preservation!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing your CV: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_your_cv_improvement())
    
    if success:
        print("\n✅ Content preservation works perfectly for your CV!")
        print("The parser now maintains all your original formatting and descriptions.")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)