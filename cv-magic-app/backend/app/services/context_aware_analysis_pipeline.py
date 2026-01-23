"""
Context-Aware Analysis Pipeline

This service orchestrates the entire analysis pipeline with awareness of:
- Fresh analysis vs rerun scenarios
- CV version selection (original vs tailored)
- JD caching and reuse
- Intelligent processing optimization
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from app.unified_latest_file_selector import FileContext
from app.services.jd_cache_manager import jd_cache_manager, JDCacheData
from app.services.skill_extraction.skill_extraction_service import SkillExtractionService
from app.services.skill_extraction.prompt_templates import SkillCategorizer, get_skill_prompts
from app.services.cv_jd_matching.cv_jd_matcher import CVJDMatcher
from app.services.jd_analysis.jd_analyzer import JDAnalyzer
from app.services.job_extraction_service import JobExtractionService
from app.ai.ai_service import ai_service
from app.services.ats.component_assembler import ComponentAssembler
from app.services.ats_recommendation_service import ATSRecommendationService
from app.services.ai_recommendation_generator import AIRecommendationGenerator
from app.utils.timestamp_utils import TimestampUtils
from app.services.skill_extraction.preextracted_comparator import execute_skills_semantic_comparison

logger = logging.getLogger(__name__)


class AnalysisContext:
    """Container for analysis context and metadata"""
    
    def __init__(self, data: Dict[str, Any]):
        self.company: str = data.get('company', '')
        self.jd_url: str = data.get('jd_url', '')
        self.is_rerun: bool = data.get('is_rerun', False)
        self.cv_context: Optional[FileContext] = data.get('cv_context')
        self.jd_cached: bool = data.get('jd_cached', False)
        self.jd_cache_data: Optional[JDCacheData] = data.get('jd_cache_data')
        self.analysis_id: str = data.get('analysis_id', TimestampUtils.get_timestamp())
        self.started_at: str = data.get('started_at', datetime.now().isoformat())
        self.user_id: int = data.get('user_id', 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'company': self.company,
            'jd_url': self.jd_url,
            'is_rerun': self.is_rerun,
            'cv_context': self.cv_context.to_dict() if self.cv_context else None,
            'jd_cached': self.jd_cached,
            'jd_cache_stats': self.jd_cache_data.to_dict() if self.jd_cache_data else None,
            'analysis_id': self.analysis_id,
            'started_at': self.started_at,
            'user_id': self.user_id
        }


class AnalysisResults:
    """Container for complete analysis results"""
    
    def __init__(self):
        self.success: bool = False
        self.context: Optional[AnalysisContext] = None
        self.cv_skills: Dict = {}
        self.jd_skills: Dict = {}
        self.jd_analysis: Dict = {}
        self.job_info: Dict = {}
        self.cv_jd_matching: Dict = {}
        self.analyze_match_decision: Optional[Dict[str, Any]] = None  # New: analyze match decision data
        self.component_analysis: Dict = {}
        self.ats_recommendations: Dict = {}
        self.ai_recommendations: Dict = {}
        self.tailored_cv_path: Optional[str] = None
        self.processing_time: float = 0.0
        self.steps_completed: List[str] = []
        self.steps_skipped: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.requires_user_decision: bool = False  # New: flag indicating if user decision is needed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'success': self.success,
            'context': self.context.to_dict() if self.context else None,
            'results': {
                'cv_skills': self.cv_skills,
                'jd_skills': self.jd_skills,
                'jd_analysis': self.jd_analysis,
                'job_info': self.job_info,
                'cv_jd_matching': self.cv_jd_matching,
                'analyze_match_decision': self.analyze_match_decision,
                'component_analysis': self.component_analysis,
                'ats_recommendations': self.ats_recommendations,
                'ai_recommendations': self.ai_recommendations,
                'tailored_cv_path': self.tailored_cv_path
            },
            'processing_time': self.processing_time,
            'steps_completed': self.steps_completed,
            'steps_skipped': self.steps_skipped,
            'errors': self.errors,
            'warnings': self.warnings,
            'requires_user_decision': self.requires_user_decision
        }


class ContextAwareAnalysisPipeline:
    """
    Main pipeline orchestrator with context awareness
    """
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        # Initialize services with user context
        self.skill_extraction_service = SkillExtractionService()
        self.cv_jd_matcher = CVJDMatcher(user_email=user_email)
        self.jd_analyzer = JDAnalyzer(user_email=user_email)
        self.job_extractor = JobExtractionService(user_email=user_email)
        self.component_assembler = ComponentAssembler(user_email=user_email)
        self.ats_recommender = ATSRecommendationService(user_email=user_email)
        self.ai_recommender = AIRecommendationGenerator(user_email=user_email)
        
        # Initialize base directory for file operations
        from app.utils.user_path_utils import get_user_base_path
        self.base_dir = get_user_base_path(user_email)
        
        logger.info(f"🏗️ [CONTEXT_AWARE_PIPELINE] Initialized all services for user: {user_email}")
    
    async def run_full_analysis(
        self, 
        jd_url: str, 
        company: str, 
        is_rerun: bool = False,
        user_id: int = 1,
        include_tailoring: bool = True
    ) -> AnalysisResults:
        """
        Run complete analysis pipeline with context awareness
        
        Args:
            jd_url: Job description URL
            company: Company name
            is_rerun: True if this is a "Run ATS Test Again" scenario
            user_id: User ID for the analysis
            include_tailoring: Whether to include CV tailoring step
            
        Returns:
            AnalysisResults with complete analysis data
        """
        start_time = datetime.now()
        results = AnalysisResults()
        
        try:
            logger.info(f"🚀 [CONTEXT_AWARE_PIPELINE] Starting {'rerun' if is_rerun else 'fresh'} analysis")
            logger.info(f"🎯 [CONTEXT_AWARE_PIPELINE] Company: {company}, JD: {jd_url}")
            
            # Step 1: Initialize analysis context
            context = await self._initialize_context(jd_url, company, is_rerun, user_id)
            results.context = context
            
            # Step 2: CV Selection using user-specific unified selector with JD usage tracking
            from app.unified_latest_file_selector import get_selector_for_user
            user_selector = get_selector_for_user(self.user_email)
            cv_context = user_selector.get_latest_cv_for_company(company, jd_url, "")
            context.cv_context = cv_context
            
            # Record JD usage for tracking (use user-specific tracker to match unified selector)
            from app.services.jd_usage_tracker import JDUsageTracker
            # Create user-specific tracker (same as unified selector uses)
            user_jd_tracker = JDUsageTracker(self.user_email)
            # Use EXACT same logic as unified selector for matching
            effective_jd_url = jd_url if jd_url and jd_url.strip() else ""
            effective_jd_text = "" if jd_url else "default_jd_text"  # Match unified selector logic
            
            logger.info(f"🔍 [CONTEXT_AWARE_PIPELINE] Recording JD usage:")
            logger.info(f"- jd_url: {jd_url}")
            logger.info(f"- effective_jd_url: {effective_jd_url}")
            logger.info(f"- effective_jd_text: {effective_jd_text}")
            logger.info(f"- company: {company}")
            logger.info(f"- user_email: {self.user_email}")
            
            user_jd_tracker.record_jd_usage(effective_jd_url, effective_jd_text, company, "")
            
            if not cv_context.exists:
                results.errors.append(f"No CV found for company: {company}")
                return results
            
            logger.info(f"📄 [CONTEXT_AWARE_PIPELINE] Using {cv_context.file_type} CV - {cv_context.json_path}")
            
            # Step 3: JD Analysis (with caching)
            jd_data = await self._handle_jd_analysis(context, results)
            if not jd_data:
                results.errors.append("JD analysis failed")
                return results
            
            # Step 4: CV Skills Extraction (always fresh for rerun)
            cv_skills = await self._extract_cv_skills(context, results)
            if not cv_skills:
                results.errors.append("CV skills extraction failed")
                return results
            
            # Step 5: CV-JD Matching (always recalculated)
            cv_jd_matching = await self._perform_cv_jd_matching(context, cv_skills, jd_data, results)
            if not cv_jd_matching:
                results.errors.append("CV-JD matching failed")
                return results
            else:
                self._persist_cv_jd_match_results(context.company, cv_jd_matching)
            
            # Step 5.5: Analyze Match (new step for cost-saving workflow)
            analyze_match_decision = await self._perform_analyze_match(context, results)
            if analyze_match_decision:
                results.analyze_match_decision = analyze_match_decision
                results.steps_completed.append("analyze_match")
            
            # Step 6: Component Analysis
            component_analysis = await self._run_component_analysis(context, results)
            
            # Step 7: ATS Recommendations
            ats_recommendations = await self._generate_ats_recommendations(context, results)
            
            # Step 8: AI Recommendations (optional for reruns)
            if include_tailoring or not is_rerun:
                ai_recommendations = await self._generate_ai_recommendations(context, results)
                
                # Step 9: CV Tailoring (if AI recommendations successful)
                if ai_recommendations and include_tailoring:
                    tailored_cv_path = await self._generate_tailored_cv(context, results)
                    results.tailored_cv_path = tailored_cv_path
            
            # Finalize results
            results.success = True
            results.processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Analysis completed successfully in {results.processing_time:.2f}s")
            logger.info(f"📊 [CONTEXT_AWARE_PIPELINE] Steps completed: {len(results.steps_completed)}")
            logger.info(f"⚡ [CONTEXT_AWARE_PIPELINE] Steps skipped: {len(results.steps_skipped)}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] Analysis failed: {e}")
            results.errors.append(str(e))
            results.processing_time = (datetime.now() - start_time).total_seconds()
            return results
    
    async def _extract_cv_skills_from_path(self, cv_path: str, jd_url: str, user_id: int, force_refresh: bool = False) -> Dict[str, Any]:
        """Extract CV skills from a specific file path"""
        try:
            from pathlib import Path
            
            # Read CV content from file
            # Paths from unified selector are relative to app root
            cv_file = Path(cv_path)
            if not cv_file.is_absolute():
                # Resolve relative to current working directory (app root in container)
                cv_file = Path(cv_path).resolve()
                # If still doesn't exist, try relative to base_dir
                if not cv_file.exists() and hasattr(self, 'base_dir') and self.base_dir:
                    # base_dir is user/{email}/cv-analysis, so go up to app root
                    app_root = self.base_dir.parent.parent
                    cv_file = app_root / cv_path
            
            if not cv_file.exists():
                return {"error": f"CV file not found: {cv_path} (resolved to: {cv_file}, cwd: {Path.cwd()})"}
            
            with open(cv_file, 'r', encoding='utf-8') as f:
                cv_text = f.read()
            
            if not cv_text.strip():
                return {"error": "CV file is empty"}
            
            # Create user object from user_email for AI service
            from app.models.auth import UserData
            from datetime import datetime, timezone
            current_user = UserData(
                id="pipeline_user",  # Use a placeholder ID for pipeline operations
                email=self.user_email,
                name=self.user_email.split("@")[0] if self.user_email else "user",
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            # Use centralized skill extraction prompt with proper categorization rules
            skill_prompts = get_skill_prompts(
                "CV",
                cv_text,
                allow_simple=True,
                simple_mode="structured"
            )
            
            # Extend prompt with CV-SPECIFIC extraction rules + additional fields
            cv_prompt = skill_prompts["user_prompt"] + """

═══════════════════════════════════════════════════════════════
CV-SPECIFIC EXTRACTION RULES
═══════════════════════════════════════════════════════════════

**RULE 1: Parse Piped/Slashed Skills**
If you see skills separated by pipes (|) or slashes (/), extract each one:
- "Python|SQL|Machine Learning" → Extract ["Python", "SQL", "Machine Learning"]
- "Tableau/Power BI" → Extract ["Tableau", "Power BI"]

**RULE 2: Extract from Experience Descriptions**
Don't just look at skills section - extract from work experience too:

Action Verbs → Technical Skills:
- "Built CV Agent with Flutter/Dart" → Extract ["Flutter", "Dart"]
- "Implemented algorithms using PyTorch" → Extract ["PyTorch"]
- "Automated ETL pipeline" → Extract ["ETL", "pipeline automation"]
- "Created Tableau dashboards" → Extract ["Tableau", "dashboard development"]
- "Used scikit-learn for..." → Extract ["scikit-learn"]
- "Deployed on AWS" → Extract ["AWS"]

Action Verbs → Soft Skills:
- "Collaborated with teams" → Extract "collaboration"
- "Optimized customer support" → Extract "problem-solving"
- "Analyzed client databases" → Extract "analytical thinking"
- "Evaluated and improved" → Extract "critical thinking"
- "Provided detailed feedback" → Extract "attention to detail"

**RULE 3: Extract Domain from Industry Mentions**
Look for industry/sector mentions throughout CV:

From Experience:
- "property tech" → Extract as domain_keyword
- "construction" → Extract as domain_keyword
- "AI sectors" → Extract "AI" as domain_keyword

From Projects:
- "Heart Attack Risk Prediction" → Extract "Healthcare" as domain_keyword
- Healthcare/medical projects → Extract relevant industry

**RULE 4: Extract Technologies from Projects**
Parse project descriptions for specific technologies:
- "Built with PyTorch" → Extract "PyTorch"
- "Used scikit-learn" → Extract "scikit-learn"
- "TensorFlow model" → Extract "TensorFlow"
- "Statistical Analysis" → Extract "Statistical Analysis"

═══════════════════════════════════════════════════════════════

IMPORTANT: Your output must include ALL these fields in valid JSON format:

{
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "domain_keywords": ["domain1", "domain2", ...],
    "experience_years": <number>,
    "education": ["degree1", "degree2", ...],
    "certifications": ["cert1", "cert2", ...],
    "languages": ["lang1", "lang2", ...],
    "summary": "Brief 2-3 sentence professional summary"
}

CRITICAL REMINDERS:
- Look at ENTIRE CV (not just skills section)
- Extract soft skills from action verbs ("collaborated", "optimized", "analyzed")
- Extract domain from industry context ("property tech", "construction", "Healthcare")
- Parse piped/slashed skill lists ("Python|SQL", "Tableau/Power BI")
- Include technologies from project descriptions (PyTorch, scikit-learn, TensorFlow)
"""
            
            logger.debug(f"🔍 [CONTEXT_AWARE_PIPELINE] CV extraction using centralized prompt from prompt_templates.py")
            
            cv_response = await ai_service.generate_response(
                prompt=cv_prompt,
                system_prompt=skill_prompts["system_prompt"],  # Contains categorization rules
                user=current_user,
                temperature=0.0,
                max_tokens=1500  # Increased for extra fields
            )
            
            parsed_payload = self._parse_ai_structured_response(cv_response.content)
            if not parsed_payload:
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] Failed to parse CV skills JSON, using fallback")
                parsed_payload = {}
            
            def _sanitize_list(values):
                cleaned = []
                seen = set()
                for value in values or []:
                    if not isinstance(value, str):
                        continue
                    trimmed = value.strip()
                    if not trimmed:
                        continue
                    lowered = trimmed.lower()
                    if lowered not in seen:
                        cleaned.append(trimmed)
                        seen.add(lowered)
                return cleaned
            
            tech_skills = _sanitize_list(parsed_payload.get("technical_skills"))
            soft_skills = _sanitize_list(parsed_payload.get("soft_skills"))
            domain_keywords = _sanitize_list(
                [kw for kw in parsed_payload.get("domain_keywords", []) if kw.lower() not in {s.lower() for s in tech_skills + soft_skills}]
            )
            
            cv_skills = {
                "technical_skills": tech_skills,
                "soft_skills": soft_skills,
                "domain_keywords": domain_keywords,
                "experience_years": parsed_payload.get("experience_years", 0),
                "education": parsed_payload.get("education", []),
                "certifications": parsed_payload.get("certifications", []),
                "languages": parsed_payload.get("languages", []),
                "summary": parsed_payload.get("summary") or "CV analysis completed"
            }
            
            # Apply rule-based categorization to fix LLM mistakes
            logger.debug(f"CV skills BEFORE categorization - Domain: {cv_skills.get('domain_keywords', [])}")
            skills_for_categorization = {
                "technical_skills": cv_skills.get("technical_skills", []),
                "soft_skills": cv_skills.get("soft_skills", []),
                "domain_keywords": cv_skills.get("domain_keywords", [])
            }
            corrected = SkillCategorizer.recategorize_skills(skills_for_categorization)
            
            # Update with corrected categorization (keep other fields unchanged)
            cv_skills["technical_skills"] = corrected["technical_skills"]
            cv_skills["soft_skills"] = corrected["soft_skills"]
            cv_skills["domain_keywords"] = corrected["domain_keywords"]
            logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Applied SkillCategorizer to CV skills")
            logger.debug(f"CV skills AFTER categorization - Domain: {cv_skills['domain_keywords']}")
            
            return {
                "cv_skills": cv_skills,
                "summary": cv_skills.get("summary"),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] CV skills extraction failed: {e}")
            return {"error": f"CV skills extraction failed: {e}"}
    
    async def _initialize_context(self, jd_url: str, company: str, is_rerun: bool, user_id: int) -> AnalysisContext:
        """Initialize analysis context"""
        # Check JD caching
        jd_cached = jd_cache_manager.should_reuse_jd_analysis(jd_url, company)
        jd_cache_data = None
        
        if jd_cached:
            jd_cache_data = jd_cache_manager.get_cached_jd_data(company)
        
        return AnalysisContext({
            'company': company,
            'jd_url': jd_url,
            'is_rerun': is_rerun,
            'jd_cached': jd_cached,
            'jd_cache_data': jd_cache_data,
            'user_id': user_id
        })
    
    async def _handle_jd_analysis(self, context: AnalysisContext, results: AnalysisResults) -> Optional[Dict[str, Any]]:
        """Handle JD analysis with caching"""
        try:
            if context.jd_cached and context.jd_cache_data:
                # Use cached data
                logger.info("♻️ [CONTEXT_AWARE_PIPELINE] Using cached JD analysis")
                
                # ⭐ CACHE VALIDATION: Check JD source
                jd_source = context.jd_cache_data.metadata.get('jd_source', 'unknown') if context.jd_cache_data.metadata else 'unknown'
                if jd_source != 'processed':
                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Using cached analysis based on {jd_source.upper()} JD - may be outdated!")
                    results.warnings.append(f"Cached analysis based on {jd_source} JD (processed JD preferred)")
                else:
                    logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Cached analysis based on PROCESSED JD - valid")
                
                # ⭐ SKIP jd_skills generation if three_section_skills exists (avoid duplication)
                results.jd_analysis = context.jd_cache_data.jd_analysis
                results.job_info = context.jd_cache_data.job_info
                results.steps_skipped.append("jd_analysis_cached")
                
                # ⭐ Populate jd_skills from three_section_skills if available, otherwise use cached
                if results.jd_analysis and isinstance(results.jd_analysis, dict):
                    three_section = results.jd_analysis.get("three_section_skills")
                    if three_section:
                        # Populate jd_skills from three_section_skills (map domain_knowledge -> domain_keywords)
                        results.jd_skills = {
                            "technical_skills": three_section.get("technical_skills", []),
                            "soft_skills": three_section.get("soft_skills", []),
                            "domain_keywords": three_section.get("domain_knowledge", []),  # Map domain_knowledge to domain_keywords
                        }
                        logger.info("✅ [CONTEXT_AWARE_PIPELINE] Populated jd_skills from three_section_skills")
                    else:
                        # Only use cached jd_skills if three_section_skills doesn't exist (backward compatibility)
                        cached_jd_skills = context.jd_cache_data.jd_skills
                        if cached_jd_skills and isinstance(cached_jd_skills, dict):
                            logger.debug(f"Cached JD skills BEFORE categorization - Technical: {cached_jd_skills.get('technical_skills', [])[:5]}")
                            corrected = SkillCategorizer.recategorize_skills(cached_jd_skills)
                            results.jd_skills = {
                                "technical_skills": corrected["technical_skills"],
                                "soft_skills": corrected["soft_skills"],
                                "domain_keywords": corrected["domain_keywords"]
                            }
                            logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Applied SkillCategorizer to cached JD skills (no three_section_skills)")
                
                return {
                    'jd_analysis': results.jd_analysis,
                    'job_info': results.job_info,
                    'jd_original': context.jd_cache_data.jd_original
                }
            else:
                # Fresh JD analysis
                logger.info("🆕 [CONTEXT_AWARE_PIPELINE] Performing fresh JD analysis")
                
                # First check if JD analysis already exists
                # ⭐ CACHE INVALIDATION: Check if processed JD exists and should force refresh
                force_refresh = False
                if self.user_email:
                    try:
                        from app.services.jd_processing_service import get_jd_processing_service
                        jd_service = get_jd_processing_service(self.user_email)
                        if jd_service.has_processed_jd(context.company):
                            logger.info(f"🔄 [CONTEXT_AWARE_PIPELINE] Processed JD exists for {context.company}, "
                                       f"checking if cache invalidation is needed")
                            # Check if cached analysis was based on processed JD
                            from pathlib import Path
                            from app.utils.timestamp_utils import TimestampUtils
                            company_dir = self.base_dir / "applied_companies" / context.company
                            analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{context.company}_jd_analysis", "json")
                            
                            if analysis_file and analysis_file.exists():
                                try:
                                    import json
                                    with open(analysis_file, 'r', encoding='utf-8') as f:
                                        analysis_data = json.load(f)
                                    analysis_metadata = analysis_data.get('metadata', {})
                                    used_processed_jd = analysis_metadata.get('used_processed_jd', False)
                                    
                                    if not used_processed_jd:
                                        logger.info(f"🔄 [CONTEXT_AWARE_PIPELINE] Cached analysis was NOT based on processed JD. "
                                                   f"Forcing refresh to use processed JD")
                                        force_refresh = True
                                    else:
                                        logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Cached analysis was based on processed JD, "
                                                   f"can reuse it")
                                except Exception as e:
                                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Could not check analysis metadata: {e}")
                                    # If we can't check, let analyze_company_jd() handle cache invalidation
                            else:
                                logger.info(f"🔄 [CONTEXT_AWARE_PIPELINE] No cached analysis found, will use processed JD")
                    except Exception as e:
                        logger.debug(f"⚠️ [CONTEXT_AWARE_PIPELINE] Could not check processed JD: {e}")
                
                try:
                    logger.info(f"🔍 [CONTEXT_AWARE_PIPELINE] Checking for existing JD analysis for {context.company} "
                               f"(force_refresh={force_refresh})")
                    # Use analyze_and_save_company_jd with force_refresh if processed JD exists
                    if force_refresh:
                        jd_analysis_result = await self.jd_analyzer.analyze_and_save_company_jd(
                            context.company, 
                            force_refresh=True
                        )
                    else:
                        jd_analysis_result = await self.jd_analyzer.analyze_company_jd(context.company)
                    
                    if jd_analysis_result and jd_analysis_result.all_keywords:
                        if force_refresh:
                            logger.info("✅ [CONTEXT_AWARE_PIPELINE] Re-analyzed JD with processed JD (cache was invalidated)")
                            results.steps_completed.append("jd_analysis_refreshed_with_processed_jd")
                        else:
                            logger.info("✅ [CONTEXT_AWARE_PIPELINE] Found existing JD analysis, using it")
                            # Check if it was based on processed JD
                            if hasattr(jd_analysis_result, 'metadata') and jd_analysis_result.metadata:
                                used_processed = jd_analysis_result.metadata.get('used_processed_jd', False)
                                if used_processed:
                                    logger.info("✅ [CONTEXT_AWARE_PIPELINE] Cached analysis was based on processed JD")
                                else:
                                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Cached analysis may not be based on processed JD")
                            results.steps_completed.append("jd_analysis_existing")
                        results.jd_analysis = jd_analysis_result.to_dict()

                        # ⭐ SKIP jd_skills generation if three_section_skills exists (avoid duplication)
                        three_section = results.jd_analysis.get("three_section_skills") or {}
                        if three_section:
                            logger.info("✅ [CONTEXT_AWARE_PIPELINE] three_section_skills exists - skipping jd_skills generation")
                        else:
                            logger.debug("⚠️ [CONTEXT_AWARE_PIPELINE] No three_section_skills found - jd_skills will not be generated")
                        
                        # Try to get job info from existing files
                        from pathlib import Path
                        from app.utils.timestamp_utils import TimestampUtils
                        
                        company_dir = self.base_dir / "applied_companies" / context.company
                        job_info_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"job_info_{context.company.replace(' ', '_')}", "json")
                        if job_info_file and job_info_file.exists():
                            import json
                            with open(job_info_file, 'r', encoding='utf-8') as f:
                                results.job_info = json.load(f)
                            results.steps_completed.append("job_info_existing")
                        else:
                            # Create minimal job info
                            results.job_info = {
                                "company_name": context.company,
                                "job_title": "Unknown",
                                "success": True
                            }
                            results.steps_completed.append("job_info_minimal")
                    else:
                        raise Exception("No existing JD analysis found")
                        
                except Exception as e:
                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] No existing JD analysis found: {e}")
                    logger.info("🔄 [CONTEXT_AWARE_PIPELINE] Attempting to use existing JD file")
                    
                    # Try to read existing JD file and create analysis
                    from pathlib import Path
                    from app.utils.timestamp_utils import TimestampUtils
                    
                    company_dir = self.base_dir / "applied_companies" / context.company
                    jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
                    
                    if jd_file and jd_file.exists():
                        logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Found existing JD file: {jd_file}")
                        
                        # Read JD content
                        import json
                        with open(jd_file, 'r', encoding='utf-8') as f:
                            jd_data = json.load(f)
                        
                        # Create job info from existing data
                        results.job_info = {
                            "company_name": jd_data.get("company", context.company),
                            "job_title": jd_data.get("job_title", "Unknown"),
                            "success": True
                        }
                        results.steps_completed.append("job_info_from_existing")
                        
                        # ⭐ Trigger JD processing if not already processed
                        try:
                            jd_text = jd_data.get("text", "")
                            if jd_text:
                                from app.services.jd_processing_service import get_jd_processing_service
                                from app.models.auth import UserData
                                from datetime import timezone
                                
                                # Create user object for processing
                                processing_user = UserData(
                                    id="pipeline_user",
                                    email=self.user_email,
                                    name=self.user_email.split("@")[0] if self.user_email else "user",
                                    created_at=datetime.now(timezone.utc),
                                    is_active=True
                                )
                                
                                jd_service = get_jd_processing_service(self.user_email)
                                logger.info(f"🔍 [JD_PROCESSING] Checking if processed JD needed for {context.company}")
                                await jd_service.process_jd_if_needed(
                                    company_name=context.company,
                                    jd_text=jd_text,
                                    job_title=jd_data.get("job_title"),
                                    job_url=jd_data.get("job_url"),
                                    user=processing_user
                                )
                                logger.info(f"✅ [JD_PROCESSING] JD processing check completed for {context.company}")
                        except Exception as proc_err:
                            logger.warning(f"⚠️ [JD_PROCESSING] Failed to process JD for {context.company}: {proc_err}")
                            # Continue without processing - fallback to original JD will work
                        
                        # Perform JD analysis using existing file
                        jd_analysis_result = await self.jd_analyzer.analyze_jd_file(jd_file)
                        results.jd_analysis = jd_analysis_result.to_dict()
                        results.steps_completed.append("jd_analysis_from_existing")
                        
                    else:
                        logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] No JD file found for company: {context.company}")
                        return None
                
                # Cache the results for future use
                # Determine if processed JD was used based on jd_analysis_result metadata
                used_processed_jd = False
                processed_jd_length = None
                if jd_analysis_result and hasattr(jd_analysis_result, 'metadata') and jd_analysis_result.metadata:
                    used_processed_jd = jd_analysis_result.metadata.get('used_processed_jd', False)
                    processed_jd_length = jd_analysis_result.metadata.get('processed_jd_length')
                
                # ⭐ Don't cache jd_skills if three_section_skills exists (avoid duplication)
                jd_skills_to_cache = {}
                if results.jd_skills and isinstance(results.jd_skills, dict):
                    jd_skills_to_cache = results.jd_skills
                elif results.jd_analysis and isinstance(results.jd_analysis, dict):
                    # Only cache jd_skills if three_section_skills doesn't exist (backward compatibility)
                    three_section = results.jd_analysis.get("three_section_skills")
                    if not three_section:
                        jd_skills_to_cache = results.jd_skills if isinstance(results.jd_skills, dict) else {}
                
                jd_data_to_cache = {
                    # Cache JD three-section snapshot only if three_section_skills doesn't exist
                    'jd_skills': jd_skills_to_cache,
                    'jd_analysis': results.jd_analysis,
                    'job_info': results.job_info,
                    'jd_original': {},  # Will be filled from saved files
                    'metadata': {
                        'used_processed_jd': used_processed_jd,
                        'jd_source': 'processed' if used_processed_jd else 'raw',
                        'processed_jd_length': processed_jd_length,
                        'cache_timestamp': datetime.now().isoformat(),
                        'company': context.company
                    }
                }
                
                jd_cache_manager.cache_jd_analysis(context.company, context.jd_url, jd_data_to_cache)
                
                return jd_data_to_cache
                
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] JD analysis failed: {e}")
            results.errors.append(f"JD analysis error: {str(e)}")
            return None
    
    async def _extract_cv_skills(self, context: AnalysisContext, results: AnalysisResults) -> Optional[Dict[str, Any]]:
        """Extract CV skills (always fresh for context-aware analysis)"""
        try:
            logger.info(f"🔍 [CONTEXT_AWARE_PIPELINE] Extracting skills from {context.cv_context.file_type} CV")

            # Get CV content using unified selector
            from app.unified_latest_file_selector import get_selector_for_user
            user_selector = get_selector_for_user(self.user_email)
            cv_content = user_selector.get_cv_content_across_all(context.company)

            # Determine path to pass to extractor
            # CRITICAL FIX: Use TXT file for skill extraction (JSON has nested structure that confuses AI)
            cv_paths = user_selector.get_latest_cv_paths_for_services(context.company)
            if not cv_paths.get('txt_path') and not cv_paths.get('json_path'):
                logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] No CV file found for {context.company}")
                return None

            # ALWAYS use TXT path for skill extraction (clean text, no nested JSON)
            # Fallback to JSON only if TXT not available (will need proper parsing)
            cv_path_to_use = cv_paths.get('txt_path') or cv_paths.get('json_path')
            logger.info(f"🔍 [CONTEXT_AWARE_PIPELINE] Using CV file for skills: {cv_path_to_use}")

            # Use the existing service with the correct file path
            skill_results = await self._extract_cv_skills_from_path(
                cv_path=cv_path_to_use,
                jd_url=context.jd_url,
                user_id=context.user_id,
                force_refresh=context.is_rerun
            )
            
            results.cv_skills = skill_results.get('cv_skills', {})
            if isinstance(results.cv_skills, dict):
                results.cv_skills.setdefault("technical_skills", [])
                results.cv_skills.setdefault("soft_skills", [])
                results.cv_skills.setdefault("domain_keywords", [])
                if "summary" not in results.cv_skills and skill_results.get("summary"):
                    results.cv_skills["summary"] = skill_results["summary"]
            results.steps_completed.append("cv_skills_extraction")
            
            return results.cv_skills
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] CV skills extraction failed: {e}")
            results.errors.append(f"CV skills extraction error: {str(e)}")
            return None
    
    async def _perform_cv_jd_matching(
        self, 
        context: AnalysisContext, 
        cv_skills: Dict, 
        jd_data: Dict, 
        results: AnalysisResults
    ) -> Optional[Dict[str, Any]]:
        """Perform CV-JD matching (always recalculated)"""
        try:
            logger.info("🎯 [CONTEXT_AWARE_PIPELINE] Performing CV-JD matching")
            
            # Get CV file path from context
            cv_file_path = str(context.cv_context.txt_path) if context.cv_context.txt_path else None
            
            matching_result = await self.cv_jd_matcher.match_cv_against_jd(
                company_name=context.company,
                cv_file_path=cv_file_path,
                jd_analysis_data=jd_data.get('jd_analysis', {})
            )
            
            # CRITICAL FIX: Save the matching result to file so it can be used by bonus calculation
            try:
                self.cv_jd_matcher._save_match_result(matching_result, context.company)
                logger.info(f"💾 [CONTEXT_AWARE_PIPELINE] CV-JD matching results saved for {context.company}")
            except Exception as save_error:
                logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Failed to save CV-JD matching results: {save_error}")
            
            results.cv_jd_matching = matching_result.to_dict()
            results.steps_completed.append("cv_jd_matching")
            
            return results.cv_jd_matching
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] CV-JD matching failed: {e}")
            results.errors.append(f"CV-JD matching error: {str(e)}")
            return None
    
    async def _run_component_analysis(self, context: AnalysisContext, results: AnalysisResults) -> Optional[Dict[str, Any]]:
        """Run component analysis"""
        try:
            logger.info("🔧 [CONTEXT_AWARE_PIPELINE] Running component analysis")
            
            component_result = await self.component_assembler.assemble_analysis(context.company, jd_url=context.jd_url)
            
            results.component_analysis = component_result
            results.steps_completed.append("component_analysis")
            
            return component_result
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] Component analysis failed: {e}")
            results.warnings.append(f"Component analysis warning: {str(e)}")
            return None
    
    async def _generate_ats_recommendations(self, context: AnalysisContext, results: AnalysisResults) -> Optional[Dict[str, Any]]:
        """Generate ATS recommendations"""
        try:
            logger.info("📊 [CONTEXT_AWARE_PIPELINE] Generating ATS recommendations")
            
            ats_success = self.ats_recommender.create_recommendation_file(context.company)
            
            if ats_success:
                results.steps_completed.append("ats_recommendations")
                return {"success": True, "company": context.company}
            else:
                results.warnings.append("ATS recommendations generation failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] ATS recommendations failed: {e}")
            results.warnings.append(f"ATS recommendations warning: {str(e)}")
            return None
    
    async def _generate_ai_recommendations(self, context: AnalysisContext, results: AnalysisResults) -> Optional[Dict[str, Any]]:
        """Generate AI recommendations"""
        try:
            logger.info("🤖 [CONTEXT_AWARE_PIPELINE] Generating AI recommendations")
            
            ai_success = await self.ai_recommender.generate_ai_recommendation(
                context.company, 
                force_regenerate=context.is_rerun
            )
            
            if ai_success:
                results.steps_completed.append("ai_recommendations")
                return {"success": True, "company": context.company}
            else:
                results.warnings.append("AI recommendations generation failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] AI recommendations failed: {e}")
            results.warnings.append(f"AI recommendations warning: {str(e)}")
            return None
    
    async def _generate_tailored_cv(self, context: AnalysisContext, results: AnalysisResults) -> Optional[str]:
        """Generate tailored CV"""
        try:
            logger.info("✨ [CONTEXT_AWARE_PIPELINE] Generating tailored CV")
            
            # The AI recommendation generator already triggers CV tailoring
            # So this step might be redundant, but we can add specific logic here if needed
            
            results.steps_completed.append("tailored_cv_generation")
            return f"Tailored CV generated for {context.company}"
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] Tailored CV generation failed: {e}")
            results.warnings.append(f"Tailored CV generation warning: {str(e)}")
            return None
    
    async def _perform_analyze_match(self, context: AnalysisContext, results: AnalysisResults) -> Optional[Dict[str, Any]]:
        """
        Perform analyze match assessment to determine if full analysis should proceed
        
        This step evaluates the CV-JD match and provides a decision (PROCEED/MAYBE/DONT_PROCEED)
        to help users decide whether to continue with expensive AI analysis steps.
        
        Args:
            context: Analysis context
            results: Analysis results container
            
        Returns:
            Dictionary with parsed decision data, or None if analysis fails
        """
        try:
            logger.info("🔍 [CONTEXT_AWARE_PIPELINE] Performing analyze match assessment")
            
            # Get CV and JD content
            from app.unified_latest_file_selector import get_selector_for_user
            user_selector = get_selector_for_user(self.user_email)
            cv_content = user_selector.get_cv_content_across_all(context.company)
            
            # ⭐ Get JD content using processed JD service (with fallback to raw JD)
            from app.services.jd_processing_service import get_jd_processing_service
            jd_service = get_jd_processing_service(self.user_email)
            jd_text = jd_service.get_jd_text_for_ai(context.company, prefer_processed=True)
            
            if not jd_text:
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] No JD content found (neither processed nor original) for analyze match")
                return None
            
            # Log JD source and size for performance tracking
            jd_source = "PROCESSED" if jd_service.has_processed_jd(context.company) else "RAW"
            has_sections = any(section in jd_text for section in [
                "ROLE OVERVIEW", "KEY RESPONSIBILITIES", "TECHNICAL REQUIREMENTS"
            ]) if jd_source == "PROCESSED" else False
            jd_preview = jd_text[:300].replace('\n', ' ')
            
            logger.info(f"🔍 [CONTEXT_AWARE_PIPELINE] Analyze match JD source: {jd_source} | "
                       f"Size: {len(jd_text)} chars | Company: {context.company} | "
                       f"Has sections format: {has_sections}")
            logger.info(f"📄 [CONTEXT_AWARE_PIPELINE] JD preview (first 300 chars): {jd_preview}")
            
            # ⭐ PRINT FULL PROCESSED JD TEXT BEING SENT TO AI FOR ANALYZE MATCH
            if jd_source == "PROCESSED":
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] ========== FULL PROCESSED JD TEXT FOR ANALYZE MATCH ==========")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] Company: {context.company}")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] Total length: {len(jd_text)} characters")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] This processed JD text will be sent to AI for analyze match:")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] Full processed JD text:\n{jd_text}")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] ========== END OF PROCESSED JD TEXT FOR ANALYZE MATCH ==========")
                print(f"📋 [CONTEXT_AWARE_PIPELINE] FULL PROCESSED JD TEXT FOR ANALYZE MATCH ({len(jd_text)} chars):\n{jd_text}")
            else:
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] JD will be sent to AI as TEXT (RAW JD, not processed)")
            
            if not cv_content or not jd_text:
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] Missing CV or JD content for analyze match")
                return None
            
            # Get analyze match prompt
            from app.services.skill_extraction.prompt_templates import get_prompt
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            analyze_match_prompt = get_prompt('analyze_match', cv_text=cv_content, job_text=jd_text, current_date=current_date)
            
            # Generate AI response for analyze match
            from app.models.auth import UserData
            from datetime import timezone
            current_user = UserData(
                id="pipeline_user",
                email=self.user_email,
                name=self.user_email.split("@")[0] if self.user_email else "user",
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            analyze_match_response = await ai_service.generate_response(
                prompt=analyze_match_prompt,
                user=current_user,
                temperature=0.0,
                max_tokens=4000
            )
            
            # Parse the decision
            from app.utils.analyze_match_parser import parse_analyze_match_decision
            decision_data = parse_analyze_match_decision(analyze_match_response.content)
            
            logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Analyze match completed: {decision_data.get('decision')}, "
                       f"match_score: {decision_data.get('match_score')}, "
                       f"should_proceed: {decision_data.get('should_proceed')}")
            
            return decision_data
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] Analyze match failed: {e}")
            results.warnings.append(f"Analyze match warning: {str(e)}")
            return None
    
    async def run_initial_analysis(
        self,
        jd_url: str,
        company: str,
        is_rerun: bool = False,
        user_id: int = 1
    ) -> AnalysisResults:
        """
        Run initial analysis up to and including analyze match, then stop for user decision
        
        This method performs:
        1. JD Analysis
        2. CV Skills Extraction
        3. CV-JD Matching
        4. Analyze Match (decision point)
        
        After analyze match, the process stops and waits for user decision.
        Use continue_from_analyze_match() to proceed with expensive steps.
        
        Args:
            jd_url: Job description URL
            company: Company name
            is_rerun: True if this is a rerun scenario
            user_id: User ID for the analysis
            
        Returns:
            AnalysisResults with initial analysis data and analyze_match_decision
        """
        start_time = datetime.now()
        results = AnalysisResults()
        
        try:
            logger.info(f"🚀 [CONTEXT_AWARE_PIPELINE] Starting initial analysis (stops after analyze match)")
            logger.info(f"🎯 [CONTEXT_AWARE_PIPELINE] Company: {company}, JD: {jd_url}")
            
            # Step 1: Initialize analysis context
            context = await self._initialize_context(jd_url, company, is_rerun, user_id)
            results.context = context
            
            # Step 2: CV Selection
            from app.unified_latest_file_selector import get_selector_for_user
            user_selector = get_selector_for_user(self.user_email)
            cv_context = user_selector.get_latest_cv_for_company(company, jd_url, "")
            context.cv_context = cv_context
            
            # Record JD usage
            from app.services.jd_usage_tracker import jd_usage_tracker
            jd_text_fallback = f"JD for {company}" if not jd_url else ""
            jd_usage_tracker.record_jd_usage(jd_url, jd_text_fallback, company, "")
            
            if not cv_context.exists:
                results.errors.append(f"No CV found for company: {company}")
                return results
            
            logger.info(f"📄 [CONTEXT_AWARE_PIPELINE] Using {cv_context.file_type} CV - {cv_context.json_path}")
            
            # Step 3: JD Analysis
            jd_data = await self._handle_jd_analysis(context, results)
            if not jd_data:
                results.errors.append("JD analysis failed")
                return results
            
            # ⭐ CRITICAL: Ensure jd_analysis.required_skills exists for frontend
            # The frontend expects jd_analysis.required_skills for side-by-side display
            # Even if jd_skills is already set from cache, we need to ensure required_skills is present
            if results.jd_analysis and isinstance(results.jd_analysis, dict):
                required_skills = results.jd_analysis.get("required_skills")
                if not required_skills or not isinstance(required_skills, dict):
                    logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] jd_analysis.required_skills missing or invalid, attempting to derive from three_section_skills")
                    # Try to derive required_skills from three_section_skills if available
                    three_section = results.jd_analysis.get("three_section_skills") or {}
                    if three_section:
                        results.jd_analysis["required_skills"] = {
                            "technical": three_section.get("technical_skills", []),
                            "soft_skills": three_section.get("soft_skills", []),
                            "domain_knowledge": three_section.get("domain_knowledge", []),
                            "experience": []  # Empty for now, can be populated from jd_analysis if available
                        }
                        logger.info("✅ [CONTEXT_AWARE_PIPELINE] Derived required_skills from three_section_skills for frontend compatibility")
                    else:
                        # Last resort: use _summarize_jd_skills to build it
                        logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] No three_section_skills available, using _summarize_jd_skills to build required_skills")
                        summarized = self._summarize_jd_skills(results.jd_analysis)
                        results.jd_analysis["required_skills"] = {
                            "technical": summarized.get("technical_skills", []),
                            "soft_skills": summarized.get("soft_skills", []),
                            "domain_knowledge": summarized.get("domain_keywords", []),
                            "experience": []
                        }
                else:
                    logger.info("✅ [CONTEXT_AWARE_PIPELINE] jd_analysis.required_skills present and valid")
                    logger.debug(f"   Technical: {len(required_skills.get('technical', []))} skills")
                    logger.debug(f"   Soft: {len(required_skills.get('soft_skills', []))} skills")
                    logger.debug(f"   Domain: {len(required_skills.get('domain_knowledge', []))} skills")
            
            # ⭐ Populate jd_skills from three_section_skills if available, otherwise generate/use cached
            if results.jd_analysis and isinstance(results.jd_analysis, dict):
                three_section = results.jd_analysis.get("three_section_skills") or {}
                if three_section:
                    # Populate jd_skills from three_section_skills (map domain_knowledge -> domain_keywords)
                    results.jd_skills = {
                        "technical_skills": three_section.get("technical_skills", []),
                        "soft_skills": three_section.get("soft_skills", []),
                        "domain_keywords": three_section.get("domain_knowledge", []),  # Map domain_knowledge to domain_keywords
                    }
                    logger.info("✅ [CONTEXT_AWARE_PIPELINE] Populated jd_skills from three_section_skills")
                else:
                    # Only generate jd_skills if three_section_skills doesn't exist
                    if isinstance(jd_data, dict) and jd_data.get('jd_skills'):
                        # Use cached jd_skills if available
                        cached_jd_skills = jd_data.get('jd_skills', {})
                        if cached_jd_skills:
                            logger.debug(f"JD skills from cache BEFORE categorization - Domain: {cached_jd_skills.get('domain_keywords', [])}")
                            corrected = SkillCategorizer.recategorize_skills(cached_jd_skills)
                            results.jd_skills = {
                                "technical_skills": corrected["technical_skills"],
                                "soft_skills": corrected["soft_skills"],
                                "domain_keywords": corrected["domain_keywords"],
                            }
                            logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Applied SkillCategorizer to cached JD skills (no three_section_skills)")
                    else:
                        # Fallback: derive a three-section summary from the 8-section analysis
                        results.jd_skills = self._summarize_jd_skills(results.jd_analysis)
                        logger.info("✅ [CONTEXT_AWARE_PIPELINE] Generated jd_skills from 8-section analysis (no three_section_skills)")
            
            # Step 4: CV Skills Extraction
            cv_skills = await self._extract_cv_skills(context, results)
            if not cv_skills:
                results.errors.append("CV skills extraction failed")
                return results
            
            # Step 5: CV-JD Matching
            cv_jd_matching = await self._perform_cv_jd_matching(context, cv_skills, jd_data, results)
            if not cv_jd_matching:
                results.errors.append("CV-JD matching failed")
                return results
            
            # Step 6: Analyze Match (STOP HERE - wait for user decision)
            analyze_match_decision = await self._perform_analyze_match(context, results)
            if analyze_match_decision:
                results.analyze_match_decision = analyze_match_decision
                results.requires_user_decision = True
                results.steps_completed.append("analyze_match")
                
                logger.info(f"⏸️ [CONTEXT_AWARE_PIPELINE] Initial analysis complete. "
                           f"Decision: {analyze_match_decision.get('decision')}, "
                           f"Waiting for user decision to continue...")
            else:
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] Analyze match failed, but continuing...")
                results.requires_user_decision = True  # Still require decision even if parse failed
            
            # Finalize results
            results.success = True
            results.processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Initial analysis completed in {results.processing_time:.2f}s")
            logger.info(f"📊 [CONTEXT_AWARE_PIPELINE] Steps completed: {len(results.steps_completed)}")
            
            # ⭐ JD SOURCE VERIFICATION SUMMARY
            try:
                from app.services.jd_processing_service import get_jd_processing_service
                jd_service = get_jd_processing_service(self.user_email)
                has_processed_jd = jd_service.has_processed_jd(company)
                
                # Check if JD analysis was based on processed JD
                jd_analysis_used_processed = False
                if results.jd_analysis and isinstance(results.jd_analysis, dict):
                    jd_analysis_metadata = results.jd_analysis.get('metadata', {}) or {}
                    jd_analysis_used_processed = jd_analysis_metadata.get('used_processed_jd', False)
                
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] ========== JD SOURCE VERIFICATION SUMMARY ==========")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] Company: {company}")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] Processed JD exists: {has_processed_jd}")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] JD Analysis used processed JD: {jd_analysis_used_processed}")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] Steps completed: {results.steps_completed}")
                logger.info(f"📋 [CONTEXT_AWARE_PIPELINE] ========== END JD SOURCE VERIFICATION ==========")
                print(f"📋 [CONTEXT_AWARE_PIPELINE] JD SOURCE: processed_jd_exists={has_processed_jd}, jd_analysis_used_processed={jd_analysis_used_processed}")
                
                # Warn if processed JD exists but wasn't used
                if has_processed_jd and not jd_analysis_used_processed:
                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] WARNING: Processed JD exists but JD analysis may not have used it!")
                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] This could indicate a cache issue - consider force_refresh=True")
            except Exception as e:
                logger.debug(f"⚠️ [CONTEXT_AWARE_PIPELINE] Could not verify JD source: {e}")
            
            # Persist snapshot so continuation + UI have baseline skills data
            saved_snapshot = self._persist_initial_skills_snapshot(context, results, jd_data, analyze_match_decision)
            if saved_snapshot:
                await self._run_preextracted_comparison(context, results, saved_snapshot)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] Initial analysis failed: {e}")
            results.errors.append(str(e))
            results.processing_time = (datetime.now() - start_time).total_seconds()
            return results
    
    async def continue_from_analyze_match(
        self,
        company: str,
        include_tailoring: bool = True
    ) -> AnalysisResults:
        """
        Continue full analysis from analyze match point (expensive steps)
        
        This method performs the expensive analysis steps that should only run
        after user confirms they want to proceed:
        1. Component Analysis
        2. ATS Recommendations
        3. AI Recommendations
        4. CV Tailoring (if requested)
        
        Args:
            company: Company name
            include_tailoring: Whether to include CV tailoring step
            
        Returns:
            AnalysisResults with complete analysis data
        """
        start_time = datetime.now()
        results = AnalysisResults()
        
        try:
            logger.info(f"🚀 [CONTEXT_AWARE_PIPELINE] Continuing full analysis for: {company}")
            
            # Reconstruct context from existing files
            from app.unified_latest_file_selector import get_selector_for_user
            user_selector = get_selector_for_user(self.user_email)
            cv_context = user_selector.get_latest_cv_across_all(company)
            
            # Create minimal context for continuation
            context = AnalysisContext({
                'company': company,
                'jd_url': '',  # Not needed for continuation
                'is_rerun': False,
                'cv_context': cv_context,
                'jd_cached': False,
                'jd_cache_data': None,
                'user_id': 1
            })
            results.context = context
            
            if not cv_context.exists:
                results.errors.append(f"No CV found for company: {company}")
                return results
            
            # Hydrate previously extracted skills/matching so UI has baseline data
            self._hydrate_previous_results(company, results)
            
            # CRITICAL: Perform CV-JD matching if not already present
            # This is needed because initial analysis stops before this step
            if not results.cv_jd_matching or not results.cv_jd_matching.get('raw_analysis'):
                logger.info("🎯 [CONTEXT_AWARE_PIPELINE] Performing CV-JD matching (not found in saved files)")
                # Load JD data for matching
                jd_file = self.base_dir / "applied_companies" / company / "jd_original.json"
                if jd_file.exists():
                    with open(jd_file, 'r', encoding='utf-8') as f:
                        jd_data = json.load(f)
                    
                    # Perform matching
                    cv_jd_matching = await self._perform_cv_jd_matching(
                        context, 
                        results.cv_skills or {}, 
                        {'jd_analysis': jd_data},
                        results
                    )
                    if cv_jd_matching:
                        self._persist_cv_jd_match_results(company, cv_jd_matching)
                        logger.info("✅ [CONTEXT_AWARE_PIPELINE] CV-JD matching completed and saved")
                else:
                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] No JD file found: {jd_file}")
            else:
                logger.info("✅ [CONTEXT_AWARE_PIPELINE] Using existing CV-JD matching from files")
            
            # Step 1: Component Analysis
            component_analysis = await self._run_component_analysis(context, results)
            
            # Step 2: ATS Recommendations
            ats_recommendations = await self._generate_ats_recommendations(context, results)
            
            # Step 3: AI Recommendations
            ai_recommendations = await self._generate_ai_recommendations(context, results)
            
            # Step 4: CV Tailoring (if requested and AI recommendations successful)
            if ai_recommendations and include_tailoring:
                tailored_cv_path = await self._generate_tailored_cv(context, results)
                results.tailored_cv_path = tailored_cv_path
            
            # Finalize results
            results.success = True
            results.processing_time = (datetime.now() - start_time).total_seconds()
            results.requires_user_decision = False  # Decision already made
            
            logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Full analysis continuation completed in {results.processing_time:.2f}s")
            logger.info(f"📊 [CONTEXT_AWARE_PIPELINE] Steps completed: {len(results.steps_completed)}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] Full analysis continuation failed: {e}")
            results.errors.append(str(e))
            results.processing_time = (datetime.now() - start_time).total_seconds()
            return results

    def _hydrate_previous_results(self, company: str, results: AnalysisResults) -> None:
        """Load previously saved skills/matching data so continuation responses stay complete."""
        try:
            from app.utils.timestamp_utils import TimestampUtils
            company_dir = self.base_dir / "applied_companies" / company
            if not company_dir.exists():
                logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] No company folder found while hydrating continuation results: {company_dir}")
                return

            # Load latest skills analysis snapshot
            skills_prefix = f"{company}_skills_analysis"
            skills_file = TimestampUtils.find_latest_timestamped_file(company_dir, skills_prefix, "json")
            if not skills_file:
                # Fallback to generic prefix in case company slug changed case
                skills_file = TimestampUtils.find_latest_timestamped_file(company_dir, "skills_analysis", "json")

            if skills_file and skills_file.exists():
                with open(skills_file, 'r', encoding='utf-8') as f:
                    saved_skills = json.load(f)
                results.cv_skills = saved_skills.get("cv_skills", {})
                
                # ⭐ Prefer three_section_skills from jd_analysis if available, otherwise use saved jd_skills
                if results.jd_analysis and isinstance(results.jd_analysis, dict):
                    three_section = results.jd_analysis.get("three_section_skills")
                    if three_section:
                        # Populate jd_skills from three_section_skills (map domain_knowledge -> domain_keywords)
                        results.jd_skills = {
                            "technical_skills": three_section.get("technical_skills", []),
                            "soft_skills": three_section.get("soft_skills", []),
                            "domain_keywords": three_section.get("domain_knowledge", []),  # Map domain_knowledge to domain_keywords
                        }
                        logger.info("✅ [CONTEXT_AWARE_PIPELINE] Populated jd_skills from three_section_skills (loaded from saved file)")
                    else:
                        results.jd_skills = saved_skills.get("jd_skills", {})
                else:
                    results.jd_skills = saved_skills.get("jd_skills", {})
                
                # Some historical files may include comprehensive analysis fields or job info
                if saved_skills.get("job_info"):
                    results.job_info = saved_skills.get("job_info", {})
                if saved_skills.get("cv_jd_matching"):
                    results.cv_jd_matching = saved_skills.get("cv_jd_matching", {})
                logger.info(f"💾 [CONTEXT_AWARE_PIPELINE] Loaded saved skills snapshot: {skills_file.name}")
            else:
                logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] No skills snapshot found for {company}")

            # Load latest CV-JD matching results (needed for ATS bonus calc + UI)
            match_file = TimestampUtils.find_latest_timestamped_file(company_dir, "cv_jd_match_results", "json")
            if not match_file:
                legacy_match = company_dir / "cv_jd_match_results.json"
                if legacy_match.exists():
                    match_file = legacy_match
            if match_file and match_file.exists():
                with open(match_file, 'r', encoding='utf-8') as f:
                    results.cv_jd_matching = json.load(f)
                logger.info(f"💾 [CONTEXT_AWARE_PIPELINE] Loaded CV-JD matching file: {match_file.name}")
            else:
                logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] No CV-JD match results found for {company}")

            # Load latest job_info as best-effort
            if not results.job_info:
                job_info_prefix = f"job_info_{company}"
                job_info_file = TimestampUtils.find_latest_timestamped_file(company_dir, job_info_prefix, "json")
                if not job_info_file:
                    legacy_job_info = company_dir / "job_info.json"
                    if legacy_job_info.exists():
                        job_info_file = legacy_job_info
                if job_info_file and job_info_file.exists():
                    with open(job_info_file, 'r', encoding='utf-8') as f:
                        results.job_info = json.load(f)
                    logger.info(f"💾 [CONTEXT_AWARE_PIPELINE] Loaded job info file: {job_info_file.name}")

        except Exception as exc:
            logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Failed to hydrate previous results for {company}: {exc}")

    def _summarize_jd_skills(self, jd_analysis: Optional[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Compile JD skill keywords into legacy structure."""
        summary = {
            "technical_skills": [],
            "soft_skills": [],
            "domain_keywords": []
        }
        if not jd_analysis:
            return summary
        
        assigned = {
            "technical_skills": set(),
            "soft_skills": set(),
            "domain_keywords": set()
        }
        
        def _add(key: str, values: Optional[List[str]], avoid_overlap: bool = False):
            if not values:
                return
            for value in values:
                if not isinstance(value, str):
                    continue
                cleaned = value.strip()
                if not cleaned:
                    continue
                lowered = cleaned.lower()
                if avoid_overlap:
                    if lowered in assigned["technical_skills"] or lowered in assigned["soft_skills"]:
                        continue
                if lowered not in assigned[key]:
                    summary[key].append(cleaned)
                    assigned[key].add(lowered)
        
        for section in ("required_skills", "preferred_skills"):
            section_data = jd_analysis.get(section, {})
            _add("technical_skills", section_data.get("technical"))
            _add("soft_skills", section_data.get("soft_skills"))
            _add("domain_keywords", section_data.get("domain_knowledge"), avoid_overlap=True)
        
        for key in summary:
            summary[key] = sorted(summary[key], key=lambda s: s.lower())
        
        # Apply rule-based categorization to fix LLM mistakes
        logger.debug(f"JD skills BEFORE categorization - Domain: {summary.get('domain_keywords', [])}")
        corrected = SkillCategorizer.recategorize_skills(summary)
        summary["technical_skills"] = corrected["technical_skills"]
        summary["soft_skills"] = corrected["soft_skills"]
        summary["domain_keywords"] = corrected["domain_keywords"]
        logger.info(f"✅ [CONTEXT_AWARE_PIPELINE] Applied SkillCategorizer to JD skills")
        logger.debug(f"JD skills AFTER categorization - Domain: {summary['domain_keywords']}")
        
        return summary
    
    def _persist_initial_skills_snapshot(
        self,
        context: AnalysisContext,
        results: AnalysisResults,
        jd_data: Optional[Dict[str, Any]],
        analyze_match_decision: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Save CV/JD skills snapshot so continuation + UI can reuse it."""
        try:
            # Check if we have skills data (either jd_skills or three_section_skills)
            has_jd_skills = results.jd_skills and isinstance(results.jd_skills, dict)
            has_three_section = results.jd_analysis and isinstance(results.jd_analysis, dict) and results.jd_analysis.get("three_section_skills")
            
            if not (results.cv_skills or has_jd_skills or has_three_section):
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] No skills data to persist for snapshot")
                return None
            
            from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
            result_saver = SkillExtractionResultSaver(user_email=self.user_email)
            
            cv_filename = "selected_cv.txt"
            cv_data = None
            cv_path = None
            if context.cv_context:
                cv_path = context.cv_context.json_path or context.cv_context.txt_path
            if cv_path and cv_path.exists():
                cv_filename = cv_path.name
                try:
                    cv_text = cv_path.read_text(encoding="utf-8")
                    cv_data = {"text": cv_text}
                except Exception as read_error:
                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Failed to read CV text: {read_error}")
            
            jd_snapshot = None
            if isinstance(jd_data, dict) and jd_data.get("jd_original"):
                jd_snapshot = jd_data.get("jd_original")
            elif context.company:
                from app.utils.timestamp_utils import TimestampUtils
                company_dir = self.base_dir / "applied_companies" / context.company
                jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
                if jd_file and jd_file.exists():
                    try:
                        jd_snapshot = json.loads(jd_file.read_text(encoding="utf-8"))
                    except Exception as jd_error:
                        logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Failed to load JD snapshot: {jd_error}")
            
            cv_summary = None
            if isinstance(results.cv_skills, dict):
                cv_summary = results.cv_skills.get("summary")
            jd_summary = self._build_jd_summary(results.jd_analysis)
            
            # ⭐ Derive jd_skills from three_section_skills if jd_skills doesn't exist
            jd_skills_for_save = results.jd_skills or {}
            if not jd_skills_for_save and results.jd_analysis and isinstance(results.jd_analysis, dict):
                three_section = results.jd_analysis.get("three_section_skills") or {}
                if three_section:
                    jd_skills_for_save = {
                        "technical_skills": three_section.get("technical_skills", []),
                        "soft_skills": three_section.get("soft_skills", []),
                        "domain_keywords": three_section.get("domain_knowledge", []),
                    }
            
            saved_file_path = result_saver.save_analysis_results(
                cv_skills=results.cv_skills or {},
                jd_skills=jd_skills_for_save,
                jd_url=context.jd_url or "preliminary_analysis",
                cv_filename=cv_filename,
                user_id=context.user_id,
                cv_data=cv_data,
                jd_data=jd_snapshot,
                company_name=context.company,
                cv_comprehensive_analysis=cv_summary,
                jd_comprehensive_analysis=jd_summary
            )
            logger.info("💾 [CONTEXT_AWARE_PIPELINE] Saved skills snapshot for %s", context.company)

            if analyze_match_decision and analyze_match_decision.get("raw_content"):
                try:
                    result_saver.append_analyze_match(
                        analyze_match_decision["raw_content"],
                        context.company
                    )
                except Exception as append_error:
                    logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Failed to append analyze match entry: {append_error}")

            return saved_file_path
        except Exception as snapshot_error:
            logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Failed to persist skills snapshot: {snapshot_error}")
            return None

    async def _run_preextracted_comparison(
        self,
        context: AnalysisContext,
        results: AnalysisResults,
        saved_file_path: str
    ) -> None:
        """Generate pre-extracted comparison text and append to analysis file."""
        try:
            cv_skills = results.cv_skills or {}
            # ⭐ Derive jd_skills from three_section_skills if jd_skills doesn't exist
            jd_skills = results.jd_skills or {}
            if not jd_skills and results.jd_analysis and isinstance(results.jd_analysis, dict):
                three_section = results.jd_analysis.get("three_section_skills") or {}
                if three_section:
                    jd_skills = {
                        "technical_skills": three_section.get("technical_skills", []),
                        "soft_skills": three_section.get("soft_skills", []),
                        "domain_keywords": three_section.get("domain_knowledge", []),
                    }
            if not any(cv_skills.get(key) for key in ("technical_skills", "soft_skills", "domain_keywords")):
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] No CV skills available for pre-extracted comparison")
                return
            if not any(jd_skills.get(key) for key in ("technical_skills", "soft_skills", "domain_keywords")):
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] No JD skills available for pre-extracted comparison")
                return
            
            def _list(values):
                cleaned = []
                seen = set()
                for value in values or []:
                    if not isinstance(value, str):
                        continue
                    trimmed = value.strip()
                    if not trimmed:
                        continue
                    lowered = trimmed.lower()
                    if lowered not in seen:
                        cleaned.append(trimmed)
                        seen.add(lowered)
                return cleaned
            
            payload_cv = {
                "technical_skills": _list(cv_skills.get("technical_skills")),
                "soft_skills": _list(cv_skills.get("soft_skills")),
                "domain_keywords": _list(cv_skills.get("domain_keywords"))
            }
            payload_jd = {
                "technical_skills": _list(jd_skills.get("technical_skills")),
                "soft_skills": _list(jd_skills.get("soft_skills")),
                "domain_keywords": _list(jd_skills.get("domain_keywords"))
            }
            
            if not any(payload_cv.values()) or not any(payload_jd.values()):
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] Sanitized skills empty, skipping comparison")
                return
            
            from app.models.auth import UserData
            from datetime import timezone
            current_user = UserData(
                id="pipeline_user",
                email=self.user_email,
                name=self.user_email.split("@")[0] if self.user_email else "user",
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            comparison_output = await execute_skills_semantic_comparison(
                ai_service,
                cv_skills=payload_cv,
                jd_skills=payload_jd,
                user=current_user,
                temperature=0.0,
                max_tokens=2000
            )
            
            if not comparison_output:
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] Pre-extracted comparison returned empty output")
                return
            
            from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
            result_saver = SkillExtractionResultSaver(user_email=self.user_email)
            result_saver.append_preextracted_comparison(
                comparison_output,
                context.company,
                saved_file_path
            )
            logger.info("📄 [CONTEXT_AWARE_PIPELINE] Pre-extracted comparison appended for %s", context.company)
        except Exception as comparison_error:
            logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Pre-extracted comparison failed: {comparison_error}")

    def _persist_cv_jd_match_results(self, company: str, match_data: Dict[str, Any]) -> None:
        """Persist CV-JD match results with timestamped filename for reuse."""
        try:
            company_dir = self.base_dir / "applied_companies" / company
            company_dir.mkdir(parents=True, exist_ok=True)
            timestamp = TimestampUtils.get_timestamp()
            file_path = company_dir / f"{company}_cv_jd_matching_{timestamp}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(match_data, f, indent=2, ensure_ascii=False)
            logger.info("💾 [CONTEXT_AWARE_PIPELINE] CV-JD match results saved to %s", file_path.name)
        except Exception as match_error:
            logger.warning(f"⚠️ [CONTEXT_AWARE_PIPELINE] Failed to persist CV-JD match results: {match_error}")

    def _build_jd_summary(self, jd_analysis: Optional[Dict[str, Any]]) -> Optional[str]:
        """Create a short textual summary of JD requirements."""
        if not jd_analysis:
            return None
        parts = []
        required = jd_analysis.get("required_skills", {})
        preferred = jd_analysis.get("preferred_skills", {})
        
        def _format(label: str, values: List[str], limit: int = 6) -> Optional[str]:
            if not values:
                return None
            trimmed = [v.strip() for v in values if isinstance(v, str) and v.strip()]
            if not trimmed:
                return None
            return f"{label}: {', '.join(trimmed[:limit])}"
        
        tech_required = _format("Must-have technical", required.get("technical", []))
        tech_pref = _format("Optional technical", preferred.get("technical", []))
        soft_required = _format("Soft skills", required.get("soft_skills", []))
        domain_required = _format("Domain knowledge", required.get("domain_knowledge", []))
        experience_req = _format("Experience", required.get("experience", []))
        
        for section in (tech_required, tech_pref, soft_required, domain_required, experience_req):
            if section:
                parts.append(section)
        
        years = jd_analysis.get("experience_years")
        if isinstance(years, (int, float)):
            parts.append(f"Experience years: {years}+")
        
        return " | ".join(parts) if parts else None

    def _parse_ai_structured_response(self, raw_content: str) -> Optional[Dict[str, Any]]:
        """Best-effort JSON extraction from AI responses that may include extra text/code fences."""
        if not raw_content:
            return None
        raw_content = raw_content.strip()
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            pass
        
        # Remove code fences if present
        if raw_content.startswith("```"):
            fence_end = raw_content.find("```", 3)
            if fence_end != -1:
                candidate = raw_content[3:fence_end].strip()
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    raw_content = candidate
        
        # Extract substring between first { and last }
        start = raw_content.find("{")
        end = raw_content.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = raw_content[start:end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                pass
        return None


# Global instance removed - service now requires user_email parameter
# Create instances per request with proper user context
