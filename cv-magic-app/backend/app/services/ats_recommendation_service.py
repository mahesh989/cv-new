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
            logger.info(f"🔍 [INPUT_RECOMMENDATION] Starting extraction for {company}")
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
            
            # Debug: Log match summary
            technical_match = match_summary.get("by_category", {}).get("technical", {})
            soft_match = match_summary.get("by_category", {}).get("soft", {})
            domain_match = match_summary.get("by_category", {}).get("domain", {})
            logger.info(f"📊 [INPUT_RECOMMENDATION] Match Summary:")
            logger.info(f"   - Overall match rate: {match_summary.get('overall_match_rate', 0)}%")
            logger.info(f"   - Technical: {len(technical_match.get('matched', []))} matched, {len(technical_match.get('missing', []))} missing")
            logger.info(f"   - Soft: {len(soft_match.get('matched', []))} matched, {len(soft_match.get('missing', []))} missing")
            logger.info(f"   - Domain: {len(domain_match.get('matched', []))} matched, {len(domain_match.get('missing', []))} missing")
            
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
            
            # Debug: Log keyword classification
            keyword_guidance = recommendation_data.get("keyword_integration_guidance", {})
            logger.info(f"🔍 [INPUT_RECOMMENDATION] Keyword Classification:")
            logger.info(f"   - Tier 1 (always add): Technical={len(keyword_guidance.get('tier1_always_add', {}).get('technical', []))}, Soft={len(keyword_guidance.get('tier1_always_add', {}).get('soft', []))}")
            logger.info(f"   - Tier 2 (with evidence): Technical={len(keyword_guidance.get('tier2_add_if_evidence', {}).get('technical', []))}, Soft={len(keyword_guidance.get('tier2_add_if_evidence', {}).get('soft', []))}")
            logger.info(f"   - Tier 3 (never add): Technical={len(keyword_guidance.get('tier3_never_add', {}).get('technical', []))}, Domain={len(keyword_guidance.get('tier3_never_add', {}).get('domain', []))}")
            logger.info(f"   - Already in CV (filtered): {len(keyword_guidance.get('already_in_cv_filtered', []))}")
            
            # Debug: Log final recommendation data summary
            missing_counts = ats_scoring.get("missing_counts", {})
            logger.info(f"✅ [INPUT_RECOMMENDATION] Created recommendation data:")
            logger.info(f"   - ATS Score: {ats_scoring.get('final_score', 0)}")
            logger.info(f"   - Missing counts: Technical={missing_counts.get('technical', 0)}, Soft={missing_counts.get('soft', 0)}, Domain={missing_counts.get('domain', 0)}")
            
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
    
    def create_recommendation_file(self, company: str) -> bool:
        """
        Create ATS recommendation file for the company (convenience method for pipeline)
        
        Args:
            company: Company name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📊 [ATS_RECOMMENDATION] Creating recommendation file for {company}")
            
            # Extract recommendation data
            recommendation_data = self.extract_ats_recommendation_data(company)
            
            if not recommendation_data:
                logger.warning(f"⚠️ [ATS_RECOMMENDATION] No data extracted for {company}")
                return False
            
            # Save the recommendation file
            output_file = self.save_optimized_recommendation(company, recommendation_data)
            
            if output_file:
                logger.info(f"✅ [ATS_RECOMMENDATION] Successfully created recommendation file for {company}")
                return True
            else:
                logger.error(f"❌ [ATS_RECOMMENDATION] Failed to save recommendation file for {company}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [ATS_RECOMMENDATION] Error creating recommendation file for {company}: {e}")
            return False
    
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
        """
        Extract clean match summary from preextracted comparison entries
        
        FIXED: Now handles both "→ Found in CV:" and legacy "CV Has:" formats
        """
        if not preextracted_entries:
            return {
                "overall_match_rate": 0,
                "by_category": {
                    "technical": {"matched": [], "missing": [], "match_rate": 0},
                    "soft": {"matched": [], "missing": [], "match_rate": 0},
                    "domain": {"matched": [], "missing": [], "match_rate": 0}
                },
                "missing_keywords": {
                    "technical": [],
                    "soft": [],
                    "domain": []
                }
            }
        
        latest_entry = preextracted_entries[-1]
        content = latest_entry.get("content", "")
        
        # Initialize structure
        match_summary = {
            "overall_match_rate": 0,
            "by_category": {
                "technical": {"matched": [], "missing": [], "match_rate": 0},
                "soft": {"matched": [], "missing": [], "match_rate": 0},
                "domain": {"matched": [], "missing": [], "match_rate": 0}
            },
            "missing_keywords": {
                "technical": [],
                "soft": [],
                "domain": []
            }
        }
        
        # Extract overall match rate
        for line in content.split("\n"):
            if "Match Rate:" in line:
                try:
                    rate_str = line.split("Match Rate:")[1].strip().replace("%", "")
                    match_summary["overall_match_rate"] = float(rate_str)
                    break
                except (IndexError, ValueError):
                    pass
        
        # Parse by category
        current_category = None
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            
            # Detect category sections (case-insensitive with emoji support)
            if "TECHNICAL SKILLS" in line_upper or "TECHNICAL SKILL" in line_upper:
                current_category = "technical"
                logger.info(f"📊 [MATCH_SUMMARY] Detected technical section")
                continue
            elif "SOFT SKILLS" in line_upper or "SOFT SKILL" in line_upper:
                current_category = "soft"
                logger.info(f"📊 [MATCH_SUMMARY] Detected soft section")
                continue
            elif "DOMAIN KEYWORDS" in line_upper or "DOMAIN KEYWORD" in line_upper:
                current_category = "domain"
                logger.info(f"📊 [MATCH_SUMMARY] Detected domain section")
                continue
            
            if not current_category:
                continue
            
            # ✅ FIX: Extract matched skills - handle BOTH formats
            # Format 1 (current): "→ Found in CV: 'skill'"
            # Format 2 (legacy): "CV Has: 'skill'"
            if ("→ Found in CV:" in line or 
                "Found in CV:" in line or 
                "CV Has:" in line or 
                "CV has:" in line):
                try:
                    # Extract skill from quotes
                    if "'" in line:
                        parts = line.split("'")
                        if len(parts) >= 2:
                            skill = parts[1].strip()
                            if skill and skill not in match_summary["by_category"][current_category]["matched"]:
                                match_summary["by_category"][current_category]["matched"].append(skill)
                                logger.info(f"   ✅ Matched {current_category}: {skill}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Error extracting matched skill: {e}")
            
            # Extract missing skills - handle both formats
            # "JD Required:" appears in matched section
            # "JD Requires:" appears in missing section
            if ("JD Requires:" in line or "JD Required:" in line):
                try:
                    # Extract skill from quotes
                    if "'" in line:
                        parts = line.split("'")
                        if len(parts) >= 2:
                            skill = parts[1].strip()
                            
                            # Only add to missing if it's NOT in the matched section
                            # Check if this is in a "MISSING FROM CV" section
                            # Look back a few lines to see if we're in missing section
                            in_missing_section = False
                            for j in range(max(0, i-5), i):
                                if "MISSING FROM CV" in lines[j].upper() or "❌" in lines[j]:
                                    in_missing_section = True
                                    break
                            
                            # If we're in missing section OR skill not in matched, add to missing
                            if in_missing_section or skill not in match_summary["by_category"][current_category]["matched"]:
                                if skill and skill not in match_summary["by_category"][current_category]["missing"]:
                                    match_summary["by_category"][current_category]["missing"].append(skill)
                                    logger.info(f"   ❌ Missing {current_category}: {skill}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Error extracting missing skill: {e}")
        
        # Calculate match rates per category
        for category in ["technical", "soft", "domain"]:
            matched_count = len(match_summary["by_category"][category]["matched"])
            missing_count = len(match_summary["by_category"][category]["missing"])
            total = matched_count + missing_count
            
            if total > 0:
                match_rate = (matched_count / total) * 100
                match_summary["by_category"][category]["match_rate"] = round(match_rate, 2)
            
            # Add to missing_keywords summary
            match_summary["missing_keywords"][category] = match_summary["by_category"][category]["missing"].copy()
            
            # Debug logging
            logger.info(f"📊 [MATCH_SUMMARY] {category.capitalize()} summary:")
            logger.info(f"   Matched: {matched_count} skills")
            logger.info(f"   Missing: {missing_count} skills")
            logger.info(f"   Match rate: {match_summary['by_category'][category]['match_rate']}%")
        
        return match_summary
    
    def _extract_component_summary(self, component_entries: List[Dict]) -> Dict[str, Any]:
        """Extract structured component summary aligned with prompt expectations"""
        
        def _to_float(value: Any) -> float:
            try:
                if value is None:
                    return 0.0
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        if not component_entries:
            return {
                "technical": {"score": 0.0, "core_match": 0.0, "stack_fit": 0.0, "strengths": [], "gaps": []},
                "skills": {"score": 0.0, "business_readiness": 0.0, "strengths": [], "gaps": []},
                "experience": {
                    "alignment_score": 0.0,
                    "years": 0.0,
                    "corporate_years": 0.0,
                    "jd_required_years": 0.0,
                    "cv_role_level": "Unknown",
                    "jd_role_level": "Unknown",
                    "strengths": [],
                    "gaps": []
                },
                "seniority": {
                    "score": 0.0,
                    "cv_level": "Unknown",
                    "jd_level": "Unknown",
                    "experience_match_percentage": 0.0,
                    "responsibility_fit": 0.0
                },
                "industry": {
                    "alignment_score": 0.0,
                    "cv_industry": "Unknown",
                    "jd_industry": "Unknown",
                    "transition_difficulty": "UNKNOWN",
                    "domain_overlap_percentage": 0.0,
                    "stakeholder_fit_score": 0.0
                },
                "raw_scores": {}
            }
        
        latest_entry = component_entries[-1]
        component_analyses = latest_entry.get("component_analyses", {})
        extracted_scores = latest_entry.get("extracted_scores", {})
        
        technical_analysis = component_analyses.get("technical", {}).get("technical_analysis", {})
        skills_analysis = component_analyses.get("skills", {})
        experience_analysis = component_analyses.get("experience", {}).get("experience_analysis", {})
        seniority_analysis = component_analyses.get("seniority", {}).get("seniority_analysis", {})
        industry_analysis = component_analyses.get("industry", {}).get("industry_analysis", {})
        
        summary = {
            "technical": {
                "score": _to_float(technical_analysis.get("technical_depth_score", extracted_scores.get("technical_depth"))),
                "core_match": _to_float(technical_analysis.get("core_skills_match_percentage", extracted_scores.get("core_skills_match_percentage"))),
                "stack_fit": _to_float(technical_analysis.get("technical_stack_fit_percentage", extracted_scores.get("technical_stack_fit_percentage"))),
                "strengths": technical_analysis.get("technical_strengths", []),
                "gaps": technical_analysis.get("technical_gaps", [])
            },
            "skills": {
                "score": _to_float(skills_analysis.get("overall_skills_score", extracted_scores.get("skills_relevance"))),
                "business_readiness": _to_float(skills_analysis.get("business_readiness_score", extracted_scores.get("business_readiness"))),
                "strengths": skills_analysis.get("strength_areas", []),
                "gaps": skills_analysis.get("critical_gaps", [])
            },
            "experience": {
                "alignment_score": _to_float(experience_analysis.get("alignment_score", extracted_scores.get("experience_alignment"))),
                "years": _to_float(experience_analysis.get("cv_experience_years", 0)),
                "corporate_years": _to_float(experience_analysis.get("cv_corporate_years", 0)),
                "jd_required_years": _to_float(experience_analysis.get("jd_required_years", 0)),
                "cv_role_level": experience_analysis.get("cv_role_level", "Unknown"),
                "jd_role_level": experience_analysis.get("jd_role_level", "Unknown"),
                "strengths": experience_analysis.get("experience_strengths", []),
                "gaps": experience_analysis.get("experience_gaps", [])
            },
            "seniority": {
                "score": _to_float(seniority_analysis.get("seniority_score", extracted_scores.get("seniority_match"))),
                "cv_level": seniority_analysis.get("cv_responsibility_scope", "Unknown"),
                "jd_level": seniority_analysis.get("jd_required_seniority", "Unknown"),
                "experience_match_percentage": _to_float(seniority_analysis.get("experience_match_percentage", extracted_scores.get("experience_match_percentage"))),
                "responsibility_fit": _to_float(seniority_analysis.get("responsibility_fit_percentage", extracted_scores.get("responsibility_fit_percentage")))
            },
            "industry": {
                "alignment_score": _to_float(industry_analysis.get("industry_alignment_score", extracted_scores.get("industry_fit"))),
                "cv_industry": industry_analysis.get("cv_primary_industry", "Unknown"),
                "jd_industry": industry_analysis.get("jd_target_industry", "Unknown"),
                "transition_difficulty": industry_analysis.get("transition_type", industry_analysis.get("hiring_risk_assessment", "UNKNOWN")),
                "domain_overlap_percentage": _to_float(industry_analysis.get("domain_overlap_percentage", extracted_scores.get("domain_overlap_percentage"))),
                "stakeholder_fit_score": _to_float(industry_analysis.get("stakeholder_fit_score", extracted_scores.get("stakeholder_fit_score")))
            },
            "raw_scores": extracted_scores
        }
        
        return summary
    
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
