#!/usr/bin/env python3
"""
LLM-Based Keyword Matcher - Strict Non-Hallucinating Version
Advanced system that uses LLM for keyword extraction and STRICT comparison
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from .hybrid_ai_service import hybrid_ai

logger = logging.getLogger(__name__)

@dataclass
class KeywordMatch:
    jd_keyword: str
    cv_keyword: Optional[str]
    match_type: str  # "exact", "semantic", "partial", "missing"
    confidence: float
    explanation: str

@dataclass
class CategoryComparison:
    category: str
    jd_keywords: List[str]
    cv_keywords: List[str]
    matches: List[KeywordMatch]
    match_percentage: float
    missing_keywords: List[str]
    additional_keywords: List[str]  # Keywords in CV but not in JD

class LLMKeywordMatcher:
    """Advanced LLM-based keyword extraction and comparison system with strict validation"""
    
    def __init__(self):
        self.ai_service = hybrid_ai
    
    def _deduplicate_across_categories(self, keywords_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Remove duplicates across categories and ensure keywords are in most relevant category
        """
        # Priority order for categories (higher priority keeps the keyword)
        category_priority = {
            "technical_skills": 5,
            "domain_keywords": 4,
            "experience_keywords": 3,
            "soft_skills": 2,
            "education_keywords": 1
        }
        
        # Track all keywords and their best category
        keyword_to_category = {}
        
        # First pass: assign each keyword to highest priority category
        for category, keyword_list in keywords_dict.items():
            for keyword in keyword_list:
                keyword_lower = keyword.lower().strip()
                if keyword_lower:
                    current_priority = category_priority.get(category, 0)
                    if keyword_lower not in keyword_to_category or current_priority > category_priority.get(keyword_to_category[keyword_lower][1], 0):
                        keyword_to_category[keyword_lower] = (keyword, category)
        
        # Second pass: rebuild categories with deduplicated keywords
        deduplicated = {category: [] for category in keywords_dict.keys()}
        for keyword_lower, (original_keyword, category) in keyword_to_category.items():
            deduplicated[category].append(original_keyword)
        
        # Sort and limit keywords per category
        for category in deduplicated:
            deduplicated[category] = sorted(list(set(deduplicated[category])))[:20]  # Limit to 20 per category
        
        return deduplicated
    
    async def extract_keywords_from_text(self, text: str, text_type: str = "CV") -> Dict[str, List[str]]:
        """
        Extract keywords from CV or JD text using LLM with structured output
        """
        print(f"🔍 [LLM-EXTRACT] Extracting keywords from {text_type} ({len(text)} chars)")
        
        # Truncate large text for better processing
        if len(text) > 12000:
            text = text[:6000] + "\n...\n" + text[-6000:]
            print(f"⚠️ [LLM-EXTRACT] Truncated large text to 12000 characters")
        
        extraction_prompt = f"""
You are an expert keyword extraction specialist. Analyze the following {text_type} text and extract keywords in different categories.

CRITICAL EXTRACTION RULES:
1. Extract ONLY keywords that ACTUALLY APPEAR in the text
2. Use exact terminology from the text (preserve original casing/naming)
3. Extract individual skills/terms, not full sentences
4. No generic terms like "skills", "experience", "knowledge"
5. Each keyword should be in its MOST RELEVANT category only
6. Return results in valid JSON format

Categories (in priority order):
- technical_skills: Programming languages, software tools, platforms, databases, frameworks, certifications, technical methodologies
- domain_keywords: Industry-specific terms, business domains, regulations, methodologies, specialized knowledge areas
- experience_keywords: Job titles, specific responsibilities, achievements, action verbs, work contexts
- soft_skills: Interpersonal abilities, work styles, communication skills, leadership qualities
- education_keywords: Degrees, institutions, academic achievements, coursework, qualifications

{text_type} TEXT:
{text}

Return ONLY a JSON object in this exact format:
{{
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "domain_keywords": ["keyword1", "keyword2", ...],
    "experience_keywords": ["keyword1", "keyword2", ...],
    "education_keywords": ["keyword1", "keyword2", ...]
}}
"""
        
        try:
            response = self.ai_service.generate_response(
                prompt=extraction_prompt,
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:-3]
            elif response_clean.startswith('```'):
                response_clean = response_clean[3:-3]
            
            keywords = json.loads(response_clean)
            
            # Validate and clean keywords
            cleaned_keywords = {}
            for category, keyword_list in keywords.items():
                if isinstance(keyword_list, list):
                    cleaned_keywords[category] = [
                        kw.strip() for kw in keyword_list 
                        if kw and isinstance(kw, str) and len(kw.strip()) > 1
                    ]
                else:
                    cleaned_keywords[category] = []
            
            # Ensure all categories exist
            for category in ["technical_skills", "soft_skills", "domain_keywords", "experience_keywords", "education_keywords"]:
                if category not in cleaned_keywords:
                    cleaned_keywords[category] = []
            
            # Deduplicate across categories
            cleaned_keywords = self._deduplicate_across_categories(cleaned_keywords)
            
            # Log extraction results
            total_keywords = sum(len(kw_list) for kw_list in cleaned_keywords.values())
            print(f"✅ [LLM-EXTRACT] Extracted keywords from {text_type}:")
            for category, keyword_list in cleaned_keywords.items():
                print(f"   {category}: {len(keyword_list)} keywords")
            
            return cleaned_keywords
            
        except Exception as e:
            print(f"❌ [LLM-EXTRACT] Error extracting keywords: {str(e)}")
            return {
                "technical_skills": [],
                "soft_skills": [],
                "domain_keywords": [],
                "experience_keywords": [],
                "education_keywords": []
            }
    
    def _strict_text_validation(self, keyword: str, text: str) -> bool:
        """
        Strictly validate if a keyword exists in the text
        """
        if not keyword or not text:
            return False
        
        # Normalize text for comparison
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Check exact match
        if keyword_lower in text_lower:
            return True
        
        # Check word boundaries to avoid partial word matches
        import re
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        if re.search(pattern, text_lower):
            return True
        
        return False
    
    async def compare_keywords_strictly(self, jd_keywords: List[str], cv_keywords: List[str], 
                                      category: str, cv_text: str, jd_text: str) -> List[KeywordMatch]:
        """
        Use LLM to intelligently compare keywords with strict validation against actual text
        """
        print(f"🧠 [LLM-COMPARE] Comparing {category} keywords with strict validation")
        
        if not jd_keywords:
            return []
        
        comparison_prompt = f"""
You are an expert in job matching and keyword analysis. Compare the job description keywords with CV keywords and identify matches.

CRITICAL COMPARISON RULES:
1. ONLY match keywords that ACTUALLY EXIST in the CV text
2. Look for exact matches first (same word/phrase)
3. Identify semantic matches (synonyms, related terms) ONLY if they exist in CV
4. Find partial matches (broader/narrower terms) ONLY if they exist in CV
5. If no match exists in CV, mark as "missing"
6. Assign confidence scores based on match quality (0.0 to 1.0)

CATEGORY: {category}

JOB DESCRIPTION KEYWORDS:
{', '.join(jd_keywords)}

CV KEYWORDS AVAILABLE:
{', '.join(cv_keywords)}

For each JD keyword, find the best match from CV keywords (if any) and return a JSON array:

[
    {{
        "jd_keyword": "keyword from JD",
        "cv_keyword": "EXACT keyword from CV list above or null if no match",
        "match_type": "exact|semantic|partial|missing",
        "confidence": 0.95,
        "explanation": "Brief explanation of the match or why it's missing"
    }}
]

IMPORTANT: cv_keyword must be EXACTLY one of the CV keywords listed above, or null if no match.

Return ONLY the JSON array, no other text.
"""
        
        try:
            response = self.ai_service.generate_response(
                prompt=comparison_prompt,
                temperature=0.1,  # Lower temperature for more consistent results
                max_tokens=1500
            )
            
            # Parse JSON response
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:-3]
            elif response_clean.startswith('```'):
                response_clean = response_clean[3:-3]
            
            matches_data = json.loads(response_clean)
            
            # Convert to KeywordMatch objects with strict validation
            matches = []
            cv_keywords_lower = [kw.lower() for kw in cv_keywords]
            
            for match_data in matches_data:
                jd_keyword = match_data.get("jd_keyword", "")
                cv_keyword = match_data.get("cv_keyword")
                match_type = match_data.get("match_type", "missing")
                confidence = float(match_data.get("confidence", 0.0))
                explanation = match_data.get("explanation", "")
                
                # Strict validation: ensure cv_keyword actually exists in CV keywords
                if cv_keyword and cv_keyword not in cv_keywords:
                    # Try to find the closest match in CV keywords
                    cv_keyword_lower = cv_keyword.lower()
                    if cv_keyword_lower in cv_keywords_lower:
                        idx = cv_keywords_lower.index(cv_keyword_lower)
                        cv_keyword = cv_keywords[idx]
                    else:
                        # No valid match found, mark as missing
                        cv_keyword = None
                        match_type = "missing"
                        confidence = 0.0
                        explanation = "No valid match found in CV"
                
                # Double validation: ensure the keyword actually exists in CV text
                if cv_keyword and not self._strict_text_validation(cv_keyword, cv_text):
                    print(f"⚠️ [VALIDATION] Keyword '{cv_keyword}' not found in CV text, marking as missing")
                    cv_keyword = None
                    match_type = "missing"
                    confidence = 0.0
                    explanation = "Keyword not found in CV text"
                
                match = KeywordMatch(
                    jd_keyword=jd_keyword,
                    cv_keyword=cv_keyword,
                    match_type=match_type,
                    confidence=confidence,
                    explanation=explanation
                )
                matches.append(match)
            
            print(f"✅ [LLM-COMPARE] Completed strict comparison for {category}")
            return matches
            
        except Exception as e:
            print(f"❌ [LLM-COMPARE] Error comparing keywords: {str(e)}")
            # Fallback to simple strict matching
            return self._simple_strict_matching(jd_keywords, cv_keywords, cv_text)
    
    def _simple_strict_matching(self, jd_keywords: List[str], cv_keywords: List[str], cv_text: str) -> List[KeywordMatch]:
        """Fallback strict keyword matching with text validation"""
        matches = []
        cv_keywords_lower = [kw.lower() for kw in cv_keywords]
        
        for jd_keyword in jd_keywords:
            jd_lower = jd_keyword.lower()
            match_found = False
            
            # Check for exact match
            if jd_lower in cv_keywords_lower:
                idx = cv_keywords_lower.index(jd_lower)
                cv_keyword = cv_keywords[idx]
                
                # Validate against actual CV text
                if self._strict_text_validation(cv_keyword, cv_text):
                    matches.append(KeywordMatch(
                        jd_keyword=jd_keyword,
                        cv_keyword=cv_keyword,
                        match_type="exact",
                        confidence=1.0,
                        explanation="Exact match found and validated in CV text"
                    ))
                    match_found = True
            
            if not match_found:
                # Check for partial match
                for cv_keyword in cv_keywords:
                    if (jd_lower in cv_keyword.lower() or cv_keyword.lower() in jd_lower) and \
                       self._strict_text_validation(cv_keyword, cv_text):
                        matches.append(KeywordMatch(
                            jd_keyword=jd_keyword,
                            cv_keyword=cv_keyword,
                            match_type="partial",
                            confidence=0.7,
                            explanation="Partial match found and validated in CV text"
                        ))
                        match_found = True
                        break
            
            if not match_found:
                matches.append(KeywordMatch(
                    jd_keyword=jd_keyword,
                    cv_keyword=None,
                    match_type="missing",
                    confidence=0.0,
                    explanation="No match found in CV"
                ))
        
        return matches
    
    async def comprehensive_comparison(self, cv_text: str, jd_text: str) -> Dict[str, CategoryComparison]:
        """
        Perform comprehensive LLM-based comparison between CV and JD with strict validation
        """
        print(f"🚀 [LLM-MATCHER] Starting comprehensive LLM-based comparison")
        
        # Extract keywords from both texts
        cv_keywords = await self.extract_keywords_from_text(cv_text, "CV")
        jd_keywords = await self.extract_keywords_from_text(jd_text, "JD")
        
        # Compare each category
        comparisons = {}
        categories = ["technical_skills", "soft_skills", "domain_keywords", "experience_keywords", "education_keywords"]
        
        for category in categories:
            print(f"🔍 [LLM-MATCHER] Processing {category}")
            
            jd_category_keywords = jd_keywords.get(category, [])
            cv_category_keywords = cv_keywords.get(category, [])
            
            # Perform strict comparison
            matches = await self.compare_keywords_strictly(
                jd_category_keywords, 
                cv_category_keywords, 
                category,
                cv_text,
                jd_text
            )
            
            # Calculate metrics
            total_jd_keywords = len(jd_category_keywords)
            matched_keywords = [m for m in matches if m.match_type != "missing"]
            match_percentage = (len(matched_keywords) / total_jd_keywords * 100) if total_jd_keywords > 0 else 0
            
            missing_keywords = [m.jd_keyword for m in matches if m.match_type == "missing"]
            additional_keywords = [kw for kw in cv_category_keywords if kw not in [m.cv_keyword for m in matches if m.cv_keyword]]
            
            comparisons[category] = CategoryComparison(
                category=category,
                jd_keywords=jd_category_keywords,
                cv_keywords=cv_category_keywords,
                matches=matches,
                match_percentage=match_percentage,
                missing_keywords=missing_keywords,
                additional_keywords=additional_keywords
            )
            
            print(f"✅ [LLM-MATCHER] {category}: {match_percentage:.1f}% match ({len(matched_keywords)}/{total_jd_keywords})")
        
        return comparisons
    
    def calculate_overall_score(self, comparisons: Dict[str, CategoryComparison]) -> float:
        """
        Calculate weighted overall score based on category importance
        """
        # Category weights (must sum to 1.0)
        weights = {
            "technical_skills": 0.35,
            "soft_skills": 0.20,
            "domain_keywords": 0.20,
            "experience_keywords": 0.15,
            "education_keywords": 0.10
        }
        
        weighted_score = 0
        for category, comparison in comparisons.items():
            weight = weights.get(category, 0)
            weighted_score += comparison.match_percentage * weight
        
        return weighted_score
    
    def generate_improvement_suggestions(self, comparisons: Dict[str, CategoryComparison]) -> List[str]:
        """
        Generate actionable improvement suggestions based on comparison results
        """
        suggestions = []
        
        for category, comparison in comparisons.items():
            if comparison.missing_keywords:
                category_name = category.replace("_", " ").title()
                missing_count = len(comparison.missing_keywords)
                
                if missing_count <= 3:
                    missing_list = ", ".join(comparison.missing_keywords)
                    suggestions.append(f"Add missing {category_name.lower()}: {missing_list}")
                else:
                    suggestions.append(f"Add {missing_count} missing {category_name.lower()} keywords")
                
                # Specific suggestions for low-scoring categories
                if comparison.match_percentage < 50:
                    suggestions.append(f"Strengthen {category_name.lower()} section - currently {comparison.match_percentage:.1f}% match")
        
        return suggestions[:5]  # Limit to top 5 suggestions 