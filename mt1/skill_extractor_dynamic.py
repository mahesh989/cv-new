import anthropic
import os
import requests

# Configuration: Set the mode to choose between CV or JD analysis
active_mode = "cv"  # Change to "jd" to analyze JD text instead

# Configuration: Set your inputs here
cv_filename = "maheshwor_tiwari.pdf"  # Change to any CV filename you want to analyze
jd_url = "https://www.ethicaljobs.com.au/members/notoviolence/data-analyst-1"  # Change to any JD URL you want to analyze

# 🔐 SECURITY WARNING: Replace with your NEW API key after revoking the old one
# Better practice: use environment variables
os.environ["ANTHROPIC_API_KEY"] = "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"  # Replace this!

# Initialize the Claude client
client = anthropic.Anthropic()

# Function to get CV text from your existing API (any CV filename)
def get_cv_text(filename):
    try:
        response = requests.get(f"http://localhost:8000/get-cv-content/{filename}")
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ Error fetching CV text: {response.status_code}")
            return ""
    except Exception as e:
        print(f"❌ Error fetching CV text: {e}")
        return ""

# Function to get JD text from your existing API (any JD URL)
def get_jd_text(url):
    try:
        response = requests.post(
            "http://localhost:8000/scrape-job-description/",
            json={"url": url}
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("job_description", "")
        else:
            print(f"❌ Error fetching JD text: {response.status_code}")
            return ""
    except Exception as e:
        print(f"❌ Error fetching JD text: {e}")
        return ""

# Dynamic text loading based on active_mode
if active_mode == "cv":
    input_text = get_cv_text(cv_filename)
    text_type = "CV/Resume"
    analysis_context = "CV/Resume"
    print(f"📋 Analyzing CV: {cv_filename}")
elif active_mode == "jd":
    input_text = get_jd_text(jd_url)
    text_type = "Job Description"
    analysis_context = "job description"
    print(f"📋 Analyzing JD from: {jd_url}")
else:
    print("❌ Invalid active_mode. Please set to 'cv' or 'jd'")
    exit(1)

print(f"📋 Analyzing {text_type} text...")
print(f"📏 Text length: {len(input_text)} characters")

# Enhanced prompt template with technical skills, soft skills, and domain keywords
prompt = f"""
Extract SOFT SKILLS, TECHNICAL SKILLS, and DOMAIN KEYWORDS from this {analysis_context} and categorize them:

IMPORTANT: Only extract skills/keywords that are explicitly mentioned or have very strong textual evidence. Avoid assumptions or industry-standard inferences. Do not repeat skills/keywords that are already mentioned. 

## {text_type.upper()}: 
{input_text}

## SOFT SKILLS:
EXPLICIT (directly stated): List soft skills clearly mentioned
STRONGLY IMPLIED (very likely based on responsibilities): List soft skills heavily suggested with strong textual evidence

## TECHNICAL SKILLS:
EXPLICIT (directly stated): List technical skills, tools, software, qualifications clearly mentioned
STRONGLY IMPLIED (very likely based on responsibilities): List technical skills heavily suggested with strong textual evidence

## DOMAIN KEYWORDS:
EXPLICIT: List industry terms, sector-specific language, compliance areas, methodologies, and domain-specific concepts that are directly mentioned
STRONGLY IMPLIED: List domain keywords that are heavily suggested by the job context and responsibilities


## DOMAIN KEYWORDS:

EXPLICIT:  Your task is to extract **domain-specific keywords** related strictly to the **job role or functional expertise**, NOT the industry, organization, or its values.  
  List **industry terms**, **role-specific language**, **tools**, **methodologies**, **compliance concepts**, and **domain knowledge** that are **directly mentioned** in the {analysis_context}.

STRONGLY IMPLIED:  
  Your task is to extract **domain-specific keywords** related strictly to the **job role or functional expertise**, NOT the industry, organization, or its values.  
  List **domain-relevant concepts** that are **heavily suggested** by the context, responsibilities, or required outputs — even if not explicitly named.

### DO NOT include:
- Company or organization names  
- Program/service titles  
- Sector-level social causes  
- Values or mission statements  



## CONTEXT EVIDENCE:
For each skill/keyword, provide the relevant quote from the {analysis_context} that supports the extraction

At the end, provide THREE FINAL CLEAN LISTS:
1. SOFT SKILLS - Python list of strings containing all soft skills
2. TECHNICAL SKILLS - Python list of strings containing all technical skills  
3. DOMAIN KEYWORDS - Python list of strings containing all domain-specific terms

Text: \"\"\"
{input_text.strip()}
\"\"\"
"""

try:
    # Call Claude Sonnet 4
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0.2,
        system=f"You are a precise extractor of soft skills from professional {analysis_context}s.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Print the result
    print(f"\n🔍 Comprehensive Skills & Domain Analysis for {text_type}:\n")
    print(response.content[0].text.strip())
    
except anthropic.AuthenticationError:
    print("❌ Authentication Error: Please check your API key")
    print("Make sure you have a valid API key from https://console.anthropic.com")
    
except anthropic.APIError as e:
    print(f"❌ API Error: {e}")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

# Expected output would include both soft and technical skills:
# SOFT: ['communication skills', 'leadership', 'accountability', 'analytical thinking', 
#        'problem-solving', 'stakeholder management', 'attention to detail', 'adaptability']
# TECHNICAL: ['Business Intelligence tools', 'Microsoft Excel', 'Database management', 
#             'Data analysis', 'Systems administration', 'KPI reporting', 'SQL', 'Data visualization'] 