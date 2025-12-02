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
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from app.utils.timestamp_utils import TimestampUtils

# Try to import NLTK for stemming (optional - graceful fallback if not available)
try:
    from nltk.stem import PorterStemmer
    # Download NLTK data if needed (only required once)
    try:
        import nltk
        nltk.download('punkt', quiet=True)
    except Exception:
        pass  # Data might already be downloaded
    NLTK_AVAILABLE = True
    stemmer = PorterStemmer()
except ImportError:
    NLTK_AVAILABLE = False
    stemmer = None
    logging.warning("⚠️ [ATS_RECOMMENDATION] NLTK not available - stemming disabled. Install with: pip install nltk")

logger = logging.getLogger(__name__)


class ATSRecommendationService:
    """Service for creating optimized AI recommendation input files"""
    
    def __init__(self, user_email: str):
        from app.utils.user_path_utils import get_user_base_path
        self.user_email = user_email
        self.base_dir = get_user_base_path(user_email)
    
    # ==================== SCHEMA V3.0 HELPER METHODS ====================
    
    def _get_schema_version(self) -> str:
        """Get current schema version"""
        return "3.0"
    
    def _build_keyword_with_context(
        self,
        keyword: str,
        category: str,
        priority: str,
        cv_content: Dict,
        cv_skills: Dict
    ) -> Dict:
        """
        Build a keyword entry with strategic context
        
        Returns:
            {
                "keyword": str,
                "priority": "critical" | "important" | "optional",
                "reasoning": str,
                "cv_evidence": str | None,
                "evidence_strength": "strong" | "moderate" | "weak" | "none",
                "integration_hints": List[str],
                "risk": "low" | "medium" | "high"
            }
        """
        keyword_lower = keyword.lower()
        
        # Check for evidence in CV content
        cv_text = " ".join(cv_content.get('experience_bullets', []))
        cv_text += " " + cv_content.get('skills_section', '')
        
        evidence = None
        evidence_strength = "none"
        
        # Direct mention
        if keyword_lower in cv_text.lower():
            evidence = f"Explicitly mentioned: '{keyword}'"
            evidence_strength = "strong"
        else:
            # Semantic evidence
            semantic_match = self._find_semantic_evidence(keyword_lower, cv_text, cv_skills)
            if semantic_match:
                evidence = semantic_match
                evidence_strength = "moderate"
        
        # Determine integration hints based on category and evidence
        integration_hints = []
        if category == "technical":
            integration_hints = ["skills section"]
            if evidence_strength in ["strong", "moderate"]:
                integration_hints.append("relevant experience bullets")
        elif category == "soft":
            integration_hints = ["skills section"]
            if evidence_strength in ["strong", "moderate"]:
                integration_hints.append("leadership/collaboration bullets")
        elif category == "domain":
            if evidence_strength in ["strong", "moderate"]:
                integration_hints = ["summary", "industry-specific bullets"]
        
        # Determine risk level
        if evidence_strength == "strong":
            risk = "low"
        elif evidence_strength == "moderate":
            risk = "medium"
        else:
            risk = "high" if category == "domain" else "medium"
        
        # Generate reasoning
        reasoning = self._generate_keyword_reasoning(keyword, category, evidence_strength)
        
        return {
            "keyword": keyword,
            "priority": priority,
            "reasoning": reasoning,
            "cv_evidence": evidence,
            "evidence_strength": evidence_strength,
            "integration_hints": integration_hints,
            "risk": risk
        }
    
    def _find_semantic_evidence(self, keyword: str, cv_text: str, cv_skills: Dict) -> Optional[str]:
        """Find semantic evidence for a keyword in CV text"""
        # Synonym mapping
        synonyms = {
            "excel": ["spreadsheet", "data analysis", "pivot table", "vlookup"],
            "data cleaning": ["data preparation", "data accuracy", "data quality", "improving accuracy"],
            "data mining": ["data analysis", "pattern recognition", "insight extraction"],
            "data transformation": ["data processing", "etl", "data pipeline"],
            "data visualization": ["dashboard", "chart", "graph", "visual report"],
            "statistical methods": ["statistical analysis", "statistics", "quantitative analysis"],
            "collaboration": ["team", "cross-functional", "worked with", "stakeholder"],
            "communication": ["presented", "reporting", "stakeholder", "client interaction"],
            "presentation skills": ["presented", "dashboard", "reporting", "stakeholder communication"],
            "interpersonal skill": ["collaboration", "team", "stakeholder", "client"],
            "mssql": ["sql", "database", "query"],
            "dashboard development": ["dashboard", "power bi", "tableau", "visualization"],
        }
        
        cv_text_lower = cv_text.lower()
        
        for synonym in synonyms.get(keyword.lower(), []):
            if synonym in cv_text_lower:
                return f"Implied by: '{synonym}'"
        
        # Check related skills
        for skill in cv_skills.get("technical_skills", []):
            if keyword.lower() in skill.lower() or skill.lower() in keyword.lower():
                return f"Related skill: '{skill}'"
        
        return None
    
    def _generate_keyword_reasoning(self, keyword: str, category: str, evidence_strength: str) -> str:
        """Generate reasoning for why this keyword should be added"""
        if evidence_strength == "strong":
            return f"Already demonstrated in CV, needs explicit mention"
        elif evidence_strength == "moderate":
            return f"Semantic evidence exists in CV, safe to integrate"
        elif category == "soft":
            return f"Universal soft skill, transferable across roles"
        elif category == "technical":
            return f"Required by JD, add if verifiable experience exists"
        else:
            return f"JD requirement, assess evidence before adding"
    
    def _build_evidence_index(self, cv_content: Dict) -> Dict:
        """Build lightweight evidence index instead of full CV content"""
        experience_bullets = cv_content.get('experience_bullets', [])
        skills_section = cv_content.get('skills_section', '')
        skills_lower = skills_section.lower()
        bullets_text = " ".join(experience_bullets).lower()
        
        return {
            "experience_bullets_count": len(experience_bullets),
            "has_power_bi": "power bi" in skills_lower,
            "has_sql": "sql" in skills_lower,
            "has_python": "python" in skills_lower,
            "has_excel": "excel" in skills_lower,
            "has_dashboards": "dashboard" in bullets_text,
            "has_data_analysis": "data analysis" in bullets_text or "analyzed" in bullets_text,
            "quantified_achievements": sum(1 for bullet in experience_bullets if '%' in bullet),
            "projects_count": len(cv_content.get('technical_projects', [])),
            "certifications_count": len(cv_content.get('certifications', []))
        }
    
    def _build_jd_context_summary(self, jd_content: Dict) -> Dict:
        """Build lightweight JD summary instead of full content"""
        responsibilities = jd_content.get('key_responsibilities', [])
        
        return {
            "role_title": jd_content.get('role_title', 'N/A'),
            "role_level": jd_content.get('role_level', 'Unknown'),
            "key_focus": responsibilities[:4] if len(responsibilities) > 4 else responsibilities,
            "required_background": self._extract_background_summary(jd_content.get('context', '')),
            "culture": jd_content.get('department', 'N/A')
        }
    
    def _extract_background_summary(self, context: str) -> str:
        """Extract required background from context (first sentence or key phrase)"""
        if not context or context == "N/A":
            return "N/A"
        
        # Extract first sentence
        sentences = context.split('.')
        if sentences:
            return sentences[0].strip()[:150]  # Max 150 chars
        
        return context[:150]
    
    def _build_gap_analysis(
        self,
        match_summary: Dict,
        component_summary: Dict,
        ats_scoring: Dict
    ) -> Dict:
        """Build structured gap analysis with impact levels"""
        gaps = []
        
        # Technical gaps
        for skill in match_summary.get("by_category", {}).get("technical", {}).get("missing", []):
            impact = self._determine_gap_impact(skill, "technical", component_summary)
            gaps.append({
                "skill": skill,
                "category": "technical",
                "impact": impact,
                "mitigation": self._suggest_mitigation(skill, "technical")
            })
        
        # Soft skill gaps
        for skill in match_summary.get("by_category", {}).get("soft", {}).get("missing", []):
            impact = self._determine_gap_impact(skill, "soft", component_summary)
            gaps.append({
                "skill": skill,
                "category": "soft",
                "impact": impact,
                "mitigation": self._suggest_mitigation(skill, "soft")
            })
        
        # Domain gaps
        for skill in match_summary.get("by_category", {}).get("domain", {}).get("missing", []):
            gaps.append({
                "skill": skill,
                "category": "domain",
                "impact": "low",  # Domain gaps usually low impact for transferable roles
                "mitigation": "Emphasize adaptability and quick learning"
            })
        
        # Calculate summary
        summary = {
            "critical": len([g for g in gaps if g["impact"] == "critical"]),
            "high": len([g for g in gaps if g["impact"] == "high"]),
            "medium": len([g for g in gaps if g["impact"] == "medium"]),
            "low": len([g for g in gaps if g["impact"] == "low"]),
            "by_category": {
                "technical": len([g for g in gaps if g["category"] == "technical"]),
                "soft": len([g for g in gaps if g["category"] == "soft"]),
                "domain": len([g for g in gaps if g["category"] == "domain"])
            }
        }
        
        return {
            "gaps": gaps,
            "summary": summary
        }
    
    def _determine_gap_impact(self, skill: str, category: str, component_summary: Dict) -> str:
        """Determine impact level of a missing skill"""
        skill_lower = skill.lower()
        
        # Critical technical skills
        if category == "technical":
            critical_keywords = ["sql", "python", "excel", "power bi", "tableau"]
            if any(kw in skill_lower for kw in critical_keywords):
                return "critical"
            
            # High impact if component score is low
            tech_score = component_summary.get("technical", {}).get("score", 0)
            if tech_score < 60:
                return "high"
            
            return "medium"
        
        # Soft skills generally medium-low impact
        if category == "soft":
            return "medium"
        
        return "low"
    
    def _suggest_mitigation(self, skill: str, category: str) -> str:
        """Suggest mitigation strategy for a gap"""
        skill_lower = skill.lower()
        
        if "excel" in skill_lower:
            return "Add to skills section with proficiency level (e.g., 'Advanced Excel')"
        elif "sql" in skill_lower:
            return "Mention SQL variant experience if applicable"
        elif category == "soft":
            return f"Highlight in skills section and demonstrate through experience bullets"
        else:
            return f"Add to relevant section if verifiable experience exists"
    
    def _build_ats_quick_wins(self, ats_scoring: Dict, match_summary: Dict, keyword_strategy: Dict) -> List[Dict]:
        """Build actionable quick wins for ATS improvement"""
        quick_wins = []
        
        current_score = ats_scoring.get("final_score", 0)
        target_score = ats_scoring.get("target_score", 75.0)
        gap = target_score - current_score
        
        # Quick win 1: Add Tier 1 keywords
        tier1_count = sum(
            len(keyword_strategy.get("tier1_immediate", {}).get(cat, []))
            for cat in ["technical", "soft", "domain"]
        )
        if tier1_count > 0:
            quick_wins.append({
                "action": f"Add all {tier1_count} Tier 1 keywords to appropriate sections",
                "expected_gain": round(min(tier1_count * 1.5, gap * 0.3), 1),
                "effort": "low"
            })
        
        # Quick win 2: Enhance matched keywords
        matched_count = len(match_summary.get("by_category", {}).get("technical", {}).get("matched", []))
        if matched_count > 0:
            quick_wins.append({
                "action": f"Enhance {matched_count} already-matched keywords in experience bullets",
                "expected_gain": round(min(matched_count * 0.8, gap * 0.25), 1),
                "effort": "low"
            })
        
        # Quick win 3: Add Tier 2 with strong evidence
        tier2_strong = [
            kw for kw in keyword_strategy.get("tier2_conditional", {}).get("technical", [])
            if isinstance(kw, dict) and kw.get("evidence_strength") == "strong"
        ]
        if tier2_strong:
            quick_wins.append({
                "action": f"Add {len(tier2_strong)} Tier 2 keywords with strong evidence",
                "expected_gain": round(min(len(tier2_strong) * 1.2, gap * 0.2), 1),
                "effort": "medium"
            })
        
        return quick_wins
    
    def _extract_top_strengths(self, component_summary: Dict, limit: int = 3) -> List[str]:
        """Extract top strengths from component summary"""
        strengths = []
        
        # Technical strengths
        tech_strengths = component_summary.get("technical", {}).get("strengths", [])
        strengths.extend(tech_strengths[:limit])
        
        # Skills strengths
        if len(strengths) < limit:
            skills_strengths = component_summary.get("skills", {}).get("strengths", [])
            remaining = limit - len(strengths)
            strengths.extend(skills_strengths[:remaining])
        
        # Experience strengths
        if len(strengths) < limit:
            exp_strengths = component_summary.get("experience", {}).get("strengths", [])
            remaining = limit - len(strengths)
            strengths.extend(exp_strengths[:remaining])
        
        return strengths[:limit]
    
    def _identify_risk_factors(self, component_summary: Dict, match_summary: Dict) -> List[str]:
        """Identify risk factors from component analysis"""
        risks = []
        
        # Industry transition risk
        industry = component_summary.get("industry", {})
        if industry.get("transition_difficulty") in ["Moderate", "High", "UNKNOWN"]:
            risks.append(
                f"Industry transition: {industry.get('cv_industry', 'Unknown')} → "
                f"{industry.get('jd_industry', 'Unknown')}"
            )
        
        # Seniority mismatch risk
        seniority = component_summary.get("seniority", {})
        if seniority.get("score", 0) < 60:
            risks.append(
                f"Seniority gap: CV level '{seniority.get('cv_level', 'Unknown')}' vs "
                f"JD level '{seniority.get('jd_level', 'Unknown')}'"
            )
        
        # Technical gap risk
        technical = component_summary.get("technical", {})
        if technical.get("score", 0) < 65:
            missing_count = len(match_summary.get("by_category", {}).get("technical", {}).get("missing", []))
            risks.append(f"Technical skills gap: {missing_count} missing skills")
        
        return risks
    
    def _generate_positioning_strategy(self, component_summary: Dict, jd_context: Dict) -> str:
        """Generate positioning strategy based on CV-JD analysis"""
        industry = component_summary.get("industry", {})
        technical = component_summary.get("technical", {})
        
        cv_industry = industry.get("cv_industry", "Unknown")
        jd_industry = jd_context.get("culture", "Unknown")
        tech_score = technical.get("score", 0)
        
        if tech_score >= 75:
            return (
                f"Emphasize strong technical foundation ({tech_score:.0f}/100) and transferable "
                f"analytical skills. Frame {cv_industry} experience as relevant to {jd_industry} context."
            )
        else:
            return (
                f"Highlight transferable skills and quick learning ability. Position "
                f"{cv_industry} background as bringing fresh perspective to {jd_industry}."
            )
    
    def _build_keyword_strategy_v3(
        self,
        missing_keywords: Dict[str, List[str]],
        cv_content: Dict,
        cv_skills: Dict,
        jd_content: Dict
    ) -> Dict:
        """
        Build keyword strategy v3.0 with strategic context
        REPLACES: _classify_keywords_optimized for v3.0 schema
        """
        # Get existing keywords (for filtering)
        existing_keywords_lower = self._extract_existing_cv_keywords()
        
        # Filter missing keywords
        filtered_missing = {}
        already_present = {}
        
        for category, keywords in missing_keywords.items():
            filtered_missing[category] = []
            already_present[category] = []
            
            for keyword in keywords:
                if self._keyword_exists_in_cv(keyword.lower(), existing_keywords_lower):
                    already_present[category].append(keyword)
                else:
                    filtered_missing[category].append(keyword)
        
        # Log filtering
        total_filtered = sum(len(kws) for kws in filtered_missing.values())
        total_already = sum(len(kws) for kws in already_present.values())
        logger.info(f"🔍 [KEYWORD_FILTER v3.0] {total_filtered} new keywords, {total_already} already in CV")
        
        # Classify into tiers WITH CONTEXT
        strategy = {
            "tier1_immediate": {"technical": [], "soft": [], "domain": []},
            "tier2_conditional": {"technical": [], "soft": [], "domain": []},
            "tier3_avoid": {"technical": [], "soft": [], "domain": []},
            "already_strong": list(set([kw for kws in already_present.values() for kw in kws]))
        }
        
        # Tier 1 patterns (generic/transferable)
        tier1_patterns = {
            "soft": ["communication", "collaboration", "teamwork", "problem solving",
                    "analytical thinking", "attention to detail", "interpersonal",
                    "presentation", "time management", "adaptability", "numeracy", "proactive"],
            "technical": ["data analysis", "data visualization", "reporting",
                         "dashboard development", "business intelligence"]
        }
        
        # Tier 3 patterns (domain-specific/unverifiable)
        tier3_patterns = {
            "domain": ["food relief", "charity", "non-profit", "humanitarian",
                      "fundraising", "volunteer", "donor", "nfp", "not for profit"],
            "certifications": ["pmp", "scrum master", "aws certified", "cissp"]
        }
        
        for category in ["technical", "soft", "domain"]:
            for keyword in filtered_missing.get(category, []):
                keyword_lower = keyword.lower()
                
                # Check Tier 1
                is_tier1 = any(pattern in keyword_lower for pattern in tier1_patterns.get(category, []))
                
                if is_tier1:
                    priority = "important" if category == "soft" else "critical"
                    kw_context = self._build_keyword_with_context(
                        keyword, category, priority, cv_content, cv_skills
                    )
                    strategy["tier1_immediate"][category].append(kw_context)
                    continue
                
                # Check Tier 3
                is_tier3 = any(
                    pattern in keyword_lower 
                    for pattern in tier3_patterns.get("domain", []) + tier3_patterns.get("certifications", [])
                )
                
                if is_tier3:
                    strategy["tier3_avoid"][category].append({
                        "keyword": keyword,
                        "reasoning": "Domain-specific or certification without CV evidence",
                        "risk": "high",
                        "alternative": "Emphasize adaptability and transferable skills"
                    })
                    continue
                
                # Default: Tier 2
                priority = "critical" if category == "technical" else "optional"
                kw_context = self._build_keyword_with_context(
                    keyword, category, priority, cv_content, cv_skills
                )
                kw_context["require_validation"] = True
                strategy["tier2_conditional"][category].append(kw_context)
        
        return strategy
    
    # ==================== END SCHEMA V3.0 HELPER METHODS ====================
    
    def extract_ats_recommendation_data(self, company: str) -> Optional[Dict[str, Any]]:
        """
        Extract and optimize recommendation data from skills analysis file
        SCHEMA v3.0: Streamlined structure with strategic context
        
        Args:
            company: Company name
            
        Returns:
            Optimized dictionary for AI consumption or None if not found
        """
        try:
            logger.info("=" * 80)
            logger.info(f"🔍 [INPUT_OPTIMIZATION v3.0] Starting input file generation for {company}")
            logger.info("=" * 80)
            
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
            
            # ⭐ Prefer three_section_skills from jd_analysis if available, otherwise use saved jd_skills
            jd_analysis = analysis_data.get("jd_analysis", {})
            jd_skills = {}
            if jd_analysis and isinstance(jd_analysis, dict):
                three_section = jd_analysis.get("three_section_skills")
                if three_section:
                    # Populate jd_skills from three_section_skills (map domain_knowledge -> domain_keywords)
                    jd_skills = {
                        "technical_skills": three_section.get("technical_skills", []),
                        "soft_skills": three_section.get("soft_skills", []),
                        "domain_keywords": three_section.get("domain_knowledge", []),  # Map domain_knowledge to domain_keywords
                    }
                    logger.info("✅ [ATS_RECOMMENDATION] Using jd_skills from three_section_skills")
                else:
                    jd_skills = analysis_data.get("jd_skills", {})
            else:
                jd_skills = analysis_data.get("jd_skills", {})
            
            match_entries = analysis_data.get("analyze_match_entries", [])
            preextracted_entries = analysis_data.get("preextracted_comparison_entries", [])
            component_entries = analysis_data.get("component_analysis_entries", [])
            ats_entries = analysis_data.get("ats_calculation_entries", [])
            
            # Parse components
            preliminary_decision = self._extract_preliminary_decision(match_entries)
            match_summary = self._extract_match_summary(preextracted_entries)
            component_summary_optimized = self._extract_component_summary_optimized(component_entries)
            ats_scoring = self._extract_ats_scoring(ats_entries)
            cv_content = self._extract_cv_content(company)
            jd_content = self._extract_jd_content(company)
            
            # Log what sections are in the original analysis file
            logger.info(f"📂 [INPUT_OPTIMIZATION v3.0] Original analysis file sections:")
            logger.info(f"   - cv_skills: {'✅' if cv_skills else '❌'}")
            logger.info(f"   - jd_skills: {'✅' if jd_skills else '❌'}")
            logger.info(f"   - match_entries: {len(match_entries)} entries")
            logger.info(f"   - preextracted_entries: {len(preextracted_entries)} entries")
            logger.info(f"   - component_entries: {len(component_entries)} entries")
            logger.info(f"   - ats_entries: {len(ats_entries)} entries")
            
            # Debug: Log match summary
            technical_match = match_summary.get("by_category", {}).get("technical", {})
            soft_match = match_summary.get("by_category", {}).get("soft", {})
            domain_match = match_summary.get("by_category", {}).get("domain", {})
            logger.info(f"📊 [INPUT_RECOMMENDATION v3.0] Match Summary:")
            logger.info(f"   - Overall match rate: {match_summary.get('overall_match_rate', 0)}%")
            logger.info(f"   - Technical: {len(technical_match.get('matched', []))} matched, {len(technical_match.get('missing', []))} missing")
            logger.info(f"   - Soft: {len(soft_match.get('matched', []))} matched, {len(soft_match.get('missing', []))} missing")
            logger.info(f"   - Domain: {len(domain_match.get('matched', []))} matched, {len(domain_match.get('missing', []))} missing")
            
            # ==================== NEW v3.0 STRUCTURE ====================
            
            # Build keyword strategy with context (REPLACES _classify_keywords_optimized)
            keyword_strategy = self._build_keyword_strategy_v3(
                match_summary.get("missing_keywords", {}),
                cv_content,
                cv_skills,
                jd_content
            )
            
            # Build gap analysis
            gap_analysis = self._build_gap_analysis(
                match_summary,
                component_summary_optimized,
                ats_scoring
            )
            
            # Build ATS quick wins
            ats_quick_wins = self._build_ats_quick_wins(
                ats_scoring,
                match_summary,
                keyword_strategy
            )
            
            # Build evidence index (lightweight CV summary)
            evidence_index = self._build_evidence_index(cv_content)
            
            # Build JD context summary (lightweight JD summary)
            jd_context_summary = self._build_jd_context_summary(jd_content)
            
            # ==================== STREAMLINED v3.0 OUTPUT ====================
            
            recommendation_data = {
                "meta": {
                    "company": company,
                    "job_title": jd_content.get('role_title', 'N/A'),
                    "generated_at": datetime.now().isoformat(),
                    "schema_version": self._get_schema_version(),
                    "iteration": 1  # TODO: Detect iteration number
                },
                
                "decision": {
                    "verdict": preliminary_decision.get("decision", "UNKNOWN"),
                    "confidence": preliminary_decision.get("confidence", 0),
                    "match_score": preliminary_decision.get("match_score", 0),
                    "reasoning": {
                        "strengths": self._extract_top_strengths(component_summary_optimized, 3),
                        "critical_gaps": preliminary_decision.get("critical_missing", []),
                        "risk_factors": self._identify_risk_factors(component_summary_optimized, match_summary)
                    },
                    "positioning_strategy": self._generate_positioning_strategy(
                        component_summary_optimized, jd_context_summary
                    )
                },
                
                "keyword_strategy": keyword_strategy,
                
                "gap_analysis": gap_analysis,
                
                "ats_intelligence": {
                    "current_score": ats_scoring.get("final_score", 0),
                    "target_score": 75.0,
                    "gap": max(0, 75.0 - ats_scoring.get("final_score", 0)),
                    "breakdown": {
                        "keyword_match": ats_scoring.get("category1_keywords", 0),
                        "semantic_match": ats_scoring.get("category2_ai_analysis", 0),
                        "formatting": 0
                    },
                    "quick_wins": ats_quick_wins,
                    "improvement_path": {
                        "phase1": f"Quick wins ({min(15, ats_scoring.get('improvement_needed', 0) * 0.6):.0f}-20 points)",
                        "phase2": "Evidence-based additions (5-10 points)",
                        "phase3": "Experience reframing (5 points)"
                    }
                },
                
                "component_scores": component_summary_optimized,
                
                "evidence_index": evidence_index,
                
                "jd_context_summary": jd_context_summary
            }
            
            # ==================== LOGGING ====================
            
            total_size = sys.getsizeof(json.dumps(recommendation_data))
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("📊 [INPUT_OPTIMIZATION v3.0] Summary:")
            logger.info(f"   Schema version: {self._get_schema_version()}")
            logger.info(f"   Total sections: {len(recommendation_data.keys())}")
            logger.info(f"   File size: ~{total_size} bytes ({total_size / 1024:.2f} KB)")
            logger.info("")
            logger.info("📦 [v3.0] REMOVED redundancies:")
            logger.info(f"   ❌ match_summary.missing_keywords (now in keyword_strategy)")
            logger.info(f"   ❌ cv_content full text (replaced with evidence_index: 10 fields)")
            logger.info(f"   ❌ jd_content full text (replaced with jd_context_summary: 5 fields)")
            logger.info("")
            logger.info("📦 [v3.0] ADDED strategic context:")
            logger.info(f"   ✅ keyword_strategy: {sum(len(keyword_strategy.get('tier1_immediate', {}).get(c, [])) for c in ['technical', 'soft', 'domain'])} tier1, "
                       f"{sum(len(keyword_strategy.get('tier2_conditional', {}).get(c, [])) for c in ['technical', 'soft', 'domain'])} tier2, "
                       f"{sum(len(keyword_strategy.get('tier3_avoid', {}).get(c, [])) for c in ['technical', 'soft', 'domain'])} tier3")
            logger.info(f"   ✅ gap_analysis: {gap_analysis['summary']['critical']} critical, {gap_analysis['summary']['high']} high, {gap_analysis['summary']['medium']} medium gaps")
            logger.info(f"   ✅ ats_intelligence.quick_wins: {len(ats_quick_wins)} actionable items")
            logger.info(f"   ✅ decision.positioning_strategy: strategic guidance added")
            logger.info("=" * 80)
            
            # Log keyword strategy details
            logger.info(f"🔍 [INPUT_RECOMMENDATION v3.0] Keyword Strategy:")
            for tier_name, tier_key in [("Tier 1 (immediate)", "tier1_immediate"), ("Tier 2 (conditional)", "tier2_conditional"), ("Tier 3 (avoid)", "tier3_avoid")]:
                tier_data = keyword_strategy.get(tier_key, {})
                tech_count = len(tier_data.get('technical', []))
                soft_count = len(tier_data.get('soft', []))
                domain_count = len(tier_data.get('domain', []))
                logger.info(f"   - {tier_name}: Technical={tech_count}, Soft={soft_count}, Domain={domain_count}")
            logger.info(f"   - Already strong: {len(keyword_strategy.get('already_strong', []))}")
            
            # Debug: Log final recommendation data summary
            missing_counts = ats_scoring.get("missing_counts", {})
            logger.info(f"✅ [INPUT_RECOMMENDATION v3.0] Created recommendation data:")
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
            
            # Detailed file size logging
            file_size = output_file.stat().st_size
            file_size_kb = file_size / 1024
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("💾 [INPUT_OPTIMIZATION] File saved:")
            logger.info(f"   Path: {output_file}")
            logger.info(f"   Size: {file_size} bytes ({file_size_kb:.2f} KB)")
            
            # Compare with expected optimized size
            if file_size > 6000:  # ~6KB threshold
                logger.warning(f"   ⚠️  File larger than expected (target: <6KB)")
                logger.warning(f"   💡 Check if raw_scores or skills_extraction are still included")
            else:
                logger.info(f"   ✅ File size within optimal range")
            
            # Estimate savings from optimization
            estimated_unoptimized_size = file_size * 1.5  # Rough estimate
            savings = estimated_unoptimized_size - file_size
            logger.info(f"   💰 Estimated savings: ~{savings:.0f} bytes ({savings / 1024:.2f} KB)")
            logger.info("=" * 80)
            
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
        
        # Try structured fields first (new format)
        if "decision" in latest_entry:
            decision = latest_entry.get("decision", "UNKNOWN")
            match_score = latest_entry.get("match_score", 0)
            confidence = latest_entry.get("confidence", 0)
            critical_missing = latest_entry.get("critical_missing", [])
            implicit_likely = latest_entry.get("implicit_likely", [])
            
            return {
                "decision": decision,
                "match_score": match_score,
                "confidence": confidence,
                "should_proceed": decision in ["PROCEED", "CONDITIONAL", "MAYBE"],
                "critical_missing": critical_missing if isinstance(critical_missing, list) else [],
                "implicit_likely": implicit_likely if isinstance(implicit_likely, list) else [],
                "learnable_gaps": [],
                "primary_reason": latest_entry.get("primary_reason", "")
            }
        
        # Fallback to parsing content string (legacy format)
        content = latest_entry.get("content", "")
        
        # Extract structured decision fields
        decision_match = re.search(r"DECISION:\s*(PROCEED|MAYBE|DONT_PROCEED|CONDITIONAL)", content, re.IGNORECASE)
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
        
        # Try structured fields first (new format)
        if "overall_match_rate" in latest_entry or "by_category" in latest_entry:
            match_summary = {
                "overall_match_rate": latest_entry.get("overall_match_rate", 0),
                "by_category": latest_entry.get("by_category", {
                    "technical": {"matched": [], "missing": [], "match_rate": 0},
                    "soft": {"matched": [], "missing": [], "match_rate": 0},
                    "domain": {"matched": [], "missing": [], "match_rate": 0}
                }),
                "missing_keywords": latest_entry.get("missing_keywords", {
                    "technical": [],
                    "soft": [],
                    "domain": []
                })
            }
            return match_summary
        
        # Fallback to parsing content string (legacy format)
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
        
        # FIXED: Deduplicate - remove keywords from missing if they're already in matched
        # This prevents duplicates like "Power BI" appearing in both matched and missing
        for category in ["technical", "soft", "domain"]:
            matched_list = match_summary["by_category"][category]["matched"]
            missing_list = match_summary["by_category"][category]["missing"]
            
            # Normalize for case-insensitive comparison
            matched_normalized = {skill.lower().strip() for skill in matched_list}
            
            # Track duplicates before removal for logging
            duplicates_found = [
                skill for skill in missing_list 
                if skill.lower().strip() in matched_normalized
            ]
            
            # Remove duplicates from missing list
            original_missing_count = len(missing_list)
            missing_list[:] = [
                skill for skill in missing_list 
                if skill.lower().strip() not in matched_normalized
            ]
            
            duplicates_removed = original_missing_count - len(missing_list)
            if duplicates_removed > 0:
                logger.warning(f"⚠️ [MATCH_SUMMARY] Removed {duplicates_removed} duplicate(s) from {category} missing list (already in matched)")
                logger.warning(f"   Duplicates removed: {duplicates_found}")
        
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
            logger.info(f"   Missing: {missing_count} skills (after deduplication)")
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
    
    def _extract_component_summary_optimized(self, component_entries: List[Dict]) -> Dict[str, Any]:
        """Extract optimized component summary with only used fields"""
        
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
                "skills": {"score": 0.0, "business_readiness": 0.0, "strengths": []},
                "experience": {
                    "alignment_score": 0.0,
                    "years": 0.0,
                    "corporate_years": 0.0,
                    "strengths": []
                },
                "seniority": {
                    "score": 0.0,
                    "cv_level": "Unknown",
                    "jd_level": "Unknown"
                },
                "industry": {
                    "alignment_score": 0.0,
                    "cv_industry": "Unknown",
                    "jd_industry": "Unknown",
                    "transition_difficulty": "UNKNOWN"
                }
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
                "strengths": skills_analysis.get("strength_areas", [])
            },
            "experience": {
                "alignment_score": _to_float(experience_analysis.get("alignment_score", extracted_scores.get("experience_alignment"))),
                "years": _to_float(experience_analysis.get("cv_experience_years", 0)),
                "corporate_years": _to_float(experience_analysis.get("cv_corporate_years", 0)),
                "strengths": experience_analysis.get("experience_strengths", [])
            },
            "seniority": {
                "score": _to_float(seniority_analysis.get("seniority_score", extracted_scores.get("seniority_match"))),
                "cv_level": seniority_analysis.get("cv_responsibility_scope", "Unknown"),
                "jd_level": seniority_analysis.get("jd_required_seniority", "Unknown")
            },
            "industry": {
                "alignment_score": _to_float(industry_analysis.get("industry_alignment_score", extracted_scores.get("industry_fit"))),
                "cv_industry": industry_analysis.get("cv_primary_industry", "Unknown"),
                "jd_industry": industry_analysis.get("jd_target_industry", "Unknown"),
                "transition_difficulty": industry_analysis.get("transition_type", industry_analysis.get("hiring_risk_assessment", "UNKNOWN"))
            }
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
    
    def _classify_keywords_optimized(self, missing_keywords: Dict[str, List[str]], 
                          cv_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Classify missing keywords into tiers based on CV tailoring framework (OPTIMIZED).
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
            "already_in_cv_filtered": list(set([kw for keywords in already_present.values() for kw in keywords]))
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
            # Handle both old format (list of dicts) and new format (dict of lists)
            skills_data = cv_data.get('skills', {})
            if isinstance(skills_data, dict):
                # New format: {"technical_skills": [...], "soft_skills": [...], ...}
                for skill_list in skills_data.values():
                    if isinstance(skill_list, list):
                        for skill in skill_list:
                            if skill:
                                keywords.add(str(skill).lower())
            elif isinstance(skills_data, list):
                # Old format: [{"skills": [...]}, ...]
                for skill_cat in skills_data:
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
    
    def _stem_keyword(self, keyword: str) -> str:
        """
        Stem a keyword using NLTK's PorterStemmer.
        
        Examples:
        - "Data Warehousing" → "data warehous"
        - "Data Warehouse" → "data warehous"
        - "analyzing" → "analyz"
        
        Returns:
            Stemmed keyword, or original keyword if NLTK unavailable
        """
        if not NLTK_AVAILABLE or not stemmer:
            return keyword.lower()
        
        try:
            words = keyword.lower().split()
            stemmed_words = [stemmer.stem(word) for word in words]
            return ' '.join(stemmed_words)
        except Exception as e:
            logger.warning(f"⚠️ [KEYWORD_FILTER] Stemming failed for '{keyword}': {e}")
            return keyword.lower()
    
    def _keyword_exists_in_cv(self, keyword: str, cv_keywords: set) -> bool:
        """
        Check if a keyword exists in CV keywords (with fuzzy matching).
        Handles variations like "python" vs "python programming", "sql" vs "structured query language".
        
        FIXED:
        - Now handles 3-character keywords like "SQL" by using >= instead of >.
        - Added stemming support for pluralization (e.g., "Data Warehouse" vs "Data Warehousing").
        """
        keyword_lower = keyword.lower()
        
        # Direct match
        if keyword_lower in cv_keywords:
            return True
        
        # NEW: Stemming-based matching for pluralization
        # Example: "Data Warehousing" (stemmed: "data warehous") matches "Data Warehouse" (stemmed: "data warehous")
        if NLTK_AVAILABLE:
            keyword_stemmed = self._stem_keyword(keyword)
            for cv_kw in cv_keywords:
                cv_kw_stemmed = self._stem_keyword(cv_kw)
                if keyword_stemmed == cv_kw_stemmed:
                    logger.debug(f"🔍 [KEYWORD_FILTER] Found '{keyword}' via stemming: '{cv_kw}' (stemmed: '{cv_kw_stemmed}' == '{keyword_stemmed}')")
                    return True
        
        # Check if keyword is part of any CV keyword (e.g., "python" in "python programming")
        # FIXED: Changed > to >= to allow 3-character keywords like "SQL"
        for cv_kw in cv_keywords:
            if keyword_lower in cv_kw or cv_kw in keyword_lower:
                # Only match if significant overlap (not just "a" in "data")
                # Now includes 3-char keywords like "SQL", "ETL", "AWS", "GCP"
                if len(keyword_lower) >= 3 or len(cv_kw) >= 3:
                    return True
        
        # Enhanced variations dict with parenthetical patterns
        variations = {
            'python': ['python programming', 'python development', 'py'],
            'sql': ['structured query language', 'mysql', 'postgresql', 'sql server', 'sql ('],
            'etl': ['extract transform load', 'data pipeline', 'etl pipeline'],
            'aws': ['amazon web services', 'amazon aws'],
            'gcp': ['google cloud platform', 'google cloud'],
            'javascript': ['js', 'javascript programming', 'node', 'nodejs'],
            'data analysis': ['data analytics', 'analyzing data', 'analytical'],
            'machine learning': ['ml', 'ai', 'artificial intelligence'],
            'project management': ['pm', 'project coordination', 'managed projects'],
        }
        
        for base, vars in variations.items():
            if keyword_lower == base or keyword_lower in vars:
                if base in cv_keywords or any(v in cv_keywords for v in vars):
                    return True
                
                # NEW: Check if any CV keyword starts with base + space or parenthesis
                # This catches "SQL (PostgreSQL, MySQL)" when looking for "SQL"
                for cv_kw in cv_keywords:
                    if cv_kw.startswith(base + ' ') or cv_kw.startswith(base + '('):
                        logger.debug(f"🔍 [KEYWORD_FILTER] Found '{keyword}' via base pattern: '{cv_kw}' starts with '{base}'")
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
    
    def _extract_cv_content(self, company: str) -> Dict:
        """Extract CV content for Tier 2 evidence checking"""
        try:
            # Try to load from latest tailored CV first, then original CV
            cv_dir = self.base_dir / "cvs"
            tailored_dir = cv_dir / "tailored"
            original_dir = cv_dir / "original"
            
            cv_data = None
            
            # Try tailored CV first
            if tailored_dir.exists():
                tailored_files = list(tailored_dir.glob("*_tailored_cv_*.json"))
                if tailored_files:
                    latest_tailored = max(tailored_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_tailored, 'r', encoding='utf-8') as f:
                        cv_data = json.load(f)
                    logger.info(f"🔍 [CV_CONTENT] Loaded tailored CV: {latest_tailored.name}")
            
            # Fallback to original CV
            if not cv_data:
                original_cv = original_dir / "original_cv.json"
                if original_cv.exists():
                    with open(original_cv, 'r', encoding='utf-8') as f:
                        cv_data = json.load(f)
                    logger.info(f"🔍 [CV_CONTENT] Loaded original CV")
            
            if not cv_data:
                logger.warning(f"⚠️ [CV_CONTENT] No CV data found")
                return {
                    "experience_bullets": [],
                    "skills_section": "",
                    "technical_projects": [],
                    "certifications": []
                }
            
            # Extract all experience bullets
            experience_bullets = []
            for exp in cv_data.get("experience", []):
                bullets = exp.get("bullets", [])
                experience_bullets.extend(bullets)
            
            # Extract skills section text
            # Handle both old format (list of dicts) and new format (dict of lists)
            skills_text = []
            skills_data = cv_data.get("skills", {})
            
            if isinstance(skills_data, dict):
                # New format: {"technical_skills": [...], "soft_skills": [...], ...}
                for skill_list in skills_data.values():
                    if isinstance(skill_list, list):
                        skills_text.extend(skill_list)
            elif isinstance(skills_data, list):
                # Old format: [{"skills": [...]}, ...]
                for skill_cat in skills_data:
                    if isinstance(skill_cat, dict):
                        skills = skill_cat.get("skills", [])
                        skills_text.extend(skills)
            
            skills_section = ", ".join(skills_text)
            
            # Extract projects
            technical_projects = []
            for project in cv_data.get("projects", []):
                title = project.get("title", project.get("name", ""))
                desc = project.get("description", "")
                project_desc = f"{title} - {desc}" if title and desc else title or desc
                if project_desc:
                    technical_projects.append(project_desc)
            
            # Extract certifications
            certifications = []
            for cert in cv_data.get("certifications", []):
                if isinstance(cert, dict):
                    cert_title = cert.get("title", cert.get("name", ""))
                else:
                    cert_title = str(cert)
                if cert_title:
                    certifications.append(cert_title)
            
            return {
                "experience_bullets": experience_bullets,
                "skills_section": skills_section,
                "technical_projects": technical_projects,
                "certifications": certifications
            }
        except Exception as e:
            logger.error(f"❌ [CV_CONTENT] Error extracting CV content: {e}")
            return {
                "experience_bullets": [],
                "skills_section": "",
                "technical_projects": [],
                "certifications": []
            }
    
    def _extract_jd_content(self, company: str) -> Dict:
        """
        Extract JD content for contextual understanding - NOW WITH PROCESSED JD SUPPORT
        
        Tries processed JD first (if available), falls back to original JD file.
        This ensures better extraction results while maintaining backward compatibility.
        """
        try:
            # ⭐ NEW: Try processed JD first (with fallback)
            jd_text = None
            jd_source = "legacy"
            if self.user_email:
                try:
                    logger.debug(f"🔍 [ATS_RECOMMENDATION] Attempting to use processed JD for {company}")
                    print(f"🔍 [ATS_RECOMMENDATION] Attempting to use processed JD for {company}")
                    from app.services.jd_processing_service import get_jd_processing_service
                    jd_service = get_jd_processing_service(self.user_email)
                    processed_text = jd_service.get_jd_text_for_ai(company, prefer_processed=True)
                    if processed_text:
                        jd_text = processed_text
                        jd_source = "processed"
                        logger.info(f"✅ [ATS_RECOMMENDATION] ✅ Using PROCESSED JD for {company} | "
                                   f"Length: {len(jd_text)} chars")
                        
                        # ⭐ PRINT FULL PROCESSED JD TEXT BEING SENT TO AI FOR ATS RECOMMENDATIONS
                        logger.info(f"📋 [ATS_RECOMMENDATION] ========== FULL PROCESSED JD TEXT FOR ATS RECOMMENDATIONS ==========")
                        logger.info(f"📋 [ATS_RECOMMENDATION] Company: {company}")
                        logger.info(f"📋 [ATS_RECOMMENDATION] Total length: {len(jd_text)} characters")
                        logger.info(f"📋 [ATS_RECOMMENDATION] This processed JD text will be used for ATS recommendations:")
                        logger.info(f"📋 [ATS_RECOMMENDATION] Full processed JD text:\n{jd_text}")
                        logger.info(f"📋 [ATS_RECOMMENDATION] ========== END OF PROCESSED JD TEXT FOR ATS RECOMMENDATIONS ==========")
                        print(f"✅ [ATS_RECOMMENDATION] ✅ Using PROCESSED JD for {company} | Length: {len(jd_text)} chars")
                        print(f"📋 [ATS_RECOMMENDATION] FULL PROCESSED JD TEXT FOR ATS RECOMMENDATIONS ({len(jd_text)} chars):\n{jd_text}")
                except Exception as e:
                    logger.warning(f"⚠️ [ATS_RECOMMENDATION] Error attempting processed JD, falling back to LEGACY file: {e}")
                    print(f"⚠️ [ATS_RECOMMENDATION] Error attempting processed JD, falling back to LEGACY file: {e}")
            
            # ✅ FALLBACK: Original legacy behavior (unchanged)
            if not jd_text:
                company_dir = self.base_dir / "applied_companies" / company
                
                # Try to load JD from jd_original.json
                jd_file = TimestampUtils.find_latest_timestamped_file(
                    company_dir, "jd_original", "json"
                )
                if not jd_file:
                    jd_file = company_dir / "jd_original.json"
                
                if not jd_file.exists():
                    logger.warning(f"⚠️ [JD_CONTENT] JD file not found: {jd_file}")
                    return {
                        "role_title": "N/A",
                        "department": "N/A",
                        "role_level": "Mid",
                        "key_responsibilities": ["N/A"],
                        "required_skills": ["N/A"],
                        "preferred_skills": ["N/A"],
                        "context": "N/A"
                    }
                
                with open(jd_file, 'r', encoding='utf-8') as f:
                    jd_data = json.load(f)
                
                # Extract from JD record
                jd_record = jd_data.get("record", {})
                jd_text = jd_data.get("text", "")
                jd_source = "legacy"
                logger.info(f"📄 [ATS_RECOMMENDATION] Using LEGACY (original) JD file | "
                           f"Path: {jd_file.name} | Length: {len(jd_text)} chars | "
                           f"Reason: Processed JD not available or error occurred")
                print(f"📄 [ATS_RECOMMENDATION] Using LEGACY (original) JD file | "
                      f"Path: {jd_file.name} | Length: {len(jd_text)} chars")
            
            # Extract from JD record (for metadata, always need original file for record data)
            jd_record = {}
            try:
                company_dir = self.base_dir / "applied_companies" / company
                jd_file = TimestampUtils.find_latest_timestamped_file(
                    company_dir, "jd_original", "json"
                )
                if not jd_file:
                    jd_file = company_dir / "jd_original.json"
                if jd_file.exists():
                    with open(jd_file, 'r', encoding='utf-8') as f:
                        jd_data = json.load(f)
                    jd_record = jd_data.get("record", {})
            except Exception as e:
                logger.debug(f"⚠️ [ATS_RECOMMENDATION] Could not load JD metadata: {e}")
                jd_record = {}
            
            return {
                "role_title": jd_record.get("title", "N/A"),
                "department": self._extract_department(jd_text),
                "role_level": jd_record.get("level", "Mid"),
                "key_responsibilities": self._extract_responsibilities(jd_text),
                "required_skills": self._extract_required_skills(jd_text),
                "preferred_skills": self._extract_preferred_skills(jd_text),
                "context": self._extract_context(jd_text)
            }
        except Exception as e:
            logger.error(f"❌ [JD_CONTENT] Error extracting JD content: {e}")
            return {
                "role_title": "N/A",
                "department": "N/A",
                "role_level": "Mid",
                "key_responsibilities": ["N/A"],
                "required_skills": ["N/A"],
                "preferred_skills": ["N/A"],
                "context": "N/A"
            }
    
    def _extract_department(self, jd_text: str) -> str:
        """Extract department from JD text"""
        # Look for common department patterns
        import re
        patterns = [
            r"department[:\s]+([^\n\.]+)",
            r"team[:\s]+([^\n\.]+)",
            r"division[:\s]+([^\n\.]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "N/A"
    
    def _extract_responsibilities(self, jd_text: str) -> List[str]:
        """Extract key responsibilities from JD text"""
        import re
        
        # Look for responsibilities section
        responsibilities = []
        
        # Pattern 1: Bullet points after "responsibilities" heading
        resp_section = re.search(
            r"(?:responsibilities|duties|role)[:\s]*\n((?:[-•*]\s*.+\n?)+)",
            jd_text,
            re.IGNORECASE
        )
        
        if resp_section:
            bullets = re.findall(r"[-•*]\s*(.+)", resp_section.group(1))
            responsibilities.extend([b.strip() for b in bullets[:5]])  # Limit to 5
        
        return responsibilities if responsibilities else ["N/A"]
    
    def _extract_required_skills(self, jd_text: str) -> List[str]:
        """Extract required skills from JD text"""
        import re
        
        # Look for required skills section
        required_skills = []
        
        # Pattern: Skills after "required" heading
        req_section = re.search(
            r"(?:required|must have|essential)[:\s]*\n((?:[-•*]\s*.+\n?)+)",
            jd_text,
            re.IGNORECASE
        )
        
        if req_section:
            bullets = re.findall(r"[-•*]\s*(.+)", req_section.group(1))
            required_skills.extend([b.strip() for b in bullets[:5]])  # Limit to 5
        
        return required_skills if required_skills else ["N/A"]
    
    def _extract_preferred_skills(self, jd_text: str) -> List[str]:
        """Extract preferred skills from JD text"""
        import re
        
        # Look for preferred skills section
        preferred_skills = []
        
        # Pattern: Skills after "preferred" heading
        pref_section = re.search(
            r"(?:preferred|nice to have|desirable)[:\s]*\n((?:[-•*]\s*.+\n?)+)",
            jd_text,
            re.IGNORECASE
        )
        
        if pref_section:
            bullets = re.findall(r"[-•*]\s*(.+)", pref_section.group(1))
            preferred_skills.extend([b.strip() for b in bullets[:5]])  # Limit to 5
        
        return preferred_skills if preferred_skills else ["N/A"]
    
    def _extract_context(self, jd_text: str) -> str:
        """Extract context from JD text (first few sentences)"""
        # Get first 200 characters or first 2 sentences
        import re
        
        sentences = re.split(r'[.!?]\s+', jd_text[:500])
        context = '. '.join(sentences[:2])
        
        if len(context) > 200:
            context = context[:200] + "..."
        
        return context if context else "N/A"
