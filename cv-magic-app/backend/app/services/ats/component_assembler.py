"""
ATS Component Assembler

Assembles individual component analyses into a unified ATS analysis result.
"""

import asyncio
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from app.utils.timestamp_utils import TimestampUtils

from app.services.ats.components.consistency_validator import ConsistencyValidator
from app.services.ats.requirement_bonus_calculator import RequirementBonusCalculator
from app.services.jd_analysis.jd_analyzer import RequirementsExtractor
from app.services.ats.ats_score_calculator import ATSScoreCalculator
from app.services.ats.components.technical_skills_analyzer import TechnicalSkillsAnalyzer
from app.services.ats.components.experience_fit_analyzer import ExperienceFitAnalyzer
from app.services.ats.components.new_to_legacy_mapper import NewToLegacyMapper

logger = logging.getLogger(__name__)


class ComponentAssembler:
    """Assembles individual component analyses into unified results."""

    def __init__(self, base_dir: Optional[Path] = None, user_email: str = None):
        if base_dir:
            self.base_dir: Path = base_dir
        else:
            from app.utils.user_path_utils import get_user_base_path
            self.base_dir: Path = get_user_base_path(user_email)
        self.user_email = user_email
        
        # Initialize v2 analyzers only (v1 removed)
        self.tech_skills_analyzer_v2 = TechnicalSkillsAnalyzer()
        self.exp_fit_analyzer_v2 = ExperienceFitAnalyzer()
        self.mapper = NewToLegacyMapper()
        self.bonus_calculator = RequirementBonusCalculator()
        self.requirements_extractor = RequirementsExtractor()
        self.ats_calculator = ATSScoreCalculator()
        self.consistency_validator = ConsistencyValidator()
        logger.info("[ASSEMBLER] Using v2 2-analyzer approach only (v1 removed)")

    def _read_cv_text(self, company_name: str = "Unknown", jd_url: str = "") -> str:
        """
        Read CV text from the appropriate CV.
        For reruns/component analysis, always use the latest CV (preferring tailored if available).
        """
        from app.unified_latest_file_selector import get_selector_for_user
        
        logger.info("🔍 [COMPONENT_ASSEMBLER] Selecting CV for component analysis")
        user_selector = get_selector_for_user(self.user_email)
        
        # CRITICAL: For component analysis (which runs after tailored CV is generated),
        # always use the latest CV across all (preferring tailored CV if it exists and is newer)
        # This ensures reruns use the latest tailored CV with all improvements
        cv_context = user_selector.get_latest_cv_across_all(company_name)
        
        if not cv_context.exists:
            raise FileNotFoundError(f"No CV found for company: {company_name}")
        
        logger.info(f"📄 [COMPONENT_ASSEMBLER] Using {cv_context.file_type} CV: {cv_context.json_path or cv_context.txt_path}")
        
        # Read content from the selected CV
        cv_file_path = cv_context.txt_path if cv_context.txt_path else cv_context.json_path
        if not cv_file_path or not cv_file_path.exists():
            raise FileNotFoundError(f"CV file not found: {cv_file_path}")
        
        with open(cv_file_path, 'r', encoding='utf-8') as f:
            cv_content = f.read()
        
        if not cv_content:
            logger.error("❌ [COMPONENT_ASSEMBLER] Failed to get CV content")
            raise FileNotFoundError(f"Could not load CV content for company: {company_name}")
            
        if not cv_content.strip():
            logger.error("❌ [COMPONENT_ASSEMBLER] No text content available in CV")
            raise ValueError("CV text content is empty")
        
        logger.info(f"📄 [COMPONENT_ASSEMBLER] Selected CV content ({cv_context.file_type})")
        logger.info(f"📊 [COMPONENT_ASSEMBLER] Content length: {len(cv_content)} chars")
        
        return cv_content

    def _read_jd_text(self, company: str) -> str:
        """
        Read JD text for a specific company - NOW WITH PROCESSED JD SUPPORT
        
        Tries processed JD first (if available), falls back to original JD file.
        This ensures better component analysis results while maintaining backward compatibility.
        """
        # ⭐ NEW: Try processed JD first (with fallback)
        if self.user_email:
            try:
                logger.debug(f"🔍 [COMPONENT_ASSEMBLER] Attempting to use processed JD for {company}")
                print(f"🔍 [COMPONENT_ASSEMBLER] Attempting to use processed JD for {company}")
                from app.services.jd_processing_service import get_jd_processing_service
                jd_service = get_jd_processing_service(self.user_email)
                processed_text = jd_service.get_jd_text_for_ai(company, prefer_processed=True)
                if processed_text:
                    logger.info(f"✅ [COMPONENT_ASSEMBLER] ✅ Using PROCESSED JD for {company} | "
                               f"Length: {len(processed_text)} chars")
                    print(f"✅ [COMPONENT_ASSEMBLER] ✅ Using PROCESSED JD for {company} | Length: {len(processed_text)} chars")
                    return processed_text
                else:
                    logger.info(f"📄 [COMPONENT_ASSEMBLER] Processed JD not available for {company}, "
                               f"falling back to LEGACY file")
                    print(f"📄 [COMPONENT_ASSEMBLER] Processed JD not available for {company}, falling back to LEGACY file")
            except Exception as e:
                logger.warning(f"⚠️ [COMPONENT_ASSEMBLER] Error attempting processed JD, falling back to LEGACY file: {e}")
                print(f"⚠️ [COMPONENT_ASSEMBLER] Error attempting processed JD, falling back to LEGACY file: {e}")
                # Continue with original file reading
        else:
            logger.debug(f"📄 [COMPONENT_ASSEMBLER] No user_email available, using LEGACY file")
        
        # ✅ FALLBACK: Original legacy behavior (unchanged)
        company_dir = self.base_dir / "applied_companies" / company
        jd_json = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
        
        # Fallback to non-timestamped file if no timestamped file exists
        if not jd_json:
            jd_json = company_dir / "jd_original.json"
        
        if not jd_json.exists():
            raise FileNotFoundError(f"JD text not found: {jd_json}")
        with open(jd_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        text = (data.get("text") or "").strip()
        if not text:
            raise ValueError("JD text is empty")
        logger.info(f"📄 [COMPONENT_ASSEMBLER] Using LEGACY (original) JD file | "
                   f"Path: {jd_json.name} | Length: {len(text)} chars | "
                   f"Reason: Processed JD not available or error occurred")
        print(f"📄 [COMPONENT_ASSEMBLER] Using LEGACY (original) JD file | "
              f"Path: {jd_json.name} | Length: {len(text)} chars")
        return text

    def _read_matched_skills(self, company: str) -> str:
        """Read matched skills for a specific company."""
        company_dir = self.base_dir / "applied_companies" / company
        match_file = TimestampUtils.find_latest_timestamped_file(company_dir, "cv_jd_match_results", "json")
        
        # Fallback to non-timestamped file if no timestamped file exists
        if not match_file:
            match_file = company_dir / "cv_jd_match_results.json"
        
        if not match_file.exists():
            logger.warning("[ASSEMBLER] Match results not found: %s", match_file)
            return "[]"
        
        try:
            with open(match_file, "r", encoding="utf-8") as f:
                md = json.load(f)
            matched_req = md.get("matched_required_keywords", [])
            matched_pref = md.get("matched_preferred_keywords", [])
            return json.dumps({
                "matched_required": matched_req[:10],  # Limit to avoid token overflow
                "matched_preferred": matched_pref[:10],
            }, ensure_ascii=False)
        except Exception as e:
            logger.warning("[ASSEMBLER] Failed to load matched skills: %s", e)
            return "[]"

    def _calculate_requirement_bonus(self, company: str) -> Dict[str, Any]:
        """Calculate requirement bonus from CV-JD match results."""
        # Strictly use the per-user cv_jd_matching file pattern
        from app.utils.timestamp_utils import TimestampUtils
        company_dir = self.base_dir / "applied_companies" / company
        match_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_cv_jd_matching", "json")
        
        try:
            if not match_file or not match_file.exists():
                raise FileNotFoundError(f"CV-JD matching file not found for bonus calculation: expected pattern '{company}_cv_jd_matching_<timestamp>.json' in {company_dir}")
            
            logger.info("[ASSEMBLER] Requirement bonus using match file: %s", match_file)
            with open(match_file, "r", encoding="utf-8") as f:
                match_data = json.load(f)
            
            # Check if match_counts already exists in the file
            if "match_counts" in match_data:
                match_counts = match_data["match_counts"]
                logger.info("[ASSEMBLER] Using existing match_counts from file")
            else:
                # Extract match counts from keyword arrays
                total_required = len(match_data.get("required_keywords", []))
                total_preferred = len(match_data.get("preferred_keywords", []))
                matched_required = len(match_data.get("matched_required_keywords", []))
                matched_preferred = len(match_data.get("matched_preferred_keywords", []))
                
                match_counts = {
                    "total_required_keywords": total_required,
                    "total_preferred_keywords": total_preferred,
                    "matched_required_count": matched_required,
                    "matched_preferred_count": matched_preferred,
                }
                logger.info("[ASSEMBLER] Calculated match_counts from keyword arrays")
            
            # Calculate bonus
            bonus_result = self.bonus_calculator.calculate(match_counts)
            logger.info("[ASSEMBLER] Requirement bonus calculated: %.2f points", bonus_result["bonus_breakdown"]["total_bonus"])
            return bonus_result
            
        except Exception as e:
            logger.error("[ASSEMBLER] Failed to calculate requirement bonus: %s", e)
            raise


    async def _run_new_component_analyses(self, cv_text: str, jd_text: str, matched_skills: str, company: str) -> Dict[str, Any]:
        """
        Run NEW 2-analyzer approach in parallel and map to legacy structure.
        """
        logger.info("[ASSEMBLER] Running NEW 2-analyzer approach")
        try:
            tech_skills_task = self.tech_skills_analyzer_v2.analyze(cv_text, jd_text, matched_skills, self.user_email)
            exp_fit_task = self.exp_fit_analyzer_v2.analyze(cv_text, jd_text, self.user_email)
            bonus_task = asyncio.get_event_loop().run_in_executor(None, self._calculate_requirement_bonus, company)
            tech_skills_result, exp_fit_result, bonus_result = await asyncio.gather(
                tech_skills_task, exp_fit_task, bonus_task, return_exceptions=True
            )
            if isinstance(tech_skills_result, Exception):
                logger.error(f"[ASSEMBLER] Technical & Skills analysis failed: {tech_skills_result}")
                raise tech_skills_result
            if isinstance(exp_fit_result, Exception):
                logger.error(f"[ASSEMBLER] Experience & Fit analysis failed: {exp_fit_result}")
                raise exp_fit_result
            if isinstance(bonus_result, Exception):
                logger.warning(f"[ASSEMBLER] Bonus calculation failed: {bonus_result}")
                bonus_result = {"total_bonus": 0, "bonus_breakdown": {"total_bonus": 0}}
            legacy_results = self.mapper.map_to_legacy_structure(tech_skills_result, exp_fit_result, bonus_result)
            logger.info("[ASSEMBLER] NEW analyzer results mapped to legacy structure successfully")
            return legacy_results
        except Exception as e:
            logger.error(f"[ASSEMBLER] New analyzer approach failed: {str(e)}", exc_info=True)
            raise

    async def _run_component_analyses_with_fallback(self, cv_text: str, jd_text: str, matched_skills: str, company: str) -> Dict[str, Any]:
        """
        Run component analyses using NEW v2 2-analyzer approach only.
        v1 is no longer supported.
        """
        logger.info("[ASSEMBLER] Using NEW v2 2-analyzer approach (v1 removed)")
        return await self._run_new_component_analyses(cv_text, jd_text, matched_skills, company)

    def _get_match_rates_for_company(self, company: str) -> Dict[str, Any]:
        """
        Extract match rates and missing counts from latest preextracted comparison entry for ATS v2.
        """
        try:
            company_dir = self.base_dir / "applied_companies" / company
            file_path = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
            if not file_path:
                file_path = company_dir / f"{company}_skills_analysis.json"
            if not file_path.exists():
                logger.warning("[ASSEMBLER] No skills analysis file found for match rates")
                return {
                    "technical_skills_match_rate": 0.0,
                    "domain_keywords_match_rate": 0.0,
                    "soft_skills_match_rate": 0.0,
                    "technical_missing_count": 0,
                    "soft_missing_count": 0,
                    "domain_missing_count": 0
                }
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            preextracted_entries = data.get("preextracted_comparison_entries", [])
            if not preextracted_entries:
                return {
                    "technical_skills_match_rate": 0.0,
                    "domain_keywords_match_rate": 0.0,
                    "soft_skills_match_rate": 0.0,
                    "technical_missing_count": 0,
                    "soft_missing_count": 0,
                    "domain_missing_count": 0
                }
            latest_preextracted = preextracted_entries[-1]
            preextracted_data = {"content": latest_preextracted.get("content", "")}
            tech_rate, domain_rate, soft_rate, tech_missing, soft_missing, domain_missing = self.ats_calculator._calculate_match_rates(preextracted_data)
            return {
                "technical_skills_match_rate": tech_rate,
                "domain_keywords_match_rate": domain_rate,
                "soft_skills_match_rate": soft_rate,
                "technical_missing_count": tech_missing,
                "soft_missing_count": soft_missing,
                "domain_missing_count": domain_missing
            }
        except Exception as e:
            logger.error("[ASSEMBLER] Failed to extract match rates for v2: %s", e)
            return {
                "technical_skills_match_rate": 0.0,
                "domain_keywords_match_rate": 0.0,
                "soft_skills_match_rate": 0.0,
                "technical_missing_count": 0,
                "soft_missing_count": 0,
                "domain_missing_count": 0
            }


    def _extract_scores(self, component_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract scores from component results."""
        scores = {}
        
        # Skills relevance
        if "overall_skills_score" in component_results["skills"]:
            scores["skills_relevance"] = float(component_results["skills"]["overall_skills_score"])
        
        # Experience alignment
        if "experience_analysis" in component_results["experience"]:
            exp_analysis = component_results["experience"]["experience_analysis"]
            if "alignment_score" in exp_analysis:
                scores["experience_alignment"] = float(exp_analysis["alignment_score"])
        
        # Industry fit - include detailed scores
        if "industry_analysis" in component_results["industry"]:
            industry_analysis = component_results["industry"]["industry_analysis"]
            scores["industry_fit"] = float(industry_analysis.get("industry_alignment_score", 0.0))
            scores["domain_overlap_percentage"] = float(industry_analysis.get("domain_overlap_percentage", 0.0))
            scores["data_familiarity_score"] = float(industry_analysis.get("data_familiarity_score", 0.0))
            scores["stakeholder_fit_score"] = float(industry_analysis.get("stakeholder_fit_score", 0.0))
            scores["business_cycle_alignment"] = float(industry_analysis.get("business_cycle_alignment", 0.0))
            # Map industry_alignment_score to industry_transition_fit for v2 calculation
            scores["industry_transition_fit"] = float(industry_analysis.get("industry_alignment_score", 0.0))
        
        # Role seniority - include detailed scores
        if "seniority_analysis" in component_results["seniority"]:
            seniority_analysis = component_results["seniority"]["seniority_analysis"]
            if "seniority_score" in seniority_analysis:
                scores["role_seniority"] = float(seniority_analysis["seniority_score"])
            if "experience_match_percentage" in seniority_analysis:
                scores["experience_match_percentage"] = float(seniority_analysis["experience_match_percentage"])
                # Map experience_match_percentage to role_similarity for v2 calculation
                scores["role_similarity"] = float(seniority_analysis["experience_match_percentage"])
            if "responsibility_fit_percentage" in seniority_analysis:
                scores["responsibility_fit_percentage"] = float(seniority_analysis["responsibility_fit_percentage"])
            if "leadership_readiness_score" in seniority_analysis:
                scores["leadership_readiness_score"] = float(seniority_analysis["leadership_readiness_score"])
            if "growth_trajectory_score" in seniority_analysis:
                scores["growth_trajectory_score"] = float(seniority_analysis["growth_trajectory_score"])
            if "corporate_seniority_match" in seniority_analysis:
                # Map corporate_seniority_match to seniority_match for v2 calculation
                scores["seniority_match"] = float(seniority_analysis["corporate_seniority_match"])
        
        # Technical depth - include detailed scores
        if "technical_analysis" in component_results["technical"]:
            technical_analysis = component_results["technical"]["technical_analysis"]
            if "technical_depth_score" in technical_analysis:
                scores["technical_depth"] = float(technical_analysis["technical_depth_score"])
            if "core_skills_match_percentage" in technical_analysis:
                scores["core_skills_match_percentage"] = float(technical_analysis["core_skills_match_percentage"])
                # Map core_skills_match_percentage to required_skills_coverage for v2 calculation
                scores["required_skills_coverage"] = float(technical_analysis["core_skills_match_percentage"])
            if "technical_stack_fit_percentage" in technical_analysis:
                scores["technical_stack_fit_percentage"] = float(technical_analysis["technical_stack_fit_percentage"])
                # Map technical_stack_fit_percentage to tech_stack_similarity for v2 calculation
                scores["tech_stack_similarity"] = float(technical_analysis["technical_stack_fit_percentage"])
            if "complexity_readiness_score" in technical_analysis:
                scores["complexity_readiness_score"] = float(technical_analysis["complexity_readiness_score"])
            if "learning_agility_score" in technical_analysis:
                scores["learning_agility_score"] = float(technical_analysis["learning_agility_score"])
            if "jd_problem_complexity" in technical_analysis:
                scores["jd_problem_complexity"] = float(technical_analysis["jd_problem_complexity"])
        
        # Business readiness - extract from skills section for v2 calculation
        if "skills" in component_results:
            if "business_readiness_score" in component_results["skills"]:
                scores["business_readiness"] = float(component_results["skills"]["business_readiness_score"])
        
        # Requirement bonus scores
        if "requirement_bonus" in component_results:
            bonus_breakdown = component_results["requirement_bonus"].get("bonus_breakdown", {})
            if "total_bonus" in bonus_breakdown:
                scores["requirement_bonus"] = float(bonus_breakdown["total_bonus"])
                scores["total_bonus"] = float(bonus_breakdown["total_bonus"])  # Add total_bonus as well
            if "required_bonus" in bonus_breakdown:
                scores["required_bonus"] = float(bonus_breakdown["required_bonus"])
            if "required_penalty" in bonus_breakdown:
                scores["required_penalty"] = float(bonus_breakdown["required_penalty"])
            if "preferred_bonus" in bonus_breakdown:
                scores["preferred_bonus"] = float(bonus_breakdown["preferred_bonus"])
            if "preferred_penalty" in bonus_breakdown:
                scores["preferred_penalty"] = float(bonus_breakdown["preferred_penalty"])
            
            coverage_metrics = component_results["requirement_bonus"].get("coverage_metrics", {})
            if "required_coverage" in coverage_metrics:
                scores["required_coverage"] = float(coverage_metrics["required_coverage"])
            if "preferred_coverage" in coverage_metrics:
                scores["preferred_coverage"] = float(coverage_metrics["preferred_coverage"])
        
        return scores

    def _save_results(self, company: str, component_results: Dict[str, Any], scores: Dict[str, float]) -> None:
        """Save assembled results to the company's skills analysis file."""
        # Use timestamped analysis file with fallback
        from app.utils.timestamp_utils import TimestampUtils
        company_dir = self.base_dir / "applied_companies" / company
        file_path = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
        if not file_path:
            file_path = company_dir / f"{company}_skills_analysis.json"
        
        # Create the assembled entry
        assembled_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "component_analyses": component_results,
            "extracted_scores": scores,
            "analysis_type": "modular_component_analysis"
        }
        
        # Read existing file or create new structure
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = {}
        else:
            existing_data = {}
        
        # Ensure we have the right structure
        if "component_analysis_entries" not in existing_data:
            existing_data["component_analysis_entries"] = []
        
        # Append new entry
        existing_data["component_analysis_entries"].append(assembled_entry)
        
        # Save back to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        logger.info("[ASSEMBLER] Results saved to: %s", file_path)

    def _save_minimal_cv_results(self, company: str, minimal_results: Dict[str, Any]) -> None:
        """Save minimal CV results to the company's skills analysis file."""
        # Use timestamped analysis file with fallback
        from app.utils.timestamp_utils import TimestampUtils
        company_dir = self.base_dir / "applied_companies" / company
        file_path = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
        if not file_path:
            file_path = company_dir / f"{company}_skills_analysis.json"
        
        # Create the assembled entry for minimal CV
        assembled_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "component_analyses": minimal_results.get("ats_breakdown", {}),
            "extracted_scores": {
                "skills_relevance": minimal_results.get("ats_breakdown", {}).get("category1_skills_relevance", {}).get("total", 0),
                "experience_alignment": minimal_results.get("ats_breakdown", {}).get("category2_component_analysis", {}).get("experience_seniority", {}).get("total", 0),
                "industry_fit": minimal_results.get("ats_breakdown", {}).get("category2_component_analysis", {}).get("potential_ability", {}).get("total", 0),
                "role_seniority": minimal_results.get("ats_breakdown", {}).get("category2_component_analysis", {}).get("experience_seniority", {}).get("total", 0),
                "technical_depth": minimal_results.get("ats_breakdown", {}).get("category2_component_analysis", {}).get("core_competency", {}).get("total", 0),
            },
            "analysis_type": "minimal_cv_realistic"
        }
        
        # Read existing file or create new structure
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = {}
        else:
            existing_data = {}
        
        # Ensure we have the right structure
        if "component_analysis_entries" not in existing_data:
            existing_data["component_analysis_entries"] = []
        
        # Append new entry
        existing_data["component_analysis_entries"].append(assembled_entry)
        
        # Save back to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        logger.info("[ASSEMBLER] Minimal CV results saved to: %s", file_path)

    async def _run_ats_calculation(self, company: str, extracted_scores: Dict[str, float]) -> Dict[str, Any]:
        """Run ATS score calculation and save results using v2 method."""
        try:
            # Use v2 calculation method for consistency
            logger.info("[ASSEMBLER] Using v2 ATS calculation method")
            match_rates = self._get_match_rates_for_company(company)
            
            # Calculate ATS score using v2
            ats_result = self.ats_calculator.calculate_ats_score_v2(
                match_rates=match_rates,
                extracted_scores=extracted_scores
            )
            
            # Add timestamp and ensure all required fields are present
            ats_result_dict = {
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                "final_ats_score": ats_result["final_ats_score"],
                "category_status": ats_result["category_status"],
                "recommendation": ats_result["recommendation"],
                "breakdown": ats_result["breakdown"],
                "scoring_version": ats_result.get("scoring_version", "v2_65_35_split")
            }
            
            # Save ATS results to the analysis file
            company_dir = self.base_dir / "applied_companies" / company
            file_path = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
            if not file_path:
                file_path = company_dir / f"{company}_skills_analysis.json"
            
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}
            
            if "ats_calculation_entries" not in data:
                data["ats_calculation_entries"] = []
            
            data["ats_calculation_entries"].append(ats_result_dict)
            
            # Save back to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("[ASSEMBLER] ATS calculation completed. Score: %.1f/100 (%s)", 
                       ats_result_dict["final_ats_score"], ats_result_dict["category_status"])
            
            # Create recommendation file after ATS calculation is completed
            try:
                from app.services.ats_recommendation_service import ATSRecommendationService
                recommendation_service = ATSRecommendationService(self.user_email)
                
                # Extract and save optimized recommendation
                recommendation_data = recommendation_service.extract_ats_recommendation_data(company)
                if recommendation_data:
                    saved_file = recommendation_service.save_optimized_recommendation(company, recommendation_data)
                    if saved_file:
                        logger.info("[ASSEMBLER] Recommendation file created for %s: %s", company, saved_file)
                    else:
                        logger.warning("[ASSEMBLER] Failed to save recommendation file for %s", company)
                else:
                    logger.warning("[ASSEMBLER] Failed to extract recommendation data for %s", company)
            except Exception as e:
                logger.error("[ASSEMBLER] Error creating recommendation file for %s: %s", company, e, exc_info=True)
            
            return ats_result_dict
            
        except Exception as e:
            logger.error("[ASSEMBLER] ATS calculation failed: %s", e)
            return {"error": str(e)}
    
    def _generate_minimal_cv_results(self, minimal_analysis: Dict[str, Any], company: str) -> Dict[str, Any]:
        """
        Generate realistic results for minimal CVs.
        
        Args:
            minimal_analysis: Results from minimal CV analyzer
            company: Company name
            
        Returns:
            Dict with realistic analysis results
        """
        try:
            logger.info("📄 [ASSEMBLER] Generating realistic results for minimal CV")
            
            realistic_analysis = minimal_analysis['realistic_analysis']
            constraints = minimal_analysis['constraints']
            warnings = minimal_analysis['warnings']
            
            # Extract scores with constraints applied
            core_competency = realistic_analysis['core_competency']
            experience_analysis = realistic_analysis['experience_analysis']
            skills_analysis = realistic_analysis['skills_analysis']
            overall_assessment = realistic_analysis['overall_assessment']
            
            # Generate ATS score breakdown
            ats_breakdown = {
                "category1_skills_relevance": {
                    "technical_skills": 15.0,  # Constrained score
                    "domain_skills": 10.0,
                    "soft_skills": 5.0,
                    "total": 30.0
                },
                "category2_component_analysis": {
                    "core_competency": {
                        "technical_depth": core_competency['technical_depth'],
                        "core_skills_match_percentage": core_competency['core_skills_match_percentage'],
                        "technical_stack_fit_percentage": core_competency['technical_stack_fit_percentage'],
                        "data_familiarity_score": core_competency['data_familiarity_score'],
                        "total": (core_competency['technical_depth'] + 
                                core_competency['core_skills_match_percentage'] + 
                                core_competency['technical_stack_fit_percentage'] + 
                                core_competency['data_familiarity_score']) / 4
                    },
                    "experience_seniority": {
                        "experience_alignment": experience_analysis['experience_alignment'],
                        "experience_match_percentage": experience_analysis['experience_match_percentage'],
                        "responsibility_fit_percentage": experience_analysis['responsibility_fit_percentage'],
                        "role_seniority": experience_analysis['role_seniority'],
                        "leadership_readiness_score": experience_analysis['leadership_readiness_score'],
                        "total": (experience_analysis['experience_alignment'] + 
                                experience_analysis['experience_match_percentage'] + 
                                experience_analysis['responsibility_fit_percentage'] + 
                                experience_analysis['role_seniority'] + 
                                experience_analysis['leadership_readiness_score']) / 5
                    },
                    "potential_ability": {
                        "growth_trajectory_score": 15.0,  # Constrained
                        "complexity_readiness_score": 10.0,
                        "learning_agility_score": 15.0,
                        "jd_problem_complexity": 5.0,
                        "total": 45.0
                    },
                    "company_fit": {
                        "industry_fit": 10.0,  # Constrained
                        "domain_overlap_percentage": 8.0,
                        "stakeholder_fit_score": 7.0,
                        "business_cycle_alignment": 5.0,
                        "total": 30.0
                    }
                },
                "category3_requirement_bonus": {
                    "bonus_points": 0.0,
                    "total": 0.0
                }
            }
            
            # Calculate final ATS score
            final_ats_score = (
                ats_breakdown["category1_skills_relevance"]["total"] +
                ats_breakdown["category2_component_analysis"]["core_competency"]["total"] +
                ats_breakdown["category2_component_analysis"]["experience_seniority"]["total"] +
                ats_breakdown["category2_component_analysis"]["potential_ability"]["total"] +
                ats_breakdown["category2_component_analysis"]["company_fit"]["total"] +
                ats_breakdown["category3_requirement_bonus"]["total"]
            )
            
            # Generate insights
            insights = {
                "key_strengths": [
                    f"Basic technical skills: {', '.join(core_competency.get('available_skills', []))}",
                    "Willingness to learn and develop"
                ],
                "critical_gaps": [
                    "Limited experience information",
                    "Minimal skills demonstration",
                    "No quantified achievements",
                    "Lack of detailed work history"
                ],
                "recommendations": [
                    "Add more detailed work experience",
                    "Include specific projects and achievements",
                    "Quantify accomplishments with numbers",
                    "Add more technical skills and certifications",
                    "Include leadership and teamwork examples"
                ],
                "overall_assessment": overall_assessment['realistic_summary']
            }
            
            return {
                "ats_breakdown": ats_breakdown,
                "final_ats_score": final_ats_score,
                "insights": insights,
                "minimal_cv_analysis": minimal_analysis,
                "warnings": warnings,
                "realistic_constraints": constraints,
                "analysis_type": "minimal_cv_realistic"
            }
            
        except Exception as e:
            logger.error(f"❌ [ASSEMBLER] Failed to generate minimal CV results: {e}")
            return {
                "error": f"Failed to generate minimal CV results: {str(e)}",
                "minimal_cv_analysis": minimal_analysis
            }
    
    async def assemble_analysis(self, company: str, cv_text: Optional[str] = None, jd_url: str = "") -> Dict[str, Any]:
        """
        Assemble complete ATS component analysis for a company.
        
        Args:
            company: Company name for analysis
            cv_text: Optional CV text (if not provided, will be read from files)
            jd_url: Job description URL for JD-aware CV selection
            
        Returns:
            Dict containing assembled analysis results
        """
        logger.info("===== [ASSEMBLER] Starting component assembly for: %s =====", company)
        
        try:
            # Read input data (auto-select appropriate CV based on JD usage when not provided)
            if cv_text is None:
                cv_text = self._read_cv_text(company, jd_url)
            else:
                logger.info("📄 [ASSEMBLER] Using CV text provided by caller")
                if not isinstance(cv_text, str) or not cv_text.strip():
                    raise ValueError("Provided CV text is empty")
            jd_text = self._read_jd_text(company)
            
            # Check if CV is minimal and use appropriate analyzer
            from app.services.minimal_cv_analyzer import minimal_cv_analyzer
            minimal_analysis = minimal_cv_analyzer.analyze_minimal_cv(cv_text, jd_text)
            
            if minimal_analysis['is_minimal_cv']:
                logger.info("📄 [ASSEMBLER] CV is minimal - using realistic analysis with constraints")
                minimal_results = self._generate_minimal_cv_results(minimal_analysis, company)
                
                # Save minimal CV results to analysis file
                self._save_minimal_cv_results(company, minimal_results)
                
                # Run ATS calculation for minimal CV using v2 (same as regular CV)
                logger.info("[ASSEMBLER] Starting ATS v2 score calculation for minimal CV...")
                extracted_scores = minimal_results.get("extracted_scores", {})
                match_rates = self._get_match_rates_for_company(company)
                ats_result = self.ats_calculator.calculate_ats_score_v2(
                    match_rates=match_rates,
                    extracted_scores=extracted_scores
                )
                # Convert to dict format for consistency
                ats_result = {
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                    "final_ats_score": ats_result["final_ats_score"],
                    "category_status": ats_result["category_status"],
                    "recommendation": ats_result["recommendation"],
                    "breakdown": ats_result["breakdown"],
                    "scoring_version": ats_result.get("scoring_version", "v2_65_35_split")
                }
                
                # Add ATS results to minimal results
                minimal_results["ats_results"] = ats_result
                
                return minimal_results
            
            matched_skills = self._read_matched_skills(company)
            
            # Run component analyses with feature-flagged fallback
            component_results = await self._run_component_analyses_with_fallback(cv_text, jd_text, matched_skills, company)
            
            # Extract scores
            scores = self._extract_scores(component_results)
            
            # Validate consistency across analyzers
            logger.info("[ASSEMBLER] Validating cross-analyzer consistency...")
            consistency_results = self.consistency_validator.validate_cross_analyzer_consistency(component_results)
            
            if not consistency_results["is_consistent"]:
                logger.warning("[ASSEMBLER] Inconsistencies detected in analysis results")
                logger.warning(f"[ASSEMBLER] Confidence score: {consistency_results['confidence_score']}%")
                for recommendation in consistency_results["recommendations"]:
                    logger.warning(f"[ASSEMBLER] Recommendation: {recommendation}")
            
            # Save results
            self._save_results(company, component_results, scores)
            
            # Run ATS calculation after component analysis (v2 only)
            logger.info("[ASSEMBLER] Starting ATS score calculation (v2 - 65/35 split)")
            ats_result = None
            try:
                match_rates = self._get_match_rates_for_company(company)
                logger.info(f"[ASSEMBLER] Match rates: tech={match_rates.get('technical_skills_match_rate', 0):.1f}%, domain={match_rates.get('domain_keywords_match_rate', 0):.1f}%, soft={match_rates.get('soft_skills_match_rate', 0):.1f}%")
                logger.info(f"[ASSEMBLER] Missing counts: tech={match_rates.get('technical_missing_count', 0)}, domain={match_rates.get('domain_missing_count', 0)}, soft={match_rates.get('soft_missing_count', 0)}")
                
                ats_result = self.ats_calculator.calculate_ats_score_v2(
                    match_rates=match_rates,
                    extracted_scores=scores
                )
                logger.info(f"[ASSEMBLER] ATS v2 calculated: {ats_result['final_ats_score']}/100")
                
                # Verify missing_counts are included
                missing_counts = ats_result.get('breakdown', {}).get('category1', {}).get('missing_counts')
                if missing_counts:
                    logger.info(f"[ASSEMBLER] ✅ Missing counts included: {missing_counts}")
                else:
                    logger.warning("[ASSEMBLER] ⚠️ Missing counts NOT found in breakdown!")
                
                # Persist ATS v2 result to the same file structure
                company_dir = self.base_dir / "applied_companies" / company
                file_path = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
                if not file_path:
                    file_path = company_dir / f"{company}_skills_analysis.json"
                try:
                    existing = {}
                    if file_path.exists():
                        with open(file_path, "r", encoding="utf-8") as f:
                            existing = json.load(f)
                    if "ats_calculation_entries" not in existing:
                        existing["ats_calculation_entries"] = []
                    ats_entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                        "final_ats_score": ats_result["final_ats_score"],
                        "category_status": ats_result["category_status"],
                        "recommendation": ats_result["recommendation"],
                        "breakdown": ats_result["breakdown"],
                        "scoring_version": ats_result.get("scoring_version", "v2_65_35_split")
                    }
                    existing["ats_calculation_entries"].append(ats_entry)
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(existing, f, indent=2, ensure_ascii=False)
                    logger.info(f"[ASSEMBLER] ✅ ATS v2 result persisted to {file_path}")
                    logger.info(f"[ASSEMBLER] ATS entry saved with breakdown keys: {list(ats_entry['breakdown'].keys())}")
                    logger.info(f"[ASSEMBLER] Category1 keys in saved entry: {list(ats_entry['breakdown'].get('category1', {}).keys())}")
                except Exception as e:
                    logger.error("[ASSEMBLER] Failed to persist ATS v2 calculation: %s", e, exc_info=True)
                    raise
            except Exception as e:
                logger.error(f"[ASSEMBLER] ❌ ATS calculation failed: {e}", exc_info=True)
                # Don't raise - allow component analysis to complete even if ATS fails
                logger.warning("[ASSEMBLER] Continuing without ATS score due to calculation error")
            
            # Prepare return result
            result = {
                "company": company,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                "component_results": component_results,
                "extracted_scores": scores,
                "ats_results": ats_result,
                "consistency_validation": consistency_results,
                "status": "success"
            }
            
            # Log ATS result availability for debugging
            if ats_result:
                logger.info(f"[ASSEMBLER] ✅ ATS result included in response: score={ats_result.get('final_ats_score')}")
            else:
                logger.warning("[ASSEMBLER] ⚠️ ATS result not available in response")
            
            logger.info(
                "===== [ASSEMBLER] Completed assembly. Scores: skills=%.1f exp=%.1f industry=%.1f seniority=%.1f tech=%.1f =====",
                scores.get("skills_relevance", 0),
                scores.get("experience_alignment", 0),
                scores.get("industry_fit", 0),
                scores.get("role_seniority", 0),
                scores.get("technical_depth", 0)
            )
            
            return result
            
        except Exception as e:
            logger.error("[ASSEMBLER] Assembly failed for %s: %s", company, str(e))
            raise


# Global instance removed - service now requires user_email parameter
# Create instances per request with proper user context
