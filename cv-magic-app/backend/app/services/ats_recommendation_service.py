"""
ATS Recommendation Service - Optimized for AI Consumption

This service creates highly optimized recommendation files with:
- Zero redundancy
- Structured data only
- Keyword tier classification
- Strategic tailoring guidance
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
                
                # Strategic tailoring guidance
                "tailoring_strategy": self._generate_tailoring_strategy(
                    component_summary,
                    match_summary,
                    ats_scoring
                ),
                
                # Simplified ATS scoring (no deep nesting)
                "ats_scoring": ats_scoring
            }
            
            logger.info(f"✅ Generated optimized recommendation data for {company}")
            logger.info(f"   ATS Score: {ats_scoring.get('final_score', 0)}")
            logger.info(f"   Match Rate: {match_summary.get('overall_match_rate', 0):.1f}%")
            logger.info(f"   Tier 1 Keywords: {len(recommendation_data['keyword_integration_guidance']['tier1_always_add']['technical']) + len(recommendation_data['keyword_integration_guidance']['tier1_always_add']['soft'])}")
            
            return recommendation_data
            
        except Exception as e:
            logger.error(f"Error extracting recommendation data for {company}: {e}")
            return None
    
    def _extract_preliminary_decision(self, match_entries: List[Dict]) -> Dict[str, Any]:
        """
        Extract structured preliminary decision (remove verbose analysis)
        
        Args:
            match_entries: List of analyze match entries
            
        Returns:
            Clean structured decision data
        """
        if not match_entries:
            return {
                "decision": "UNKNOWN",
                "confidence": 0,
                "match_score": 0,
                "primary_reason": "",
                "critical_missing": [],
                "implicit_likely": [],
                "blocker_found": False
            }
        
        latest_entry = match_entries[-1]
        content = latest_entry.get("content", "")
        
        # Parse structured fields only (ignore verbose DETAILED_ANALYSIS)
        decision_data = {
            "decision": "UNKNOWN",
            "confidence": 0,
            "match_score": 0,
            "primary_reason": "",
            "critical_missing": [],
            "implicit_likely": [],
            "blocker_found": False
        }
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("DECISION:"):
                decision_data["decision"] = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    decision_data["confidence"] = int(line.split(":", 1)[1].strip())
                except:
                    pass
            elif line.startswith("MATCH_SCORE:"):
                try:
                    decision_data["match_score"] = int(line.split(":", 1)[1].strip())
                except:
                    pass
            elif line.startswith("PRIMARY_REASON:"):
                decision_data["primary_reason"] = line.split(":", 1)[1].strip()
            elif line.startswith("CRITICAL_MISSING:"):
                missing = line.split(":", 1)[1].strip()
                if missing and missing.lower() != "none":
                    decision_data["critical_missing"] = [m.strip() for m in missing.split(",")]
            elif line.startswith("IMPLICIT_LIKELY:"):
                implicit = line.split(":", 1)[1].strip()
                if implicit and implicit.lower() != "none":
                    decision_data["implicit_likely"] = [i.strip() for i in implicit.split(",")]
            elif line.startswith("BLOCKER_FOUND:"):
                blocker = line.split(":", 1)[1].strip()
                decision_data["blocker_found"] = blocker.lower() in ["yes", "true"]
            elif line.startswith("---"):
                # Stop at detailed analysis section (we don't need verbose paragraphs)
                break
        
        return decision_data
    
    def _extract_match_summary(self, preextracted_entries: List[Dict]) -> Dict[str, Any]:
        """
        Extract clean match summary (remove emoji, verbose reasoning, duplicate lists)
        
        Args:
            preextracted_entries: List of preextracted comparison entries
            
        Returns:
            Clean structured match data
        """
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
        
        # Parse by category
        current_category = None
        lines = content.split('\n')
        
        for line in lines:
            line_upper = line.upper()
            
            # Identify category sections
            if "TECHNICAL SKILLS" in line_upper:
                current_category = "technical"
            elif "SOFT SKILLS" in line_upper:
                current_category = "soft"
            elif "DOMAIN KEYWORDS" in line_upper:
                current_category = "domain"
            elif "INPUT SUMMARY" in line_upper:
                # Stop before the redundant INPUT SUMMARY section
                break
            
            # Extract matched skills (look for "→ Found in CV: 'skill'")
            if "→ Found in CV:" in line and current_category:
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
            matched = len(match_summary["by_category"][category]["matched"])
            missing = len(match_summary["by_category"][category]["missing"])
            total = matched + missing
            if total > 0:
                match_summary["by_category"][category]["match_rate"] = round((matched / total) * 100, 2)
        
        return match_summary
    
    def _extract_component_summary(self, component_entries: List[Dict]) -> Dict[str, Any]:
        """
        Extract clean component summary (remove duplicates, placeholder text, verbose context)
        
        Args:
            component_entries: List of component analysis entries
            
        Returns:
            Clean structured component data
        """
        if not component_entries:
            return {}
        
        latest_entry = component_entries[-1]
        component_analyses = latest_entry.get("component_analyses", {})
        
        component_summary = {}
        
        # Technical component (keep scores, strengths, gaps only)
        technical = component_analyses.get("technical", {}).get("technical_analysis", {})
        if technical:
            component_summary["technical"] = {
                "score": technical.get("technical_depth_score", 0),
                "core_match": technical.get("core_skills_match_percentage", 0),
                "stack_fit": technical.get("technical_stack_fit_percentage", 0),
                "strengths": technical.get("technical_strengths", [])[:3],  # Top 3 only
                "gaps": technical.get("technical_gaps", [])[:3]  # Top 3 only
            }
        
        # Skills component (remove duplicate fields)
        skills = component_analyses.get("skills", {})
        if skills:
            component_summary["skills"] = {
                "score": skills.get("overall_skills_score", 0),
                "business_readiness": skills.get("business_readiness_score", 0),
                "strengths": skills.get("strength_areas", [])[:3],  # No need for immediate_value_skills duplicate
                "critical_gaps": skills.get("critical_gaps", [])  # No need for training_investment_needed duplicate
            }
        
        # Experience component (keep only essential data)
        experience = component_analyses.get("experience", {}).get("experience_analysis", {})
        if experience:
            component_summary["experience"] = {
                "years": experience.get("cv_experience_years", "0"),
                "corporate_years": experience.get("cv_corporate_years", "0"),
                "alignment_score": experience.get("alignment_score", 0),
                "strengths": experience.get("experience_strengths", [])[:3],
                "gaps": experience.get("experience_gaps", [])[:3]
            }
        
        # Seniority component
        seniority = component_analyses.get("seniority", {}).get("seniority_analysis", {})
        if seniority:
            component_summary["seniority"] = {
                "score": seniority.get("seniority_score", 0),
                "cv_level": seniority.get("cv_responsibility_scope", "Unknown"),
                "jd_level": seniority.get("jd_required_seniority", "Unknown"),
                "match": seniority.get("corporate_seniority_match", 0)
            }
        
        # Industry component (essential fields only)
        industry = component_analyses.get("industry", {}).get("industry_analysis", {})
        if industry:
            component_summary["industry"] = {
                "cv_industry": industry.get("cv_primary_industry", "Unknown"),
                "jd_industry": industry.get("jd_target_industry", "Unknown"),
                "alignment_score": industry.get("industry_alignment_score", 0),
                "transition_type": industry.get("transition_type", "Unknown"),
                "transition_difficulty": industry.get("cultural_adaptation_difficulty", "UNKNOWN"),
                "adaptation_timeline": industry.get("adaptation_timeline", "Unknown")
            }
        
        return component_summary
    
    def _extract_ats_scoring(self, ats_entries: List[Dict]) -> Dict[str, Any]:
        """
        Extract simplified ATS scoring (flatten structure, remove duplicates)
        
        Args:
            ats_entries: List of ATS calculation entries
            
        Returns:
            Clean structured ATS data
        """
        if not ats_entries:
            return {
                "final_score": 0,
                "status": "Unknown",
                "category1_keywords": 0,
                "category2_ai_analysis": 0,
                "missing_counts": {}
            }
        
        latest_entry = ats_entries[-1]
        breakdown = latest_entry.get("breakdown", {})
        
        # Clean status (remove emoji)
        status = latest_entry.get("category_status", "Unknown")
        status = status.replace("❌", "").replace("✅", "").replace("⚠️", "").strip()
        
        return {
            "final_score": latest_entry.get("final_ats_score", 0),
            "status": status,
            "target_score": 75.0,
            "improvement_needed": max(0, 75.0 - latest_entry.get("final_ats_score", 0)),
            "category1_keywords": breakdown.get("category1", {}).get("score", 0),
            "category2_ai_analysis": breakdown.get("category2", {}).get("score", 0),
            "missing_counts": breakdown.get("category1", {}).get("missing_counts", {}),
            "scoring_version": latest_entry.get("scoring_version", "unknown")
        }
    
    def _classify_keywords(self, missing_keywords: Dict[str, List[str]], 
                          cv_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Classify missing keywords into tiers based on CV tailoring framework
        
        Tier 1: Always add (generic/transferable)
        Tier 2: Add if semantic evidence exists
        Tier 3: Never add (domain-specific/unverifiable)
        """
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
            "integration_instructions": (
                "Tier 1: Integrate ALL keywords into skills section and relevant bullets. "
                "Tier 2: Integrate ONLY if semantic evidence exists in CV experience. "
                "Tier 3: DO NOT add - domain-specific, unverifiable, or lacks evidence."
            )
        }
        
        cv_technical = [s.lower() for s in cv_skills.get("technical_skills", [])]
        
        for category in ["technical", "soft", "domain"]:
            for keyword in missing_keywords.get(category, []):
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
    
    def _is_specific_tool_variant(self, keyword: str, cv_technical_lower: List[str]) -> bool:
        """Check if keyword is a specific tool variant not in CV"""
        # SQL variants without generic SQL
        if keyword in ["postgresql", "mysql", "mssql", "oracle", "mariadb"]:
            return not any("sql" in skill for skill in cv_technical_lower)
        
        # Power BI advanced features without Power BI
        if keyword in ["dax", "power query", "power bi service"]:
            return not any("power bi" in skill for skill in cv_technical_lower)
        
        # Tableau variants without Tableau
        if keyword in ["tableau server", "tableau prep", "tableau desktop"]:
            return not any("tableau" in skill for skill in cv_technical_lower)
        
        # Excel advanced features without Excel
        if keyword in ["vba", "pivot tables", "pivot table", "macros"]:
            return not any("excel" in skill for skill in cv_technical_lower)
        
        # Python frameworks without Python
        if keyword in ["django", "flask", "fastapi", "pandas", "numpy", "scikit-learn"]:
            return not any("python" in skill for skill in cv_technical_lower)
        
        return False
    
    def _generate_tailoring_strategy(self, component_summary: Dict, 
                                     match_summary: Dict,
                                     ats_scoring: Dict) -> Dict[str, Any]:
        """Generate strategic tailoring guidance"""
        
        industry_data = component_summary.get("industry", {})
        cv_industry = industry_data.get("cv_industry", "Unknown")
        jd_industry = industry_data.get("jd_industry", "Unknown")
        is_transition = cv_industry.lower() != jd_industry.lower()
        
        # Get gaps from match summary
        technical_gaps = match_summary.get("by_category", {}).get("technical", {}).get("missing", [])[:5]
        soft_gaps = match_summary.get("by_category", {}).get("soft", {}).get("missing", [])[:3]
        domain_gaps = match_summary.get("by_category", {}).get("domain", {}).get("missing", [])[:2]
        
        # Get CV skills that are not in JD (to de-emphasize)
        cv_technical = match_summary.get("by_category", {}).get("technical", {}).get("matched", [])
        all_missing = match_summary.get("by_category", {}).get("technical", {}).get("missing", [])
        
        # Identify non-relevant skills (skills in CV but not matched or missing in JD)
        # This is a simplified approach - in practice, you'd need the full CV and JD skill lists
        non_relevant = []
        technical_strengths = component_summary.get("technical", {}).get("strengths", [])
        for strength in technical_strengths:
            # Extract skill names from strength descriptions
            if any(keyword in strength.lower() for keyword in ["ai", "ml", "edge", "flutter", "dart", "yolo", "pytorch"]):
                non_relevant.append(strength.split()[0:3])  # First few words
        
        strategy = {
            "primary_objective": (
                f"Transition from {cv_industry} to {jd_industry}" 
                if is_transition 
                else f"Optimize CV for {jd_industry} role"
            ),
            
            "emphasis_areas": [
                "Highlight transferable data analysis and technical skills",
                "Emphasize stakeholder engagement and business impact",
                "Frame achievements with quantified metrics and results"
            ],
            
            "de_emphasize": [
                "Minimize AI engineering specifics (PyTorch, Edge AI, YOLOv8n)",
                "Reduce focus on Flutter/Dart development details",
                "De-emphasize hardware optimization and edge computing"
            ] if non_relevant else [],
            
            "critical_additions": {
                "technical": technical_gaps,
                "soft": soft_gaps,
                "domain": [] if is_transition else domain_gaps  # Don't add domain keywords for transitions
            },
            
            "tone_guidance": self._get_tone_guidance(jd_industry, ats_scoring.get("final_score", 0)),
            
            "industry_bridging": self._get_bridging_statements(
                cv_industry, jd_industry
            ) if is_transition else []
        }
        
        return strategy
    
    def _get_tone_guidance(self, industry: str, ats_score: float) -> str:
        """Generate tone guidance based on industry"""
        industry_lower = industry.lower()
        
        if any(term in industry_lower for term in ["non-profit", "charity", "nfp", "ngo", "humanitarian"]):
            return "Professional yet passionate about social impact; data-focused but human-centered"
        elif any(term in industry_lower for term in ["tech", "software", "it", "saas"]):
            return "Technical and results-driven; emphasize innovation and scalability"
        elif any(term in industry_lower for term in ["finance", "banking", "investment", "fintech"]):
            return "Precise and analytical; emphasize accuracy, compliance, and risk management"
        elif any(term in industry_lower for term in ["healthcare", "medical", "clinical", "pharma"]):
            return "Detail-oriented and patient-focused; emphasize accuracy and care quality"
        else:
            return "Professional and results-oriented; emphasize business value and stakeholder impact"
    
    def _get_bridging_statements(self, cv_industry: str, jd_industry: str) -> List[str]:
        """Generate industry transition bridging statements"""
        return [
            f"{cv_industry} data analysis experience → Operational efficiency for {jd_industry}",
            f"Technical skills from {cv_industry} → Modern data practices for {jd_industry}",
            "Cross-industry analytical mindset → Adaptable problem-solving approach"
        ]
    
    def create_recommendation_file(self, company: str) -> bool:
        """Create optimized recommendation file"""
        try:
            # Extract optimized recommendation data
            recommendation_data = self.extract_ats_recommendation_data(company)
            
            if not recommendation_data:
                logger.error(f"Could not extract ATS data for {company}")
                return False
            
            # Save recommendation file
            company_dir = self.base_dir / "applied_companies" / company
            timestamp = TimestampUtils.get_timestamp()
            recommendation_file = company_dir / f"{company}_input_recommendation_{timestamp}.json"
            
            company_dir.mkdir(parents=True, exist_ok=True)
            
            with open(recommendation_file, 'w', encoding='utf-8') as f:
                json.dump(recommendation_data, f, indent=2)
            
            file_size_kb = recommendation_file.stat().st_size / 1024
            logger.info(f"✅ Created optimized recommendation file: {recommendation_file}")
            logger.info(f"   📊 File size: {file_size_kb:.1f} KB (optimized)")
            logger.info(f"   🎯 ATS Score: {recommendation_data['metadata']['ats_score_current']}")
            logger.info(f"   📈 Match Rate: {recommendation_data['metadata']['match_rate_current']:.1f}%")
            logger.info(f"   🔑 Tier 1 Keywords: {len(recommendation_data['keyword_integration_guidance']['tier1_always_add'].get('technical', [])) + len(recommendation_data['keyword_integration_guidance']['tier1_always_add'].get('soft', []))}")

            # Register in DB
            try:
                from app.database import SessionLocal
                from app.services.file_registry_service import FileRegistryService
                db = SessionLocal()
                try:
                    registry = FileRegistryService.from_email(db, self.user_email)
                    company_id = registry.upsert_company(company, display_name=company.replace('_', ' '))
                    file_id = registry.register_file(company_id, "input_recommendation", recommendation_file, timestamp=timestamp)
                    registry.record_analysis_run(company_id, kind="input_reco", output_file_id=file_id)
                    db.commit()
                finally:
                    db.close()
            except Exception as reg_err:
                logger.warning(f"⚠️ [DB] Failed to register input recommendation: {reg_err}")
            
            # Trigger AI recommendation generation
            try:
                from .ai_recommendation_generator import AIRecommendationGenerator
                
                logger.info(f"🤖 [TRIGGER] Starting AI recommendation generation for {company}")
                ai_generator = AIRecommendationGenerator(user_email=self.user_email)
                
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop and loop.is_running():
                        async def background_ai_generation():
                            try:
                                success = await ai_generator.generate_ai_recommendation(company, force_regenerate=False)
                                if success:
                                    logger.info(f"✅ [TRIGGER] AI recommendation generated for {company}")
                                else:
                                    logger.warning(f"⚠️ [TRIGGER] AI generation failed for {company}")
                            except Exception as e:
                                logger.error(f"❌ [TRIGGER] AI generation error for {company}: {e}")
                        
                        asyncio.create_task(background_ai_generation())
                        logger.info(f"📋 [TRIGGER] AI generation scheduled for {company}")
                    else:
                        def run_ai_generation():
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            try:
                                success = new_loop.run_until_complete(
                                    ai_generator.generate_ai_recommendation(company, force_regenerate=False)
                                )
                                if success:
                                    logger.info(f"✅ [TRIGGER] AI recommendation generated for {company}")
                            except Exception as e:
                                logger.error(f"❌ [TRIGGER] AI generation error: {e}")
                            finally:
                                new_loop.close()
                        
                        import threading
                        ai_thread = threading.Thread(target=run_ai_generation, daemon=True)
                        ai_thread.start()
                        logger.info(f"🧵 [TRIGGER] AI generation started in thread for {company}")
                except Exception as loop_e:
                    logger.error(f"Error with event loop for {company}: {loop_e}")
                    
            except Exception as e:
                logger.error(f"Error triggering AI generation for {company}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating recommendation file for {company}: {e}")
            return False
    
    def get_recommendation_file_path(self, company: str) -> Path:
        """Get latest recommendation file path"""
        company_dir = self.base_dir / "applied_companies" / company
        latest_file = TimestampUtils.find_latest_timestamped_file(
            company_dir, f"{company}_input_recommendation", "json"
        )
        if latest_file:
            return latest_file
        return company_dir / f"{company}_input_recommendation.json"
    
    def check_if_recommendation_exists(self, company: str) -> bool:
        """Check if recommendation file exists"""
        company_dir = self.base_dir / "applied_companies" / company
        latest_file = TimestampUtils.find_latest_timestamped_file(
            company_dir, f"{company}_input_recommendation", "json"
        )
        return latest_file is not None and latest_file.exists()
    
    def update_existing_recommendation(self, company: str, force_update: bool = False) -> bool:
        """Update recommendation file if needed"""
        try:
            recommendation_file = self.get_recommendation_file_path(company)
            
            company_dir = self.base_dir / "applied_companies" / company
            analysis_file = TimestampUtils.find_latest_timestamped_file(
                company_dir, f"{company}_skills_analysis", "json"
            )
            if not analysis_file:
                analysis_file = company_dir / f"{company}_skills_analysis.json"
            
            # Check if update needed
            if not force_update and recommendation_file.exists():
                if recommendation_file.stat().st_mtime >= analysis_file.stat().st_mtime:
                    logger.info(f"Recommendation file for {company} is up to date")
                    return False
            
            return self.create_recommendation_file(company)
            
        except Exception as e:
            logger.error(f"Error updating recommendation file for {company}: {e}")
            return False
    
    def list_companies_with_ats_data(self) -> List[str]:
        """List all companies with ATS calculation entries"""
        companies_with_ats = []
        
        try:
            applied_companies_dir = self.base_dir / "applied_companies"
            if not applied_companies_dir.exists():
                return companies_with_ats
            
            for company_dir in applied_companies_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    analysis_file = TimestampUtils.find_latest_timestamped_file(
                        company_dir, f"{company_dir.name}_skills_analysis", "json"
                    )
                    if not analysis_file:
                        analysis_file = company_dir / f"{company_dir.name}_skills_analysis.json"
                    
                    if analysis_file.exists():
                        try:
                            with open(analysis_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            if data.get("ats_calculation_entries"):
                                companies_with_ats.append(company_dir.name)
                                
                        except Exception as e:
                            logger.warning(f"Could not read analysis file for {company_dir.name}: {e}")
            
            logger.info(f"Found {len(companies_with_ats)} companies with ATS data")
            return companies_with_ats
            
        except Exception as e:
            logger.error(f"Error listing companies with ATS data: {e}")
            return companies_with_ats
    
    def batch_create_recommendations(self, companies: Optional[List[str]] = None, 
                                    force_update: bool = False) -> Dict[str, bool]:
        """Create recommendation files for multiple companies"""
        results = {}
        
        if companies is None:
            companies = self.list_companies_with_ats_data()
        
        logger.info(f"Processing {len(companies)} companies for recommendation file creation")
        
        for company in companies:
            try:
                success = self.update_existing_recommendation(company, force_update)
                results[company] = success
                
                if success:
                    logger.info(f"✅ Created/updated recommendation file for {company}")
                else:
                    logger.warning(f"⚠️ No update needed for {company}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to process {company}: {e}")
                results[company] = False
        
        successful_count = sum(1 for success in results.values() if success)
        logger.info(f"Batch processing complete: {successful_count}/{len(companies)} successful")
        
        return results