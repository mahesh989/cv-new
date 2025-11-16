# Phase 6, 7, 8 Complete Code

## PHASE 6: Input Recommendation Service

**File:** `backend/app/services/ats_recommendation_service.py`

```python
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
            
            # Get the latest CV JSON file
            cv_dir = self.base_dir / "cvs"
            tailored_dir = cv_dir / "tailored"
            
            keywords = set()
            
            # Try to find latest tailored CV first
            tailored_files = list(tailored_dir.glob("*_tailored_cv_*.json"))
            if tailored_files:
                latest_tailored = max(tailored_files, key=lambda f: f.stat().st_mtime)
                keywords.update(self._extract_keywords_from_cv_file(latest_tailored))
                logger.info(f"🔍 [KEYWORD_FILTER] Extracted {len(keywords)} keywords from latest tailored CV: {latest_tailored.name}")
            
            # Also check original CV
            original_dir = cv_dir / "original"
            original_cv = original_dir / "original_cv.json"
            if original_cv.exists():
                original_keywords = self._extract_keywords_from_cv_file(original_cv)
                keywords.update(original_keywords)
                logger.info(f"🔍 [KEYWORD_FILTER] Total {len(keywords)} keywords after checking original CV")
            
            return keywords
            
        except Exception as e:
            logger.error(f"❌ [KEYWORD_FILTER] Error extracting CV keywords: {e}")
            return set()
    
    def _extract_keywords_from_cv_file(self, cv_file_path: Path) -> set:
        """Extract keywords from a CV JSON file"""
        keywords = set()
        
        try:
            with open(cv_file_path, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
            
            # Extract from skills section
            for skill_cat in cv_data.get('skills', []):
                if isinstance(skill_cat, dict):
                    for skill in skill_cat.get('skills', []):
                        skill_str = str(skill) if skill is not None else ""
                        if skill_str and len(skill_str.strip()) > 0:
                            keywords.add(skill_str.strip().lower())
            
            # Extract from experience bullets
            for exp in cv_data.get('experience', []):
                if isinstance(exp, dict):
                    for bullet in exp.get('bullets', []):
                        bullet_str = str(bullet) if bullet is not None else ""
                        # Extract keywords from bullet text (simple word extraction)
                        words = bullet_str.split()
                        for word in words:
                            clean_word = word.strip('.,;:()[]{}').lower()
                            if len(clean_word) > 3:  # Only meaningful words
                                keywords.add(clean_word)
            
            # Extract from role highlights
            role_highlights = cv_data.get('role_highlights', '')
            if isinstance(role_highlights, str):
                words = role_highlights.split()
                for word in words:
                    clean_word = word.strip('.,;:()[]{}|').lower()
                    if len(clean_word) > 3:
                        keywords.add(clean_word)
            
        except Exception as e:
            logger.error(f"❌ [KEYWORD_FILTER] Error extracting from {cv_file_path}: {e}")
        
        return keywords
    
    def _keyword_exists_in_cv(self, keyword: str, existing_keywords: set) -> bool:
        """
        Check if a keyword exists in the CV (with fuzzy matching)
        
        Args:
            keyword: Keyword to check (lowercase)
            existing_keywords: Set of existing keywords (lowercase)
            
        Returns:
            True if keyword exists (exact or fuzzy match)
        """
        # Exact match
        if keyword in existing_keywords:
            return True
        
        # Check for partial matches (keyword appears as part of CV content)
        keyword_parts = keyword.split()
        if len(keyword_parts) > 1:
            # Multi-word keyword: check if all words appear
            if all(part in existing_keywords for part in keyword_parts):
                return True
        
        # Check if keyword is contained in any existing keyword
        for existing_kw in existing_keywords:
            if keyword in existing_kw or existing_kw in keyword:
                return True
        
        return False
```

---

## PHASE 7: AI Recommendation Generator

**File:** `backend/app/services/ai_recommendation_generator.py`

```python
"""
AI Recommendation Generator Service

This service executes AI recommendation prompts using the centralized AI system
and saves the generated recommendations as structured JSON files.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from app.ai.ai_service import ai_service
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)


class AIRecommendationGenerator:
    """Service for generating AI-based CV optimization recommendations"""
    
    def __init__(self, user_email: str):
        from app.utils.user_path_utils import get_user_base_path
        self.user_email = user_email
        self.base_dir = get_user_base_path(user_email)
        self.prompt_dir = Path("/app/prompt")
    
    async def generate_ai_recommendation(self, company: str, force_regenerate: bool = False) -> bool:
        """
        Generate AI recommendation for a company using the centralized AI system
        
        Args:
            company: Company name
            force_regenerate: Force regeneration even if file exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🤖 [AI GENERATOR] Starting AI recommendation generation for: {company}")
            
            # Check if CV has been updated since input recommendation
            if not self._check_cv_freshness(company):
                logger.warning(f"⚠️ [AI GENERATOR] CV has been updated since input recommendation")
            
            # Load the AI prompt
            prompt_content = self._load_ai_prompt(company)
            if not prompt_content:
                logger.error(f"Could not load AI prompt for {company}")
                return False
            
            # Generate AI response using centralized AI system
            logger.info(f"🧠 [AI GENERATOR] Executing AI prompt for {company}")
            ai_response = await self._execute_ai_prompt(prompt_content)
            
            if not ai_response:
                logger.error(f"Failed to get AI response for {company}")
                return False
            
            # Parse and structure the AI response
            structured_response = self._structure_ai_response(ai_response, company)
            
            # Save the structured response as JSON
            success = self._save_ai_recommendation(company, structured_response)
            
            if success:
                logger.info(f"✅ [AI GENERATOR] AI recommendation generated and saved for {company}")
                logger.info(f"💰 Cost: ${ai_response.cost:.4f}")
                logger.info(f"🔤 Tokens: {ai_response.tokens_used}")
                
                # Automatically trigger CV tailoring
                try:
                    cv_success = await self._trigger_cv_tailoring(company)
                    if cv_success:
                        logger.info(f"🎯 [AI GENERATOR] CV tailoring completed for {company}")
                except Exception as cv_error:
                    logger.error(f"❌ [AI GENERATOR] CV tailoring error: {cv_error}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error generating AI recommendation: {e}")
            return False
    
    def _load_ai_prompt(self, company: str) -> Optional[str]:
        """Generate AI prompt using the centralized template with company analysis data"""
        try:
            input_file = self._get_input_recommendation_file_path(company)
            if not input_file.exists():
                logger.error(f"Input recommendation file not found: {input_file}")
                return None
            
            with open(input_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            import importlib.util
            
            template_path = self.prompt_dir / "ai_recommendation_prompt_template.py"
            if not template_path.exists():
                logger.error(f"AI recommendation template not found: {template_path}")
                return None
            
            spec = importlib.util.spec_from_file_location("ai_recommendation_prompt_template", template_path)
            template_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_module)
            
            prompt_content = template_module.generate_ai_recommendation_prompt(company, analysis_data)
            
            logger.info(f"📄 [AI GENERATOR] Generated prompt for {company} ({len(prompt_content)} chars)")
            return prompt_content
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error loading AI prompt: {e}")
            return None
    
    async def _execute_ai_prompt(self, prompt_content: str):
        """Execute the AI prompt using the centralized AI service"""
        try:
            from app.models.auth import UserData
            from datetime import datetime
            
            user_data = UserData(
                id="system",
                email=self.user_email,
                name="CV Magic User",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            ai_response = await ai_service.generate_response(
                prompt=prompt_content,
                system_prompt="You are an expert CV optimization specialist.",
                temperature=0.3,
                max_tokens=4000,
                user=user_data
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error executing AI prompt: {e}")
            return None
    
    def _structure_ai_response(self, ai_response, company: str) -> Dict[str, Any]:
        """Parse and structure the AI response into the expected format"""
        try:
            # Extract JSON from AI response
            content = ai_response.content
            
            # Try to find JSON block
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                recommendation_json = json.loads(json_str)
            else:
                # Assume entire content is JSON
                recommendation_json = json.loads(content)
            
            # Add metadata
            structured_response = {
                "company": company,
                "generated_at": datetime.utcnow().isoformat(),
                "recommendation_content": recommendation_json.get("recommendation_content", ""),
                "structured_recommendations": recommendation_json.get("structured_recommendations", {}),
                "actionable_guidance": recommendation_json.get("actionable_guidance", {}),
                "ai_model_info": {
                    "provider": ai_response.provider,
                    "model": ai_response.model,
                    "cost": ai_response.cost,
                    "tokens_used": ai_response.tokens_used
                },
                "metadata": {
                    "content_length": len(content),
                    "format_version": "2.0",
                    "has_structured_data": "structured_recommendations" in recommendation_json,
                    "has_actionable_guidance": "actionable_guidance" in recommendation_json
                }
            }
            
            return structured_response
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error structuring AI response: {e}")
            return {}
    
    def _save_ai_recommendation(self, company: str, structured_response: Dict[str, Any]) -> bool:
        """Save the structured AI recommendation to file"""
        try:
            company_dir = self.base_dir / "applied_companies" / company
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = company_dir / f"{company}_ai_recommendation_{timestamp}.json"
            
            # Save with clean formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_response, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ [AI GENERATOR] Saved recommendation to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error saving recommendation: {e}")
            return False
    
    async def _trigger_cv_tailoring(self, company: str) -> bool:
        """Trigger CV tailoring after recommendation generation"""
        try:
            from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
            
            cv_service = CVTailoringService(self.user_email)
            original_cv, recommendation, is_tailored = cv_service.load_real_cv_and_recommendation(company)
            
            if not original_cv or not recommendation:
                logger.error(f"Could not load CV or recommendation for {company}")
                return False
            
            from app.tailored_cv.models.cv_models import CVTailoringRequest
            
            request = CVTailoringRequest(
                original_cv=original_cv,
                recommendations=recommendation
            )
            
            response = await cv_service.tailor_cv(request)
            
            if response.success:
                # Save tailored CV
                cv_service.save_tailored_cv_to_file(company, response.tailored_cv)
                logger.info(f"✅ CV tailoring successful for {company}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error triggering CV tailoring: {e}")
            return False
```

---

## PHASE 8: CV Tailoring Service

**File:** `backend/app/tailored_cv/services/cv_tailoring_service.py`

```python
"""
CV Tailoring Service

Main service for tailoring CVs based on job recommendations and optimization framework.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from app.ai.ai_service import ai_service
from app.utils.timestamp_utils import TimestampUtils
from app.tailored_cv.models.cv_models import (
    OriginalCV, RecommendationAnalysis, TailoredCV, 
    CVTailoringRequest, CVTailoringResponse,
    OptimizationStrategy
)

logger = logging.getLogger(__name__)


class CVTailoringService:
    """Service for tailoring CVs based on job recommendations"""
    
    def __init__(self, user_email: str):
        from app.utils.user_path_utils import get_user_base_path
        self.user_email = user_email
        self.cv_analysis_path = get_user_base_path(user_email)
        self.framework_path = Path(__file__).parent.parent / "prompts" / "framework.md"
        self._load_framework()
    
    def _load_framework(self) -> None:
        """Load the CV optimization framework"""
        try:
            with open(self.framework_path, 'r', encoding='utf-8') as f:
                self.framework_content = f.read()
            logger.info(f"✅ Loaded CV optimization framework")
        except Exception as e:
            logger.error(f"❌ Failed to load framework: {e}")
            raise Exception(f"Failed to load CV optimization framework: {e}")
    
    async def tailor_cv(self, request: CVTailoringRequest) -> CVTailoringResponse:
        """
        Main method to tailor a CV based on recommendations
        
        Args:
            request: CVTailoringRequest containing original CV and recommendations
            
        Returns:
            CVTailoringResponse with tailored CV and processing details
        """
        try:
            logger.info(f"🎯 Starting CV tailoring for {request.recommendations.company}")
            
            # Step 1: Validate input data
            validation_result = self._validate_cv_data(request.original_cv)
            if not validation_result.is_valid:
                raise ValueError(f"CV validation failed")
            
            # Step 2: Determine optimization strategy
            optimization_strategy = self._determine_optimization_strategy(
                request.original_cv, 
                request.recommendations
            )
            
            # Step 3: Generate tailored CV using AI
            tailored_cv = await self._generate_tailored_cv(
                request.original_cv,
                request.recommendations, 
                optimization_strategy,
                request.custom_instructions
            )
            
            # Step 4: Generate processing summary
            processing_summary = self._generate_processing_summary(
                request.original_cv,
                tailored_cv,
                request.recommendations
            )
            
            # Step 5: Estimate ATS score improvement
            estimated_score = await self._estimate_ats_score(...)
            tailored_cv.estimated_ats_score = estimated_score
            
            response = CVTailoringResponse(
                tailored_cv=tailored_cv,
                processing_summary=processing_summary,
                recommendations_applied=self._extract_applied_recommendations(tailored_cv),
                success=True
            )
            
            logger.info(f"✅ CV tailoring completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"❌ CV tailoring failed: {e}")
            raise Exception(f"CV tailoring process failed: {str(e)}")
    
    async def _generate_tailored_cv(
        self,
        original_cv: OriginalCV,
        recommendations: RecommendationAnalysis,
        strategy: OptimizationStrategy,
        custom_instructions: Optional[str]
    ) -> TailoredCV:
        """Generate tailored CV using AI"""
        try:
            # Build the prompt for AI
            user_prompt = self._build_user_prompt(
                original_cv,
                recommendations,
                strategy,
                custom_instructions
            )
            
            # Call AI to generate the tailored CV
            from app.models.auth import UserData
            from datetime import datetime
            
            user_data = UserData(
                id="system",
                email=self.user_email,
                name="CV Magic User",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            ai_response = await ai_service.generate_response(
                prompt=user_prompt,
                system_prompt=self.framework_content,
                temperature=0.3,
                max_tokens=4000,
                user=user_data
            )
            
            # Parse the JSON response
            content = ai_response.content
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_str = content[json_start:json_end]
            
            tailored_cv_data = json.loads(json_str)
            
            # Convert to TailoredCV model
            tailored_cv = TailoredCV(**tailored_cv_data)
            
            return tailored_cv
            
        except Exception as e:
            logger.error(f"❌ Failed to generate tailored CV: {e}")
            raise
    
    def _build_user_prompt(
        self,
        original_cv: OriginalCV,
        recommendations: RecommendationAnalysis,
        strategy: OptimizationStrategy,
        custom_instructions: Optional[str]
    ) -> str:
        """Build the user prompt for AI CV generation"""
        prompt_parts = []
        
        # Add CV context
        prompt_parts.append("# Original CV")
        prompt_parts.append(json.dumps(original_cv.model_dump(), indent=2))
        
        # Add recommendations
        prompt_parts.append("\n# Recommendations")
        prompt_parts.append(recommendations.model_dump_json(indent=2))
        
        # Add strategy
        prompt_parts.append("\n# Optimization Strategy")
        prompt_parts.append(f"- Target Industry: {strategy.target_industry}")
        prompt_parts.append(f"- Target Role: {strategy.target_role}")
        
        # Add Tier 1 keywords to integrate
        tier1_keywords = recommendations.tier1_keywords
        prompt_parts.append("\n# TIER 1 KEYWORDS TO INTEGRATE:")
        prompt_parts.append(json.dumps(tier1_keywords, indent=2))
        
        # Add instructions
        prompt_parts.append("\n# INSTRUCTIONS:")
        prompt_parts.append("1. Integrate ALL Tier 1 keywords naturally")
        prompt_parts.append("2. Preserve ALL existing content if this is a rerun")
        prompt_parts.append("3. Follow the framework guidelines")
        prompt_parts.append("4. Output VALID JSON only")
        prompt_parts.append("5. At least ONE bullet per job/project must be 20+ words")
        prompt_parts.append("6. ALL bullets must end with period (.)")
        prompt_parts.append("7. Add 'keywords' field to experience and projects")
        
        if custom_instructions:
            prompt_parts.append(f"\n# CUSTOM INSTRUCTIONS:")
            prompt_parts.append(custom_instructions)
        
        return "\n".join(prompt_parts)
    
    def load_real_cv_and_recommendation(
        self, 
        company: str
    ) -> Tuple[Optional[OriginalCV], Optional[RecommendationAnalysis], bool]:
        """
        Load the real CV and recommendation for a company
        
        Returns:
            Tuple of (OriginalCV, RecommendationAnalysis, is_tailored_cv_base)
        """
        try:
            from app.unified_latest_file_selector import get_selector_for_user
            
            # Get the latest CV (tailored or original)
            selector = get_selector_for_user(self.user_email)
            cv_context = selector.get_latest_cv_across_all(company)
            
            if not cv_context.exists:
                logger.error(f"No CV found for {company}")
                return None, None, False
            
            # Load CV JSON
            with open(cv_context.json_path, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
            
            original_cv = OriginalCV(**cv_data)
            is_tailored = cv_context.file_type == "tailored"
            
            # Load recommendation
            company_dir = self.cv_analysis_path / "applied_companies" / company
            rec_file = TimestampUtils.find_latest_timestamped_file(
                company_dir, f"{company}_ai_recommendation", "json"
            )
            
            if not rec_file or not rec_file.exists():
                logger.error(f"No recommendation found for {company}")
                return original_cv, None, is_tailored
            
            with open(rec_file, 'r', encoding='utf-8') as f:
                rec_data = json.load(f)
            
            recommendation = RecommendationAnalysis(**rec_data.get("structured_recommendations", {}))
            
            return original_cv, recommendation, is_tailored
            
        except Exception as e:
            logger.error(f"❌ Error loading CV and recommendation: {e}")
            return None, None, False
    
    def save_tailored_cv_to_file(self, company: str, tailored_cv: TailoredCV) -> bool:
        """Save the tailored CV to file"""
        try:
            cvs_dir = self.cv_analysis_path / "cvs" / "tailored"
            cvs_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = cvs_dir / f"{company}_tailored_cv_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tailored_cv.model_dump(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved tailored CV to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving tailored CV: {e}")
            return False
```

---

## VALIDATION CODE

**File:** `backend/app/tailored_cv/services/enhanced_cv_validator.py`

```python
"""
Enhanced CV Validator

Validates CV structure, content quality, and keyword integration.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of CV validation"""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.suggestions = []
    
    def add_error(self, field: str, message: str):
        """Add a validation error"""
        self.errors.append({"field": field, "message": message})
        self.is_valid = False
    
    def add_warning(self, field: str, message: str):
        """Add a validation warning"""
        self.warnings.append({"field": field, "message": message})
    
    def add_suggestion(self, message: str):
        """Add a validation suggestion"""
        self.suggestions.append(message)


class EnhancedCVValidator:
    """Enhanced validator for CV structure and content"""
    
    def validate_cv_structure(self, cv_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate CV structure and content
        
        Args:
            cv_data: CV data dictionary
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()
        
        # Required fields
        if not cv_data.get('contact', {}).get('name'):
            result.add_error('contact.name', 'Name is required')
        
        if not cv_data.get('contact', {}).get('email'):
            result.add_error('contact.email', 'Email is required')
        
        if not cv_data.get('experience'):
            result.add_error('experience', 'At least one experience entry is required')
        
        if not cv_data.get('skills'):
            result.add_error('skills', 'Skills section is required')
        
        # Content quality checks
        for i, exp in enumerate(cv_data.get('experience', [])):
            if len(exp.get('bullets', [])) < 2:
                result.add_warning(
                    f'experience[{i}].bullets',
                    'Experience should have at least 2 bullet points'
                )
            
            # Check for quantification
            bullets = exp.get('bullets', [])
            quantified = [b for b in bullets if any(char.isdigit() for char in b)]
            if len(quantified) < len(bullets) * 0.5:
                result.add_suggestion(
                    f"Experience at {exp.get('company')}: Add more quantified achievements"
                )
        
        # Skills validation
        total_skills = sum(len(cat.get('skills', [])) for cat in cv_data.get('skills', []))
        if total_skills < 10:
            result.add_warning(
                'skills',
                'Consider adding more skills (minimum 10 recommended)'
            )
        
        return result
    
    def validate_keyword_integration(
        self,
        tailored_cv: Dict[str, Any],
        tier1_keywords: Dict[str, List[str]]
    ) -> ValidationResult:
        """
        Validate that Tier 1 keywords were integrated
        
        Args:
            tailored_cv: Tailored CV data
            tier1_keywords: Tier 1 keywords that should be integrated
            
        Returns:
            ValidationResult with integration status
        """
        result = ValidationResult()
        
        # Extract all text from CV
        cv_text = json.dumps(tailored_cv).lower()
        
        # Check each Tier 1 keyword
        for category, keywords in tier1_keywords.items():
            for keyword in keywords:
                if keyword.lower() not in cv_text:
                    result.add_warning(
                        'keyword_integration',
                        f"Tier 1 keyword '{keyword}' ({category}) not found in CV"
                    )
        
        return result
```

