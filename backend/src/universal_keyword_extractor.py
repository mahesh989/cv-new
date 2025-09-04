"""
Universal job description keyword extraction that works for any JD
without hardcoded industry-specific terms or standardizations
"""

import re
import logging
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
import json
from .ai_config import get_model_params

@dataclass
class ExtractedKeywords:
    """Data class to hold extracted keywords"""
    technical_skills: List[str]
    soft_skills: List[str]
    domain_keywords: List[str]
    
    def to_dict(self) -> Dict[str, List[str]]:
        return {
            'technical_skills': self.technical_skills,
            'soft_skills': self.soft_skills,
            'domain_keywords': self.domain_keywords
        }
    
    def get_all_keywords(self) -> List[str]:
        """Get all keywords as a flat list"""
        return self.technical_skills + self.soft_skills + self.domain_keywords

class UniversalKeywordExtractor:
    """Universal keyword extractor that adapts to any job description"""
    
    def __init__(self):
        # Only include truly universal patterns that apply to ALL job descriptions
        self.universal_skip_patterns = [
            # Geographic locations (broad patterns)
            r'\b\w+\s+(cbd|city|area|region)\b',
            r'\bmajor\s+city\b',
            
            # Work arrangements (universal)
            r'\b(remote|hybrid|on-?site|work\s+from\s+home|wfh)\b',
            r'\b(full-?time|part-?time|contract|temporary|permanent|fixed\s+term)\b',
            
            # Application instructions (universal)
            r'\b(apply\s+(now|today|online)|send\s+(cv|resume)|email\s+your)\b',
            r'\b(contact\s+us|get\s+in\s+touch|reach\s+out)\b',
            
            # Benefits/compensation (universal)
            r'\b(competitive\s+(salary|package)|attractive\s+package)\b',
            r'\b(health\s+insurance|dental|vision|401k|superannuation)\b',
            
            # Company descriptors (universal)
            r'\b(equal\s+opportunity|eeo|diversity|inclusion)\b',
            r'\b(market\s+leader|industry\s+leader|established|growing)\b',
            
            # Generic phrases that appear in most JDs
            r'\b(key\s+responsibilities|main\s+duties|role\s+overview)\b',
            r'\b(ideal\s+candidate|successful\s+applicant|right\s+person)\b',
            r'\b(we\s+are\s+looking|we\s+seek|join\s+our\s+team)\b',
        ]
        
        # Universal cleaning patterns
        self.cleaning_patterns = [
            # Remove qualifiers that don't add value
            (r'\b(strong|excellent|good|solid|proven|demonstrated)\s+', ''),
            (r'\b(skills?|abilities?|experience|knowledge)\s*$', ''),
            (r'\b(advanced|intermediate|basic|proficient)\s+', ''),
            # Remove redundant phrases
            (r'\btechnical\s+proficiency\s+(with|in)\s+', ''),
            (r'\bability\s+to\s+(use|work\s+with|operate)\s+', ''),
            (r'\bexperience\s+(with|in|using)\s+', ''),
        ]

    def get_extraction_prompt(self, job_description_text: str) -> str:
        """Generate adaptive extraction prompt based on JD content"""
        
        # Analyze JD to provide context-aware instructions
        jd_lower = job_description_text.lower()
        
        # Detect likely industry/domain for better guidance
        domain_hints = []
        if any(term in jd_lower for term in ['data', 'analysis', 'analytics', 'sql', 'database']):
            domain_hints.append("Data/Analytics")
        if any(term in jd_lower for term in ['software', 'development', 'programming', 'code']):
            domain_hints.append("Software Development")
        if any(term in jd_lower for term in ['marketing', 'social media', 'campaign', 'brand']):
            domain_hints.append("Marketing")
        if any(term in jd_lower for term in ['sales', 'client', 'customer', 'revenue']):
            domain_hints.append("Sales/Customer Service")
        if any(term in jd_lower for term in ['finance', 'accounting', 'budget', 'financial']):
            domain_hints.append("Finance/Accounting")
        if any(term in jd_lower for term in ['hr', 'human resources', 'recruitment', 'talent']):
            domain_hints.append("Human Resources")
        
        domain_context = f"\nDetected domains: {', '.join(domain_hints)}" if domain_hints else ""
        
        prompt = f"""
Extract standardized keywords from this job description. Adapt your extraction to the specific industry and role type shown.{domain_context}

CORE PRINCIPLES:
1. Extract SKILLS and KNOWLEDGE AREAS, not job activities or responsibilities
2. Use standard industry terminology for the detected domain(s)
3. Convert verbose descriptions into clean, searchable keywords
4. Focus on transferable skills that could be matched against other roles

EXTRACTION GUIDELINES:

TECHNICAL SKILLS - Extract:
- Software/tools (use official names: "Microsoft Excel", "Salesforce", "Adobe Photoshop")
- Programming languages ("Python", "JavaScript", "SQL") 
- Platforms/systems ("AWS", "SAP", "SharePoint")
- Technical methodologies ("Agile", "Scrum", "Lean Six Sigma")
- Industry-specific tools and technologies
- Certifications and qualifications (if mentioned as requirements)

SOFT SKILLS - Extract:
- Communication abilities ("communication", "presentation", "writing")
- Leadership/management ("leadership", "team management", "mentoring")
- Problem-solving ("analytical thinking", "problem-solving", "critical thinking")
- Personal attributes ("attention to detail", "time management", "adaptability")
- Interpersonal skills ("collaboration", "stakeholder management", "negotiation")

DOMAIN KEYWORDS - Extract:
- Industry terminology specific to this role's domain
- Business processes relevant to the function
- Regulatory/compliance areas (if applicable)
- Service/product categories
- Functional areas ("budget management", "strategic planning", "quality assurance")

TRANSFORMATION EXAMPLES:
- "Advanced proficiency in Microsoft Excel" → "Microsoft Excel"
- "Excellent communication and presentation abilities" → "communication", "presentation"
- "Experience managing cross-functional teams" → "team management"
- "Strong analytical and problem-solving skills" → "analytical thinking", "problem-solving"
- "Proficient in data analysis using SQL databases" → "data analysis", "SQL"

AVOID EXTRACTING:
- Job titles, company names, locations
- Work arrangements (remote, full-time, etc.)
- Benefits, salary, application instructions
- Generic phrases like "fast-paced environment"
- Years of experience requirements
- Educational requirements (unless specific certifications)

JOB DESCRIPTION:
{job_description_text}

Extract clean, standardized keywords organized by category:

## Technical Skills
[comma-separated list]

## Soft Skills  
[comma-separated list]

## Domain Keywords
[comma-separated list]
"""
        return prompt

    def clean_extracted_text(self, text: str) -> str:
        """Apply universal text cleaning"""
        if not text:
            return ""
        
        # Apply cleaning patterns
        cleaned = text
        for pattern, replacement in self.cleaning_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Remove universal skip patterns
        for pattern in self.universal_skip_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Final cleanup
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Multiple spaces to single
        cleaned = cleaned.strip('.,;:()[]{}"-')  # Remove punctuation
        cleaned = cleaned.strip()
        
        return cleaned

    def is_valid_keyword(self, keyword: str) -> bool:
        """Check if keyword is valid using universal criteria"""
        if not keyword or len(keyword.strip()) < 2:
            return False
        
        keyword_lower = keyword.lower().strip()
        
        # Universal invalid patterns
        invalid_patterns = [
            r'^\d+\s*(years?|months?|weeks?)\b',  # Time periods
            r'\b(we|you|your|our|the|this|that|these|those)\b',  # Pronouns/articles
            r'\b(and|or|but|with|for|from|to|of|in|on|at)\b$',  # Standalone prepositions
            r'^\w{1}$',  # Single characters
            r'\d{4,}',  # Long numbers (likely dates/IDs)
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, keyword_lower):
                return False
        
        return True

    def deduplicate_keywords(self, keywords_list: List[str]) -> List[str]:
        """Remove duplicates while preserving most specific versions"""
        if not keywords_list:
            return []
        
        # Group similar keywords
        seen = {}  # lowercase -> original
        deduplicated = []
        
        # Sort by length (longer first) to prefer more specific terms
        sorted_keywords = sorted(keywords_list, key=len, reverse=True)
        
        for keyword in sorted_keywords:
            keyword_clean = keyword.strip()
            keyword_lower = keyword_clean.lower()
            
            # Check if we've seen this exact keyword
            if keyword_lower in seen:
                continue
            
            # Check if this is a subset of an existing keyword
            is_subset = False
            for existing_lower in seen:
                if keyword_lower in existing_lower or existing_lower in keyword_lower:
                    # Keep the longer, more specific version
                    if len(keyword_lower) > len(existing_lower):
                        # Replace the shorter version
                        existing_original = seen[existing_lower]
                        if existing_original in deduplicated:
                            deduplicated.remove(existing_original)
                        del seen[existing_lower]
                        break
                    else:
                        is_subset = True
                        break
            
            if not is_subset:
                seen[keyword_lower] = keyword_clean
                deduplicated.append(keyword_clean)
        
        return deduplicated

    def parse_extraction_response(self, response_text: str) -> ExtractedKeywords:
        """Parse AI response with adaptive parsing"""
        technical_skills = []
        soft_skills = []
        domain_keywords = []
        
        # Split by headers (flexible matching)
        sections = re.split(r'##\s*', response_text, flags=re.IGNORECASE)
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.split('\n', 1)
            if len(lines) < 2:
                continue
            
            header = lines[0].strip().lower()
            content = lines[1].strip()
            
            # Extract keywords from content
            keywords = []
            if content:
                # Split by commas and clean
                raw_keywords = [k.strip() for k in content.split(',') if k.strip()]
                for keyword in raw_keywords:
                    cleaned = self.clean_extracted_text(keyword)
                    if cleaned and self.is_valid_keyword(cleaned):
                        keywords.append(cleaned)
            
            # Categorize based on header
            if 'technical' in header or 'tech' in header:
                technical_skills.extend(keywords)
            elif 'soft' in header or 'personal' in header:
                soft_skills.extend(keywords)
            elif 'domain' in header or 'industry' in header or 'business' in header:
                domain_keywords.extend(keywords)
        
        # Deduplicate within each category
        return ExtractedKeywords(
            technical_skills=self.deduplicate_keywords(technical_skills),
            soft_skills=self.deduplicate_keywords(soft_skills),
            domain_keywords=self.deduplicate_keywords(domain_keywords)
        )

    def extract_keywords(self, job_description: str, api_client) -> ExtractedKeywords:
        """Main extraction method - works for any JD"""
        try:
            config = {
                "model": get_model_params(\'ANALYSIS\', max_tokens=2000, temperature=0.0)[\'model\'],
                "max_tokens": 2000,
                "temperature": 0.0,  # Maximum consistency for reliable extraction
                "messages": [
                    {
                        "role": "user",
                        "content": self.get_extraction_prompt(job_description)
                    }
                ]
            }
            
            response = api_client.messages.create(**config)
            response_text = response.content[0].text
            
            keywords = self.parse_extraction_response(response_text)
            
            # Final cross-category deduplication
            all_keywords = keywords.get_all_keywords()
            deduplicated_all = self.deduplicate_keywords(all_keywords)
            
            # Redistribute deduplicated keywords (simple heuristic)
            # This prevents the same keyword from appearing in multiple categories
            final_tech = [k for k in keywords.technical_skills if k in deduplicated_all]
            final_soft = [k for k in keywords.soft_skills if k in deduplicated_all and k not in final_tech]
            final_domain = [k for k in keywords.domain_keywords if k in deduplicated_all and k not in final_tech and k not in final_soft]
            
            return ExtractedKeywords(
                technical_skills=final_tech,
                soft_skills=final_soft,
                domain_keywords=final_domain
            )
            
        except Exception as e:
            logging.error(f"Error extracting keywords: {str(e)}")
            return ExtractedKeywords([], [], [])

    def get_extraction_quality_score(self, keywords: ExtractedKeywords, original_jd: str) -> Dict[str, float]:
        """Assess quality of extraction (universal metrics)"""
        total_keywords = len(keywords.get_all_keywords())
        jd_word_count = len(original_jd.split())
        
        return {
            'keyword_density': total_keywords / max(jd_word_count, 1) * 100,
            'category_balance': min(len(keywords.technical_skills), len(keywords.soft_skills), len(keywords.domain_keywords)) / max(total_keywords, 1),
            'avg_keyword_length': sum(len(k.split()) for k in keywords.get_all_keywords()) / max(total_keywords, 1),
            'total_keywords': total_keywords
        } 