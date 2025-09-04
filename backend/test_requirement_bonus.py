#!/usr/bin/env python3
"""
Enhanced Requirement Bonus Test Script
Tests the _analyze_requirement_bonus functionality with real CV and JD data
"""

import json
import os
import sys
from typing import Dict, List, Any

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ats_enhanced_scorer import EnhancedATSScorer

def load_test_data():
    """Load the test CV and JD data"""
    cv_text = """Maheshwor Tiwari
0414 032 507 | maheshtwari99@gmail.com | LinkedIn | Hurstville, NSW, 2220
Blogs on Medium | GitHub | Dashboard Portfolio
CAREER PROFILE
I hold a PhD in Physics and completed a Master's in Data Science, bringing over three years of experience in Python
coding, AI, and machine learning. My expertise encompasses modeling and training AI models, writing efficient Python
scripts, designing and deploying robust data pipelines, conducting innovative research, and creating advanced
visualizations that convert complex data into actionable insights. I am also proficient in SQL, Tableau, and Power BI, building
comprehensive dashboards that support data-driven decision-making.
TECHNICAL SKILLS
• Specialized in Python programming, including data analysis, automation, and machine learning using libraries such
as Pandas, NumPy, and scikit-learn.
• Proficient in SQL for querying, modeling, and managing complex relational databases like PostgreSQL and MySQL.
• Skilled in creating interactive dashboards and visualizations using Tableau, Power BI, and Matplotlib.
• Experienced with GitHub for version control, Docker for containerization, and Snowflake for cloud data warehousing.
• Adept at leveraging tools like Visual Studio Code, Google Analytics, and Excel for data-driven solutions and reporting.
EDUCATION
Master of Data Science
Charles Darwin University, Sydney, AustraliaGPA Mar 2023 - Nov 2024
PhD in Physics
CY Cergy Paris University, Cergy, France Oct 2018 - Sep 2022
Master of Theoretical Physics
CY Cergy Paris University, Cergy, France Sep 2016 - Jun 2018
EXPERIENCE
Data Analyst Jul 2024 – Present
The Bitrates, Sydney, New South Wales, Australia
• Designed and implemented Python scripts for data cleaning, preprocessing, and analysis, improving data pipeline
efficiency by 30%.
• Developed machine learning models in Python for predictive analytics, enabling data-driven business decisions.
• Leveraged AI techniques to automate repetitive tasks, reducing manual effort and improving productivity.
• Built dynamic dashboards and visualizations using Python libraries like Matplotlib and Seaborn to communicate
insights effectively.
• Integrated Google Analytics data with Python for advanced analysis, enhancing customer behavior insights.
Data Analyst Mar 2024 – Jun 2024
iBuild Building Solutions, Victoria, Australia
• Automated data extraction and structuring of population datasets using Python, improving data accuracy and
team collaboration.
• Analyzed customer support data with Python to optimize response times and enhance operational efficiency.
• Developed Python-based solutions to generate actionable insights, meeting strict deadlines for strategic decision-
making.
• Designed Python scripts to create dynamic reports and dashboards, significantly improving customer satisfaction
and decision-making processes.
Software engineer and Analyst Jun 2023 - Nov 2023
Property Console, Sydney, Australia
• Built Python scripts to track key metrics, ensuring 99% data accuracy and improving data integrity and
operational efficiency.
• Collaborated with the development team to enhance analytics capabilities, using Python to improve data
processing speed by 25%.
• Leveraged Python for data preprocessing and analysis, producing Tableau dashboards that improved decision-
making.
• Supported cross-functional teams with Python-driven insights, enabling customer-focused initiatives.
Research Assistant Oct 2018 - Sep 2022
CY Cergy Paris University, Cergy-Pontoise, France
• Utilized advanced Python programming for computational modeling and solving complex research problems.
• Developed Python-based workflows to manage and analyze large datasets across multiple research projects.
• Presented Python-enabled research findings at international conferences, demonstrating technical expertise and
communication skills.
Lecturer and Course Facilitator
CY Cergy Paris University, Cergy-Pontoise, France Sep 2019 - Jun 2022
• Led engaging physics tutorials for master's students, enhancing understanding and promoting teamwork.
• Designed course materials, assignments, and exams, strengthening the learning experience.
• Mentored students on projects, collaborated with faculty, and fostered student engagement.
Research Intern
CY Cergy Paris University, Cergy-Pontoise, France Feb 2018 - Jun 2018
• Developed proficiency in Python programming by researching the effect of magnetic fields on 2D materials.
• Managed and analysed complex data sets, improving their accuracy and reliability.
• Used dashboard using Power BI to present research findings and participated in weekly reviews, improving
collaboration and research skills."""

    jd_text = """Business Analyst
Our Community
Job description
THE HIGHLIGHTS

Excellent career opportunity to apply your skills and make a difference
Join an innovative, established team
Generous conditions of employment
A new opportunity in 2025 with a progressive and innovative social enterprise!
USE YOUR BUSINESS ANALYTICAL SKILLS TO CREATE FAR-REACHING SOCIAL CHANGE

Calling all business analysts – Are you tired of the corporate grind? Would you like to make a difference in the community you live in?
Then we've got the job for you!
This position offers a rare opportunity to extend your career in a dynamic and successful social enterprise. You can help us maintain our software's position at the top of its class in Australia and New Zealand. You can have it all! Stimulating work, great conditions and a positive impact through your work.
ABOUT OUR COMMUNITY

The Our Community Group provides advice, connections, training and easy-to-use tech tools for people and organisations working to build stronger communities.
Our partners in that work are not-for-profit organisations and social enterprises; government, philanthropic and corporate grantmakers; donors and volunteers; enlightened businesses; and other community builders.
Our vision centres on social inclusion and social equity. Our dream is that every Australian should be able to go out their front door and stroll or wheel to a community group that suits their interests, passions and needs - or log on and do the same.
We want to help make it easy for people to join in, learn, celebrate, worship, plant trees, play a game, entertain, and be entertained, care and be cared for, support others and be supported, advocate for rights and celebrate diversity. To get involved. To be valued.
ABOUT THE OPPORTUNITY - BUSINESS ANALYST WITH A FLAIR FOR LEADERSHIP

We are looking for an experienced, enthusiastic and energetic Business Analyst with a flair for Leadership. You'll be working with a diverse team of high performing, committed and enthusiastic people who really care about making a difference for people and the not-for-profit sector.
As a Business Analyst you'll be integral to our team, helping us to prioritise, shape and define new features for our platform. You have excellent written and verbal communication skills, and your initiative and analytical skills are outstanding. With your flair for Project Management and high calibre organisation skills, you'll be essential in knowing what needs to be done, when it needs to be done and then making sure it happens.
Your strong communication and collaboration skills will enable you to lead and inspire team members to meet established goals. You will, of course, have a keen eye for detail and a commitment to continuous improvement and quality control. You'll take an idea from conception right through to release, leading the team and deliverables throughout the process.
WHAT WE NEED YOU TO DO

Work with stakeholders to take an idea, tease it out, and shape it into a deliverable scope
Lead and inspire fellow team mates to deliver the goal on time, to agreed scope and quality
Work with stakeholders to prioritise new features alongside other commitments including bug fixes, and small enhancements
Seek specific requirements from users, support and train staff, and developers, to produce a functional design that will meet users' needs while progressing the strategy of the product
Refine the scope and specific requirements into deliverables and testable user stories
Participate in planning and decision-making and other tasks as required
YOU WILL HAVE

Demonstrated ability to translate customer needs into requirements, user stories, business rules and acceptance criteria.
Proven track record managing the delivery of a piece of work to agreed scope, schedule and quality.
Strong analytical and lateral thinking skills that drive you to find the best solution, while being cognisant of constraints.
Strong communication skills (including listening, written and verbal) to ensure that you're able to elicit the requirements and convey them to others in an efficient and effective manner.
Experience working in an agile environment (scrum).
Experience in web-based application/s and web form projects, including mobile friendly applications.
Interest in and ability to use web-based technologies including Java and CSS
A belief in and commitment to our Manifesto.
THE IMPACT YOU WILL HAVE

This is your opportunity to be part of a game-changing agenda. We are impatient for progressive social change, and we aren't prepared to wait for others to create it. We want to be right at the centre of it. This role offers a unique opportunity to help shape the future of your community.
You'll get the opportunity to work in an ethical company with all the excitement and agility of a start-up without the headaches. We're built on solid foundations, we're sustainable and successful – but we've only just begun. We're not interested in just keeping things ticking along. We're builders and we're on a mission."""

    return cv_text, jd_text

def test_requirement_bonus():
    """Test the requirement bonus analysis"""
    print("🧪 Testing Enhanced Requirement Bonus Analysis")
    print("=" * 60)
    
    # Load test data
    cv_text, jd_text = load_test_data()
    
    print(f"📄 CV Length: {len(cv_text)} characters")
    print(f"📄 JD Length: {len(jd_text)} characters")
    
    # Initialize the scorer
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("💡 Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return None
    
    scorer = EnhancedATSScorer(api_key)
    
    try:
        print("\n🎯 Testing _analyze_requirement_bonus method...")
        
        # Test the requirement bonus analysis directly
        result = scorer._analyze_requirement_bonus(cv_text, jd_text)
        
        print("✅ Requirement bonus analysis completed successfully!")
        
        # Display the results
        print("\n📊 REQUIREMENT BONUS RESULTS:")
        print("=" * 50)
        
        # Critical requirements
        critical_reqs = result.get('critical_requirements', [])
        print(f"🔴 CRITICAL REQUIREMENTS: {len(critical_reqs)} found")
        for i, req in enumerate(critical_reqs[:5]):  # Show first 5
            status = "✅ MATCHED" if req.get('matched') else "❌ MISSING"
            print(f"   {i+1}. {req.get('requirement', 'Unknown')} - {status}")
            print(f"      JD Proof: {req.get('jd_proof_text', '')[:80]}...")
            print(f"      CV Evidence: {req.get('cv_evidence', '')[:80]}...")
            print()
        
        # Preferred requirements
        preferred_reqs = result.get('preferred_requirements', [])
        print(f"🟡 PREFERRED REQUIREMENTS: {len(preferred_reqs)} found")
        for i, req in enumerate(preferred_reqs[:3]):  # Show first 3
            status = "✅ MATCHED" if req.get('matched') else "❌ MISSING"
            print(f"   {i+1}. {req.get('requirement', 'Unknown')} - {status}")
            print(f"      JD Proof: {req.get('jd_proof_text', '')[:80]}...")
            print()
        
        # Bonus calculation
        bonus_calc = result.get('bonus_calculation', {})
        print("💰 BONUS CALCULATION:")
        print(f"   Critical Matches: {bonus_calc.get('critical_matches', 0)}/{bonus_calc.get('critical_total', 0)}")
        print(f"   Preferred Matches: {bonus_calc.get('preferred_matches', 0)}/{bonus_calc.get('preferred_total', 0)}")
        print(f"   Critical Points: {bonus_calc.get('critical_points', 0.0)}")
        print(f"   Preferred Points: {bonus_calc.get('preferred_points', 0.0)}")
        print(f"   Total Bonus Points: {bonus_calc.get('total_bonus_points', 0.0)}")
        
        # Save results to file for inspection
        output_file = "requirement_bonus_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing requirement bonus: {e}")
        import traceback
        print(f"📋 Stack trace:\n{traceback.format_exc()}")
        return None

def analyze_matches_in_detail(result):
    """Analyze the matches in more detail"""
    if not result:
        return
    
    print("\n🔍 DETAILED MATCH ANALYSIS:")
    print("=" * 50)
    
    # Critical requirements analysis
    critical_reqs = result.get('critical_requirements', [])
    matched_critical = [r for r in critical_reqs if r.get('matched')]
    missing_critical = [r for r in critical_reqs if not r.get('matched')]
    
    print(f"🔴 Critical Requirements: {len(matched_critical)} matched, {len(missing_critical)} missing")
    
    if matched_critical:
        print("✅ Matched Critical Requirements:")
        for req in matched_critical:
            print(f"   • {req.get('requirement')}")
    
    if missing_critical:
        print("❌ Missing Critical Requirements:")
        for req in missing_critical:
            print(f"   • {req.get('requirement')}")
            print(f"     JD Proof: {req.get('jd_proof_text', '')[:100]}...")
    
    # Preferred requirements analysis
    preferred_reqs = result.get('preferred_requirements', [])
    matched_preferred = [r for r in preferred_reqs if r.get('matched')]
    missing_preferred = [r for r in preferred_reqs if not r.get('matched')]
    
    print(f"\n🟡 Preferred Requirements: {len(matched_preferred)} matched, {len(missing_preferred)} missing")
    
    if matched_preferred:
        print("✅ Matched Preferred Requirements:")
        for req in matched_preferred:
            print(f"   • {req.get('requirement')}")
    
    if missing_preferred:
        print("❌ Missing Preferred Requirements:")
        for req in missing_preferred:
            print(f"   • {req.get('requirement')}")

if __name__ == "__main__":
    print("🚀 Enhanced Requirement Bonus Test Script")
    print("=" * 50)
    
    # Test the requirement bonus functionality
    result = test_requirement_bonus()
    
    if result:
        analyze_matches_in_detail(result)
        
        # Check if the result structure is correct
        required_keys = ['critical_requirements', 'preferred_requirements', 'bonus_calculation']
        missing_keys = [key for key in required_keys if key not in result]
        
        if missing_keys:
            print(f"\n⚠️  Missing keys in result: {missing_keys}")
        else:
            print(f"\n✅ All required keys present in result")
            
        print(f"\n🎯 Test completed successfully!")
    else:
        print(f"\n❌ Test failed - check API key and connectivity")