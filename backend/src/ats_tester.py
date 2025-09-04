# Standard library imports
import os
import json
import re
import asyncio
from pathlib import Path
from typing import List, Tuple, Dict
import signal
import sys
import time

# Third-party imports
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
# OpenAI imports removed - we only use DeepSeek
from dotenv import load_dotenv
import pdfplumber
from docx import Document
import spacy
from datetime import datetime
import httpx
import logging
import atexit
from .ai_config import get_model_params

# Local imports
from src.cv_parser import extract_text_from_pdf, extract_text_from_docx
# from .ats_prompt import system_prompt  # Removed - will be moved to dedicated ATS rules file
# Local implementations to avoid dependency on generate_tailored_cv
import string
import re
from .llm_keyword_matcher import LLMKeywordMatcher, CategoryComparison

# Standard LLM-based ATS testing only

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# We only use DeepSeek AI service - OpenAI client removed
# The DeepSeek service is initialized via hybrid_ai_service

# Initialize spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.warning(f"Failed to load spaCy model: {str(e)}")
    nlp = None

# Constants
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
TAILORED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tailored_cvs"))
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
# ATS constants will be imported from rules engine at runtime

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TAILORED_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

router = APIRouter()

# Global state for tracking active operations
active_operations = set()

def cleanup_resources():
    """Cleanup function to be called on shutdown"""
    logger.info("Cleaning up resources...")
    # Add any cleanup operations here
    logger.info("Cleanup complete")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    cleanup_resources()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Register cleanup function
atexit.register(cleanup_resources)

# Local implementations of functions from generate_tailored_cv to avoid dependencies
def normalize(text: str) -> str:
    """Normalize text by removing punctuation and converting to lowercase."""
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def extract_jd_analysis(jd_text: str) -> dict:
    """Extract skills from job description using DeepSeek AI"""
    try:
        # Import DeepSeek service
        from .hybrid_ai_service import hybrid_ai
        
        # Initialize services
        ai_service = hybrid_ai
        
        print("🔍 [JD-DEEPSEEK] Using DeepSeek AI for JD analysis...")
        
        prompt = f"""You are a job description keyword extractor.

Extract exactly three comma-separated lists, strictly from the text below—only include terms that appear verbatim. Do NOT infer, rephrase, or hallucinate.

CRITICAL RULES:
1. Extract ONLY keywords that ACTUALLY APPEAR in the text
2. Use exact terminology from the text (preserve original casing/naming)
3. Do NOT add skills that are not explicitly mentioned
4. Return results in the exact format specified

Technical Skills: (tools, software, platforms, programming languages, frameworks)
Soft Skills: (interpersonal, work habits, communication, leadership)
Domain Keywords: (industry terms, organizational phrases, certifications, methodologies)

Return exactly in this format (no extra commentary):

Technical Skills: term1, term2, ...
Soft Skills: term1, term2, ...
Domain Keywords: term1, term2, ...

Job Description:
{jd_text}
"""
        
        response_text = ai_service.generate_response(
            prompt=prompt,
            temperature=0.0,
            max_tokens=1000
        )
        
        print(f"🔍 [JD-DEEPSEEK] Raw response: {response_text}")
        
        def extract_list(label: str, text: str):
            pattern = rf"{label}:\s*(.*?)(?=\n[A-Z][^:]*:|$)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                items = [w.strip() for w in match.group(1).split(",") if w.strip()]
                # Filter out obvious artifacts
                valid_items = []
                for item in items:
                    item = item.strip().strip('"').strip("'")
                    if (item and 
                        len(item) > 1 and 
                        item.lower() not in ['n/a', 'none', 'not applicable', 'not found']):
                        valid_items.append(item)
                return valid_items if valid_items else ["N/A"]
            return ["N/A"]
        
        technical_skills = extract_list("Technical Skills", response_text)
        soft_skills = extract_list("Soft Skills", response_text)
        domain_keywords = extract_list("Domain Keywords", response_text)
        
        print(f"✅ [JD-DEEPSEEK] Technical: {technical_skills}")
        print(f"✅ [JD-DEEPSEEK] Soft: {soft_skills}")
        print(f"✅ [JD-DEEPSEEK] Domain: {domain_keywords}")
        
        # Return in expected format
        return {
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'domain_keywords': domain_keywords
        }
        
    except Exception as e:
        print(f"❌ [JD-UNIVERSAL] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'technical_skills': [],
            'soft_skills': [],
            'domain_keywords': [],
            'error': str(e)
        }

def extract_cv_skills(cv_text: str) -> dict:
    """Extract skills from CV text using AI"""
    try:
        # Import hybrid_ai service
        from .hybrid_ai_service import hybrid_ai
        # Use DeepSeek API for consistency with JD extraction
        ai_service = hybrid_ai
        
        prompt = f"""You are a CV keyword extractor.

Extract exactly three comma-separated lists, strictly from the text below—only include terms that appear verbatim. Do NOT infer, rephrase, or hallucinate.

CRITICAL RULES:
1. Extract ONLY keywords that ACTUALLY APPEAR in the text
2. Use exact terminology from the text (preserve original casing/naming)
3. Do NOT add skills that are not explicitly mentioned
4. Return results in the exact format specified

Technical Skills: (tools, software, platforms)
Soft Skills: (interpersonal, work habits, communication)
Domain Keywords: (industry terms, organizational phrases)

Return exactly in this format (no extra commentary):

Technical Skills: term1, term2, ...
Soft Skills: term1, term2, ...
Domain Keywords: term1, term2, ...

CV:
{cv_text}
"""
        
        response_text = ai_service.generate_response(
            prompt=prompt,
            temperature=0.0,
            max_tokens=800
        )
        
        print(f"🔍 [CV-DEEPSEEK] Raw response: {response_text}")
        
        def extract_list(label: str, text: str):
            pattern = rf"{label}:\s*(.*?)(?=\n[A-Z][^:]*:|$)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                items = [w.strip() for w in match.group(1).split(",") if w.strip()]
                # Filter out obvious artifacts
                valid_items = []
                for item in items:
                    item = item.strip().strip('"').strip("'")
                    if (item and 
                        len(item) > 1 and 
                        item.lower() not in ['n/a', 'none', 'not applicable', 'not found']):
                        valid_items.append(item)
                return valid_items if valid_items else ["N/A"]
            return ["N/A"]

        technical_skills = extract_list("Technical Skills", response_text)
        soft_skills = extract_list("Soft Skills", response_text)
        domain_keywords = extract_list("Domain Keywords", response_text)
        
        print(f"✅ [CV-DEEPSEEK] Technical: {technical_skills}")
        print(f"✅ [CV-DEEPSEEK] Soft: {soft_skills}")
        print(f"✅ [CV-DEEPSEEK] Domain: {domain_keywords}")
        
        return {
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "domain_keywords": domain_keywords
        }
        
    except Exception as e:
        print(f"❌ [CV-DEEPSEEK] Error: {e}, falling back to basic extraction")
        # Fallback to basic extraction
        return {
            "technical_skills": ["N/A"],
            "soft_skills": ["N/A"],
            "domain_keywords": ["N/A"]
        }

# Helper functions for cleaning AI responses
def _clean_ai_response(ai_response: str) -> str:
    """Clean AI response by removing instructional text artifacts."""
    # Remove common AI response prefixes and explanatory text
    ai_artifacts = [
        "from the text provided",
        "from the provided text", 
        "from this text",
        "here are the relevant",
        "here are the",
        "here's the extracted",
        "here's the",
        "extracted soft skills list",
        "extracted technical skills list",
        "extracted domain keywords list",
        "the following are",
        "below are the",
        "i can extract",
        "i have extracted",
        "based on the text",
        "from the given text",
        "technical skills:",
        "soft skills:",
        "soft skills",
        "domain keywords:",
        "domain-specific keywords and",
        "domain-specific keywords:",
        "industry terms:",
        "keywords:",
        "skills:",
        "certifications:",
        "requirements:",
        "good examples:",
        "bad examples:",
        "strict rules:",
        "task:",
        "which were excluded as per the strict rules",
        "and benefits",
        "company information",
        "list:",
        "list",
        "and interpersonal traits:",
        "and interpersonal traits",
        "interpersonal traits:",
        "interpersonal traits",
        "note: i've kept only the",
        "i've kept only the",
        "note:",
        "excluding generic",
        "excluding",
        "generic job responsibilities",
        "job responsibilities",
        "industry-specific terms and methodologies",
        "terms and methodologies",
        "methodologies",
        "clean of only:",
        "clean of only"
    ]
    
    cleaned = ai_response.lower()
    
    # Remove artifacts from the beginning and middle of response
    for artifact in ai_artifacts:
        cleaned = cleaned.replace(artifact, "")
    
    # Remove any remaining colons at the beginning
    cleaned = re.sub(r'^[:\s]+', '', cleaned)
    
    # Remove newlines and normalize whitespace
    cleaned = re.sub(r'\n+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove any text in parentheses that looks like explanations
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    
    # Remove any numbered lists or bullet points
    cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
    cleaned = re.sub(r'^[-•]\s*', '', cleaned)
    
    # Remove any sentences that don't look like skill names
    words = cleaned.split(',')
    valid_words = []
    for word in words:
        word = word.strip()
        if word and _looks_like_skill(word):
            valid_words.append(word)
    
    return ', '.join(valid_words)

def _looks_like_skill(text: str) -> bool:
    """Check if text looks like a skill name."""
    text = text.strip().lower()
    
    # Skip empty or very short text
    if not text or len(text) < 2:
        return False
    
    # Skip anything containing AI instruction words
    ai_instruction_words = [
        "clean", "only", "interpersonal", "traits", "extract", "list",
        "following", "based", "provided", "relevant", "examples",
        "strict", "rules", "task", "excluded", "note", "information"
    ]
    
    # If text contains multiple AI instruction words, it's likely an artifact
    ai_word_count = sum(1 for word in ai_instruction_words if word in text)
    if ai_word_count >= 2:
        return False
    
    # Skip if it contains colons (often indicates explanatory text)
    if ":" in text:
        return False
    
    # Skip obvious non-skills
    skip_phrases = [
        "from", "the", "text", "provided", "here", "are", "relevant",
        "following", "based", "on", "given", "extract", "extracted",
        "good", "bad", "examples", "strict", "rules", "task",
        "which", "were", "excluded", "per", "company", "information",
        "benefits", "and", "as", "of", "in", "to", "for", "with",
        "this", "that", "these", "those", "they", "them", "their",
        "apply", "now", "sign", "search", "jobs", "career", "advice",
        "join", "us", "main", "navigation", "menu", "click", "link",
        "clean of", "only"
    ]
    
    # If the text is just one of these skip phrases, reject it
    if text in skip_phrases:
        return False
    
    # If the text contains mostly skip phrases, reject it
    words = text.split()
    skip_word_count = sum(1 for word in words if word in skip_phrases)
    if skip_word_count > len(words) / 2:
        return False
    
    # Accept if it looks like a skill
    return True

def _is_valid_skill(skill: str) -> bool:
    """Validate if a skill is actually a skill and not an artifact."""
    skill = skill.strip()
    
    # Skip empty skills
    if not skill:
        return False
    
    # Skip very long skills (likely sentences)
    if len(skill) > 100:
        return False
    
    # Skip skills that are clearly categories or generic terms
    invalid_terms = [
        "technical skills", "soft skills", "domain keywords",
        "locations", "responsibilities", "requirements",
        "business intelligence", "note", "excluding",
        "generic", "methodologies", "terms"
    ]
    
    skill_lower = skill.lower()
    for invalid_term in invalid_terms:
        if skill_lower == invalid_term:
            return False
    
    # Skip obvious UI/navigation elements
    ui_elements = [
        "apply now", "sign in", "search jobs", "main navigation",
        "menu", "click here", "job ad", "career advice", "join us",
        "ethical jobs", "logo", "advanced search", "work from home"
    ]
    
    for ui_element in ui_elements:
        if ui_element in skill_lower:
            return False
    
    # Skip if it starts with common AI response prefixes
    ai_prefixes = ["eap", "note:", "excluding", "generic"]
    for prefix in ai_prefixes:
        if skill_lower.startswith(prefix):
            return False
    
    return True

class ATSTestRequest(BaseModel):
    cv_filename: str
    jd_text: str
    prompt: str
    cv_type: str  # 'uploaded' or 'tailored'

class ATSTestResult(BaseModel):
    overall_score: int
    keyword_match: int
    skills_match: int
    matched_hard_skills: List[str]
    missed_hard_skills: List[str]
    matched_soft_skills: List[str]
    missed_soft_skills: List[str]
    matched_domain_keywords: List[str]
    missed_domain_keywords: List[str]
    tips: List[str]

def read_uploaded_cv_text(filename: str) -> str:
    path = os.path.join(UPLOAD_DIR, filename)
    print(f"🛠️ Checking uploaded CV at path: {path}")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Uploaded CV not found.")
    
    try:
        # Determine file type and use appropriate parser
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            print(f"📄 Parsing PDF file: {filename}")
            return extract_text_from_pdf(path)
        elif ext == ".docx":
            print(f"📄 Parsing DOCX file: {filename}")
            return extract_text_from_docx(path)
        else:
            # For plain text files, try UTF-8 encoding
            print(f"📄 Reading text file: {filename}")
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"❌ Error reading uploaded CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read uploaded CV: {str(e)}")

def read_tailored_cv_text(filename: str) -> str:
    path = os.path.join(TAILORED_DIR, filename)
    print(f"🛠️ Checking tailored CV at path: {path}")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Tailored CV not found.")
    
    try:
        # Determine file type and use appropriate parser
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            print(f"📄 Parsing PDF file: {filename}")
            return extract_text_from_pdf(path)
        elif ext == ".docx":
            print(f"📄 Parsing DOCX file: {filename}")
            doc = Document(path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            print(f"✅ Parsed {len(paragraphs)} non-empty paragraphs from tailored CV")
            return "\n".join(paragraphs)
        else:
            # For plain text files, try UTF-8 encoding
            print(f"📄 Reading text file: {filename}")
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"❌ Error reading tailored CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read tailored CV: {str(e)}")

# Helper: Parse CV into sections
def parse_cv_sections(cv_text):
    sections = {}
    current_section = None
    for line in cv_text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Simple section header detection
        if re.match(r'^(Experience|Work Experience|Projects|Skills|Education|Certifications|Summary)[:\s]*$', line, re.IGNORECASE):
            current_section = line.lower().replace(':', '').strip()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)
    return sections

# Helper: Extract skills from section text using LLM/NLP (fallback to list)
def extract_skills_from_section(section_lines):
    text = ' '.join(section_lines)
    # Use simple regex for now; can be replaced with LLM call
    skills = re.findall(r'\b([A-Za-z][A-Za-z0-9\-\+\#\. ]{2,})\b', text)
    return [s.strip().lower() for s in skills if len(s.strip()) > 2]

# Helper: Extract skills using LLM with better prompts and deduplication
async def extract_skills_llm(text: str, skill_type: str) -> list[str]:
    print(f"🔍 [LLM] Extracting {skill_type} from text (length: {len(text)})")

    # Expert-level, example-rich prompts for each skill type
    if skill_type == "technical skills":
        prompt = f"""You are an expert in parsing CVs and job descriptions for technical skills.

Task:
From the text below, extract ONLY individual technical skills, programming languages, software tools, platforms, libraries, frameworks, and certifications.

Strict rules:
- Do NOT include job titles, soft skills, company names, locations, UI/navigation text, or full sentences.
- Do NOT include generic phrases, responsibilities, or action verbs.
- Do NOT include domain-specific jargon unless it is a tool, platform, or certification.
- Output a clean, comma-separated list of technical skills only — no extra commentary, no duplicates.

Good examples:
Python, SQL, Tableau, AWS, Docker, ReactJS, Microsoft Excel, Power BI, Salesforce, Google Analytics, Java, C++, Linux, Git, Kubernetes, TensorFlow, Azure, SAP, HTML, CSS, JavaScript, R, SPSS, Hadoop, Jenkins, Scrum Master, PMP, AWS Certified Solutions Architect, CCNA, ITIL

Bad examples:
work from home advanced search, main navigation ethical jobs logo, Data Analyst at Deloitte, managed a team, excellent communication, Sydney, Australia, project management experience, responsible for, join us sign in, job ad, career advice, led a project, passionate about technology

Text:
{text}
"""
    elif skill_type == "soft skills":
        prompt = f"""You are analyzing text for interpersonal and behavioral competencies.

Task:
From the text below, extract ONLY individual soft skills or interpersonal traits (e.g., teamwork, communication, leadership, adaptability, problem solving, time management, empathy, resilience, attention to detail, critical thinking, decision-making, conflict resolution, creativity, flexibility, work ethic, reliability, collaboration, active listening, negotiation, emotional intelligence, self-motivation, stress management, organization, accountability, patience, openness to feedback).

Strict rules:
- Do NOT include job titles, technical skills, company names, locations, UI/navigation text, or full sentences.
- Do NOT include generic phrases, responsibilities, or action verbs.
- Do NOT include domain-specific jargon or certifications.
- Output a clean, comma-separated list of soft skills only — no extra commentary, no duplicates.

Good examples:
Communication, Teamwork, Leadership, Adaptability, Problem Solving, Time Management, Empathy, Resilience, Attention to Detail, Critical Thinking, Decision-Making, Conflict Resolution, Creativity, Flexibility, Work Ethic, Reliability, Collaboration, Active Listening, Negotiation, Emotional Intelligence, Self-Motivation, Stress Management, Organization, Accountability, Patience, Openness to Feedback

Bad examples:
apply now, sign in, search jobs, Data Analyst, Python, Sydney, Australia, managed a team, responsible for, join us sign in, job ad, career advice, led a project, passionate about technology, project management experience

Text:
{text}
"""
    else:  # domain keywords
        prompt = f"""You are parsing text for industry-specific terms and sector-specific certifications.

Task:
From the text below, extract ONLY individual domain-specific keywords, industry jargon, sector-specific methodologies, standards, regulations, or certifications (e.g., IFRS, HIPAA, GDPR, Six Sigma, Lean, Agile, Scrum, Basel III, SOX, Clinical Trials, EHR, PCI DSS, ISO 9001, Financial Modeling, Equity Valuation, White Card, RSA, NDIS, AHPRA, APRA, AML, KYC, SAP FICO, Epic, Meditech, Salesforce CRM, Clinical Governance, GMP, HACCP, TGA, PBX, NDIS, RTO, VET, NDIS Worker Screening, NDIS Practice Standards).

Strict rules:
- Do NOT include job titles, soft skills, technical skills, company names, locations, UI/navigation text, or full sentences.
- Do NOT include generic phrases, responsibilities, or action verbs.
- Output a clean, comma-separated list of domain-specific keywords only — no extra commentary, no duplicates.

Good examples:
IFRS, HIPAA, GDPR, Six Sigma, Lean, Agile, Scrum, Basel III, SOX, Clinical Trials, EHR, PCI DSS, ISO 9001, Financial Modeling, Equity Valuation, White Card, RSA, NDIS, AHPRA, APRA, AML, KYC, SAP FICO, Epic, Meditech, Salesforce CRM, Clinical Governance, GMP, HACCP, TGA, PBX, RTO, VET, NDIS Worker Screening, NDIS Practice Standards

Bad examples:
apply now, sign in, search jobs, Data Analyst, Python, Sydney, Australia, managed a team, responsible for, join us sign in, job ad, career advice, led a project, passionate about technology, project management experience, communication, teamwork

Text:
{text}
"""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skill extraction expert. Extract skills and return them as a comma-separated list. Be specific and avoid duplicates."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            timeout=120
        )

        llm_content = response.choices[0].message.content
        print(f"📥 [LLM] Raw response for {skill_type}: '{llm_content}'")

        # Check if response is empty or None
        if not llm_content or llm_content.strip() == "":
            print(f"❌ [LLM] Empty response for {skill_type}, falling back to regex")
            return extract_skills_from_section(text.splitlines())

        # 🔧 CLEAN AI RESPONSE: Remove instructional text artifacts
        cleaned_content = _clean_ai_response(llm_content)
        print(f"🧹 [LLM] Cleaned response for {skill_type}: '{cleaned_content}'")

        # Parse comma-separated list
        skills = [normalize(s) for s in cleaned_content.split(',') if s and s.strip() and s.strip().lower() != "n/a"]
        skills = [s for s in skills if s and _is_valid_skill(s)]
        print(f"✅ [LLM] Successfully extracted {len(skills)} {skill_type}: {skills}")

        if not skills:
            print(f"⚠️ [LLM] LLM returned empty list for {skill_type}, trying fallback")
            fallback_skills = extract_skills_from_section(text.splitlines())
            print(f"🔄 [FALLBACK] Regex extracted {len(fallback_skills)} {skill_type}: {fallback_skills}")
            return fallback_skills

        return skills

    except Exception as e:
        print(f"❌ [LLM] Error in LLM skill extraction for {skill_type}: {str(e)}")
        print(f"🔄 [LLM] Falling back to regex-based skill extraction for {skill_type}")
        fallback_skills = extract_skills_from_section(text.splitlines())
        print(f"✅ [FALLBACK] Regex extracted {len(fallback_skills)} {skill_type}: {fallback_skills}")
        return fallback_skills

# Helper: Remove duplicates across skill categories
def deduplicate_skills(technical: list[str], soft: list[str], domain: list[str]) -> tuple[list[str], list[str], list[str]]:
    print(f"🔄 [DEDUP] Removing duplicates across categories...")
    print(f"🔄 [DEDUP] Before - Technical: {len(technical)}, Soft: {len(soft)}, Domain: {len(domain)}")
    
    # Normalize all skills for comparison
    tech_normalized = [normalize(s) for s in technical]
    soft_normalized = [normalize(s) for s in soft]
    domain_normalized = [normalize(s) for s in domain]
    
    # Define common terms that should not be in domain keywords
    common_terms = {
        'data analysis', 'reporting', 'business intelligence', 'data management',
        'data visualization', 'process improvement', 'project management',
        'communication', 'teamwork', 'leadership', 'problem solving',
        'time management', 'analytical skills', 'critical thinking',
        'excel', 'microsoft office', 'powerpoint', 'word', 'outlook',
        'training', 'troubleshooting', 'documentation', 'testing'
    }
    
    # Priority: Technical > Soft > Domain
    # Remove from soft skills if already in technical
    soft_filtered = []
    for i, skill in enumerate(soft):
        if soft_normalized[i] not in tech_normalized:
            soft_filtered.append(skill)
        else:
            print(f"🔄 [DEDUP] Removed '{skill}' from soft (already in technical)")
    
    # Remove from domain if already in technical or soft, or if it's a common term
    domain_filtered = []
    soft_filtered_normalized = [normalize(s) for s in soft_filtered]
    for i, skill in enumerate(domain):
        skill_norm = domain_normalized[i]
        
        # Check if it's already in technical or soft
        if skill_norm in tech_normalized:
            print(f"🔄 [DEDUP] Removed '{skill}' from domain (already in technical)")
            continue
        elif skill_norm in soft_filtered_normalized:
            print(f"🔄 [DEDUP] Removed '{skill}' from domain (already in soft)")
            continue
        
        # Check if it's a common term that shouldn't be domain-specific
        is_common = False
        for common_term in common_terms:
            if common_term in skill_norm or skill_norm in common_term:
                print(f"🔄 [DEDUP] Removed '{skill}' from domain (common term)")
                is_common = True
                break
        
        # Check if it contains only common words
        words = skill_norm.split()
        if len(words) <= 2 and all(word in ['data', 'analysis', 'business', 'management', 'process', 'system', 'support', 'service', 'work', 'experience'] for word in words):
            print(f"🔄 [DEDUP] Removed '{skill}' from domain (too generic)")
            is_common = True
        
        if not is_common:
            domain_filtered.append(skill)
    
    print(f"🔄 [DEDUP] After - Technical: {len(technical)}, Soft: {len(soft_filtered)}, Domain: {len(domain_filtered)}")
    return technical, soft_filtered, domain_filtered

# Helper: Improved semantic matching with individual skill comparison
async def semantic_match_with_synonyms(jd_skills: list[str], cv_skills: list[str], threshold: float = 0.6) -> tuple[list[str], list[str]]:
    """Match skills between JD and CV using string similarity and LLM-based synonym matching."""
    print(f"🔍 [MATCH] Starting skill matching...")
    
    # Filter out UI text and very long strings
    ui_terms = ['menu', 'navigation', 'search', 'arrow', 'form', 'button', 'click', 'link', 'page', 'website']
    jd_skills = [s for s in jd_skills if len(s) <= 100 and not any(term in s.lower() for term in ui_terms)]
    cv_skills = [s for s in cv_skills if len(s) <= 100 and not any(term in s.lower() for term in ui_terms)]
    
    print(f"🔍 [MATCH] Filtered JD skills ({len(jd_skills)}): {jd_skills}")
    print(f"🔍 [MATCH] Filtered CV skills ({len(cv_skills)}): {cv_skills}")
    
    if not jd_skills:
        print(f"⚠️ [MATCH] No JD skills to match")
        return [], []
    
    if not cv_skills:
        print(f"⚠️ [MATCH] No CV skills to match against")
        return [], jd_skills
    
    matched = []
    missed = []
    
    # Convert all skills to lowercase for better matching
    cv_skills_lower = [skill.lower() for skill in cv_skills]
    jd_skills_lower = [skill.lower() for skill in jd_skills]
    
    for i, jd_skill in enumerate(jd_skills):
        jd_skill_lower = jd_skills_lower[i]
        skill_matched = False
        
        # 1. Try exact match
        if jd_skill_lower in cv_skills_lower:
            matched.append(jd_skill)
            skill_matched = True
            print(f"✅ [MATCH] Exact match: '{jd_skill}'")
            continue
        
        # 2. Try partial match
        words_in_jd_skill = jd_skill_lower.split()
        if len(words_in_jd_skill) > 1:
            # Check if all significant words are present in any CV skill
            significant_words = [w for w in words_in_jd_skill if len(w) > 3]
            for cv_skill_lower in cv_skills_lower:
                if all(word in cv_skill_lower for word in significant_words):
                    matched.append(jd_skill)
                    skill_matched = True
                    print(f"✅ [MATCH] Partial match: '{jd_skill}' (all significant words found)")
                    break
        
        # 3. Try LLM-based synonym matching
        if not skill_matched:
            try:
                # Get synonyms for the JD skill
                synonyms = await get_skill_synonyms(jd_skill)
                if synonyms:  # Only proceed if we got valid synonyms
                    synonyms_lower = [s.lower() for s in synonyms]
                    
                    # Check if any synonym matches a CV skill
                    for cv_skill_lower in cv_skills_lower:
                        if cv_skill_lower in synonyms_lower:
                            matched.append(jd_skill)
                            skill_matched = True
                            print(f"✅ [MATCH] Synonym match: '{jd_skill}'")
                            break
            except Exception as e:
                print(f"❌ [MATCH] Error in synonym matching for '{jd_skill}': {str(e)}")
        
        # If still not matched, add to missed list
        if not skill_matched:
            missed.append(jd_skill)
            print(f"❌ [MATCH] No match found for '{jd_skill}'")
    
    # Final verification: ensure no skill appears in both lists
    matched_set = set(normalize(s) for s in matched)
    missed_verified = [s for s in missed if normalize(s) not in matched_set]
    
    print(f"🎯 [MATCH] Final results - Matched: {len(matched)}, Missed: {len(missed_verified)}")
    print(f"🔍 [MATCH] Matched skills: {matched}")
    print(f"🔍 [MATCH] Missed skills: {missed_verified}")
    
    return matched, missed_verified

# Helper: Get skill synonyms using LLM
async def get_skill_synonyms(skill: str) -> list[str]:
    """Get synonyms for a skill using OpenAI."""
    print(f"🔍 [SYNONYMS] Getting synonyms for: '{skill}'")
    
    # Skip very long strings or UI text
    if len(skill) > 100 or any(ui_term in skill.lower() for ui_term in ['menu', 'navigation', 'search', 'arrow', 'form', 'button']):
        print(f"⏭️ [SYNONYMS] Skipping UI text or long string: '{skill}'")
        return []
    
    prompt = f"""Given the skill "{skill}", return a JSON array of common synonyms or alternative terms used in job descriptions.
    Include variations in spelling, common abbreviations, and related terms.
    Return only the JSON array, no other text."""
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skill synonym expert. Return synonyms as a JSON array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            timeout=120
        )
        
        llm_content = response.choices[0].message.content
        print(f"📥 [SYNONYMS] Raw response for '{skill}': '{llm_content}'")
        
        # Check if response is empty or None
        if not llm_content or llm_content.strip() == "":
            print(f"❌ [SYNONYMS] Empty response for '{skill}', returning empty list")
            return []
        
        # Check if response looks like JSON
        if not (llm_content.strip().startswith('[') and llm_content.strip().endswith(']')):
            print(f"❌ [SYNONYMS] Response doesn't look like JSON array for '{skill}': '{llm_content[:50]}...'")
            return []
        
        try:
            synonyms = json.loads(llm_content)
            if not isinstance(synonyms, list):
                print(f"❌ [SYNONYMS] Response is not a list for '{skill}': {type(synonyms)}")
                return []
            
            normalized_synonyms = [normalize(s) for s in synonyms if s and s != "N/A" and isinstance(s, str)]
            print(f"✅ [SYNONYMS] Found {len(normalized_synonyms)} synonyms for '{skill}': {normalized_synonyms}")
            return normalized_synonyms
            
        except json.JSONDecodeError as json_err:
            print(f"❌ [SYNONYMS] JSON decode error for '{skill}': {json_err}")
            print(f"📄 [SYNONYMS] Problematic content: '{llm_content}'")
            return []
            
    except Exception as e:
        print(f"❌ [SYNONYMS] Error getting synonyms for '{skill}': {str(e)}")
        return []

# Helper: Assign weights based on importance (LLM/rule-based)
def assign_weights(jd_skills):
    # For demo: if skill contains 'required' or 'must', weight=2, else 1
    weights = {}
    for s in jd_skills:
        if 'required' in s or 'must' in s:
            weights[s] = 2
        else:
            weights[s] = 1
    return weights

# Helper: Sectional and frequency-aware scoring
def section_and_freq_bonus(skill, section_map):
    freq = 0
    bonus = 0
    for section, lines in section_map.items():
        count = sum(skill in l.lower() for l in lines)
        freq += count
        if count > 0 and section in ['experience', 'work experience', 'projects']:
            bonus += 1  # +1 for appearing in Experience/Projects
    freq = min(freq, 3)  # Cap at 3
    return bonus, freq

def extract_skills(text: str, skill_type: str = "hard") -> List[str]:
    """Extract skills from text using OpenAI."""
    try:
        # 🔧 TRUNCATE LARGE TEXT: Limit to 8000 characters to avoid token limits
        if len(text) > 8000:
            print(f"⚠️ [EXTRACT] Truncating large text from {len(text)} to 8000 characters")
            # Take first 4000 and last 4000 characters to capture key information
            text = text[:4000] + "\n...\n" + text[-4000:]
        
        # Enhanced prompt for better skill extraction
        prompt = f"""Extract {skill_type} skills from the following text. 
        Return ONLY atomic skills, one per line, without any additional text or formatting.
        For example, instead of 'experience with data analysis', return 'Data Analysis'.
        Instead of 'proficient in SQL and database management', return 'SQL' and 'Database Management'.
        
        IMPORTANT: Focus on the most relevant skills for job matching. Ignore UI elements, navigation text, and generic phrases.
        
        Text to analyze:
        {text}
        
        List of {skill_type} skills (one per line):"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,  # Increased token limit
            timeout=60  # Reduced timeout
        )
        
        # Process the response to get clean skills
        skills = response.choices[0].message.content.strip().split('\n')
        
        # Clean up each skill
        cleaned_skills = []
        for skill in skills:
            # Remove any numbering, dashes, or extra whitespace
            skill = re.sub(r'^[\d\-\.\s]+', '', skill).strip()
            # Remove any parenthetical explanations
            skill = re.sub(r'\([^)]*\)', '', skill).strip()
            # Remove any "and" or "&" and split into separate skills
            if ' and ' in skill.lower() or ' & ' in skill.lower():
                parts = re.split(r'\s+(?:and|&)\s+', skill, flags=re.IGNORECASE)
                cleaned_skills.extend([p.strip() for p in parts if p.strip() and _is_valid_skill(p.strip())])
            else:
                if _is_valid_skill(skill):
                    cleaned_skills.append(skill)
        
        # Remove duplicates and empty strings
        final_skills = list(set(skill for skill in cleaned_skills if skill))
        print(f"✅ [EXTRACT] Extracted {len(final_skills)} {skill_type} skills: {final_skills[:10]}{'...' if len(final_skills) > 10 else ''}")
        return final_skills
        
    except Exception as e:
        print(f"❌ [EXTRACT] Error extracting {skill_type} skills: {str(e)}")
        # Fallback to simple regex extraction
        fallback_skills = _extract_skills_fallback(text, skill_type)
        print(f"🔄 [EXTRACT] Fallback extracted {len(fallback_skills)} {skill_type} skills")
        return fallback_skills

def extract_domain_keywords(text: str) -> List[str]:
    """Extract domain-specific keywords from text."""
    try:
        # 🔧 TRUNCATE LARGE TEXT: Limit to 8000 characters to avoid token limits
        if len(text) > 8000:
            print(f"⚠️ [EXTRACT] Truncating large domain text from {len(text)} to 8000 characters")
            # Take first 4000 and last 4000 characters to capture key information
            text = text[:4000] + "\n...\n" + text[-4000:]
            
        prompt = f"""Extract domain-specific keywords and industry terms from the following text.
        Focus on:
        1. Organization names and types
        2. Industry-specific terminology
        3. Domain expertise areas
        4. Sector-specific concepts
        
        Return ONLY the keywords, one per line, without any additional text.
        Ignore UI elements, navigation text, and generic web content.
        
        Text to analyze:
        {text}
        
        List of domain keywords (one per line):"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,  # Increased token limit
            timeout=60  # Reduced timeout
        )
        
        keywords = response.choices[0].message.content.strip().split('\n')
        
        # Clean up each keyword
        cleaned_keywords = []
        for keyword in keywords:
            # Remove any numbering, dashes, or extra whitespace
            keyword = re.sub(r'^[\d\-\.\s]+', '', keyword).strip()
            # Remove any parenthetical explanations
            keyword = re.sub(r'\([^)]*\)', '', keyword).strip()
            if keyword and _is_valid_skill(keyword):
                cleaned_keywords.append(keyword)
        
        # Remove duplicates and empty strings
        final_keywords = list(set(cleaned_keywords))
        print(f"✅ [EXTRACT] Extracted {len(final_keywords)} domain keywords: {final_keywords[:10]}{'...' if len(final_keywords) > 10 else ''}")
        return final_keywords
        
    except Exception as e:
        print(f"❌ [EXTRACT] Error extracting domain keywords: {str(e)}")
        # Fallback to simple regex extraction
        fallback_keywords = _extract_keywords_fallback(text)
        print(f"🔄 [EXTRACT] Fallback extracted {len(fallback_keywords)} domain keywords")
        return fallback_keywords

def _extract_skills_fallback(text: str, skill_type: str) -> List[str]:
    """Fallback skill extraction using regex patterns"""
    skills = []
    
    # Common technical skills patterns
    if skill_type == "hard":
        patterns = [
            r'\b(Python|Java|JavaScript|SQL|HTML|CSS|React|Angular|Node\.js|Docker|AWS|Azure|GCP)\b',
            r'\b(Tableau|Power BI|Excel|Word|PowerPoint|Salesforce|SAP|Oracle)\b',
            r'\b(Machine Learning|Data Analysis|Database|Programming|Development)\b'
        ]
    else:  # soft skills
        patterns = [
            r'\b(Communication|Leadership|Teamwork|Problem Solving|Time Management)\b',
            r'\b(Project Management|Analytical|Creative|Adaptable|Collaborative)\b'
        ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)
    
    return list(set(skills))

def _extract_keywords_fallback(text: str) -> List[str]:
    """Fallback domain keyword extraction using regex patterns"""
    keywords = []
    
    # Common domain patterns
    patterns = [
        r'\b(Healthcare|Finance|Technology|Education|Manufacturing|Retail)\b',
        r'\b(Non-profit|Government|Consulting|Marketing|Sales|Operations)\b',
        r'\b(GDPR|HIPAA|SOX|Agile|Scrum|Lean|Six Sigma)\b'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend(matches)
    
    return list(set(keywords))

def match_skills(cv_skills: List[str], jd_skills: List[str], skill_type: str = "hard") -> Tuple[List[str], List[str]]:
    """Match skills between CV and JD using OpenAI."""
    try:
        # Create a more structured prompt for skill matching
        prompt = f"""Compare these two lists of {skill_type} skills and identify:
        1. Skills that appear in both lists (exact matches or very close synonyms)
        2. Skills that are in the JD but not in the CV
        
        CV Skills:
        {', '.join(cv_skills)}
        
        Job Description Skills:
        {', '.join(jd_skills)}
        
        Return the results in this exact format:
        MATCHED: skill1, skill2, skill3
        MISSED: skill1, skill2, skill3"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
            timeout=120
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the response
        matched = []
        missed = []
        
        for line in result.split('\n'):
            if line.startswith('MATCHED:'):
                matched = [s.strip() for s in line.replace('MATCHED:', '').split(',') if s.strip()]
            elif line.startswith('MISSED:'):
                missed = [s.strip() for s in line.replace('MISSED:', '').split(',') if s.strip()]
        
        return matched, missed
    except Exception as e:
        print(f"Error matching {skill_type} skills: {str(e)}")
        return [], []

def match_domain_keywords(cv_keywords: List[str], jd_keywords: List[str]) -> Tuple[List[str], List[str]]:
    """Match domain keywords between CV and JD."""
    try:
        prompt = """Compare these two lists of domain keywords and identify:
        1. Keywords that appear in both lists (exact matches or very close synonyms)
        2. Keywords that are in the JD but not in the CV
        
        CV Keywords:
        {', '.join(cv_keywords)}
        
        Job Description Keywords:
        {', '.join(jd_keywords)}
        
        Return the results in this exact format:
        MATCHED: keyword1, keyword2, keyword3
        MISSED: keyword1, keyword2, keyword3"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
            timeout=120
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the response
        matched = []
        missed = []
        
        for line in result.split('\n'):
            if line.startswith('MATCHED:'):
                matched = [s.strip() for s in line.replace('MATCHED:', '').split(',') if s.strip()]
            elif line.startswith('MISSED:'):
                missed = [s.strip() for s in line.replace('MISSED:', '').split(',') if s.strip()]
        
        return matched, missed
    except Exception as e:
        print(f"Error matching domain keywords: {str(e)}")
        return [], []

def generate_improvement_tips(
    matched_hard: List[str],
    missed_hard: List[str],
    matched_soft: List[str],
    missed_soft: List[str],
    matched_domain: List[str],
    missed_domain: List[str]
) -> List[str]:
    """Generate improvement tips based on skill matches and gaps."""
    tips = []
    
    # Hard skills tips
    if missed_hard:
        tips.append(f"Add these technical skills to your CV: {', '.join(missed_hard[:3])}")
        if len(missed_hard) > 3:
            tips.append(f"And {len(missed_hard) - 3} more technical skills")
    
    # Soft skills tips
    if missed_soft:
        tips.append(f"Highlight these soft skills in your CV: {', '.join(missed_soft[:3])}")
        if len(missed_soft) > 3:
            tips.append(f"And {len(missed_soft) - 3} more soft skills")
    
    # Domain knowledge tips
    if missed_domain:
        tips.append(f"Include these domain-specific terms: {', '.join(missed_domain[:3])}")
        if len(missed_domain) > 3:
            tips.append(f"And {len(missed_domain) - 3} more domain terms")
    
    # General tips based on matches
    if not matched_hard and not matched_soft and not matched_domain:
        tips.append("Your CV needs significant improvement to match the job requirements.")
    elif len(matched_hard) < len(missed_hard):
        tips.append("Focus on adding more technical skills to your CV.")
    elif len(matched_soft) < len(missed_soft):
        tips.append("Emphasize your soft skills more in your CV.")
    elif len(matched_domain) < len(missed_domain):
        tips.append("Add more industry-specific terminology to your CV.")
    
    # Formatting tips
    tips.append("Use bullet points to highlight your skills and achievements.")
    tips.append("Quantify your achievements with specific numbers and metrics.")
    
    return tips

def calculate_score(matched_count: int, total_count: int) -> int:
    """Calculate the match score as a percentage."""
    try:
        if total_count == 0:
            return 0
        score = (matched_count / total_count) * 100
        return min(100, max(0, int(score)))  # Ensure score is between 0 and 100
    except Exception as e:
        logger.error(f"Error calculating score: {str(e)}")
        return 0

async def test_ats_compatibility(cv_text: str, jd_text: str) -> Dict:
    """Test CV compatibility with job description using enhanced semantic matching."""
    try:
        # Import enhanced ATS matcher for better accuracy
        from .ats_rules_engine import enhanced_ats_matcher, evaluate_ats_compatibility, MIN_MATCH_THRESHOLD, MAX_SKILLS_TO_SHOW, MAX_SKILLS_TO_MATCH
        
        # 🔧 TRUNCATE LARGE JD: Limit to 10000 characters for better processing
        original_jd_length = len(jd_text)
        if len(jd_text) > 10000:
            print(f"⚠️ [ENHANCED-ATS] Truncating large JD from {len(jd_text)} to 10000 characters")
            # Take first 5000 and last 5000 characters to capture key information
            jd_text = jd_text[:5000] + "\n...\n" + jd_text[-5000:]
        
        # Extract skills and keywords using improved method
        print(f"🔍 [ENHANCED-ATS] Extracting skills from CV ({len(cv_text)} chars) and JD ({len(jd_text)} chars)")
        cv_hard_skills = extract_skills(cv_text, "hard")
        jd_hard_skills = extract_skills(jd_text, "hard")
        cv_soft_skills = extract_skills(cv_text, "soft")
        jd_soft_skills = extract_skills(jd_text, "soft")
        cv_domain_keywords = extract_domain_keywords(cv_text)
        jd_domain_keywords = extract_domain_keywords(jd_text)
        
        # Validate extracted skills
        if not jd_hard_skills and not jd_soft_skills and not jd_domain_keywords:
            print("⚠️ [ENHANCED-ATS] No skills extracted from JD, falling back to traditional method")
            raise Exception("No skills extracted from job description")
        
        # 🚀 ENHANCED ACCURACY: Use semantic matching for better keyword recognition
        print("🧠 [ENHANCED-ATS] Using semantic matching for improved accuracy...")
        
        # Use enhanced ATS matching from new rules engine
        print(f"\n🔍 SKILL EXTRACTION RESULTS:")
        print(f"   📄 CV Hard Skills ({len(jd_hard_skills)}): {jd_hard_skills[:10]}{'...' if len(jd_hard_skills) > 10 else ''}")
        print(f"   📄 CV Soft Skills ({len(jd_soft_skills)}): {jd_soft_skills[:10]}{'...' if len(jd_soft_skills) > 10 else ''}")
        print(f"   📄 CV Domain Keywords ({len(jd_domain_keywords)}): {jd_domain_keywords[:10]}{'...' if len(jd_domain_keywords) > 10 else ''}")
        
        hard_skills_analysis = await enhanced_ats_matcher.comprehensive_keyword_analysis(cv_text, jd_hard_skills)
        soft_skills_analysis = await enhanced_ats_matcher.comprehensive_keyword_analysis(cv_text, jd_soft_skills)
        domain_analysis = await enhanced_ats_matcher.comprehensive_keyword_analysis(cv_text, jd_domain_keywords)
        
        print(f"\n🎯 ENHANCED MATCHING RESULTS:")
        print(f"   🔧 Hard Skills: {hard_skills_analysis['match_percentage']:.1f}% match")
        print(f"   🤝 Soft Skills: {soft_skills_analysis['match_percentage']:.1f}% match") 
        print(f"   🏢 Domain Keywords: {domain_analysis['match_percentage']:.1f}% match")
        
        # Extract results from enhanced analysis
        matched_hard = hard_skills_analysis['matched_keywords']
        missed_hard = hard_skills_analysis['missing_keywords']
        matched_soft = soft_skills_analysis['matched_keywords']
        missed_soft = soft_skills_analysis['missing_keywords']
        matched_domain = domain_analysis['matched_keywords']
        missed_domain = domain_analysis['missing_keywords']
        
        # Calculate scores using enhanced matching percentages
        hard_score = int(hard_skills_analysis['match_percentage'])
        soft_score = int(soft_skills_analysis['match_percentage'])
        domain_score = int(domain_analysis['match_percentage'])
        
        # Calculate overall score (weighted)
        overall_score = int((hard_score * 0.5) + (soft_score * 0.3) + (domain_score * 0.2))
        
        # Generate improvement tips
        tips = generate_improvement_tips(matched_hard, missed_hard, matched_soft, missed_soft, matched_domain, missed_domain)
        
        return {
            "overall_score": overall_score,
            "keyword_match": hard_score,
            "skills_match": soft_score,
            "matched_hard_skills": matched_hard,
            "missed_hard_skills": missed_hard,
            "matched_soft_skills": matched_soft,
            "missed_soft_skills": missed_soft,
            "matched_domain_keywords": matched_domain,
            "missed_domain_keywords": missed_domain,
            "tips": tips
        }
    except Exception as e:
        print(f"Error in ATS compatibility test: {str(e)}")
        raise

async def test_ats_compatibility_llm(cv_text: str, jd_text: str) -> Dict:
    """
    Advanced ATS compatibility testing using LLM for both extraction and comparison
    """
    print("🚀 [LLM-ATS] Starting LLM-based ATS compatibility testing")
    
    try:
        # Create LLM matcher instance
        llm_matcher = LLMKeywordMatcher()
        
        # Perform comprehensive LLM-based comparison
        comparisons = await llm_matcher.comprehensive_comparison(cv_text, jd_text)
        
        # Calculate overall score
        overall_score = llm_matcher.calculate_overall_score(comparisons)
        
        # Generate improvement suggestions
        suggestions = llm_matcher.generate_improvement_suggestions(comparisons)
        
        # Extract detailed results for each category
        results = {
            "overall_score": int(overall_score),
            "method": "LLM-based extraction and comparison",
            "detailed_analysis": {},
            "improvement_suggestions": suggestions
        }
        
        # Process each category
        for category, comparison in comparisons.items():
            category_name = category.replace('_', ' ').title()
            
            # Extract matched and missing keywords
            matched_keywords = []
            missing_keywords = []
            match_details = []
            
            for match in comparison.matches:
                if match.match_type != "missing":
                    matched_keywords.append(match.jd_keyword)
                    match_details.append({
                        "jd_keyword": match.jd_keyword,
                        "cv_keyword": match.cv_keyword,
                        "match_type": match.match_type,
                        "confidence": match.confidence,
                        "explanation": match.explanation
                    })
                else:
                    missing_keywords.append(match.jd_keyword)
            
            results["detailed_analysis"][category] = {
                "match_percentage": comparison.match_percentage,
                "matched_keywords": matched_keywords,
                "missing_keywords": missing_keywords,
                "additional_keywords": comparison.additional_keywords,
                "match_details": match_details,
                "total_jd_keywords": len(comparison.jd_keywords),
                "total_cv_keywords": len(comparison.cv_keywords)
            }
            
            # Set legacy field names for backward compatibility
            if category == "technical_skills":
                results["keyword_match"] = int(comparison.match_percentage)
                results["matched_hard_skills"] = matched_keywords
                results["missed_hard_skills"] = missing_keywords
            elif category == "soft_skills":
                results["skills_match"] = int(comparison.match_percentage)
                results["matched_soft_skills"] = matched_keywords
                results["missed_soft_skills"] = missing_keywords
            elif category == "domain_keywords":
                results["domain_match"] = int(comparison.match_percentage)
                results["matched_domain_keywords"] = matched_keywords
                results["missed_domain_keywords"] = missing_keywords
        
        # Print detailed results
        print(f"\n🎯 LLM-BASED ATS RESULTS:")
        print(f"   📊 Overall Score: {overall_score:.1f}%")
        
        for category, analysis in results["detailed_analysis"].items():
            print(f"   📈 {category.replace('_', ' ').title()}: {analysis['match_percentage']:.1f}% match")
            print(f"      ✅ Matched: {len(analysis['matched_keywords'])}/{analysis['total_jd_keywords']}")
            print(f"      ❌ Missing: {len(analysis['missing_keywords'])}")
            if analysis['additional_keywords']:
                print(f"      ➕ Additional: {len(analysis['additional_keywords'])}")
        
        if suggestions:
            print(f"   💡 Improvement Suggestions:")
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"      {i}. {suggestion}")
        
        return results
        
    except Exception as e:
        print(f"❌ [LLM-ATS] Error in LLM-based testing: {str(e)}")
        # Fallback to traditional method
        return await test_ats_compatibility(cv_text, jd_text)



@router.post("/ats-test/", response_model=ATSTestResult)
async def ats_test(payload: ATSTestRequest):
    """
    Enhanced ATS testing endpoint with support for both traditional and LLM-based methods
    """
    start_time = time.time()
    operation_id = f"ats_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    active_operations.add(operation_id)
    
    try:
        # Read correct file with integrity verification
        try:
            if payload.cv_type == 'tailored':
                cv_text = read_tailored_cv_text(payload.cv_filename)
            elif payload.cv_type == 'uploaded':
                cv_text = read_uploaded_cv_text(payload.cv_filename)
            else:
                raise HTTPException(status_code=400, detail="Invalid cv_type. Must be 'uploaded' or 'tailored'.")
                
            # Verify content was actually read
            if not cv_text or len(cv_text.strip()) < 50:
                logger.error(f"❌ [FILE-INTEGRITY] CV content appears empty or too short: {len(cv_text)} chars")
                raise HTTPException(status_code=500, detail="CV file appears to be empty or corrupted")
                
            logger.info(f"✅ [FILE-INTEGRITY] Successfully read CV: {len(cv_text)} characters")
            
        except Exception as e:
            logger.error(f"Error reading CV file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading CV file: {str(e)}")

        logger.info(f"CV text length: {len(cv_text)} characters")
        logger.info(f"JD text length: {len(payload.jd_text)} characters")

        # 🚀 TRY LLM-BASED METHOD FIRST for better accuracy
        logger.info("Attempting LLM-based ATS compatibility testing...")
        
        # 🔍 PRINT CV AND JD FOR DEBUGGING
        print("\n" + "="*80)
        print("🎯 ATS EVALUATION STARTED")
        print("="*80)
        print(f"📄 CV TEXT (first 500 chars):")
        print(cv_text[:500] + "..." if len(cv_text) > 500 else cv_text)
        print(f"\n🧾 JD TEXT (first 500 chars):")
        print(payload.jd_text[:500] + "..." if len(payload.jd_text) > 500 else payload.jd_text)
        print("="*80)
        
        try:
            # Try traditional method first for stability
            ats_results = await test_ats_compatibility(cv_text, payload.jd_text)
            
            # Try LLM method if traditional works
            try:
                llm_results = await test_ats_compatibility_llm(cv_text, payload.jd_text)
                logger.info("✅ LLM method also successful - using LLM results")
                ats_results = llm_results
                method_used = "LLM-based extraction and comparison"
            except Exception as llm_error:
                logger.warning(f"LLM method failed, using traditional: {str(llm_error)}")
                method_used = "Traditional extraction with semantic matching"
            
            # Extract results from testing
            overall_score = ats_results["overall_score"]
            
            # Extract category scores with fallback
            if "detailed_analysis" in ats_results:
                # LLM-based results
                technical_analysis = ats_results.get("detailed_analysis", {}).get("technical_skills", {})
                soft_analysis = ats_results.get("detailed_analysis", {}).get("soft_skills", {})
                domain_analysis = ats_results.get("detailed_analysis", {}).get("domain_keywords", {})
                
                hard_score = technical_analysis.get("match_percentage", 0)
                soft_score = soft_analysis.get("match_percentage", 0)
                domain_score = domain_analysis.get("match_percentage", 0)
                
                matched_hard = technical_analysis.get("matched_keywords", [])
                missed_hard = technical_analysis.get("missing_keywords", [])
                matched_soft = soft_analysis.get("matched_keywords", [])
                missed_soft = soft_analysis.get("missing_keywords", [])
                matched_domain = domain_analysis.get("matched_keywords", [])
                missed_domain = domain_analysis.get("missing_keywords", [])
                
                # 🎯 PRINT DETAILED LLM-BASED RESULTS
                print("\n" + "🎯 LLM-BASED ATS EVALUATION RESULTS:")
                print(f"   📊 Overall Score: {overall_score:.1f}%")
                print(f"   🔧 Technical Skills Score: {hard_score:.1f}%")
                print(f"   🤝 Soft Skills Score: {soft_score:.1f}%")
                print(f"   🏢 Domain Keywords Score: {domain_score:.1f}%")
                print(f"   📈 Detailed Analysis:")
                
                for category, analysis in ats_results.get("detailed_analysis", {}).items():
                    print(f"      📊 {category.replace('_', ' ').title()}:")
                    print(f"         ✅ Matched: {len(analysis.get('matched_keywords', []))}/{analysis.get('total_jd_keywords', 0)}")
                    print(f"         ❌ Missing: {len(analysis.get('missing_keywords', []))}")
                    if analysis.get('additional_keywords'):
                        print(f"         ➕ Additional: {len(analysis.get('additional_keywords', []))}")
                    
                    # Show match details if available
                    if analysis.get('match_details'):
                        print(f"         🔍 Match Details:")
                        for detail in analysis['match_details'][:3]:  # Show first 3
                            print(f"            • {detail['jd_keyword']} → {detail['cv_keyword']} ({detail['match_type']}, {detail['confidence']:.2f})")
                
                # Print improvement suggestions
                if ats_results.get("improvement_suggestions"):
                    print(f"   💡 Improvement Suggestions:")
                    for i, suggestion in enumerate(ats_results["improvement_suggestions"][:5], 1):
                        print(f"      {i}. {suggestion}")
            else:
                # Traditional results
                hard_score = ats_results.get("keyword_match", 0)
                soft_score = ats_results.get("skills_match", 0)
                domain_score = ats_results.get("domain_match", 0)
                
                matched_hard = ats_results.get("matched_hard_skills", [])
                missed_hard = ats_results.get("missed_hard_skills", [])
                matched_soft = ats_results.get("matched_soft_skills", [])
                missed_soft = ats_results.get("missed_soft_skills", [])
                matched_domain = ats_results.get("matched_domain_keywords", [])
                missed_domain = ats_results.get("missed_domain_keywords", [])
                
                print(f"🎯 [TRADITIONAL] ATS Scoring Results:")
                print(f"   📊 Overall Score: {overall_score}%")
                print(f"   🔧 Technical Skills: {hard_score}% ({len(matched_hard)}/{len(matched_hard) + len(missed_hard)} matched)")
                print(f"   🤝 Soft Skills: {soft_score}% ({len(matched_soft)}/{len(matched_soft) + len(missed_soft)} matched)")
                print(f"   🏢 Domain Keywords: {domain_score}% ({len(matched_domain)}/{len(matched_domain) + len(missed_domain)} matched)")
            
            print("="*80)
            
            logger.info(f"ATS test completed - Overall Score: {overall_score}%")
            
        except Exception as e:
            logger.error(f"ATS test failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"ATS test failed: {str(e)}")

        # Generate improvement tips
        try:
            tips = generate_improvement_tips(
                matched_hard, missed_hard,
                matched_soft, missed_soft,
                matched_domain, missed_domain
            )
        except Exception as e:
            logger.error(f"Error generating tips: {str(e)}")
            tips = ["Unable to generate specific tips. Please review your CV manually."]

        result = ATSTestResult(
            overall_score=overall_score,
            keyword_match=int(hard_score),
            skills_match=int(soft_score),
            matched_hard_skills=matched_hard,
            missed_hard_skills=missed_hard,
            matched_soft_skills=matched_soft,
            missed_soft_skills=missed_soft,
            matched_domain_keywords=matched_domain,
            missed_domain_keywords=missed_domain,
            tips=tips
        )

        logger.info(f"ATS test completed successfully - Overall Score: {overall_score}%")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ATS test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'operation_id' in locals():
            active_operations.discard(operation_id)



@router.get("/test-tailored/{filename}")
def test_tailored(filename: str):
    text = read_tailored_cv_text(filename)
    return {"length": len(text), "preview": text[:300]}


