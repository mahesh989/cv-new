"""
ATS Recommendation Service - Optimized for AI Consumption

This service creates highly optimized recommendation files with:
- Zero redundancy
- Structured data only
- Keyword tier classification
- Strategic tailoring guidance
- PRE-FILTERING: Excludes keywords already in CV
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)


class ATSRecommendationService:
    """Service for creating optimized AI recommendation input files"""
    
    def __init__(self, user_email: str):
        from app.utils.user_path_utils import get_user_base_path
        self.user_email = user_email
        self.base_dir = get_user_base_path(user_email)
    
    def extract_ats_recommendation_data(self, company: str) -> Optional[Dict[str, Any]]:
        """
        Extract and optimize recommendation data from skills analysis file
        
        Args:
            company: Company name
            
        Returns:
            Optimized dictionary for AI consumption or None if not found
        """
        try:
            # Locate analysis file
            company_dir = self.base_dir / "applied_companies" / company
            analysis_file = TimestampUtils.find_latest_timestamped_file(
                company_dir, f"{company}_skills_analysis", "json"
            )
            if not analysis_file:
                analysis_file = company_dir / f"{company}_skills_analysis.json"
            
            if not analysis_file.exists():
                logger.error(f"Skills analysis file not found: {analysis_file}")
                return None
            
            # Read analysis file
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Extract components
            cv_skills = analysis_data.get("cv_skills", {})
            jd_skills = analysis_data.get("jd_skills", {})
            match_entries = analysis_data.get("analyze_match_entries", [])
            preextracted_entries = analysis_data.get("preextracted_comparison_entries", [])
            component_entries = analysis_data.get("component_analysis_entries", [])
            ats_entries = analysis_data.get("ats_calculation_entries", [])
            
            # Parse and simplify each component
            preliminary_decision = self._extract_preliminary_decision(match_entries)
            match_summary = self._extract_match_summary(preextracted_entries)
            component_summary = self._extract_component_summary(component_entries)
            ats_scoring = self._extract_ats_scoring(ats_entries)
            
            # Generate optimized recommendation data
            recommendation_data = {
                "metadata": {
                    "company": company,
                    "generated_at": datetime.utcnow().isoformat(),
                    "ats_score_current": ats_scoring.get("final_score", 0),
                    "match_rate_current": match_summary.get("overall_match_rate", 0)
                },
                
                # Clean structured skills (no verbose text)
                "skills_extraction": {
                    "cv": {
                        "technical": cv_skills.get("technical_skills", []),
                        "soft": cv_skills.get("soft_skills", []),
                        "domain": cv_skills.get("domain_keywords", [])
                    },
                    "jd": {
                        "technical": jd_skills.get("technical_skills", []),
                        "soft": jd_skills.get("soft_skills", []),
                        "domain": jd_skills.get("domain_keywords", [])
                    }
                },
                
                # Simplified preliminary decision (no verbose analysis)
                "preliminary_decision": preliminary_decision,
                
                # Clean match summary (no emoji, no verbose reasoning)
                "match_summary": match_summary,
                
                # Keyword tier classification for CV framework
                "keyword_integration_guidance": self._classify_keywords(
                    match_summary.get("missing_keywords", {}),
                    cv_skills
                ),
                
                # Simplified component summary (no redundant fields)
                "component_summary": component_summary,
                
                # Clean ATS scoring (numbers only)
                "ats_scoring": ats_scoring
            }
            
            return recommendation_data
            
        except Exception as e:
            logger.error(f"Error extracting ATS recommendation data: {e}", exc_info=True)
            return None
    
    def save_optimized_recommendation(self, company: str, data: Dict[str, Any]) -> Optional[Path]:
        """
        Save optimized recommendation data to file
        
        Args:
            company: Company name
            data: Recommendation data dictionary
            
        Returns:
            Path to saved file or None if failed
        """
        try:
            company_dir = self.base_dir / "applied_companies" / company
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = company_dir / f"{company}_input_recommendation_{timestamp}.json"
            
            # Save with clean formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            file_size_kb = output_file.stat().st_size / 1024
            logger.info(f"✅ Created optimized recommendation file: {output_file} ({file_size_kb:.1f}KB)")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving recommendation file: {e}", exc_info=True)
            return None
    
    def _extract_preliminary_decision(self, match_entries: List[Dict]) -> Dict[str, Any]:
        """Extract simplified preliminary decision (no verbose analysis)"""
        if not match_entries:
            return {
                "decision": "UNKNOWN",
                "match_score": 0,
                "confidence": 0,
                "should_proceed": True,
                "critical_missing": [],
                "implicit_likely": [],
                "learnable_gaps": []
            }
        
        latest_entry = match_entries[-1]
        content = latest_entry.get("content", "")
        
        # Extract structured decision fields
        decision_match = re.search(r"DECISION:\s*(PROCEED|MAYBE|DONT_PROCEED)", content, re.IGNORECASE)
        match_score_match = re.search(r"MATCH_SCORE:\s*(\d+)", content)
        confidence_match = re.search(r"CONFIDENCE:\s*(\d+)", content)
        
        decision = decision_match.group(1).upper() if decision_match else "UNKNOWN"
        match_score = int(match_score_match.group(1)) if match_score_match else 0
        confidence = int(confidence_match.group(1)) if confidence_match else 0
        
        # Extract skill categories (brief lists only)
        critical_missing = []
        implicit_likely = []
        learnable_gaps = []
        
        for line in content.split('\n'):
            if line.startswith("CRITICAL_MISSING:"):
                skills_text = line.split(":", 1)[1].strip()
                if skills_text and skills_text.lower() != "none":
                    critical_missing = [s.strip() for s in skills_text.split(",")][:5]
            
            elif line.startswith("IMPLICIT_LIKELY:"):
                skills_text = line.split(":", 1)[1].strip()
                if skills_text and skills_text.lower() != "none":
                    implicit_likely = [s.strip() for s in skills_text.split(",")][:5]
            
            elif line.startswith("LEARNABLE_GAPS:"):
                skills_text = line.split(":", 1)[1].strip()
                if skills_text and skills_text.lower() != "none":
                    learnable_gaps = [s.strip() for s in skills_text.split(",")][:5]
        
        return {
            "decision": decision,
            "match_score": match_score,
            "confidence": confidence,
            "should_proceed": decision in ["PROCEED", "MAYBE"],
            "critical_missing": critical_missing,
            "implicit_likely": implicit_likely,
            "learnable_gaps": learnable_gaps
        }
    
    def _extract_match_summary(self, preextracted_entries: List[Dict]) -> Dict[str, Any]:
        """Extract clean match summary (no verbose reasoning)"""
        if not preextracted_entries:
            return {
                "overall_match_rate": 0,
                "by_category": {},
                "missing_keywords": {"technical": [], "soft": [], "domain": []}
            }
        
        latest_entry = preextracted_entries[-1]
        content = latest_entry.get("content", "")
        
        match_summary = {
            "overall_match_rate": 0,
            "by_category": {
                "technical": {"matched": [], "missing": [], "match_rate": 0},
                "soft": {"matched": [], "missing": [], "match_rate": 0},
                "domain": {"matched": [], "missing": [], "match_rate": 0}
            },
            "missing_keywords": {"technical": [], "soft": [], "domain": []}
        }
        
        # Extract overall match rate
        match_rate_pattern = r"Match Rate:\s*([\d.]+)%"
        match = re.search(match_rate_pattern, content)
        if match:
            match_summary["overall_match_rate"] = float(match.group(1))
        
        # Extract per-category data
        current_category = None
        for line in content.split("\n"):
            # Detect category sections
            if "Technical Skills" in line:
                current_category = "technical"
            elif "Soft Skills" in line:
                current_category = "soft"
            elif "Domain Keywords" in line:
                current_category = "domain"
            
            # Extract match rate for category
            if current_category:
                cat_match_rate = re.search(r"Match Rate:\s*([\d.]+)%", line)
                if cat_match_rate:
                    match_summary["by_category"][current_category]["match_rate"] = float(cat_match_rate.group(1))
            
            # Extract matched skills (look for "CV Has: 'skill'")
            if ("CV Has:" in line or "CV has:" in line) and current_category:
                try:
                    skill = line.split("'")[1]
                    match_summary["by_category"][current_category]["matched"].append(skill)
                except:
                    pass
            
            # Extract missing skills (look for "JD Requires: 'skill'")
            if ("JD Required:" in line or "JD Requires:" in line) and current_category:
                try:
                    skill = line.split("'")[1]
                    match_summary["by_category"][current_category]["missing"].append(skill)
                    match_summary["missing_keywords"][current_category].append(skill)
                except:
                    pass
        
        # Calculate match rates per category
        for category in ["technical", "soft", "domain"]:
            matched_count = len(match_summary["by_category"][category]["matched"])
            missing_count = len(match_summary["by_category"][category]["missing"])
            total = matched_count + missing_count
            if total > 0:
                match_summary["by_category"][category]["match_rate"] = (matched_count / total) * 100
        
        return match_summary
    
    def _extract_component_summary(self, component_entries: List[Dict]) -> Dict[str, Any]:
        """Extract clean component summary (no redundant analysis text)"""
        if not component_entries:
            return {
                "skills_relevance": 0,
                "experience_alignment": 0,
                "role_similarity": 0,
                "seniority_match": 0,
                "industry_fit": 0
            }
        
        latest_entry = component_entries[-1]
        extracted_scores = latest_entry.get("extracted_scores", {})
        
        return {
            "skills_relevance": extracted_scores.get("skills_relevance", 0),
            "experience_alignment": extracted_scores.get("experience_alignment", 0),
            "role_similarity": extracted_scores.get("role_similarity", 0),
            "seniority_match": extracted_scores.get("seniority_match", 0),
            "industry_fit": extracted_scores.get("industry_fit", 0),
            "required_skills_coverage": extracted_scores.get("required_skills_coverage", 0),
            "tech_stack_similarity": extracted_scores.get("tech_stack_similarity", 0),
            "business_readiness": extracted_scores.get("business_readiness", 0),
            "industry_transition_fit": extracted_scores.get("industry_transition_fit", 0)
            }
    
    def _extract_ats_scoring(self, ats_entries: List[Dict]) -> Dict[str, Any]:
        """Extract clean ATS scoring (numbers only, no verbose explanation)"""
        if not ats_entries:
            return {
                "final_score": 0,
                "category1_score": 0,
                "category2_score": 0,
                "category3_score": 0,
                "improvement_needed": 75.0,
                "scoring_version": "unknown"
            }
        
        latest_entry = ats_entries[-1]
        breakdown = latest_entry.get("breakdown", {})
        
        return {
            "final_score": latest_entry.get("final_ats_score", 0),
            "category1_score": breakdown.get("category1", {}).get("score", 0),
            "category2_score": breakdown.get("category2", {}).get("score", 0),
            "category3_score": breakdown.get("category3", {}).get("score", 0),
            "improvement_needed": max(0, 75.0 - latest_entry.get("final_ats_score", 0)),
            "category1_keywords": breakdown.get("category1", {}).get("score", 0),
            "category2_ai_analysis": breakdown.get("category2", {}).get("score", 0),
            "missing_counts": breakdown.get("category1", {}).get("missing_counts", {}),
            "scoring_version": latest_entry.get("scoring_version", "unknown")
        }
    
    def _classify_keywords(self, missing_keywords: Dict[str, List[str]], 
                          cv_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Classify missing keywords into tiers based on CV tailoring framework.
        NOW WITH PRE-FILTERING: Removes keywords already present in the latest CV.
        
        Tier 1: Always add (generic/transferable)
        Tier 2: Add if semantic evidence exists
        Tier 3: Never add (domain-specific/unverifiable)
        """
        # STEP 1: Extract existing keywords from latest CV (including tailored CV if it exists)
        existing_keywords_lower = self._extract_existing_cv_keywords()
        
        # STEP 2: Filter missing keywords to exclude those already in CV
        filtered_missing = {}
        already_present = {}
        
        for category, keywords in missing_keywords.items():
            filtered_missing[category] = []
            already_present[category] = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Check if keyword or any variation exists in CV
                if self._keyword_exists_in_cv(keyword_lower, existing_keywords_lower):
                    already_present[category].append(keyword)
                    logger.info(f"🔍 [KEYWORD_FILTER] Skipping '{keyword}' - already in CV")
                else:
                    filtered_missing[category].append(keyword)
        
        # Log filtering results
        total_original = sum(len(keywords) for keywords in missing_keywords.values())
        total_filtered = sum(len(keywords) for keywords in filtered_missing.values())
        total_already_present = sum(len(keywords) for keywords in already_present.values())
        
        logger.info(f"🔍 [KEYWORD_FILTER] Original missing keywords: {total_original}")
        logger.info(f"✅ [KEYWORD_FILTER] Actually new keywords: {total_filtered}")
        logger.info(f"⏭️  [KEYWORD_FILTER] Already in CV (filtered): {total_already_present}")
        
        if total_already_present > 0:
            for category, keywords in already_present.items():
                if keywords:
                    logger.info(f"   - {category}: {', '.join(keywords[:5])}")
        
        # STEP 3: Now classify the FILTERED keywords (only genuinely missing ones)
        # Tier 1 patterns (generic soft skills and transferable competencies)
        tier1_patterns = {
            "soft": [
                "leadership", "communication", "teamwork", "problem solving", "problem-solving",
                "collaboration", "time management", "adaptability", "attention to detail",
                "analytical thinking", "critical thinking", "interpersonal", "presentation",
                "organizational", "numeracy", "proactive"
            ],
            "technical": [
                "data analysis", "project management", "stakeholder management",
                "business intelligence", "reporting", "data visualization", "visualisation"
            ]
        }
        
        # Tier 3 patterns (domain-specific terms - NEVER add)
        tier3_patterns = {
            "domain": [
                "refugee", "humanitarian", "fundraising", "donor", "charity", "nfp",
                "not for profit", "community engagement", "social impact", "food relief",
                "school breakfast", "food bank", "volunteer", "non-profit"
            ],
            "certifications": [
                "pmp", "scrum master", "aws certified", "azure certified", "google cloud",
                "comptia", "cissp", "cisa", "prince2"
            ]
        }
        
        classified = {
            "tier1_always_add": {"technical": [], "soft": [], "domain": []},
            "tier2_add_if_evidence": {"technical": [], "soft": [], "domain": []},
            "tier3_never_add": {"technical": [], "soft": [], "domain": []},
            "already_in_cv_filtered": list(set([kw for keywords in already_present.values() for kw in keywords])),
            "integration_instructions": (
                "Tier 1: Integrate ALL keywords into skills section and relevant bullets. "
                "Tier 2: Integrate ONLY if semantic evidence exists in CV experience. "
                "Tier 3: DO NOT add - domain-specific, unverifiable, or lacks evidence. "
                "Already in CV: These keywords were filtered out as they already exist in the CV."
            )
        }
        
        cv_technical = [s.lower() for s in cv_skills.get("technical_skills", [])]
        
        for category in ["technical", "soft", "domain"]:
            for keyword in filtered_missing.get(category, []):
                keyword_lower = keyword.lower()
                
                # Check Tier 1 (generic/transferable)
                is_tier1 = any(
                    pattern in keyword_lower 
                    for pattern in tier1_patterns.get(category, [])
                )
                
                if is_tier1:
                    classified["tier1_always_add"][category].append(keyword)
                    continue
                
                # Check Tier 3 (domain-specific/unverifiable)
                is_tier3_domain = any(
                    pattern in keyword_lower 
                    for pattern in tier3_patterns.get("domain", [])
                )
                
                is_tier3_cert = any(
                    pattern in keyword_lower 
                    for pattern in tier3_patterns.get("certifications", [])
                )
                
                is_specific_variant = self._is_specific_tool_variant(keyword_lower, cv_technical)
                
                if is_tier3_domain or is_tier3_cert or is_specific_variant:
                    classified["tier3_never_add"][category].append(keyword)
                    continue
                
                # Default to Tier 2
                classified["tier2_add_if_evidence"][category].append(keyword)
        
        return classified
    
    def _extract_existing_cv_keywords(self) -> set:
        """
        Extract existing keywords from the latest CV (including tailored CV if exists).
        Returns a set of lowercase keywords for case-insensitive matching.
        """
        try:
            from app.unified_latest_file_selector import get_selector_for_user
            
            # Get company from current context (this will be set during extraction)
            # For now, we'll extract from the latest CV regardless of company
            user_selector = get_selector_for_user(self.user_email)
            
            # Get the latest CV JSON file
            cv_dir = self.base_dir / "cvs"
            tailored_dir = cv_dir / "tailored"
            original_dir = cv_dir / "original"
            
            keywords = set()
            
            # Try to find latest tailored CV first
            tailored_files = list(tailored_dir.glob("*_tailored_cv_*.json"))
            if tailored_files:
                latest_tailored = max(tailored_files, key=lambda f: f.stat().st_mtime)
                keywords.update(self._extract_keywords_from_cv_file(latest_tailored))
                logger.info(f"🔍 [KEYWORD_FILTER] Extracted {len(keywords)} keywords from latest tailored CV: {latest_tailored.name}")
            
            # Also check original CV
            original_cv = original_dir / "original_cv.json"
            if original_cv.exists():
                original_keywords = self._extract_keywords_from_cv_file(original_cv)
                keywords.update(original_keywords)
                logger.info(f"🔍 [KEYWORD_FILTER] Total {len(keywords)} keywords after checking original CV")
            
            return keywords
            
        except Exception as e:
            logger.warning(f"⚠️ [KEYWORD_FILTER] Could not extract existing CV keywords: {e}")
            return set()
    
    def _extract_keywords_from_cv_file(self, cv_file: Path) -> set:
        """Extract keywords from a CV JSON file"""
        keywords = set()
        
        try:
            import json
            with open(cv_file, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
            
            # Extract from skills
            for skill_cat in cv_data.get('skills', []):
                if isinstance(skill_cat, dict):
                    for skill in skill_cat.get('skills', []):
                        if skill:
                            keywords.add(str(skill).lower())
            
            # Extract from experience bullets (2-3 word phrases)
            for exp in cv_data.get('experience', []):
                if isinstance(exp, dict):
                    for bullet in exp.get('bullets', []):
                        if bullet:
                            # Extract 2-word and 3-word phrases
                            words = str(bullet).lower().split()
                            for i in range(len(words) - 1):
                                keywords.add(f"{words[i]} {words[i+1]}")
                            for i in range(len(words) - 2):
                                keywords.add(f"{words[i]} {words[i+1]} {words[i+2]}")
            
            # Extract from role highlights
            role_highlights = cv_data.get('role_highlights', '')
            if role_highlights:
                words = str(role_highlights).lower().split()
                for i in range(len(words) - 1):
                    keywords.add(f"{words[i]} {words[i+1]}")
            
        except Exception as e:
            logger.warning(f"⚠️ [KEYWORD_FILTER] Error extracting keywords from {cv_file}: {e}")
        
        return keywords
    
    def _keyword_exists_in_cv(self, keyword: str, cv_keywords: set) -> bool:
        """
        Check if a keyword exists in CV keywords (with fuzzy matching).
        Handles variations like "python" vs "python programming", "sql" vs "structured query language".
        """
        keyword_lower = keyword.lower()
        
        # Direct match
        if keyword_lower in cv_keywords:
            return True
        
        # Check if keyword is part of any CV keyword (e.g., "python" in "python programming")
        for cv_kw in cv_keywords:
            if keyword_lower in cv_kw or cv_kw in keyword_lower:
                # Only match if significant overlap (not just "a" in "data")
                if len(keyword_lower) > 3 or len(cv_kw) > 3:
                    return True
        
        # Check common variations
        variations = {
            'python': ['python programming', 'python development', 'py'],
            'sql': ['structured query language', 'mysql', 'postgresql', 'sql server'],
            'javascript': ['js', 'javascript programming', 'node', 'nodejs'],
            'data analysis': ['data analytics', 'analyzing data', 'analytical'],
            'machine learning': ['ml', 'ai', 'artificial intelligence'],
            'project management': ['pm', 'project coordination', 'managed projects'],
        }
        
        for base, vars in variations.items():
            if keyword_lower == base or keyword_lower in vars:
                if base in cv_keywords or any(v in cv_keywords for v in vars):
                    return True
        
        return False
    
    def _is_specific_tool_variant(self, keyword: str, cv_technical_lower: List[str]) -> bool:
        """Check if keyword is a specific tool variant not in CV"""
        # SQL variants without generic SQL
        if keyword in ["postgresql", "mysql", "mssql", "oracle", "mariadb"]:
            has_generic_sql = any("sql" in skill and skill != keyword for skill in cv_technical_lower)
            return not has_generic_sql
        
        # Python variants without generic Python
        if keyword in ["django", "flask", "fastapi", "pytorch", "tensorflow"]:
            has_python = any("python" in skill for skill in cv_technical_lower)
            return not has_python
        
        return False
