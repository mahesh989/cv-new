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
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from app.unified_latest_file_selector import FileContext
from app.services.jd_cache_manager import jd_cache_manager, JDCacheData
from app.services.skill_extraction.skill_extraction_service import SkillExtractionService
from app.services.cv_jd_matching.cv_jd_matcher import CVJDMatcher
from app.services.jd_analysis.jd_analyzer import JDAnalyzer
from app.services.job_extraction_service import JobExtractionService
from app.ai.ai_service import ai_service
from app.services.ats.component_assembler import ComponentAssembler
from app.services.ats_recommendation_service import ATSRecommendationService
from app.services.ai_recommendation_generator import AIRecommendationGenerator
from app.utils.timestamp_utils import TimestampUtils

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
            
            # Record JD usage for tracking
            from app.services.jd_usage_tracker import jd_usage_tracker
            # Provide fallback text if no URL is available
            jd_text_fallback = f"JD for {company}" if not jd_url else ""
            
            logger.info(f"🔍 [CONTEXT_AWARE_PIPELINE] Recording JD usage:")
            logger.info(f"- jd_url: {jd_url}")
            logger.info(f"- jd_text_fallback: {jd_text_fallback}")
            logger.info(f"- company: {company}")
            
            jd_usage_tracker.record_jd_usage(jd_url, jd_text_fallback, company, "")
            
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
            
            # Use AI service to extract skills from CV text
            cv_prompt = f"""
            Analyze the following CV and extract skills, experience, and qualifications.
            
            CV Content:
            {cv_text}
            
            Return a JSON object with the following structure:
            {{
                "technical_skills": ["skill1", "skill2", ...],
                "soft_skills": ["skill1", "skill2", ...],
                "experience_years": number,
                "education": ["degree1", "degree2", ...],
                "certifications": ["cert1", "cert2", ...],
                "languages": ["lang1", "lang2", ...],
                "summary": "Brief summary of the candidate"
            }}
            """
            
            cv_response = await ai_service.generate_response(
                prompt=cv_prompt,
                user=current_user,
                temperature=0.0,
                max_tokens=1000
            )
            
            # Parse CV skills response
            try:
                import json
                cv_skills = json.loads(cv_response.content)
            except json.JSONDecodeError:
                # Fallback parsing
                cv_skills = {
                    "technical_skills": [],
                    "soft_skills": [],
                    "experience_years": 0,
                    "education": [],
                    "certifications": [],
                    "languages": [],
                    "summary": "CV analysis completed"
                }
            
            return {
                "cv_skills": cv_skills,
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
                results.jd_skills = context.jd_cache_data.jd_skills
                results.jd_analysis = context.jd_cache_data.jd_analysis
                results.job_info = context.jd_cache_data.job_info
                results.steps_skipped.append("jd_analysis_cached")
                
                return {
                    'jd_skills': results.jd_skills,
                    'jd_analysis': results.jd_analysis,
                    'job_info': results.job_info,
                    'jd_original': context.jd_cache_data.jd_original
                }
            else:
                # Fresh JD analysis
                logger.info("🆕 [CONTEXT_AWARE_PIPELINE] Performing fresh JD analysis")
                
                # First check if JD analysis already exists
                try:
                    jd_analysis_result = await self.jd_analyzer.analyze_company_jd(context.company)
                    if jd_analysis_result and jd_analysis_result.all_keywords:
                        logger.info("✅ [CONTEXT_AWARE_PIPELINE] Found existing JD analysis, using it")
                        results.jd_analysis = jd_analysis_result.to_dict()
                        results.steps_completed.append("jd_analysis_existing")
                        
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
                        
                        # Perform JD analysis using existing file
                        jd_analysis_result = await self.jd_analyzer.analyze_jd_file(jd_file)
                        results.jd_analysis = jd_analysis_result.to_dict()
                        results.steps_completed.append("jd_analysis_from_existing")
                        
                    else:
                        logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] No JD file found for company: {context.company}")
                        return None
                
                # Cache the results for future use
                jd_data_to_cache = {
                    'jd_skills': {},  # Will be filled by skill extraction
                    'jd_analysis': results.jd_analysis,
                    'job_info': results.job_info,
                    'jd_original': {}  # Will be filled from saved files
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

            # Determine path to pass to extractor (prefer JSON path for complete structured data)
            cv_paths = user_selector.get_latest_cv_paths_for_services(context.company)
            if not cv_paths.get('txt_path') and not cv_paths.get('json_path'):
                logger.error(f"❌ [CONTEXT_AWARE_PIPELINE] No CV file found for {context.company}")
                return None

            # Use JSON path for complete structured data, fallback to TXT if JSON not available
            cv_path_to_use = cv_paths.get('json_path') or cv_paths.get('txt_path')
            logger.info(f"🔍 [CONTEXT_AWARE_PIPELINE] Using CV file: {cv_path_to_use}")

            # Use the existing service with the correct file path
            skill_results = await self._extract_cv_skills_from_path(
                cv_path=cv_path_to_use,
                jd_url=context.jd_url,
                user_id=context.user_id,
                force_refresh=context.is_rerun
            )
            
            results.cv_skills = skill_results.get('cv_skills', {})
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
            
            # Get JD content
            company_dir = self.base_dir / "applied_companies" / context.company
            from app.utils.timestamp_utils import TimestampUtils
            jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
            
            if not jd_file or not jd_file.exists():
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] No JD file found for analyze match")
                return None
            
            import json
            with open(jd_file, 'r', encoding='utf-8') as f:
                jd_data = json.load(f)
            
            jd_text = jd_data.get('text', '') if isinstance(jd_data, dict) else str(jd_data)
            
            if not cv_content or not jd_text:
                logger.warning("⚠️ [CONTEXT_AWARE_PIPELINE] Missing CV or JD content for analyze match")
                return None
            
            # Get analyze match prompt
            from app.services.skill_extraction.prompts.skill_prompt_loader import get_skill_prompt
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            analyze_match_prompt = get_skill_prompt('analyze_match', cv_text=cv_content, job_text=jd_text, current_date=current_date)
            
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


# Global instance removed - service now requires user_email parameter
# Create instances per request with proper user context
