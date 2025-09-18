"""
Enhanced ATS Analysis Orchestrator

Integrates all the enhanced components to provide consistent, improved ATS analysis:
1. Centralized Requirements Extractor
2. Enhanced Skills Matcher with semantic equivalence
3. Industry Alignment Scorer with realistic transitions  
4. ATS Score Calculator with structured framework
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from ..requirements.centralized_requirements_extractor import CentralizedRequirementsExtractor, RequirementsExtraction
from ..matching.enhanced_skills_matcher import EnhancedSkillsMatcher, SkillAnalysis
from ..matching.industry_alignment_scorer import IndustryAlignmentScorer, IndustryAlignment  
from .ats_score_calculator import ATSScoreCalculator, ATSScoreBreakdown

logger = logging.getLogger(__name__)


@dataclass 
class EnhancedATSResults:
    """Complete enhanced ATS analysis results"""
    
    # Core scoring
    final_ats_score: float
    ats_breakdown: ATSScoreBreakdown
    
    # Requirements analysis
    requirements_extraction: RequirementsExtraction
    
    # Skills matching
    skills_analysis: Dict[str, SkillAnalysis]  # technical, soft, domain
    
    # Industry alignment
    industry_alignment: IndustryAlignment
    
    # Summary insights
    key_strengths: List[str]
    critical_gaps: List[str]
    improvement_recommendations: List[str]
    overall_assessment: str
    
    # Metadata
    analysis_version: str
    processing_time_ms: int
    confidence_score: float


class EnhancedATSOrchestrator:
    """
    Orchestrates the enhanced ATS analysis workflow using improved components
    """
    
    def __init__(self):
        self.requirements_extractor = CentralizedRequirementsExtractor()
        self.skills_matcher = EnhancedSkillsMatcher() 
        self.industry_scorer = IndustryAlignmentScorer()
        self.ats_calculator = ATSScoreCalculator()
        
        self.analysis_version = "2.0-enhanced"
    
    def _extract_cv_data(self, cv_content: str) -> Dict[str, Any]:
        """Extract structured data from CV content"""
        
        # Simple extraction - in production, this would be more sophisticated
        cv_data = {
            "technical_skills": [],
            "soft_skills": [],
            "experience_descriptions": [],
            "years_experience": 0
        }
        
        # Basic pattern matching for skills and experience
        import re
        
        # Extract technical skills (basic patterns)
        tech_patterns = [
            r'\b(?i)(python|java|javascript|typescript|sql|excel|tableau|aws|azure)\b',
            r'\b(?i)(react|angular|django|flask|docker|kubernetes)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, cv_content, re.IGNORECASE)
            cv_data["technical_skills"].extend([m.lower() for m in matches])
        
        # Extract soft skills
        soft_patterns = [
            r'\b(?i)(leadership|management|communication|teamwork|organized|analytical)\b',
            r'\b(?i)(problem.solving|adaptability|presentation)\b'
        ]
        
        for pattern in soft_patterns:
            matches = re.findall(pattern, cv_content, re.IGNORECASE)
            cv_data["soft_skills"].extend([m.lower().replace('.', ' ') for m in matches])
        
        # Extract experience descriptions (sentences mentioning work/role/company)
        experience_patterns = [
            r'[A-Z][^.!?]*(?:worked|managed|developed|led|implemented|designed)[^.!?]*[.!?]',
            r'[A-Z][^.!?]*(?:experience|role|position|company|team)[^.!?]*[.!?]'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, cv_content)
            cv_data["experience_descriptions"].extend(matches)
        
        # Extract years of experience (basic)
        years_pattern = r'(\d+)(?:\+)?\s*(?:years?|yrs?)'
        years_matches = re.findall(years_pattern, cv_content, re.IGNORECASE)
        if years_matches:
            cv_data["years_experience"] = max([int(y) for y in years_matches])
        
        # Remove duplicates
        cv_data["technical_skills"] = list(set(cv_data["technical_skills"]))
        cv_data["soft_skills"] = list(set(cv_data["soft_skills"]))
        
        logger.info(f"[Enhanced ATS] Extracted CV data - Tech skills: {len(cv_data['technical_skills'])}, "
                   f"Soft skills: {len(cv_data['soft_skills'])}, Experience years: {cv_data['years_experience']}")
        
        return cv_data
    
    def _generate_insights(
        self, 
        ats_breakdown: ATSScoreBreakdown,
        skills_analysis: Dict[str, SkillAnalysis],
        industry_alignment: IndustryAlignment
    ) -> Tuple[List[str], List[str], List[str], str]:
        """Generate key insights from the analysis"""
        
        key_strengths = []
        critical_gaps = []
        recommendations = []
        
        # Analyze strengths
        if ats_breakdown.technical_skills_match_rate > 70:
            key_strengths.append("Strong technical skills alignment")
        
        if ats_breakdown.soft_skills_match_rate > 80:
            key_strengths.append("Excellent soft skills match")
        
        if industry_alignment.transition_difficulty > 0.7:
            key_strengths.append(f"Natural industry fit ({industry_alignment.source_industry} → {industry_alignment.target_industry})")
        
        # Add transferable advantages
        if industry_alignment.transferable_advantages:
            key_strengths.extend(industry_alignment.transferable_advantages[:2])
        
        # Analyze gaps  
        if ats_breakdown.technical_missing_count > 5:
            critical_gaps.append(f"Missing {ats_breakdown.technical_missing_count} key technical skills")
        
        if ats_breakdown.soft_missing_count > 3:
            critical_gaps.append(f"Missing {ats_breakdown.soft_missing_count} important soft skills")
        
        # Add industry transition gaps
        if industry_alignment.key_gaps:
            critical_gaps.extend(industry_alignment.key_gaps[:2])
        
        # Generate recommendations
        if ats_breakdown.final_ats_score < 60:
            recommendations.append("Focus on developing missing technical skills")
            recommendations.append("Consider highlighting transferable experience")
        elif ats_breakdown.final_ats_score < 75:
            recommendations.append("Emphasize relevant project experience")
            recommendations.append("Address key skill gaps through training")
        else:
            recommendations.append("Strong candidate - highlight unique value proposition")
        
        # Add industry-specific recommendations
        if industry_alignment.transition_category == "Difficult":
            recommendations.append("Consider informational interviews in target industry")
            recommendations.append("Highlight relevant transferable skills prominently")
        
        # Overall assessment
        if ats_breakdown.final_ats_score >= 80:
            overall_assessment = "Excellent candidate with strong alignment"
        elif ats_breakdown.final_ats_score >= 65:
            overall_assessment = "Good candidate with addressable gaps"
        elif ats_breakdown.final_ats_score >= 50:
            overall_assessment = "Moderate fit requiring skill development"
        else:
            overall_assessment = "Significant gaps requiring substantial preparation"
        
        return key_strengths[:4], critical_gaps[:4], recommendations[:4], overall_assessment
    
    def _calculate_confidence_score(
        self,
        requirements_extraction: RequirementsExtraction,
        skills_analysis: Dict[str, SkillAnalysis],
        industry_alignment: IndustryAlignment
    ) -> float:
        """Calculate confidence score for the analysis"""
        
        confidence_factors = []
        
        # Requirements extraction confidence
        if requirements_extraction.total_requirements > 10:
            confidence_factors.append(0.9)  # Good requirement extraction
        elif requirements_extraction.total_requirements > 5:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)  # Limited requirements
        
        # Skills matching confidence
        total_skills_analyzed = sum(
            len(analysis.matched_skills) + len(analysis.missing_skills) 
            for analysis in skills_analysis.values()
        )
        
        if total_skills_analyzed > 15:
            confidence_factors.append(0.85)
        elif total_skills_analyzed > 8:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.6)
        
        # Industry alignment confidence
        if industry_alignment.source_industry != "unknown" and industry_alignment.target_industry != "unknown":
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def analyze_cv_job_fit(
        self,
        cv_content: str,
        job_description: str,
        company_info: str = "",
        current_industry: str = ""
    ) -> EnhancedATSResults:
        """
        Perform comprehensive enhanced ATS analysis
        
        Args:
            cv_content: Full CV/resume text content
            job_description: Complete job description
            company_info: Additional company information
            current_industry: Candidate's current industry (if known)
            
        Returns:
            EnhancedATSResults with complete analysis
        """
        import time
        start_time = time.time()
        
        logger.info("[Enhanced ATS] Starting comprehensive ATS analysis")
        
        try:
            # Step 1: Extract requirements using centralized extractor
            logger.info("[Enhanced ATS] Step 1: Extracting requirements")
            requirements_extraction = self.requirements_extractor.extract_requirements(
                job_description, company_info
            )
            
            # Step 2: Extract CV data
            logger.info("[Enhanced ATS] Step 2: Extracting CV data")  
            cv_data = self._extract_cv_data(cv_content)
            
            # Step 3: Perform enhanced skills matching
            logger.info("[Enhanced ATS] Step 3: Enhanced skills matching")
            requirement_lists = self.requirements_extractor.get_requirement_lists_for_matching(requirements_extraction)
            
            cv_skills = {
                "technical": cv_data["technical_skills"],
                "soft": cv_data["soft_skills"],
                "domain": []  # Could be extracted from experience
            }
            
            skills_analysis = self.skills_matcher.analyze_skills(cv_skills, requirement_lists)
            
            # Step 4: Industry alignment assessment
            logger.info("[Enhanced ATS] Step 4: Industry alignment assessment")
            industry_alignment = self.industry_scorer.assess_industry_alignment(
                cv_experience=cv_data["experience_descriptions"],
                cv_skills=cv_data["technical_skills"] + cv_data["soft_skills"],
                jd_text=job_description,
                company_info=company_info,
                years_experience=cv_data["years_experience"],
                current_industry=current_industry
            )
            
            # Step 5: Calculate ATS score
            logger.info("[Enhanced ATS] Step 5: ATS score calculation")
            
            # Prepare mock preextracted data (normally from previous analysis)
            preextracted_data = {
                "content": f"Technical Skills Match Rate: {skills_analysis.get('technical', type('', (), {'match_rate': 0})).match_rate * 100:.0f}%\\n" +
                          f"Soft Skills Match Rate: {skills_analysis.get('soft', type('', (), {'match_rate': 0})).match_rate * 100:.0f}%\\n" +
                          f"Domain Keywords Match Rate: {skills_analysis.get('domain', type('', (), {'match_rate': 0})).match_rate * 100:.0f}%\\n" +
                          f"MISSING FROM CV - Technical: {len(skills_analysis.get('technical', type('', (), {'missing_skills': []})).missing_skills)} items\\n" +
                          f"MISSING FROM CV - Soft: {len(skills_analysis.get('soft', type('', (), {'missing_skills': []})).missing_skills)} items\\n" +
                          f"MISSING FROM CV - Domain: {len(skills_analysis.get('domain', type('', (), {'missing_skills': []})).missing_skills)} items"
            }
            
            # Extract scores for ATS calculation
            extracted_scores = {
                "technical_depth": 75.0,  # Default values - would be calculated by component analyzers
                "core_skills_match_percentage": skills_analysis.get('technical', type('', (), {'match_rate': 0})).match_rate * 100,
                "technical_stack_fit_percentage": 70.0,
                "data_familiarity_score": 65.0,
                
                "experience_alignment": industry_alignment.experience_relevance_score,
                "experience_match_percentage": 70.0,
                "responsibility_fit_percentage": 75.0,
                "role_seniority": 80.0,
                "leadership_readiness_score": 70.0,
                
                "growth_trajectory_score": 75.0,
                "complexity_readiness_score": 70.0,
                "learning_agility_score": 80.0,
                "jd_problem_complexity": 7.0,
                
                "industry_fit": industry_alignment.overall_fit_score,
                "domain_overlap_percentage": industry_alignment.domain_overlap_score,
                "stakeholder_fit_score": 70.0,
                "business_cycle_alignment": 75.0,
                
                "requirement_bonus": 0.0  # No bonus points for now
            }
            
            ats_breakdown = self.ats_calculator.calculate_ats_score(
                preextracted_data=preextracted_data,
                component_analysis={},  # Not used in current implementation
                extracted_scores=extracted_scores
            )
            
            # Step 6: Generate insights
            logger.info("[Enhanced ATS] Step 6: Generating insights")
            key_strengths, critical_gaps, recommendations, overall_assessment = self._generate_insights(
                ats_breakdown, skills_analysis, industry_alignment
            )
            
            # Step 7: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                requirements_extraction, skills_analysis, industry_alignment
            )
            
            # Create final results
            processing_time = int((time.time() - start_time) * 1000)
            
            results = EnhancedATSResults(
                final_ats_score=ats_breakdown.final_ats_score,
                ats_breakdown=ats_breakdown,
                requirements_extraction=requirements_extraction,
                skills_analysis=skills_analysis,
                industry_alignment=industry_alignment,
                key_strengths=key_strengths,
                critical_gaps=critical_gaps,
                improvement_recommendations=recommendations,
                overall_assessment=overall_assessment,
                analysis_version=self.analysis_version,
                processing_time_ms=processing_time,
                confidence_score=confidence_score
            )
            
            logger.info(f"[Enhanced ATS] Analysis complete - Final Score: {ats_breakdown.final_ats_score:.1f}/100, "
                       f"Processing Time: {processing_time}ms, Confidence: {confidence_score:.1%}")
            
            return results
            
        except Exception as e:
            logger.error(f"[Enhanced ATS] Error in analysis: {e}")
            # Return minimal results on error
            processing_time = int((time.time() - start_time) * 1000)
            return EnhancedATSResults(
                final_ats_score=0.0,
                ats_breakdown=ATSScoreBreakdown(
                    technical_skills_match_rate=0, domain_keywords_match_rate=0, soft_skills_match_rate=0, cat1_score=0,
                    core_competency_avg=0, experience_seniority_avg=0, potential_ability_avg=0, company_fit_avg=0, cat2_score=0,
                    ats1_score=0, bonus_points=0, final_ats_score=0,
                    category_status="❌ Analysis Error", recommendation="Please retry analysis",
                    technical_missing_count=0, soft_missing_count=0, domain_missing_count=0
                ),
                requirements_extraction=RequirementsExtraction(
                    required_skills=[], preferred_skills=[], nice_to_have_skills=[],
                    technical_skills=[], soft_skills=[], domain_keywords=[], tools_and_platforms=[],
                    years_experience_required=0, education_requirements=[], certifications=[],
                    total_requirements=0, priority_weights={}
                ),
                skills_analysis={},
                industry_alignment=IndustryAlignment(
                    source_industry="unknown", target_industry="unknown", transition_difficulty=0,
                    domain_overlap_score=0, skill_transferability_score=0, experience_relevance_score=0,
                    overall_fit_score=0, transition_category="Unknown", key_gaps=[], transferable_advantages=[]
                ),
                key_strengths=[],
                critical_gaps=["Analysis error occurred"],
                improvement_recommendations=["Please retry the analysis"],
                overall_assessment="Analysis error - please retry",
                analysis_version=self.analysis_version,
                processing_time_ms=processing_time,
                confidence_score=0.0
            )
    
    async def run_enhanced_analysis(self, company_name: str) -> Dict[str, Any]:
        """
        Run enhanced ATS analysis for a specific company and save results to the analysis file
        
        Args:
            company_name: Company name to analyze
            
        Returns:
            Dictionary with ATS analysis results
        """
        try:
            logger.info(f"[Enhanced ATS] Starting analysis for company: {company_name}")
            
            # Define paths with dynamic CV selection
            from app.services.dynamic_cv_selector import dynamic_cv_selector
            
            base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
            company_dir = base_dir / company_name
            analysis_file = company_dir / f"{company_name}_skills_analysis.json"
            
            # Use dynamic CV selection for the latest CV file
            latest_cv_paths = dynamic_cv_selector.get_latest_cv_paths_for_services()
            cv_file = Path(latest_cv_paths['txt_path']) if latest_cv_paths['txt_path'] else None
            jd_file = company_dir / "jd_original.json"
            
            logger.info(f"📄 [Enhanced ATS] Using dynamic CV from {latest_cv_paths['txt_source']} folder: {cv_file}")
            
            # Check if required files exist
            if not analysis_file.exists():
                logger.error(f"[Enhanced ATS] Analysis file not found: {analysis_file}")
                return {"error": "Analysis file not found"}
            
            if not cv_file.exists():
                logger.error(f"[Enhanced ATS] CV file not found: {cv_file}")
                return {"error": "CV file not found"}
            
            if not jd_file.exists():
                logger.error(f"[Enhanced ATS] JD file not found: {jd_file}")
                return {"error": "JD file not found"}
            
            # Read existing analysis data
            with open(analysis_file, 'r') as f:
                existing_analysis = json.load(f)
            
            # Read CV content
            with open(cv_file, 'r') as f:
                cv_content = f.read()
            
            # Read JD content
            with open(jd_file, 'r') as f:
                jd_data = json.load(f)
                job_description = jd_data.get('text', '')
            
            # Run enhanced ATS analysis
            results = self.analyze_cv_job_fit(
                cv_content=cv_content,
                job_description=job_description,
                company_info=company_name,
                current_industry="Data Science and Analytics"  # Default, could be extracted
            )
            
            # Convert results to dictionary for JSON serialization
            ats_results_dict = self.export_results_json(results)
            
            # Add ATS results to existing analysis
            if 'ats_analysis' not in existing_analysis:
                existing_analysis['ats_analysis'] = {}
            
            existing_analysis['ats_analysis'] = {
                "timestamp": results.analysis_version,
                "final_ats_score": results.final_ats_score,
                "category_status": results.ats_breakdown.category_status,
                "recommendation": results.ats_breakdown.recommendation,
                "technical_skills_match_rate": results.ats_breakdown.technical_skills_match_rate,
                "soft_skills_match_rate": results.ats_breakdown.soft_skills_match_rate,
                "domain_keywords_match_rate": results.ats_breakdown.domain_keywords_match_rate,
                "cat1_score": results.ats_breakdown.cat1_score,
                "cat2_score": results.ats_breakdown.cat2_score,
                "bonus_points": results.ats_breakdown.bonus_points,
                "technical_missing_count": results.ats_breakdown.technical_missing_count,
                "soft_missing_count": results.ats_breakdown.soft_missing_count,
                "domain_missing_count": results.ats_breakdown.domain_missing_count,
                "key_strengths": results.key_strengths,
                "critical_gaps": results.critical_gaps,
                "improvement_recommendations": results.improvement_recommendations,
                "overall_assessment": results.overall_assessment,
                "processing_time_ms": results.processing_time_ms,
                "confidence_score": results.confidence_score,
                "analysis_version": results.analysis_version
            }
            
            # Save updated analysis back to file
            with open(analysis_file, 'w') as f:
                json.dump(existing_analysis, f, indent=2, default=str)
            
            logger.info(f"[Enhanced ATS] ATS analysis saved to {analysis_file}")
            logger.info(f"[Enhanced ATS] Final ATS Score: {results.final_ats_score:.1f}/100 ({results.ats_breakdown.category_status})")
            
            # Create recommendation file after ATS analysis is completed
            try:
                from ..ats_recommendation_service import ats_recommendation_service
                recommendation_created = ats_recommendation_service.create_recommendation_file(company_name)
                
                if recommendation_created:
                    logger.info(f"[Enhanced ATS] Recommendation file created for {company_name}")
                else:
                    logger.warning(f"[Enhanced ATS] Failed to create recommendation file for {company_name}")
            except Exception as e:
                logger.error(f"[Enhanced ATS] Error creating recommendation file for {company_name}: {e}")
            
            return ats_results_dict
            
        except Exception as e:
            logger.error(f"[Enhanced ATS] Error in run_enhanced_analysis: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    def export_results_json(self, results: EnhancedATSResults, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export results to JSON format"""
        
        try:
            # Convert dataclasses to dict
            results_dict = asdict(results)
            
            # Handle non-serializable objects
            def serialize_object(obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                elif hasattr(obj, '_asdict'):
                    return obj._asdict()
                else:
                    return str(obj)
            
            # Clean up the results for JSON serialization
            def clean_for_json(data):
                if isinstance(data, dict):
                    return {k: clean_for_json(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_for_json(item) for item in data]
                elif hasattr(data, '__dict__') or hasattr(data, '_asdict'):
                    return serialize_object(data)
                else:
                    return data
            
            cleaned_results = clean_for_json(results_dict)
            
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(cleaned_results, f, indent=2, default=str)
                logger.info(f"[Enhanced ATS] Results exported to {output_path}")
            
            return cleaned_results
            
        except Exception as e:
            logger.error(f"[Enhanced ATS] Error exporting results: {e}")
            return {"error": str(e)}
