from src.generate_tailored_cv import generate_tailored_cv
from pydantic import BaseModel

class RealTestRequest(BaseModel):
    cv_filename: str = 'maheshwor_tiwari.pdf'
    jd_text: str = '''Data Analyst - Australia for UNHCR
    
Work in a high performing, values-driven organisation
Competitive salary with salary packaging benefits
Hybrid work arrangement with office located in Sydney CBD
Full-time 15-month contract position

ABOUT US
Our passionate team empowers refugees to find safety and protection when they need it most.
Australia for UNHCR is the UN Refugee Agency's partner in Australia, raising funds and awareness to assist people forced to flee conflict, disaster or persecution.

WHO WE ARE LOOKING FOR
A highly motivated, organised and detail-oriented Data Analyst to join our high performing Business Intelligence Unit, who work closely with our business stakeholders, providing data to support data-driven business decision-making across Australia for UNHCR and New Zealand for UNHCR.

YOU'LL MAKE AN IMPACT BY
- Delivering analytics on the business-critical objective of understanding how to maximise the value from our donors, in the form of data-mining, profile analysis, building analytical models and BI report authoring in Power BI or a similar reporting suite.
- Addressing data extract requirements for direct marketing campaigns with a high degree of service; manipulating data in preparation for bulk communications, updating records with contact history, and working with Fundraising stakeholders to advise on segmentation strategies considering a multi-channel communication and donor-centricity approach.
- Producing reports and analysis for reviewing results post campaign.
- Building projection and segmentation models to answer key business questions.
- Assisting the BI Analyst and BI Manager to administer and develop A4U's data warehouse (DWH) considering current and future business requirements to strategise and implement enhancements to the platform through research, analysis, consultation and evaluation of program needs.

WE WOULD LIKE YOU TO HAVE
- Minimum 2 years' experience in a similar role
- Experience building models in spreadsheets, and comfortable writing formulas and VBA in Excel.
- Experience in the development, maintenance and remediation of issues relating to data models within a SQL data warehouse environment.
- Strong SQL coding skills and database knowledge
- Experience using business intelligence tools such as Power BI, Tableau, etc.
- Hands on experience in querying and extracting data across multiple, disparate and complex relational databases or a data warehouse
- Strong project management skills to deliver multiple projects and work autonomously to meet deadlines
- Strong stakeholder management skills. Excellent communication and customer service skills
- Experience extracting data for marketing campaigns with knowledge of how to best utilise data to optimise campaign outcomes
- An advanced understanding of how data is used for communication purposes, the process and the governing regulations / best practice guidelines.
- An appreciation of data issues and their solutions, particularly de-duplication and the importance of maintaining clean data.'''
    custom_prompt: str = '''You are a smart CV assessment and tailoring agent embedded in an AI-powered resume assistant application.

The candidate has uploaded their general CV, and a job description has been either pasted directly or extracted from a provided link.

The applicant holds an advanced academic background: a PhD in Physics, two Master's degrees in Physics, and a Master's degree in Data Science. However, they are primarily applying for entry-level or graduate positions, or roles that require 2 to 3 years of experience. Unless the job description explicitly demands research-level qualifications or more than 2 to 3 years of experience, the PhD should be excluded from the final tailored CV.

The uploaded CV may contain 1 to 2 slightly enhanced or fabricated professional experiences to simulate industry relevance. These should only be included if they are realistic, believable, and clearly aligned with the job description.
This means the AI shouldn't automatically include these 1 to 2 potentially embellished experiences. It must evaluate them and only keep them in the tailored CV if they meet specific criteria (realistic, believable, relevant).

The candidate's technical skills (e.g., Python, SQL, Excel, Tableau) are genuine and listed in the original CV. Do not include technologies or tools that the candidate has not mentioned. For example, if the job description asks for BigQuery experience and it is not listed in the uploaded CV, you must not add it. Strictly avoid hallucinating experiences, technologies, or situations.

You may:
- Rename or rephrase role titles to better align with the job title (e.g., "Data Analyst Intern" -> "Data Coordinator").
- Emphasize transferable skills from academic projects or coursework.
- Slightly adjust bullet points within work experience and projects to incorporate relevant keywords and phrases from the job description, but only if these accurately reflect the candidate's experience and knowledge.
- Modify only the necessary sections of the CV to increase relevance and clarity.
- Ensure that the final CV is clean, professional, and optimized for Applicant Tracking Systems (ATS).

---

STEP 1: Fit Evaluation

Evaluate how well the uploaded CV matches the provided job description.

- If the match is poor, respond with: "Fit: Low" and suggest 2 to 3 realistic improvements that could improve the CV's alignment with the job, followed by a match score out of 10.
- If the match is good, respond with: "Fit: Good. Proceeding to tailored CV."

---

STEP 2: Tailored CV Generation

If the fit is good, generate a tailored CV in clean plain-text format that:

- Respects all the constraints above
- Integrates relevant keywords and key phrases previously extracted during the "Analyze Fit" step
- Reflects the user's actual capabilities and experience without hallucinating
- Prioritizes clarity, conciseness, and ATS-compatibility'''
    source: str = 'real_test'
    use_last_tested: bool = False
    is_new_cv: bool = False
    job_link: str = 'https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst?sectors=4'

def test_real_cv_generation():
    print("\n=== Testing Real CV Generation ===")
    print("CV: maheshwor_tiwari.pdf")
    print("Job: Australia for UNHCR Data Analyst")
    print("Link: https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst?sectors=4")
    
    print("\nCreating test request...")
    request = RealTestRequest()
    
    print("\nCalling generate_tailored_cv...")
    try:
        result = generate_tailored_cv(request)
        print("\n=== Generation Result ===")
        if isinstance(result, dict):
            print(f"✅ Success! Generated filename: {result.get('tailored_cv_filename', 'Unknown')}")
            print(f"Message: {result.get('message', 'No message')}")
            if 'metadata' in result:
                metadata = result['metadata']
                print(f"Company: {metadata.get('company', 'Unknown')}")
                print(f"Role: {metadata.get('role', 'Unknown')}")
        else:
            print(f"Result: {result}")
    except Exception as e:
        print(f"\n❌ Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_cv_generation() 