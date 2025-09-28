"""
ATS Component Assembler

Assembles individual component analyses into a unified ATS analysis result.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from app.utils.timestamp_utils import TimestampUtils

from app.services.ats.components import (
    SkillsAnalyzer,
    ExperienceAnalyzer,
    IndustryAnalyzer,
    SeniorityAnalyzer,
    TechnicalAnalyzer
)
from app.services.ats.components.consistency_validator import ConsistencyValidator
from app.services.ats.components.batched_analyzer import BatchedAnalyzer
from app.services.ats.requirement_bonus_calculator import RequirementBonusCalculator
from app.services.jd_analysis.jd_analyzer import RequirementsExtractor
from app.services.ats.ats_score_calculator import ATSScoreCalculator

logger = logging.getLogger(__name__)


class ComponentAssembler:
    """Assembles individual component analyses into unified results."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir: Path = base_dir or Path("cv-analysis")
        
        # Initialize analyzers
        self.skills_analyzer = SkillsAnalyzer()
        self.experience_analyzer = ExperienceAnalyzer()
        self.industry_analyzer = IndustryAnalyzer()
        self.seniority_analyzer = SeniorityAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.batched_analyzer = BatchedAnalyzer()  # New batched analyzer for performance
        self.bonus_calculator = RequirementBonusCalculator()
        self.requirements_extractor = RequirementsExtractor()
        self.ats_calculator = ATSScoreCalculator()
        self.consistency_validator = ConsistencyValidator()

    def _read_cv_text(self, company_name: str = "Unknown", jd_url: str = "") -> str:
        """Read CV text from the appropriate CV based on JD usage history."""
        from app.unified_latest_file_selector import unified_selector
        
        logger.info("🔍 [COMPONENT_ASSEMBLER] Selecting appropriate CV based on JD usage")
        cv_context = unified_selector.get_latest_cv_for_company(company_name, jd_url, "")
        
        if not cv_context.exists:
            raise FileNotFoundError(f"No CV found for company: {company_name}")
        
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
        
        logger.info(f"📄 [COMPONENT_ASSEMBLER] Selected CV content")
        logger.info(f"📊 [COMPONENT_ASSEMBLER] Content length: {len(cv_content)} chars")
        
        return cv_content

    def _read_jd_text(self, company: str) -> str:
        """Read JD text for a specific company."""
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
        # Use timestamped file with robust fallback to newest by mtime
        from app.utils.timestamp_utils import TimestampUtils
        company_dir = self.base_dir / "applied_companies" / company
        match_file = TimestampUtils.find_latest_timestamped_file(company_dir, "cv_jd_match_results", "json")
        try:
            # Scan all possible files and choose newest by modification time
            candidates = list(company_dir.glob("cv_jd_match_results*.json"))
            if candidates:
                newest = max(candidates, key=lambda p: p.stat().st_mtime)
                if not match_file or newest.stat().st_mtime > match_file.stat().st_mtime:
                    match_file = newest
        except Exception:
            # Fallback to non-timestamped file if no timestamped file exists
            if not match_file:
                match_file = company_dir / "cv_jd_match_results.json"
        
        try:
            if not match_file or not match_file.exists():
                logger.warning("[ASSEMBLER] Match results not found for bonus calculation: %s", match_file)
                return {
                    "match_counts": {
                        "total_required_keywords": 0,
                        "total_preferred_keywords": 0,
                        "matched_required_count": 0,
                        "matched_preferred_count": 0,
                        "missing_required": 0,
                        "missing_preferred": 0,
                    },
                    "bonus_breakdown": {
                        "required_bonus": 0.0,
                        "required_penalty": 0.0,
                        "preferred_bonus": 0.0,
                        "preferred_penalty": 0.0,
                        "total_bonus": 0.0,
                    },
                    "coverage_metrics": {
                        "required_coverage": 0.0,
                        "preferred_coverage": 0.0,
                    },
                }
            
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
            return {
                "match_counts": {
                    "total_required_keywords": 0,
                    "total_preferred_keywords": 0,
                    "matched_required_count": 0,
                    "matched_preferred_count": 0,
                    "missing_required": 0,
                    "missing_preferred": 0,
                },
                "bonus_breakdown": {
                    "required_bonus": 0.0,
                    "required_penalty": 0.0,
                    "preferred_bonus": 0.0,
                    "preferred_penalty": 0.0,
                    "total_bonus": 0.0,
                },
                "coverage_metrics": {
                    "required_coverage": 0.0,
                    "preferred_coverage": 0.0,
                },
            }

    async def _run_batched_component_analyses(self, cv_text: str, jd_text: str, matched_skills: str, company: str) -> Dict[str, Any]:
        """Run component analyses using batched approach (2 LLM calls instead of 5)."""
        logger.info("[ASSEMBLER] Starting batched component analyses (Performance Optimization)...")
        
        try:
            # Run batched analysis (2 LLM calls instead of 5)
            batched_result = await self.batched_analyzer.analyze_all_batched(cv_text, jd_text, matched_skills)
            
            # Run bonus calculation in parallel
            bonus_task = asyncio.get_event_loop().run_in_executor(
                None, self._calculate_requirement_bonus, company
            )
            
            # Wait for bonus calculation
            bonus_result = await bonus_task
            
            # Structure results to match the expected format
            results = {
                "skills": batched_result["skills"],
                "experience": batched_result["experience"],
                "industry": batched_result["industry"],
                "seniority": batched_result["seniority"],
                "technical": batched_result["technical"],
                "requirement_bonus": bonus_result
            }
            
            logger.info("[ASSEMBLER] Batched component analyses completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"[ASSEMBLER] Batched analysis failed: {e}")
            # Fallback to individual analyses if batched approach fails
            logger.info("[ASSEMBLER] Falling back to individual component analyses...")
            return await self._run_component_analyses(cv_text, jd_text, matched_skills, company)

    async def _run_component_analyses(self, cv_text: str, jd_text: str, matched_skills: str, company: str) -> Dict[str, Any]:
        """Run all component analyses in parallel."""
        logger.info("[ASSEMBLER] Starting parallel component analyses...")
        
        # Run all analyses in parallel
        skills_task = self.skills_analyzer.analyze(cv_text, jd_text, matched_skills)
        experience_task = self.experience_analyzer.analyze(cv_text, jd_text)
        industry_task = self.industry_analyzer.analyze(cv_text, jd_text)
        seniority_task = self.seniority_analyzer.analyze(cv_text, jd_text)
        technical_task = self.technical_analyzer.analyze(cv_text, jd_text)
        
        # Run bonus calculation in parallel (synchronous but wrapped in asyncio)
        bonus_task = asyncio.get_event_loop().run_in_executor(
            None, self._calculate_requirement_bonus, company
        )
        
        # Wait for all to complete
        skills_result, experience_result, industry_result, seniority_result, technical_result, bonus_result = await asyncio.gather(
            skills_task,
            experience_task,
            industry_task,
            seniority_task,
            technical_task,
            bonus_task,
            return_exceptions=True
        )
        
        # Check for exceptions
        results = {
            "skills": skills_result,
            "experience": experience_result,
            "industry": industry_result,
            "seniority": seniority_result,
            "technical": technical_result,
            "requirement_bonus": bonus_result
        }
        
        for component, result in results.items():
            if isinstance(result, Exception):
                logger.error("[ASSEMBLER] %s analysis failed: %s", component.title(), str(result))
                raise result
        
        logger.info("[ASSEMBLER] All component analyses completed successfully")
        return results

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
        
        # Role seniority - include detailed scores
        if "seniority_analysis" in component_results["seniority"]:
            seniority_analysis = component_results["seniority"]["seniority_analysis"]
            if "seniority_score" in seniority_analysis:
                scores["role_seniority"] = float(seniority_analysis["seniority_score"])
            if "experience_match_percentage" in seniority_analysis:
                scores["experience_match_percentage"] = float(seniority_analysis["experience_match_percentage"])
            if "responsibility_fit_percentage" in seniority_analysis:
                scores["responsibility_fit_percentage"] = float(seniority_analysis["responsibility_fit_percentage"])
            if "leadership_readiness_score" in seniority_analysis:
                scores["leadership_readiness_score"] = float(seniority_analysis["leadership_readiness_score"])
            if "growth_trajectory_score" in seniority_analysis:
                scores["growth_trajectory_score"] = float(seniority_analysis["growth_trajectory_score"])
        
        # Technical depth - include detailed scores
        if "technical_analysis" in component_results["technical"]:
            technical_analysis = component_results["technical"]["technical_analysis"]
            if "technical_depth_score" in technical_analysis:
                scores["technical_depth"] = float(technical_analysis["technical_depth_score"])
            if "core_skills_match_percentage" in technical_analysis:
                scores["core_skills_match_percentage"] = float(technical_analysis["core_skills_match_percentage"])
            if "technical_stack_fit_percentage" in technical_analysis:
                scores["technical_stack_fit_percentage"] = float(technical_analysis["technical_stack_fit_percentage"])
            if "complexity_readiness_score" in technical_analysis:
                scores["complexity_readiness_score"] = float(technical_analysis["complexity_readiness_score"])
            if "learning_agility_score" in technical_analysis:
                scores["learning_agility_score"] = float(technical_analysis["learning_agility_score"])
            if "jd_problem_complexity" in technical_analysis:
                scores["jd_problem_complexity"] = float(technical_analysis["jd_problem_complexity"])
        
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

    async def _run_ats_calculation(self, company: str, extracted_scores: Dict[str, float]) -> Dict[str, Any]:
        """Run ATS score calculation and save results."""
        try:
            # Read preextracted comparison data
            # Use timestamped analysis file with fallback
            from app.utils.timestamp_utils import TimestampUtils
            company_dir = self.base_dir / "applied_companies" / company
            file_path = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
            if not file_path:
                file_path = company_dir / f"{company}_skills_analysis.json"
            if not file_path.exists():
                logger.warning("[ASSEMBLER] Skills analysis file not found for ATS calculation")
                return {"error": "Skills analysis file not found"}
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Get the latest preextracted comparison entry
            preextracted_entries = data.get("preextracted_comparison_entries", [])
            if not preextracted_entries:
                logger.warning("[ASSEMBLER] No preextracted comparison found for ATS calculation")
                return {"error": "No preextracted comparison data"}
            
            latest_preextracted = preextracted_entries[-1]
            preextracted_data = {"content": latest_preextracted.get("content", "")}
            
            # Calculate ATS score
            ats_breakdown = self.ats_calculator.calculate_ats_score(
                preextracted_data=preextracted_data,
                component_analysis={},  # Not used in current implementation
                extracted_scores=extracted_scores
            )
            
            # Convert to dictionary for saving
            ats_result = {
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                "final_ats_score": ats_breakdown.final_ats_score,
                "category_status": ats_breakdown.category_status,
                "recommendation": ats_breakdown.recommendation,
                "breakdown": {
                    "category1": {
                        "score": ats_breakdown.cat1_score,
                        "technical_skills_match_rate": ats_breakdown.technical_skills_match_rate,
                        "domain_keywords_match_rate": ats_breakdown.domain_keywords_match_rate,
                        "soft_skills_match_rate": ats_breakdown.soft_skills_match_rate,
                        "missing_counts": {
                            "technical": ats_breakdown.technical_missing_count,
                            "domain": ats_breakdown.domain_missing_count,
                            "soft": ats_breakdown.soft_missing_count
                        }
                    },
                    "category2": {
                        "score": ats_breakdown.cat2_score,
                        "core_competency_avg": ats_breakdown.core_competency_avg,
                        "experience_seniority_avg": ats_breakdown.experience_seniority_avg,
                        "potential_ability_avg": ats_breakdown.potential_ability_avg,
                        "company_fit_avg": ats_breakdown.company_fit_avg
                    },
                    "ats1_score": ats_breakdown.ats1_score,
                    "bonus_points": ats_breakdown.bonus_points
                }
            }
            
            # Save ATS results to the analysis file
            if "ats_calculation_entries" not in data:
                data["ats_calculation_entries"] = []
            
            data["ats_calculation_entries"].append(ats_result)
            
            # Save back to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("[ASSEMBLER] ATS calculation completed. Score: %.1f/100 (%s)", 
                       ats_breakdown.final_ats_score, ats_breakdown.category_status)
            
            # Create recommendation file after ATS calculation is completed
            try:
                from app.services.ats_recommendation_service import ats_recommendation_service
                recommendation_created = ats_recommendation_service.create_recommendation_file(company)
                
                if recommendation_created:
                    logger.info("[ASSEMBLER] Recommendation file created for %s", company)
                else:
                    logger.warning("[ASSEMBLER] Failed to create recommendation file for %s", company)
            except Exception as e:
                logger.error("[ASSEMBLER] Error creating recommendation file for %s: %s", company, e)
            
            return ats_result
            
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
                return self._generate_minimal_cv_results(minimal_analysis, company)
            
            matched_skills = self._read_matched_skills(company)
            
            # Run component analyses
            component_results = await self._run_component_analyses(cv_text, jd_text, matched_skills, company)
            
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
            
            # Run ATS calculation after component analysis
            logger.info("[ASSEMBLER] Starting ATS score calculation...")
            ats_result = await self._run_ats_calculation(company, scores)
            
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


# Global instance
component_assembler = ComponentAssembler()
