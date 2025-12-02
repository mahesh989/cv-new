# test_jd_analysis.py
import os
import json
import asyncio
from openai import AsyncOpenAI

# API Key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")  # Set OPENAI_API_KEY environment variable
MODEL = "gpt-4o"

# Hardcoded JD Text - paste your JD here
JD_TEXT = """
### ROLE OVERVIEW & CONTEXT

A highly motivated, organised and detail-oriented Data Analyst to join our high performing Business Intelligence Unit, who work closely with our business stakeholders, providing data to support data-driven business decision-making across Australia for UNHCR and New Zealand for UNHCR.

A data-passionate individual with strong analytical and problem-solving skills, to play a vital part in contributing to the evolving data requirements of the organisation by providing segmented data selections, data mining, analysis, and developing and maintaining reports.

### KEY RESPONSIBILITIES

- Delivering analytics on the business-critical objective of understanding how to maximise the value from our donors, in the form of data-mining, profile analysis, building analytical models and BI report authoring in Power BI or a similar reporting suite.  
- Addressing data extract requirements for direct marketing campaigns with a high degree of service; manipulating data in preparation for bulk communications, updating records with contact history, and working with Fundraising stakeholders to advise on segmentation strategies considering a multi-channel communication and donor-centricity approach.  
- Producing reports and analysis for reviewing results post campaign.  
- Building projection and segmentation models to answer key business questions.  
- Assisting the BI Analyst and BI Manager to administer and develop A4U’s data warehouse (DWH) considering current and future business requirements to strategise and implement enhancements to the platform through research, analysis, consultation and evaluation of program needs.  
- Working with a range of internal and external stakeholders to satisfy their business intelligence requirements for analysis, report creation, data selections, and data mining within a strong project management framework, driving evidence-based decision making throughout the organisation.  

### TECHNICAL REQUIREMENTS

- Experience building models in spreadsheets, and comfortable writing formulas and VBA in Excel.  
- Experience in the development, maintenance and remediation of issues relating to data models within a SQL data warehouse environment.  
- Strong SQL coding skills and database knowledge.  
- Experience using business intelligence tools such as Power BI, Tableau, etc.  
- Hands on experience in querying and extracting data across multiple, disparate and complex relational databases or a data warehouse.  

### EXPERIENCE REQUIREMENTS

- Minimum 2 years’ experience in a similar role.  
- Experience extracting data for marketing campaigns with knowledge of how to best utilise data to optimise campaign outcomes.  

### SOFT SKILLS & COMPETENCIES

- Strong project management skills to deliver multiple projects and work autonomously to meet deadlines.  
- Strong stakeholder management skills.  
- Excellent communication and customer service skills.  
- An advanced understanding of how data is used for communication purposes, the process and the governing regulations / best practice guidelines.  
- An appreciation of data issues and their solutions, particularly de-duplication and the importance of maintaining clean data.  

### WORK ARRANGEMENT

- Hybrid work arrangement with office located in Sydney CBD.  
- Full-time 15-month contract position.

"""
# SIMPLE PROMPT - Three sections only
# IMPROVED PROMPT
SYSTEM_PROMPT = """You are a skilled job description analyzer. Extract skills and categorize them into technical skills, soft skills, and domain knowledge. Return ONLY valid JSON.

CATEGORIZATION RULES:
- TECHNICAL: Tools (SQL, Excel), processes (data cleaning, ETL), technical artifacts (dashboards)
- SOFT SKILLS: Human interaction + behavioral traits (communication, leadership)  
- DOMAIN: Industry-specific terms (Healthcare, Finance, Nonprofit, Fundraising, Marketing)

EXTRACTION RULES:
- Extract direct mentions AS-IS
- Remove qualifiers: "strong SQL" → "SQL"
- Preserve specific tools: "Power BI" → "Power BI"
- Include implied skills from context
- Dont extract skills that are not mentioned in the job description"""

USER_PROMPT = f"""Extract ALL skills from this job description and categorize them:
{JD_TEXT}

Return ONLY this JSON format (three sections only):
{{
    "technical_skills": [],
    "soft_skills": [], 
    "domain_knowledge": []
}}

Be comprehensive - extract ALL mentioned tools, technologies, processes, and domain terms."""

async def test_three_sections():
    """Test with three sections only"""
    client = AsyncOpenAI(api_key=API_KEY)
    
    print("🔍 Testing JD Analysis - Three Sections Only")
    print("=" * 60)
    
    try:
        # Test with three sections format
        print("\n🧪 THREE SECTIONS ONLY")
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT}
            ],
            temperature=0.0,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        print(f"📦 Response length: {len(result)} characters")
        
        try:
            data = json.loads(result)
            print("✅ JSON parsed successfully")
            
            print(f"\n🎯 RESULTS:")
            print(f"Technical skills ({len(data.get('technical_skills', []))}):")
            for skill in data.get('technical_skills', []):
                print(f"  - {skill}")
            
            print(f"\nSoft skills ({len(data.get('soft_skills', []))}):")
            for skill in data.get('soft_skills', []):
                print(f"  - {skill}")
            
            print(f"\nDomain knowledge ({len(data.get('domain_knowledge', []))}):")
            for skill in data.get('domain_knowledge', []):
                print(f"  - {skill}")
                
        except Exception as e:
            print(f"❌ JSON parse failed: {e}")
            print("Raw response:", result)
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run the test"""
    if API_KEY == "your-api-key-here":
        print("❌ Please replace API_KEY with your actual OpenAI API key")
        return
        
    await test_three_sections()

if __name__ == "__main__":
    asyncio.run(main())
    