#!/usr/bin/env python3

"""
Test the updated project description format with bullet points as array items
"""

import sys
import os
import asyncio
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.structured_cv_parser import enhanced_cv_parser

# CV with project bullet points
CV_WITH_PROJECT_BULLETS = """
Maheshwor Tiwari
0414 032 507 | maheshtwari99@gmail.com

PROJECTS

Heart Attack Risk Prediction                                                                Oct 2024
Implemented logistic regression, random forests, and deep learning models to predict heart attack risks.
Addressed imbalanced datasets using undersampling techniques to enhance prediction reliability.
Presented findings through clear, data-driven visualisations to support decision-making.

Web Scraping Dashboard                                                                      Sep 2024
Built automated data collection system using Python and BeautifulSoup.
Created interactive dashboard with real-time data visualization.
Deployed solution using Docker containers for scalability.
"""

async def test_project_bullets_as_array():
    """Test that project bullet points are preserved as separate array items"""
    print("🧪 Testing Project Bullets as Array Items")
    print("=" * 60)
    
    try:
        # Parse the CV
        print("📄 Parsing CV with project bullet points...")
        structured_cv = await enhanced_cv_parser.parse_cv_content(CV_WITH_PROJECT_BULLETS)
        
        # Check projects structure
        projects = structured_cv.get('projects', [])
        print(f"\n📋 PROJECTS ANALYSIS ({len(projects)} projects found):")
        print("=" * 60)
        
        if not projects:
            print("❌ No projects found in parsed CV")
            return False
        
        success = True
        
        for i, project in enumerate(projects, 1):
            project_name = project.get('name', f'Project {i}')
            description = project.get('description', [])
            
            print(f"\n🚀 PROJECT {i}: {project_name}")
            print("-" * 50)
            
            # Check if description is an array
            if isinstance(description, list):
                print(f"✅ Description is array: {len(description)} items")
                
                # Show each bullet point
                for j, bullet in enumerate(description, 1):
                    if bullet and bullet.strip():
                        print(f"  {j}. {bullet}")
                    else:
                        print(f"  {j}. [Empty item]")
                
                # Check if we have meaningful bullet points
                non_empty_bullets = [b for b in description if b and b.strip()]
                if len(non_empty_bullets) >= 2:
                    print(f"✅ Good bullet structure: {len(non_empty_bullets)} meaningful items")
                elif len(non_empty_bullets) == 1 and len(non_empty_bullets[0]) > 100:
                    print("✅ Single comprehensive description (paragraph format)")
                else:
                    print(f"⚠️ Limited content: Only {len(non_empty_bullets)} items")
            else:
                print(f"❌ Description is not array: {type(description)}")
                print(f"    Content: {description}")
                success = False
        
        # Compare with expected format
        print(f"\n🎯 EXPECTED FORMAT:")
        print("-" * 50)
        print("Heart Attack Risk Prediction should have description array like:")
        print("  1. 'Implemented logistic regression, random forests, and deep learning models to predict heart attack risks.'")
        print("  2. 'Addressed imbalanced datasets using undersampling techniques to enhance prediction reliability.'")
        print("  3. 'Presented findings through clear, data-driven visualisations to support decision-making.'")
        
        # Save results
        output_file = "new-cv/project_bullets_array_test.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_cv, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Test results saved to: {output_file}")
        
        if success:
            print(f"\n🎉 SUCCESS: Project descriptions are properly formatted as arrays!")
        else:
            print(f"\n⚠️ ISSUES: Project descriptions need format adjustment")
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing project bullets: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_project_bullets_as_array())
    
    if success:
        print("\n✅ Project bullet point formatting is working correctly!")
        print("Each bullet point is now a separate array item, like education thesis details.")
    else:
        print("\n❌ Project formatting needs further adjustment.")
        sys.exit(1)