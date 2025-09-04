#!/usr/bin/env python3
"""
CV Accuracy Enhancer
Advanced system to ensure keyword integration and ATS alignment accuracy
"""

import re
import logging
from typing import Dict, List, Set, Tuple
from openai import OpenAI
import os
import json

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_resume_with_claude(resume_text: str) -> Dict:
    """
    Parse resume text using Claude AI to extract structured information
    """
    try:
        prompt = f"""
You are an expert resume parser. Extract structured information from the following resume text and return it in JSON format.

Extract the following information:
1. Contact Information (name, email, phone, location, links)
2. Summary/Objective
3. Work Experience (company, title, dates, location, bullets)
4. Education (degree, institution, dates)
5. Skills (preserve original formatting with bullet points and descriptions)
6. Projects (title, context, date, description, technologies, bullets)
7. Certifications (if any)
8. Languages (if any)

CRITICAL INSTRUCTIONS FOR SKILLS SECTION:
- For the skills section, DO NOT extract individual keywords
- Instead, preserve the EXACT original formatting and structure as it appears in the CV
- If skills are in bullet points, keep them as bullet points with full descriptions
- If skills are in paragraphs, keep them as paragraphs
- Maintain the original section title (e.g., "TECHNICAL SKILLS", "SKILLS", etc.)
- Keep the complete bullet point text, not just keywords
- Example: If the CV has "• Specialized in Python programming, including data analysis, automation, and machine learning using libraries such as Pandas, NumPy, and scikit-learn", keep the entire bullet point intact

CRITICAL INSTRUCTIONS FOR PROJECTS SECTION:
- For projects, extract the complete context (e.g., "UNIVERSITY PROJECT", "MACHINE LEARNING AND ARTIFICIAL INTELLIGENCE")
- Include the date/timeframe if mentioned
- Preserve all bullet points with full descriptions
- Extract technologies mentioned within the project description
- Maintain the original formatting and structure

Return the data in this exact JSON structure:
{{
    "contact_info": {{
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "phone number",
        "location": "City, State/Country",
        "links": ["linkedin.com/in/profile", "github.com/username"]
    }},
    "summary": "Professional summary text",
    "experience": [
        {{
            "company": "Company Name",
            "title": "Job Title",
            "date": "Start Date - End Date",
            "location": "City, State",
            "bullets": ["Achievement 1", "Achievement 2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University Name",
            "date": "Graduation Date"
        }}
    ],
    "skills": {{
        "section_title": "TECHNICAL SKILLS",
        "format": "bullets",
        "content": ["• Full bullet point text 1", "• Full bullet point text 2", "• Full bullet point text 3"]
    }},
    "projects": [
        {{
            "title": "Project Name",
            "context": "University/Course/Company context if mentioned",
            "date": "Project date or duration",
            "description": "Brief project description",
            "technologies": ["Tech 1", "Tech 2"],
            "bullets": ["• Detailed bullet point 1", "• Detailed bullet point 2"]
        }}
    ],
    "certifications": ["Certification 1", "Certification 2"],
    "languages": ["Language 1", "Language 2"]
}}

Resume Text:
{resume_text}

Return only the JSON structure, no additional text.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            timeout=60
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean up the result to ensure it's valid JSON
        if result.startswith('```json'):
            result = result[7:]
        if result.endswith('```'):
            result = result[:-3]
        
        # Parse the JSON
        try:
            parsed_data = json.loads(result)
            logger.info("✅ Successfully parsed resume with Claude")
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            # Return a basic structure if JSON parsing fails
            return {
                "contact_info": {
                    "name": "Unable to parse",
                    "email": "",
                    "phone": "",
                    "location": "",
                    "links": []
                },
                "summary": "",
                "experience": [],
                "education": [],
                "skills": {
                    "section_title": "SKILLS",
                    "format": "bullets",
                    "content": []
                },
                "projects": [],
                "certifications": [],
                "languages": []
            }
            
    except Exception as e:
        logger.error(f"❌ Error parsing resume with Claude: {e}")
        raise Exception(f"Resume parsing failed: {str(e)}")

class CVAccuracyEnhancer:
    """
    Advanced CV accuracy enhancement system that ensures:
    1. Keywords are actually included in generated CVs
    2. ATS tests read the correct content
    3. Semantic matching works properly
    4. Feedback loops are accurate
    """
    
    def __init__(self):
        self.verification_threshold = 0.8  # 80% of keywords must be present
        
    def extract_user_keywords(self, additional_prompt: str) -> List[str]:
        """
        Extract specific keywords that user wants to include
        """
        keywords = []
        
        # Common patterns for keyword requests
        patterns = [
            r'include\s+([^,\n]+)',
            r'add\s+([^,\n]+)',
            r'incorporate\s+([^,\n]+)',
            r'mention\s+([^,\n]+)',
            r'emphasize\s+([^,\n]+)',
            r'highlight\s+([^,\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, additional_prompt, re.IGNORECASE)
            for match in matches:
                # Clean and split the match
                cleaned = re.sub(r'[^\w\s]', ' ', match.strip())
                words = [w.strip() for w in cleaned.split() if len(w.strip()) > 2]
                keywords.extend(words)
        
        # Also extract quoted keywords
        quoted_keywords = re.findall(r'"([^"]+)"', additional_prompt)
        for quoted in quoted_keywords:
            words = [w.strip() for w in quoted.split() if len(w.strip()) > 2]
            keywords.extend(words)
        
        # Remove duplicates and common words
        stopwords = {'skills', 'experience', 'work', 'include', 'add', 'more', 'better', 'good'}
        unique_keywords = []
        seen = set()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen and keyword_lower not in stopwords:
                seen.add(keyword_lower)
                unique_keywords.append(keyword)
        
        logger.info(f"🎯 [ACCURACY] Extracted user keywords: {unique_keywords}")
        return unique_keywords
    
    def build_enhanced_keyword_prompt(self, base_prompt: str, additional_instructions: str, 
                                    cv_text: str, jd_text: str) -> str:
        """
        Build an enhanced prompt that GUARANTEES keyword inclusion
        """
        user_keywords = self.extract_user_keywords(additional_instructions)
        
        if not user_keywords:
            return f"{base_prompt}\n\n{additional_instructions}"
        
        # Create keyword-focused enhancement
        keyword_enhancement = f"""
🚨 CRITICAL KEYWORD INCLUSION REQUIREMENTS 🚨

The user has SPECIFICALLY requested these keywords to be included:
{', '.join(user_keywords)}

YOU MUST INCLUDE EACH OF THESE KEYWORDS in the CV using these strategies:

1. **EXPERIENCE BULLET POINTS**: Weave keywords naturally into existing job descriptions
   - Example: If "teamwork" is requested, modify bullets like:
     "• Collaborated with cross-functional teams to deliver project milestones"
     "• Demonstrated strong teamwork skills while coordinating with 5+ departments"

2. **SKILLS SECTION**: Explicitly add keywords to skills section if relevant
   - Add "{', '.join(user_keywords)}" to the skills section

3. **PROJECT DESCRIPTIONS**: Include keywords in project contexts
   - Example: "• Led teamwork-focused initiative that improved team efficiency by 20%"

🎯 KEYWORD PLACEMENT RULES:
- Include EACH keyword at least 2-3 times throughout the CV
- Use both the exact keyword AND semantic variations
- Keywords: {', '.join(user_keywords)}
- Variations: {self._generate_keyword_variations(user_keywords)}

🚨 VERIFICATION REQUIREMENT:
After generating the CV, the system will verify these keywords are present. 
If ANY keyword is missing, the generation will be considered FAILED.

ADDITIONAL USER INSTRUCTIONS:
{additional_instructions}
"""
        
        return f"{base_prompt}\n\n{keyword_enhancement}"
    
    def _generate_keyword_variations(self, keywords: List[str]) -> str:
        """
        Generate semantic variations of keywords for better inclusion
        """
        variations_map = {
            'teamwork': ['collaboration', 'team collaboration', 'cross-functional teamwork', 'team coordination'],
            'leadership': ['team leadership', 'leading teams', 'management', 'project leadership'],
            'communication': ['stakeholder communication', 'client communication', 'presentation skills'],
            'problem solving': ['analytical thinking', 'troubleshooting', 'solution development'],
            'python': ['Python programming', 'Python development', 'Python scripting'],
            'data analysis': ['data analytics', 'statistical analysis', 'data insights'],
            'machine learning': ['ML', 'predictive modeling', 'ML algorithms'],
            'project management': ['project coordination', 'project planning', 'project delivery'],
        }
        
        all_variations = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in variations_map:
                all_variations.extend(variations_map[keyword_lower])
            else:
                # Generate generic variations
                all_variations.extend([
                    f"{keyword} skills",
                    f"{keyword} experience",
                    f"strong {keyword}",
                ])
        
        return ', '.join(all_variations[:15])  # Limit to avoid overwhelming
    
    def verify_keyword_inclusion(self, generated_cv: str, requested_keywords: List[str]) -> Dict:
        """
        Verify that requested keywords are actually included in the generated CV
        """
        verification_results = {
            'success': True,
            'included_keywords': [],
            'missing_keywords': [],
            'inclusion_rate': 0.0,
            'suggestions': []
        }
        
        cv_lower = generated_cv.lower()
        
        for keyword in requested_keywords:
            keyword_lower = keyword.lower()
            
            # Check for exact match
            if keyword_lower in cv_lower:
                verification_results['included_keywords'].append(keyword)
            else:
                # Check for variations
                variations = self._get_keyword_variations(keyword_lower)
                found_variation = False
                
                for variation in variations:
                    if variation.lower() in cv_lower:
                        verification_results['included_keywords'].append(f"{keyword} (as {variation})")
                        found_variation = True
                        break
                
                if not found_variation:
                    verification_results['missing_keywords'].append(keyword)
                    verification_results['suggestions'].append(
                        f"Add '{keyword}' to experience bullets or skills section"
                    )
        
        # Calculate inclusion rate
        total_keywords = len(requested_keywords)
        included_count = len(verification_results['included_keywords'])
        verification_results['inclusion_rate'] = included_count / total_keywords if total_keywords > 0 else 1.0
        
        # Determine overall success
        verification_results['success'] = verification_results['inclusion_rate'] >= self.verification_threshold
        
        logger.info(f"🔍 [VERIFICATION] Keyword inclusion rate: {verification_results['inclusion_rate']:.2%}")
        logger.info(f"✅ [VERIFICATION] Included: {verification_results['included_keywords']}")
        logger.info(f"❌ [VERIFICATION] Missing: {verification_results['missing_keywords']}")
        
        return verification_results
    
    def _get_keyword_variations(self, keyword: str) -> List[str]:
        """
        Get semantic variations for a keyword
        """
        variations_map = {
            'teamwork': ['collaboration', 'team collaboration', 'collaborative', 'team-based'],
            'leadership': ['leading', 'management', 'supervising', 'mentoring'],
            'communication': ['presenting', 'stakeholder engagement', 'client interaction'],
            'problem solving': ['troubleshooting', 'analytical', 'solution-oriented'],
            'python': ['python programming', 'python development', 'python scripting'],
            'data analysis': ['data analytics', 'statistical analysis', 'data science'],
            'machine learning': ['ml', 'predictive modeling', 'ai'],
        }
        
        return variations_map.get(keyword, [])
    
    def regenerate_with_missing_keywords(self, cv_text: str, missing_keywords: List[str], 
                                       jd_text: str) -> str:
        """
        Regenerate CV focusing specifically on missing keywords
        """
        logger.info(f"🔄 [REGENERATION] Targeting missing keywords: {missing_keywords}")
        
        focused_prompt = f"""
🚨 URGENT KEYWORD INTEGRATION REQUIRED 🚨

The following keywords were MISSING from the previous CV generation and MUST be included:
{', '.join(missing_keywords)}

TASK: Enhance the provided CV by strategically adding these keywords while maintaining truthfulness.

INTEGRATION STRATEGIES:
1. **Experience Section**: Add the keywords to existing bullet points
   - Transform existing bullets to naturally include the keywords
   - Example: "Developed data pipeline" → "Developed data pipeline using teamwork and collaboration"

2. **Skills Section**: Explicitly add missing keywords to the skills list
   - Current skills: [extract from CV]
   - Add: {', '.join(missing_keywords)}

3. **Project Section**: Integrate keywords into project descriptions
   - Show how keywords were applied in project contexts

CRITICAL REQUIREMENTS:
- EVERY keyword must appear at least TWICE in the CV
- Use keywords in different contexts (experience, skills, projects)
- Maintain the existing CV structure and truthfulness
- Keywords to include: {', '.join(missing_keywords)}

CURRENT CV TO ENHANCE:
{cv_text}

JOB DESCRIPTION CONTEXT:
{jd_text}

Return the enhanced CV with ALL keywords properly integrated.
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": focused_prompt}],
                temperature=0.2,  # Lower temperature for more focused output
                timeout=60
            )
            
            enhanced_cv = response.choices[0].message.content.strip()
            logger.info(f"✅ [REGENERATION] Enhanced CV with missing keywords")
            return enhanced_cv
            
        except Exception as e:
            logger.error(f"❌ [REGENERATION] Failed to enhance CV: {e}")
            return cv_text  # Return original if enhancement fails
    
    def extract_cv_keywords_for_verification(self, cv_text: str) -> Set[str]:
        """
        Extract all meaningful keywords from CV for verification
        """
        # Clean the text
        cv_clean = re.sub(r'[^\w\s]', ' ', cv_text.lower())
        
        # Extract meaningful words (3+ characters, not common stopwords)
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 
            'our', 'had', 'but', 'his', 'has', 'that', 'with', 'have', 'this', 'will', 'from',
            'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
            'come', 'here', 'how', 'just', 'like', 'long', 'make', 'many', 'over', 'such',
            'take', 'than', 'them', 'well', 'were', 'what', 'work'
        }
        
        words = set()
        for word in cv_clean.split():
            if len(word) >= 3 and word not in stopwords:
                words.add(word)
        
        return words
    
    def semantic_keyword_check(self, cv_text: str, target_keywords: List[str]) -> Dict:
        """
        Use AI to perform semantic keyword matching
        """
        prompt = f"""
Analyze the provided CV and determine which of these target keywords are semantically present:

TARGET KEYWORDS: {', '.join(target_keywords)}

CV TEXT:
{cv_text}

For each target keyword, determine:
1. Is it explicitly mentioned? (exact match)
2. Is it semantically present? (similar meaning expressed differently)
3. Where is it found? (which section)

Return your analysis in this format:
KEYWORD: [keyword]
STATUS: [PRESENT/MISSING/SEMANTIC]
LOCATION: [section where found]
EVIDENCE: [specific text that demonstrates the keyword]

Analyze each keyword: {', '.join(target_keywords)}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                timeout=30
            )
            
            analysis = response.choices[0].message.content.strip()
            logger.info(f"🧠 [SEMANTIC] Keyword analysis completed")
            return {'analysis': analysis, 'success': True}
            
        except Exception as e:
            logger.error(f"❌ [SEMANTIC] Analysis failed: {e}")
            return {'analysis': '', 'success': False}


# Initialize global instance
cv_accuracy_enhancer = CVAccuracyEnhancer() 