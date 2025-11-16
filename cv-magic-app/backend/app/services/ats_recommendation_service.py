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
        
        CRITICAL FIX: Now loads missing keywords from cv_jd_matching.json (source of truth)
        instead of parsing from preextracted comparison text
        
        Args:
            company: Company name
            
        Returns:
            Optimized dictionary for AI consumption or None if not found
        """
        try:
            logger.info(f"🔍 [PHASE6] Starting recommendation data extraction for: {company}")
            
            # STEP 1: Locate and load analysis file
            company_dir = self.base_dir / "applied_companies" / company
            analysis_file = TimestampUtils.find_latest_timestamped_file(
                company_dir, f"{company}_skills_analysis", "json"
            )
            if not analysis_file:
                analysis_file = company_dir / f"{company}_skills_analysis.json"
            
            if not analysis_file.exists():
                logger.error(f"❌ [PHASE6] Skills analysis file not found: {analysis_file}")
                return None
            
            # Read analysis file
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            logger.info(f"✅ [PHASE6] Loaded skills analysis from: {analysis_file.name}")
            
            # STEP 2: Load CV-JD matching file (SOURCE OF TRUTH for missing keywords)
            matching_file = TimestampUtils.find_latest_timestamped_file(
                company_dir, f"{company}_cv_jd_matching", "json"
            )
            if not matching_file:
                matching_file = company_dir / f"{company}_cv_jd_matching.json"
            
            if not matching_file.exists():
                logger.error(f"❌ [PHASE6] CV-JD matching file not found: {matching_file}")
                return None
            
            with open(matching_file, 'r', encoding='utf-8') as f:
                matching_data = json.load(f)
            
            logger.info(f"✅ [PHASE6] Loaded CV-JD matching from: {matching_file.name}")
            
            # STEP 3: Extract complete missing keywords list
            missed_required = matching_data.get("missed_required_keywords", [])
            missed_preferred = matching_data.get("missed_preferred_keywords", [])
            all_missing_keywords = missed_required + missed_preferred
            
            logger.info(f"📊 [PHASE6] Total missing keywords: {len(all_missing_keywords)}")
            logger.info(f"   - Required: {len(missed_required)} → {missed_required}")
            logger.info(f"   - Preferred: {len(missed_preferred)} → {missed_preferred}")
            
            # Extract components
            cv_skills = analysis_data.get("cv_skills", {})
            jd_skills = analysis_data.get("jd_skills", {})
            match_entries = analysis_data.get("analyze_match_entries", [])
            preextracted_entries = analysis_data.get("preextracted_comparison_entries", [])
            component_entries = analysis_data.get("component_analysis_entries", [])
            ats_entries = analysis_data.get("ats_calculation_entries", [])
            
            # STEP 4: Categorize missing keywords by type (technical, soft, domain)
            categorized_missing = self._categorize_missing_keywords(
                all_missing_keywords,
                jd_skills
            )
            
            logger.info(f"📊 [PHASE6] Categorized missing keywords:")
            logger.info(f"   - Technical: {len(categorized_missing.get('technical', []))} → {categorized_missing.get('technical', [])}")
            logger.info(f"   - Soft: {len(categorized_missing.get('soft', []))} → {categorized_missing.get('soft', [])}")
            logger.info(f"   - Domain: {len(categorized_missing.get('domain', []))} → {categorized_missing.get('domain', [])}")
            
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
                
                # CRITICAL FIX: Use categorized missing keywords from cv_jd_matching.json
                # instead of parsing from preextracted_comparison_entries
                "keyword_integration_guidance": self._classify_keywords(
                    categorized_missing,  # NOW using cv_jd_matching.json data!
                    cv_skills
                ),
                
                # Simplified component summary (no redundant fields)
                "component_summary": component_summary,
                
                # Clean ATS scoring (numbers only)
                "ats_scoring": ats_scoring
            }
            
            logger.info(f"=" * 80)
            logger.info(f"✅ [PHASE6] COMPLETE - Summary:")
            logger.info(f"   Company: {company}")
            logger.info(f"   Total missing keywords: {len(all_missing_keywords)}")
            logger.info(f"=" * 80)
            
            return recommendation_data
            
        except Exception as e:
            logger.error(f"❌ [PHASE6] Error extracting ATS recommendation data: {e}", exc_info=True)
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
    
    def _categorize_missing_keywords(
        self,
        missing_keywords: List[str],
        jd_skills: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Categorize missing keywords into technical, soft, domain
        
        Args:
            missing_keywords: List of all missing keywords
            jd_skills: JD skills from skills_analysis.json
            
        Returns:
            Dictionary with categorized keywords
        """
        categorized = {
            "technical": [],
            "soft": [],
            "domain": []
        }
        
        # Get JD skill categories for reference
        jd_technical = [s.lower() for s in jd_skills.get("technical_skills", [])]
        jd_soft = [s.lower() for s in jd_skills.get("soft_skills", [])]
        jd_domain = [s.lower() for s in jd_skills.get("domain_keywords", [])]
        
        for keyword in missing_keywords:
            keyword_lower = keyword.lower()
            
            # Check which category it belongs to
            if keyword_lower in jd_technical or any(keyword_lower in tech for tech in jd_technical):
                categorized["technical"].append(keyword)
            elif keyword_lower in jd_soft or any(keyword_lower in soft for soft in jd_soft):
                categorized["soft"].append(keyword)
            else:
                # Default to domain if not clearly technical or soft
                categorized["domain"].append(keyword)
        
        return categorized
    
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
        Classify missing keywords into tiers with AGGRESSIVE Tier 1 strategy
        
        CRITICAL FIX: Expanded Tier 1 patterns to include ALL generic/transferable skills
        All soft skills → Tier 1 by default (unless domain-specific)
        
        Tier 1: Always add (generic/transferable) - EXPANDED
        Tier 2: Add if semantic evidence exists
        Tier 3: Never add (domain-specific/unverifiable)
        """
        logger.info(f"🔍 [PHASE6-CLASSIFY] Starting keyword classification")
        logger.info(f"   Input missing keywords: {sum(len(v) for v in missing_keywords.values())}")
        
        # STEP 1: Extract existing keywords from latest CV
        existing_keywords = self._extract_existing_cv_keywords()
        logger.info(f"   Existing CV keywords: {len(existing_keywords)}")
        
        # STEP 2: Filter out keywords already in CV
        filtered_missing = {}
        already_present = {}
        
        for category, keywords in missing_keywords.items():
            filtered_missing[category] = []
            already_present[category] = []
            
            for keyword in keywords:
                if self._keyword_exists_in_cv(keyword, existing_keywords):
                    already_present[category].append(keyword)
                    logger.info(f"   ⏭️ Filtered: '{keyword}' (already in CV)")
                else:
                    filtered_missing[category].append(keyword)
        
        total_filtered = sum(len(v) for v in filtered_missing.values())
        total_already_present = sum(len(v) for v in already_present.values())
        
        logger.info(f"✅ [PHASE6-CLASSIFY] Filtering complete:")
        logger.info(f"   - Still missing: {total_filtered}")
        logger.info(f"   - Already in CV: {total_already_present}")
        
        # STEP 3: AGGRESSIVE Tier 1 classification
        
        # EXPANDED Tier 1 patterns - ALL generic/transferable skills
        tier1_keywords = {
            "soft_skills": [
                # Communication
                "communication", "verbal communication", "written communication",
                "presentation", "public speaking", "stakeholder communication",
                
                # Collaboration
                "teamwork", "collaboration", "team collaboration", "cross-functional",
                "interpersonal", "relationship building",
                
                # Leadership
                "leadership", "team leadership", "mentoring", "coaching",
                "people management", "talent development",
                
                # Problem Solving
                "problem solving", "problem-solving", "critical thinking",
                "analytical thinking", "decision making", "strategic thinking",
                
                # Work Skills
                "time management", "project management", "organizational",
                "planning", "prioritization", "multitasking",
                
                # Adaptability
                "adaptability", "flexibility", "learning agility", "continuous learning",
                "innovation", "creativity", "curiosity",
                
                # Quality
                "attention to detail", "quality assurance", "accuracy",
                "thoroughness", "diligence"
            ],
            
            "transferable_technical": [
                # Data & Analysis (generic)
                "data analysis", "analytical skills", "data-driven",
                "reporting", "documentation", "research",
                
                # Business
                "business analysis", "process improvement", "business processes",
                "requirements gathering", "stakeholder management",
                
                # Project
                "project coordination", "project delivery", "agile", "scrum",
                
                # Tools (very common)
                "microsoft office", "ms office", "email", "calendar management"
            ]
        }
        
        # Tier 3 patterns - Domain-specific (NEVER add)
        tier3_keywords = [
            # Charity/NFP specific
            "refugee", "humanitarian", "poverty", "food relief", "food bank",
            "fundraising", "donor", "charity", "volunteer", "community engagement",
            "social impact", "nfp", "not for profit", "non-profit",
            
            # Company-specific
            "annual impact report", "growing careers", "education program",
            
            # Certifications (specific)
            "pmp", "scrum master", "aws certified", "azure certified",
            "comptia", "cissp", "cisa", "prince2",
            
            # Industry jargon
            "blockchain", "cryptocurrency", "metaverse"
        ]
        
        classified = {
            "tier1_always_add": {"technical": [], "soft": [], "domain": []},
            "tier2_add_if_evidence": {"technical": [], "soft": [], "domain": []},
            "tier3_never_add": {"technical": [], "soft": [], "domain": []},
            "already_in_cv_filtered": []
        }
        
        # Flatten already_present for the filter list
        for category_keywords in already_present.values():
            classified["already_in_cv_filtered"].extend(category_keywords)
        
        # Classify each filtered keyword
        for category in ["technical", "soft", "domain"]:
            for keyword in filtered_missing.get(category, []):
                keyword_lower = keyword.lower()
                
                # Check Tier 3 first (domain-specific - NEVER add)
                is_tier3 = any(
                    tier3_pattern in keyword_lower 
                    for tier3_pattern in tier3_keywords
                )
                
                if is_tier3:
                    classified["tier3_never_add"][category].append(keyword)
                    logger.info(f"   🚫 Tier 3: '{keyword}' (domain-specific)")
                    continue
                
                # Check Tier 1 (generic/transferable - AGGRESSIVE)
                is_tier1 = False
                
                # All soft skills → Tier 1 by default
                if category == "soft":
                    is_tier1 = True
                
                # Check against Tier 1 patterns
                for tier1_list in tier1_keywords.values():
                    if any(tier1_pattern in keyword_lower for tier1_pattern in tier1_list):
                        is_tier1 = True
                        break
                
                if is_tier1:
                    classified["tier1_always_add"][category].append(keyword)
                    logger.info(f"   ✅ Tier 1: '{keyword}' (generic/transferable)")
                else:
                    # Default to Tier 2 (needs evidence)
                    classified["tier2_add_if_evidence"][category].append(keyword)
                    logger.info(f"   ⚠️ Tier 2: '{keyword}' (needs evidence)")
        
        # VALIDATION: Ensure ALL missing keywords are classified
        total_classified = (
            sum(len(v) for v in classified["tier1_always_add"].values()) +
            sum(len(v) for v in classified["tier2_add_if_evidence"].values()) +
            sum(len(v) for v in classified["tier3_never_add"].values())
        )
        
        logger.info(f"📊 [PHASE6-CLASSIFY] Classification complete:")
        logger.info(f"   - Tier 1: {sum(len(v) for v in classified['tier1_always_add'].values())}")
        for cat, kws in classified['tier1_always_add'].items():
            if kws:
                logger.info(f"      {cat}: {kws}")
        logger.info(f"   - Tier 2: {sum(len(v) for v in classified['tier2_add_if_evidence'].values())}")
        logger.info(f"   - Tier 3: {sum(len(v) for v in classified['tier3_never_add'].values())}")
        logger.info(f"   - Already in CV: {len(classified['already_in_cv_filtered'])}")
        
        if total_classified != total_filtered:
            logger.error(f"❌ [PHASE6-CLASSIFY] VALIDATION FAILED!")
            logger.error(f"   Expected: {total_filtered}, Got: {total_classified}")
            logger.error(f"   Some keywords were lost during classification!")
        else:
            logger.info(f"✅ [PHASE6-CLASSIFY] VALIDATION PASSED - All keywords classified")
        
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
    
    def _extract_keywords_from_cv_file(self, cv_file_path: Path) -> set:
        """
        Extract keywords from CV JSON file with comprehensive phrase extraction
        Extracts: individual words, 2-word phrases, 3-word phrases, full sentences
        """
        keywords = set()
        
        try:
            with open(cv_file_path, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
            
            # 1. Extract from skills section (exact phrases)
            for skill_cat in cv_data.get('skills', []):
                if isinstance(skill_cat, dict):
                    for skill in skill_cat.get('skills', []):
                        if skill:
                            skill_str = str(skill).strip().lower()
                            if skill_str:
                                keywords.add(skill_str)
            
            # 2. Extract from experience bullets (phrases + words)
            for exp in cv_data.get('experience', []):
                if isinstance(exp, dict):
                    for bullet in exp.get('bullets', []):
                        if bullet:
                            bullet_str = str(bullet).lower()
                            
                            # Add full bullet (for phrase matching)
                            keywords.add(bullet_str)
                            
                            # Extract 2-word phrases
                            words = bullet_str.split()
                            for i in range(len(words) - 1):
                                phrase = f"{words[i]} {words[i+1]}"
                                if len(phrase) > 5:  # Skip very short phrases
                                    keywords.add(phrase.strip('.,;:()[]{}'))
                            
                            # Extract 3-word phrases
                            for i in range(len(words) - 2):
                                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                                if len(phrase) > 8:
                                    keywords.add(phrase.strip('.,;:()[]{}'))
                            
                            # Extract individual words
                            for word in words:
                                clean_word = word.strip('.,;:()[]{}')
                                if len(clean_word) > 3:
                                    keywords.add(clean_word)
            
            # 3. Extract from projects
            for project in cv_data.get('projects', []):
                if isinstance(project, dict):
                    # Project name
                    if project.get('name'):
                        keywords.add(str(project['name']).lower())
                    
                    # Project description bullets
                    for bullet in project.get('bullets', []):
                        if bullet:
                            bullet_str = str(bullet).lower()
                            keywords.add(bullet_str)
                            
                            # Extract phrases and words (same as experience)
                            words = bullet_str.split()
                            for i in range(len(words) - 1):
                                keywords.add(f"{words[i]} {words[i+1]}".strip('.,;:()[]{}'))
                            for word in words:
                                if len(word.strip('.,;:()[]{}')) > 3:
                                    keywords.add(word.strip('.,;:()[]{}'))
            
            # 4. Extract from summary/role highlights
            if cv_data.get('summary'):
                summary_text = str(cv_data['summary']).lower()
                keywords.add(summary_text)
                words = summary_text.split()
                for i in range(len(words) - 1):
                    keywords.add(f"{words[i]} {words[i+1]}".strip('.,;:()[]{}'))
            
            if cv_data.get('role_highlights'):
                role_text = str(cv_data['role_highlights']).lower()
                keywords.add(role_text)
                words = role_text.split()
                for i in range(len(words) - 1):
                    keywords.add(f"{words[i]} {words[i+1]}".strip('.,;:()[]{}'))
            
            logger.info(f"🔍 [KEYWORD-EXTRACT] Extracted {len(keywords)} keywords from {cv_file_path.name}")
            
        except Exception as e:
            logger.error(f"❌ [KEYWORD-EXTRACT] Error: {e}")
        
        return keywords
    
    def _keyword_exists_in_cv(self, keyword: str, cv_keywords: set) -> bool:
        """
        Check if keyword exists in CV with comprehensive fuzzy matching
        Handles: variations, partial matches, multi-word keywords, synonyms
        """
        keyword_lower = keyword.lower().strip()
        
        # 1. Exact match
        if keyword_lower in cv_keywords:
            return True
        
        # 2. Partial match (keyword in CV phrase or vice versa)
        for cv_kw in cv_keywords:
            # Keyword is part of CV phrase
            if keyword_lower in cv_kw and len(keyword_lower) > 3:
                return True
            
            # CV phrase is part of keyword
            if cv_kw in keyword_lower and len(cv_kw) > 3:
                return True
        
        # 3. Word-by-word match for multi-word keywords
        keyword_words = set(keyword_lower.split())
        if len(keyword_words) > 1:
            # Check if all words of the keyword exist in CV
            matches = sum(1 for word in keyword_words if any(word in cv_kw for cv_kw in cv_keywords))
            if matches == len(keyword_words):
                return True
        
        # 4. Common variations and synonyms
        variations = {
            "communication": ["communicate", "communicating", "communicated", "communications"],
            "analysis": ["analyze", "analyzing", "analyzed", "analytical", "analyst"],
            "management": ["manage", "managing", "managed", "manager"],
            "leadership": ["lead", "leading", "leader", "led"],
            "python": ["python programming", "python development", "py"],
            "sql": ["mysql", "postgresql", "sql server", "t-sql", "structured query language"],
            "excel": ["microsoft excel", "ms excel", "spreadsheet", "spreadsheets"],
            "power bi": ["powerbi", "power-bi", "power bi dashboard"],
            "data analysis": ["data analytics", "analyzing data", "data analyst"],
            "business processes": ["business process", "process improvement", "process optimization"],
            "problem solving": ["problem-solving", "solving problems", "troubleshooting"],
            "teamwork": ["team collaboration", "collaborative", "team player"],
            "analytical skills": ["analytical", "analysis", "analyzing"],
        }
        
        for base, vars in variations.items():
            if base in keyword_lower:
                for var in vars:
                    if any(var in cv_kw for cv_kw in cv_keywords):
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
