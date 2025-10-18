"""
CV Tailoring Service

Main service for tailoring CVs based on job recommendations and optimization framework.
Integrates with the centralized AI service for intelligent CV optimization.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from app.ai.ai_service import ai_service
from app.utils.timestamp_utils import TimestampUtils
from app.tailored_cv.models.cv_models import (
    OriginalCV, RecommendationAnalysis, TailoredCV, 
    CVTailoringRequest, CVTailoringResponse,
    OptimizationStrategy, ExperienceLevel,
    CVValidationResult, CVValidationError
)
from app.tailored_cv.services.recommendation_parser import RecommendationParser

logger = logging.getLogger(__name__)


class CVTailoringService:
    """
    Service for tailoring CVs based on job recommendations and optimization framework
    """
    
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
            logger.info(f"✅ Loaded CV optimization framework from {self.framework_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load framework: {e}")
            raise Exception(f"Failed to load CV optimization framework: {e}")
    
    async def tailor_cv(
        self, 
        request: CVTailoringRequest
    ) -> CVTailoringResponse:
        """
        Main method to tailor a CV based on recommendations
        
        Args:
            request: CVTailoringRequest containing original CV and recommendations
            
        Returns:
            CVTailoringResponse with tailored CV and processing details
        """
        try:
            logger.info(f"🎯 Starting CV tailoring for {request.recommendations.company} - {request.recommendations.job_title}")
            
            # Step 1: Validate input data - strict validation, no tolerance for errors
            validation_result = self._validate_cv_data(request.original_cv)
            if not validation_result.is_valid:
                error_messages = [f"{error.field}: {error.message}" for error in validation_result.errors]
                raise ValueError(f"CV validation failed. Fix these issues: {'; '.join(error_messages)}")
            
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

            # Post-fix skills taxonomy if the model misclassified
            try:
                tailored_cv = self._normalize_skills_taxonomy(tailored_cv)
            except Exception as e:
                logger.warning(f"⚠️ [TAILORING] Failed to normalize skills taxonomy: {e}")
            
            # Step 4: Post-process and validate results
            processing_summary = self._generate_processing_summary(
                request.original_cv,
                tailored_cv,
                request.recommendations
            )
            
            # Step 5: Estimate ATS score improvement
            # Create user data for AI service
            from app.models.auth import UserData
            from datetime import datetime
            from app.database import SessionLocal
            from app.models.user import User
            
            # Get the real user ID from database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == self.user_email).first()
                if user:
                    user_id = str(user.id)
                    user_name = user.full_name or ""
                else:
                    user_id = "temp"
                    user_name = ""
            finally:
                db.close()
            
            user_data = UserData(
                id=user_id, 
                email=self.user_email, 
                name=user_name, 
                created_at=datetime.now(), 
                updated_at=datetime.now()
            )
            
            estimated_score = await self._estimate_ats_score(tailored_cv, request.recommendations, user_data)
            tailored_cv.estimated_ats_score = estimated_score
            
            # Add quality warnings to processing summary if any
            if hasattr(self, '_quality_warnings') and self._quality_warnings:
                processing_summary["quality_assessment"] = self._quality_warnings["assessment"]
                processing_summary["quality_message"] = self._quality_warnings["message"]
                logger.info(f"⚠️ CV created with quality warnings: {self._quality_warnings['assessment']['quality_grade']}")
            
            response = CVTailoringResponse(
                tailored_cv=tailored_cv,
                processing_summary=processing_summary,
                recommendations_applied=self._extract_applied_recommendations(tailored_cv),
                success=True,
                warnings=self._quality_warnings["message"].split('\n') if hasattr(self, '_quality_warnings') and self._quality_warnings else None
            )
            
            logger.info(f"✅ CV tailoring completed successfully. Estimated ATS score: {estimated_score}")
            return response
            
        except Exception as e:
            logger.error(f"❌ CV tailoring failed: {e}")
            # No fallback - raise the error to be handled by the route
            raise Exception(f"CV tailoring process failed: {str(e)}")
    
    def _validate_cv_data(self, cv: OriginalCV) -> CVValidationResult:
        """
        Validate CV data structure and content
        
        Args:
            cv: OriginalCV to validate
            
        Returns:
            CVValidationResult with validation status and issues
        """
        logger.info(f"🔍 [DEBUG] Validating CV structure:")
        logger.info(f"- CV object type: {type(cv)}")
        logger.info(f"- CV attributes: {dir(cv)}")
        
        # Debug print CV data
        if hasattr(cv, 'model_dump'):
            cv_data = cv.model_dump()
            logger.info(f"- CV data: {json.dumps(cv_data, indent=2)}")
        
        # Enhanced debugging for CV validation
        logger.info(f"🔍 [CV_VALIDATION] Starting detailed validation:")
        logger.info(f"- Has contact: {hasattr(cv, 'contact')}")
        if hasattr(cv, 'contact'):
            logger.info(f"- Contact name: {getattr(cv.contact, 'name', 'MISSING')}")
            logger.info(f"- Contact email: {getattr(cv.contact, 'email', 'MISSING')}")
        
        logger.info(f"- Has experience: {hasattr(cv, 'experience')}")
        if hasattr(cv, 'experience'):
            logger.info(f"- Experience count: {len(cv.experience) if cv.experience else 0}")
            if cv.experience:
                for i, exp in enumerate(cv.experience):
                    logger.info(f"- Experience {i+1}: company={getattr(exp, 'company', 'MISSING')}, bullets={len(getattr(exp, 'bullets', []))}")
        
        logger.info(f"- Has skills: {hasattr(cv, 'skills')}")
        if hasattr(cv, 'skills'):
            logger.info(f"- Skills count: {len(cv.skills) if cv.skills else 0}")
            if cv.skills:
                for i, skill_cat in enumerate(cv.skills):
                    logger.info(f"- Skill category {i+1}: {getattr(skill_cat, 'category', 'MISSING')}, skills={len(getattr(skill_cat, 'skills', []))}")
        
        errors = []
        warnings = []
        suggestions = []
        
        # Required fields validation with detailed debugging
        logger.info(f"🔍 [CV_VALIDATION] Checking required fields:")
        
        if not cv.contact.name:
            logger.error(f"❌ [CV_VALIDATION] Missing contact name")
            errors.append(CVValidationError(field="contact.name", message="Name is required", severity="error"))
        else:
            logger.info(f"✅ [CV_VALIDATION] Contact name present: {cv.contact.name}")
        
        if not cv.contact.email:
            logger.error(f"❌ [CV_VALIDATION] Missing contact email")
            errors.append(CVValidationError(field="contact.email", message="Email is required", severity="error"))
        else:
            logger.info(f"✅ [CV_VALIDATION] Contact email present: {cv.contact.email}")
        
        if not cv.experience:
            logger.error(f"❌ [CV_VALIDATION] Missing experience entries")
            errors.append(CVValidationError(field="experience", message="At least one experience entry is required", severity="error"))
        else:
            logger.info(f"✅ [CV_VALIDATION] Experience entries present: {len(cv.experience)}")
        
        if not cv.skills:
            logger.error(f"❌ [CV_VALIDATION] Missing skills section")
            errors.append(CVValidationError(field="skills", message="Skills section is required", severity="error"))
        else:
            logger.info(f"✅ [CV_VALIDATION] Skills section present: {len(cv.skills)} categories")
        
        # Content quality warnings
        for i, exp in enumerate(cv.experience):
            if len(exp.bullets) < 2:
                warnings.append(CVValidationError(
                    field=f"experience[{i}].bullets", 
                    message="Experience should have at least 2 bullet points", 
                    severity="warning"
                ))
            
            # Check for quantification in bullets
            quantified_bullets = [bullet for bullet in exp.bullets if any(char.isdigit() for char in bullet)]
            if len(quantified_bullets) < len(exp.bullets) * 0.5:
                suggestions.append(f"Experience at {exp.company}: Add more quantified achievements")
        
        # Skills structure validation
        total_skills = sum(len(cat.skills) for cat in cv.skills)
        if total_skills < 10:
            warnings.append(CVValidationError(
                field="skills", 
                message="Consider adding more skills (minimum 10 recommended)", 
                severity="warning"
            ))
        
        return CVValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _determine_optimization_strategy(
        self, 
        cv: OriginalCV, 
        recommendations: RecommendationAnalysis
    ) -> OptimizationStrategy:
        """
        Determine the optimization strategy based on CV and recommendations
        
        Args:
            cv: Original CV
            recommendations: Recommendation analysis
            
        Returns:
            OptimizationStrategy with specific optimization approach
        """
        # Determine experience level
        experience_level = self._calculate_experience_level(cv)
        
        # Determine section ordering based on experience level
        # Projects section will be included only if CV has projects
        base_sections_entry = ["contact", "education", "experience", "skills"]
        base_sections_mid = ["contact", "experience", "skills", "education"]
        base_sections_senior = ["contact", "experience", "skills", "education"]
        
        # Add projects section if available
        if cv.projects and len(cv.projects) > 0:
            if experience_level == ExperienceLevel.ENTRY_LEVEL:
                section_order = ["contact", "education", "experience", "projects", "skills"]
            elif experience_level == ExperienceLevel.MID_LEVEL:
                section_order = ["contact", "experience", "projects", "skills", "education"]
            else:  # Senior level
                section_order = ["contact", "experience", "skills", "projects", "education"]
        else:
            if experience_level == ExperienceLevel.ENTRY_LEVEL:
                section_order = base_sections_entry
                education_strategy = "education_first"
            elif experience_level == ExperienceLevel.MID_LEVEL:
                section_order = base_sections_mid
                education_strategy = "education_minimal"
            else:  # Senior level
                section_order = base_sections_senior
                education_strategy = "education_last"
        
        # Set education strategy
        if experience_level == ExperienceLevel.ENTRY_LEVEL:
            education_strategy = "education_first"
        elif experience_level == ExperienceLevel.MID_LEVEL:
            education_strategy = "education_minimal"
        else:
            education_strategy = "education_last"
        
        # Determine keyword placement strategy
        keyword_placement = {
            "skills": recommendations.critical_gaps[:5],  # Top critical skills in skills section
            "experience": recommendations.technical_enhancements,  # Technical enhancements in experience
        }
        
        # Add projects keyword placement only if projects exist
        if cv.projects and len(cv.projects) > 0:
            keyword_placement["projects"] = recommendations.keyword_integration[:3]  # Key integrations in projects
        
        # Identify quantification targets
        quantification_targets = []
        for exp in cv.experience:
            for bullet in exp.bullets:
                if not any(char.isdigit() for char in bullet):
                    quantification_targets.append(f"{exp.company} - {bullet[:50]}...")
        
        # Plan impact enhancements
        impact_enhancements = {
            "experience": recommendations.technical_enhancements,
            "skills": recommendations.missing_technical_skills
        }
        
        # Add projects impact enhancements only if projects exist
        if cv.projects and len(cv.projects) > 0:
            impact_enhancements["projects"] = recommendations.soft_skill_improvements
        
        return OptimizationStrategy(
            section_order=section_order,
            education_strategy=education_strategy,
            keyword_placement=keyword_placement,
            quantification_targets=quantification_targets,
            impact_enhancements=impact_enhancements
        )
    
    def _calculate_experience_level(self, cv: OriginalCV) -> ExperienceLevel:
        """Calculate experience level based on CV content"""
        if cv.total_years_experience:
            years = cv.total_years_experience
        else:
            # Estimate from experience entries
            years = len(cv.experience) * 2  # Rough estimate
        
        if years <= 2:
            return ExperienceLevel.ENTRY_LEVEL
        elif years <= 7:
            return ExperienceLevel.MID_LEVEL
        else:
            return ExperienceLevel.SENIOR_LEVEL
    
    async def _generate_tailored_cv(
        self,
        original_cv: OriginalCV,
        recommendations: RecommendationAnalysis,
        strategy: OptimizationStrategy,
        custom_instructions: Optional[str] = None
    ) -> TailoredCV:
        """Generate tailored CV using AI service"""
        import uuid
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] 🎯 Starting CV tailoring for {recommendations.company} with strategy: {strategy.education_strategy}")
        
        # Log initial stats
        logger.info(f"[{request_id}] Initial stats:")
        logger.info(f"[{request_id}] - Experience entries: {len(original_cv.experience)}")
        logger.info(f"[{request_id}] - Total bullets: {sum(len(exp.bullets) for exp in original_cv.experience)}")
        logger.info(f"[{request_id}] - Skills categories: {len(original_cv.skills)}")
        logger.info(f"[{request_id}] - Total skills: {sum(len(cat.skills) for cat in original_cv.skills)}")
        
        # Log critical gaps
        if recommendations.critical_gaps:
            logger.info(f"[{request_id}] Critical gaps to address: {', '.join(recommendations.critical_gaps[:5])}")
            logger.info(f"[{request_id}] Technical enhancements needed: {', '.join(recommendations.technical_enhancements[:5])}")
        
        # Prepare the comprehensive prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            original_cv, 
            recommendations, 
            strategy, 
            custom_instructions
        )
        
        # Generate response using AI service with retry logic
        logger.info(f"[{request_id}] 🤖 Generating tailored CV using AI service...")
        
        max_attempts = 5  # Increase attempts from 3 to 5
        for attempt in range(max_attempts):
            # Use progressively lower temperature for more consistent results
            if attempt == 0:
                temperature = 0.0
            elif attempt == 1:
                temperature = 0.0
            elif attempt == 2:
                temperature = 0.0
            else:
                temperature = 0.0  # Zero temperature for maximum consistency
            
            logger.info(f"[{request_id}] Attempt {attempt + 1}/{max_attempts} with temp={temperature}")
            logger.info(f"[{request_id}] - System prompt length: {len(system_prompt)}")
            logger.info(f"[{request_id}] - User prompt length: {len(user_prompt)}")
            
            # Create user data for AI service with real user ID
            from app.models.auth import UserData
            from datetime import datetime
            from app.database import SessionLocal
            from app.models.user import User
            
            # Get the real user ID from database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == self.user_email).first()
                if user:
                    user_id = str(user.id)
                    user_name = user.full_name or ""
                else:
                    user_id = "temp"
                    user_name = ""
            finally:
                db.close()
            
            user_data = UserData(
                id=user_id, 
                email=self.user_email, 
                name=user_name, 
                created_at=datetime.now(), 
                updated_at=datetime.now()
            )
            
            # Initialize AI service for this user
            ai_service.initialize_for_user(user_data)
            logger.info(f"[{request_id}] 🔄 Initialized AI service for user {self.user_email}")
            
            # Auto-select the first available provider if none is set
            if ai_service._providers and not ai_service.config.get_current_provider():
                first_provider = list(ai_service._providers.keys())[0]
                success = ai_service.switch_provider(first_provider, "gpt-3.5-turbo")
                if success:
                    logger.info(f"[{request_id}] ✅ Auto-selected provider: {first_provider}")
                else:
                    logger.warning(f"[{request_id}] ⚠️ Failed to auto-select provider: {first_provider}")
            
            ai_response = await ai_service.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=4000,
                user=user_data
            )
            
            # Log AI response stats
            logger.info(f"[{request_id}] AI response stats:")
            logger.info(f"[{request_id}] - Content length: {len(ai_response.content)}")
            logger.info(f"[{request_id}] - First 300 chars: {ai_response.content[:300].replace(chr(10), ' ')}...")
            
            # Try to parse and validate
            try:
                tailored_data = self._extract_and_parse_json(ai_response.content)
                assessment = self._validate_tailored_json(tailored_data, request_id=request_id)
                self._validate_real_cv_data_used(tailored_data, original_cv)
                self._validate_keyword_integration(tailored_data, recommendations, request_id=request_id)
                
                # If we get here, validation passed
                logger.info(f"[{request_id}] ✅ AI generation successful on attempt {attempt + 1}")
                break
                
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"[{request_id}] Attempt {attempt + 1} failed validation: {e}")
                if attempt == max_attempts - 1:
                    raise Exception(f"AI failed to generate compliant CV after {max_attempts} attempts: {str(e)}")
                else:
                    # Add more specific instructions for next attempt
                    user_prompt = self._add_correction_instructions(
                        user_prompt, 
                        str(e),
                        assessment.get("total_bullets", 0),
                        assessment.get("bullets_with_quantification", 0),
                        0.5
                    )
                    logger.info(f"[{request_id}] 🔁 Added correction instructions and retrying...")
                    continue
        
        # If quantification is below 60%, run up to 3 targeted enhancement attempts
        try:
            quant_ratio = assessment.get("quantification_ratio", 0.0)
        except Exception:
            quant_ratio = 0.0

        enhancement_tries = 0
        while quant_ratio < 0.60 and enhancement_tries < 3:
            enhancement_tries += 1
            logger.info(f"[{request_id}] 🔁 Quantification below 60% ({quant_ratio:.1%}). Enhancement attempt {enhancement_tries}/3")
            missing_list = "\n".join(assessment.get("missing_bullets", [])[:8])
            fix_msg = f"quantification: Add numbers to these bullets:\n{missing_list}"
            user_prompt = self._add_correction_instructions(
                user_prompt, 
                fix_msg,
                assessment.get("total_bullets", 0),
                assessment.get("bullets_with_quantification", 0),
                0.5
            )
            ai_response = await ai_service.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.0,
                max_tokens=4000,
                user=user_data
            )
            try:
                tailored_data = self._extract_and_parse_json(ai_response.content)
                assessment = self._validate_tailored_json(tailored_data, request_id=request_id)
                quant_ratio = assessment.get("quantification_ratio", 0.0)
            except Exception as e:
                logger.warning(f"[{request_id}] Enhancement attempt failed: {e}")
                break

        # Build tailored CV from validated (and possibly enhanced) data
        tailored_cv = self._construct_tailored_cv(
            original_cv,
            tailored_data,
            recommendations,
            strategy
        )
        return tailored_cv

    def _normalize_skills_taxonomy(self, cv: TailoredCV) -> TailoredCV:
        """Ensure Technical Skills only contain tools/tech and move domain terms to Domain Expertise."""
        if not cv.skills:
            return cv

        # Define heuristics
        technical_whitelist = set([
            'python','sql','excel','power bi','tableau','vba','pandas','numpy','matplotlib','seaborn',
            'aws','gcp','azure','snowflake','bigquery','redshift','docker','git','github','jenkins','airflow',
            'spark','hadoop','databricks','kafka','postgresql','mysql','mongodb','firebase','flask','django',
            'fastapi','rest','graphql','power query','power pivot','lookerstudio','superset'
        ])
        domain_keywords = set([
            'international aid','fundraising','not for profit','nfp','humanitarian','community engagement',
            'social impact','donor-centricity','donor centricity','non-profit','nonprofit'
        ])

        from app.tailored_cv.models.cv_models import SkillCategory

        technical_skills = []
        domain_expertise = []
        soft_skills = []
        others = []

        def classify(skill: str) -> str:
            s = skill.strip()
            sl = s.lower()
            if any(k in sl for k in domain_keywords):
                return 'domain'
            if sl in technical_whitelist or any(k in sl for k in technical_whitelist):
                return 'technical'
            # simple soft indicators
            if any(k in sl for k in ['communication','leadership','stakeholder','collaboration','teamwork','problem','analytical']):
                return 'soft'
            return 'other'

        # Flatten existing skills
        for cat in cv.skills:
            for s in cat.skills:
                kind = classify(s)
                if kind == 'technical':
                    technical_skills.append(s)
                elif kind == 'domain':
                    domain_expertise.append(s)
                elif kind == 'soft':
                    soft_skills.append(s)
                else:
                    others.append(s)

        # De-dup and keep concise
        def uniq(xs):
            seen = set()
            out = []
            for x in xs:
                xl = x.lower()
                if xl not in seen:
                    seen.add(xl)
                    out.append(x)
            return out

        technical_skills = uniq(technical_skills)
        domain_expertise = uniq(domain_expertise)
        soft_skills = uniq(soft_skills)

        new_skills = []
        if technical_skills:
            new_skills.append(SkillCategory(category='Technical Skills', skills=technical_skills))
        if domain_expertise:
            new_skills.append(SkillCategory(category='Domain Expertise', skills=domain_expertise))
        if soft_skills:
            new_skills.append(SkillCategory(category='Soft Skills', skills=soft_skills))
        if others:
            new_skills.append(SkillCategory(category='Other Skills', skills=uniq(others)))

        cv.skills = new_skills
        return cv
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with framework content"""
        return """You are an expert CV optimization specialist. You MUST follow the STREAMLINED CV OPTIMIZATION FRAMEWORK exactly.

""" + self.framework_content + """

ABSOLUTE REQUIREMENTS - YOU MUST IMPLEMENT ALL OF THESE:

1. CONTACT INFORMATION RULES:
   - COPY ALL contact fields EXACTLY from the original CV's contact section
   - NEVER leave any contact field empty or null - use empty string if no value exists
   - If a field exists in the original CV, you MUST include it with its exact value
   - Format for contact section:
     "contact": {
       "name": "EXACT name from CV",
       "phone": "EXACT phone from CV (no whitespace-only values)",
       "email": "EXACT email from CV",
       "location": "EXACT location from CV",
       "linkedin": "EXACT LinkedIn from CV or empty string if null",
       "website": "EXACT website from CV or empty string if null"
     }

2. EVERY BULLET MUST HAVE NUMBERS:
   Transform EVERY bullet point to include quantification.
   
   BAD: "Improved data pipeline efficiency"
   GOOD: "Improved data pipeline efficiency by 35%, processing 2M records daily"
   
   BAD: "Led team to deliver projects"
   GOOD: "Led 8-person team to deliver 5 projects worth $1.2M in 6 months"

2. KEYWORD INTEGRATION RULES:
   - ONLY add keywords that have semantic matches or clear evidence in the original CV
   - NEVER add keywords that cannot be reasonably inferred from existing experience
   - Look for synonyms and related terms in the original CV before adding keywords
   
   CORRECT APPROACH:
   Original: "Analyzed customer support data to improve response strategies"
   If 'customer service' is a missing keyword: OK to enhance as it's semantically present
   
   INCORRECT APPROACH:
   Original: "Analyzed data for business insights"
   DON'T ADD: "fundraising" or "humanitarian aid" if there's no related experience
   
   VALIDATION RULES:
   - For each keyword you plan to add, identify the specific experience or skill in the original CV that justifies it
   - If you cannot find semantic evidence in the CV, DO NOT add the keyword

4. PRESERVE EXACT DATA:
   - Companies: Use EXACT company names
   - Dates: Use EXACT dates

4. JSON OUTPUT RULES:
   - Output ONLY valid JSON
   - NO markdown, NO explanations, NO comments
   - Start with { and end with }
   - Use proper JSON structure

5. SECTION PRESERVATION RULES:
   - DO NOT create new top-level sections that do not exist in the provided CV
   - Only tailor and enhance the sections that are present in the provided CV
   - If a section is missing in the provided CV (e.g., Projects), DO NOT add it
   - Keep the same set of sections as the input; optimize content only

VERIFY BEFORE RESPONDING:
✓ Count bullets - do they ALL have numbers?
✓ Search for keywords - are they ALL present?
✓ Check names/dates - are they EXACTLY preserved?
✓ Valid JSON - proper format with no extra text?
✓ Sections preserved - no new sections introduced beyond the original

The exact JSON structure must be:
{
  "contact": {
    "name": "EXACT name from provided CV",
    "email": "EXACT email from provided CV",
    "phone": "EXACT phone from provided CV",
    "location": "EXACT location from provided CV"
  },
  "education": [
    {
      "institution": "EXACT institution from provided CV",
      "degree": "EXACT degree from provided CV",
      "location": "EXACT location from provided CV",
      "graduation_date": "EXACT graduation_date from provided CV (preserve all date information)",
      "gpa": "EXACT gpa from provided CV or empty string",
      "relevant_coursework": "EXACT relevant_coursework from provided CV or null",
      "honors": "EXACT honors from provided CV or null"
    }
  ],
  "experience": [
    {
      "company": "EXACT company from provided CV",
      "title": "EXACT or enhanced title from provided CV",
      "location": "EXACT location from provided CV",
      "start_date": "EXACT date from provided CV",
      "end_date": "EXACT date from provided CV",
      "bullets": ["enhanced bullet with quantified impact based on original", ...]
    }
  ],
  "skills": [
    {
      "category": "enhanced category name",
      "skills": ["skills from original CV plus recommended additions", ...]
    }
  ],
  "projects": [  // OPTIONAL - include only if original CV has projects
    {
      "name": "EXACT project name from provided CV",
      "bullets": ["enhanced project bullet with quantified impact", ...]
    }
  ],
  "optimization_notes": {
    "keywords_added": ["keyword1", "keyword2"],
    "impact_improvements": ["improvement1", "improvement2"],
    "ats_optimizations": ["optimization1", "optimization2"]
  }
}

CRITICAL: Use the REAL CV data provided. Do NOT generate fake examples. Respond with ONLY the JSON object."""
    
    def _build_user_prompt(
        self,
        cv: OriginalCV,
        recommendations: RecommendationAnalysis,
        strategy: OptimizationStrategy,
        custom_instructions: Optional[str]
    ) -> str:
        """Build the user prompt with CV data and recommendations"""
        
        cv_json = cv.model_dump_json(indent=2)
        rec_json = recommendations.model_dump_json(indent=2)
        strategy_json = strategy.model_dump_json(indent=2)
        
        # Build prompt without f-strings to avoid format specifier issues
        prompt = """Please tailor the following CV for the target company and role using the optimization framework.

TARGET POSITION:
Company: """ + recommendations.company + """
Role: """ + recommendations.job_title + """

ORIGINAL CV:
""" + cv_json + """

RECOMMENDATIONS TO IMPLEMENT:
""" + rec_json + """

OPTIMIZATION STRATEGY:
""" + strategy_json + """

YOUR TASK - TRANSFORM THIS CV:

0. CONTACT INFORMATION HANDLING:
   You MUST first copy ALL contact information from the original CV.
   Look for fields in both 'personal_information' and 'contact' sections.
   Example from original CV data above:
   "contact": {
     "name": "COPY EXACT NAME",
     "phone": "COPY EXACT PHONE (if whitespace/null, use '')",
     "email": "COPY EXACT EMAIL",
     "location": "COPY EXACT LOCATION",
     "linkedin": "COPY EXACT LINKEDIN (if null, use '')",
     "website": "COPY EXACT WEBSITE (if null, use '')"
   }

1. QUANTIFICATION RULES:
   Add realistic numbers based ONLY on evidence from the original CV:
   
   CORRECT APPROACH:
   Original: "Developed Python scripts for data cleaning"
   Look for:
   - Scale hints in the CV (team size, project scope)
   - Timeframe from employment dates
   - Technology constraints (what's realistic for the tools mentioned)
   Good: "Developed 3-5 Python scripts for data cleaning, processing 50K records weekly"
   
   INCORRECT APPROACH:
   Bad: "Processed 10M records daily" (unrealistic without evidence)
   Bad: "Improved efficiency by 95%" (suspiciously high)
   Bad: "Led team of 50 engineers" (no evidence of such scale)
   
   QUANTIFICATION GUIDELINES:
   - Use conservative numbers when uncertain
   - Numbers should match the role level and company size
   - Prefer ranges (3-5, 20-30%) over exact numbers when uncertain
   - Ensure numbers are consistent across all bullets

2. ADD THESE MISSING KEYWORDS TO BULLETS:
   Look at critical_gaps in recommendations. For EACH keyword listed:
   - Find a relevant bullet point
   - Add the keyword naturally
   
   Example: If "Fundraising" is in critical_gaps:
   Change: "Analyzed customer data to improve outcomes"
   To: "Analyzed customer data to improve fundraising campaign outcomes, increasing donations by 35%"

3. USE EXACT INFORMATION:
   Copy these EXACTLY from the original CV:
   - Name, Email, Phone (from contact section)
   - All company names (from experience section)
   - All dates (from experience and education)
   
4. EXAMPLE OF GOOD OUTPUT:
   "bullets": [
     "Led team of 8 analysts using Python/SQL to analyze 2M+ donor records for fundraising optimization, increasing donations by 40% ($3M annually)",
     "Developed 10+ Tableau dashboards tracking international aid distribution across 15 countries, improving efficiency by 35%",
     "Managed data pipeline processing 100K+ records daily for non-profit sector clients, reducing processing time by 60%"
   ]

"""
        
        if custom_instructions:
            prompt += "\nADDITIONAL CUSTOM INSTRUCTIONS:\n" + custom_instructions + "\n"
        
        prompt += """
CRITICAL REMINDERS:
- First, EXACTLY copy ALL contact information fields
- Use ONLY existing experiences - enhance and reframe, NEVER fabricate
- Add REALISTIC numbers based on CV evidence
- ONLY integrate keywords with semantic matches in original CV
- If a recommended keyword has no CV evidence, DO NOT ADD IT
- Use conservative estimates when adding metrics
- Maintain consistency in scale across all quantification
- Numbers should reflect actual role scope and company size
- Never return whitespace-only or null values - use empty string '' instead

REALISTIC METRICS EXAMPLES:
- Team size: 2-8 people (not 50+)
- Data processing: thousands to low millions (not billions)
- Improvement %: 15-40% (not 95%)
- Project counts: 3-10 (not 100+)
- Timeframes: Match employment duration

Please provide the optimized CV in the requested JSON format."""
        
        return prompt
    
    def _construct_tailored_cv(
        self,
        original_cv: OriginalCV,
        ai_generated_data: Dict[str, Any],
        recommendations: RecommendationAnalysis,
        strategy: OptimizationStrategy
    ) -> TailoredCV:
        # Enhanced skills extraction from experience
        extracted_skills = self._extract_skills_from_experience(original_cv.experience)
        
        # Skills categorization helper
        def categorize_skill(skill: str) -> str:
            technical_indicators = ['python', 'sql', 'tableau', 'bi', 'docker', 'git', 'analytics', 'data']
            soft_indicators = ['communication', 'leadership', 'collaboration', 'teamwork', 'mentoring', 'presenting']
            skill_lower = skill.lower()
            
            if any(ind in skill_lower for ind in technical_indicators):
                return 'Technical Skills'
            elif any(ind in skill_lower for ind in soft_indicators):
                return 'Soft Skills'
            return 'Domain Expertise'
        
        # Group extracted skills by category
        categorized_skills = {}
        for skill in extracted_skills:
            category = categorize_skill(skill)
            if category not in categorized_skills:
                categorized_skills[category] = set()
            categorized_skills[category].add(skill)
        
        """Construct TailoredCV object from AI-generated content"""
        
        # Extract optimization notes and applied enhancements
        optimization_notes = ai_generated_data.get("optimization_notes", {})
        
        # Convert AI-generated data to proper models
        from app.tailored_cv.models.cv_models import (
            ContactInfo, Education, ExperienceEntry, 
            Project, SkillCategory
        )
        
        # Process contact info
        contact_data = ai_generated_data.get("contact", {})
        contact = ContactInfo(**contact_data) if contact_data else original_cv.contact
        
        # Process education entries
        education_data = ai_generated_data.get("education", [])
        education = []
        for edu in education_data:
            education.append(Education(**edu))
        
        # Process experience entries - MOST IMPORTANT
        experience_data = ai_generated_data.get("experience", [])
        experience = []
        for exp in experience_data:
            experience.append(ExperienceEntry(**exp))
        
        # Process projects if present
        projects = None
        if "projects" in ai_generated_data and ai_generated_data["projects"]:
            projects = []
            for proj in ai_generated_data["projects"]:
                projects.append(Project(**proj))
        
        # Process skills
        skills_data = ai_generated_data.get("skills", [])
        skills = []
        for skill in skills_data:
            skills.append(SkillCategory(**skill))
        
        # Create the tailored CV with AI-generated content
        tailored_cv = TailoredCV(
            contact=contact,
            education=education if education else original_cv.education,
            experience=experience if experience else original_cv.experience,
            projects=projects if projects else original_cv.projects,
            skills=skills if skills else original_cv.skills,
            
            # Metadata
            source_cv_id=getattr(original_cv, 'id', None),
            target_company=recommendations.company,
            target_role=recommendations.job_title,
            optimization_strategy=strategy,
            
            # Enhancement tracking
            enhancements_applied=optimization_notes,
            keywords_integrated=recommendations.critical_gaps + recommendations.keyword_integration,
            quantifications_added=[],  # Will be populated based on changes
            
            # Quality metrics (to be calculated)
            estimated_ats_score=None,
            keyword_density=None,
            impact_statement_compliance=None
        )
        
        return tailored_cv
    
    def _create_clean_tailored_cv(self, full_tailored_cv: TailoredCV) -> 'CleanTailoredCV':
        """
        Convert a full TailoredCV with all metadata to a clean version with only CV content
        """
        from app.tailored_cv.models.cv_models import CleanTailoredCV
        
        clean_cv = CleanTailoredCV(
            contact=full_tailored_cv.contact,
            education=full_tailored_cv.education,
            experience=full_tailored_cv.experience,
            projects=full_tailored_cv.projects,
            skills=full_tailored_cv.skills,
            created_at=full_tailored_cv.created_at
        )
        
        return clean_cv
    
    def _extract_and_parse_json(self, content: str) -> Dict[str, Any]:
        """Extract and parse JSON from AI response with multiple strategies"""
        original_content = content
        content = content.strip()
        
        logger.info(f"Starting JSON extraction from content length: {len(content)}")
        
        # Strategy 1: Look for JSON content between code blocks
        if '```json' in content:
            logger.info("Found ```json markers, extracting content")
            json_start = content.find('```json') + 7
            json_end = content.find('```', json_start)
            if json_end != -1:
                content = content[json_start:json_end].strip()
                logger.info(f"Extracted JSON from markdown block, length: {len(content)}")
        elif '```' in content:
            logger.info("Found generic code block markers")
            # Generic code block
            json_start = content.find('```') + 3
            json_end = content.find('```', json_start)
            if json_end != -1:
                content = content[json_start:json_end].strip()
                logger.info(f"Extracted content from code block, length: {len(content)}")
        
        # Strategy 2: Find JSON object boundaries
        if not content.startswith('{'):
            brace_start = content.find('{')
            if brace_start != -1:
                content = content[brace_start:]
        
        # Strategy 3: Find the last complete JSON object if there are multiple
        if content.endswith('}'):
            last_brace = content.rfind('}')
            first_brace = content.find('{')
            if first_brace != -1 and last_brace != -1:
                content = content[first_brace:last_brace + 1]
        
        # Strategy 4: Clean up common AI response artifacts
        content = content.replace('```json', '').replace('```', '')
        content = content.strip()
        
        # Remove any leading/trailing text that's not part of JSON
        lines = content.split('\n')
        json_lines = []
        in_json = False
        brace_count = 0
        
        for line in lines:
            if '{' in line and not in_json:
                in_json = True
            
            if in_json:
                json_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                
                if brace_count == 0 and '}' in line:
                    break
        
        if json_lines:
            content = '\n'.join(json_lines)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed. Content: {content[:1000]}...")
            raise ValueError(f"Invalid JSON format in AI response: {e}")
    
    def _validate_tailored_json(self, data: Dict[str, Any], request_id: str = 'debug') -> None:
        """Validate that parsed JSON has expected structure and content quality"""
        required_fields = ['contact', 'experience', 'skills']
        
        # Log validation start
        logger.info(f"[{request_id}] 🔍 Starting JSON validation")
        
        for field in required_fields:
            if field not in data:
                logger.error(f"[{request_id}] ❌ Missing required field: {field}")
                raise ValueError(f"Required field '{field}' missing from AI response")
            else:
                logger.debug(f"[{request_id}] ✓ Found field: {field}")
        
        # Validate contact structure
        if not isinstance(data['contact'], dict):
            raise ValueError("Contact field must be an object")
        
        # Validate experience structure
        if not isinstance(data['experience'], list) or not data['experience']:
            raise ValueError("Experience field must be a non-empty array")
        
        # CRITICAL: Validate Impact Statement Formula compliance
        quantification_failures = []
        total_bullets = 0
        bullets_with_quantification = 0
        
        for i, exp in enumerate(data['experience']):
            if not isinstance(exp, dict) or 'bullets' not in exp:
                raise ValueError("Each experience entry must have bullets array")
            
            for j, bullet in enumerate(exp.get('bullets', [])):
                total_bullets += 1
                # Enhanced quantification detection
                has_numbers = any(char.isdigit() for char in bullet)
                has_percentage = '%' in bullet
                has_dollar = '$' in bullet or '£' in bullet or '€' in bullet
                has_times = any(word in bullet.lower() for word in ['times', 'x', '×'])
                has_ranges = '-' in bullet and any(char.isdigit() for char in bullet)
                has_quantification = has_numbers or has_percentage or has_dollar or has_times or has_ranges
                
                if has_quantification:
                    bullets_with_quantification += 1
                else:
                    quantification_failures.append(f"Experience {i+1}, bullet {j+1}: '{bullet[:60]}...'")
        
        # More realistic quantification requirements - 50% minimum (adjusted for different AI models)
        quantification_ratio = bullets_with_quantification / total_bullets if total_bullets > 0 else 0
        minimum_ratio = 0.50  # Further reduced to 50% to work with all AI models including GPT-3.5 Turbo
        
        # Create quality assessment and recommendations
        quality_assessment = {
            "quantification_ratio": quantification_ratio,
            "bullets_with_quantification": bullets_with_quantification,
            "total_bullets": total_bullets,
            "missing_bullets": quantification_failures[:8],
            "quality_grade": self._get_quality_grade(quantification_ratio),
            "model_recommendation": self._get_model_recommendation(quantification_ratio)
        }
        
        # Always generate CV, but provide appropriate warnings based on quality
        failure_summary = "\n".join(quantification_failures[:8]) if quantification_failures else ""
        
        if quantification_ratio < minimum_ratio:
            # Below minimum threshold - strong warning
            warning_message = f"""🚨 CV QUALITY WARNING - BELOW MINIMUM STANDARDS:

📊 ACHIEVED: {bullets_with_quantification}/{total_bullets} bullets quantified ({quantification_ratio:.1%})
🎯 OPTIMAL: {int(total_bullets * 0.75)}/{total_bullets} bullets quantified (75% for best ATS performance)
📈 MINIMUM: {int(total_bullets * minimum_ratio)}/{total_bullets} bullets quantified ({minimum_ratio:.0%} minimum recommended)

⚠️ IMPACT: This CV will likely underperform significantly in ATS systems.

BULLETS NEEDING IMPROVEMENT:
{failure_summary}

💡 STRONG RECOMMENDATION:
{quality_assessment['model_recommendation']}

⚡ URGENT FIXES NEEDED:
• Add specific numbers: "analyzed 500+ datasets", "reduced time by 30%"
• Include scale metrics: "managed $2M budget", "led 8-person team"  
• Specify timeframes: "completed in 6 months", "achieved within 3 weeks"
• Switch to GPT-4o Mini for much better quantification results
"""
            
            logger.warning(f"[{request_id}] CV created below minimum standards: {quantification_ratio:.1%} quantification")
        elif quantification_ratio < 0.75:
            # Above minimum but below optimal - moderate warning
            warning_message = f"""⚠️ CV QUALITY WARNING - SUBOPTIMAL QUANTIFICATION:

📊 ACHIEVED: {bullets_with_quantification}/{total_bullets} bullets quantified ({quantification_ratio:.1%})
🎯 OPTIMAL: {int(total_bullets * 0.75)}/{total_bullets} bullets quantified (75% for best ATS performance)
✅ STATUS: Above minimum threshold ({minimum_ratio:.0%}) but room for improvement

💡 RECOMMENDATIONS:
{quality_assessment['model_recommendation']}

⚡ IMPROVEMENT SUGGESTIONS:
• Add specific numbers: "analyzed 500+ datasets", "reduced time by 30%"
• Include scale metrics: "managed $2M budget", "led 8-person team"
• Specify timeframes: "completed in 6 months", "achieved within 3 weeks"
"""
            
            logger.info(f"[{request_id}] CV created with improvement suggestions: {quantification_ratio:.1%} quantification")
        else:
            # High quality - no warnings
            warning_message = None
            logger.info(f"[{request_id}] CV created with excellent quality: {quantification_ratio:.1%} quantification")
        
        # Store warnings if any
        if warning_message:
            self._quality_warnings = {
                "message": warning_message,
                "assessment": quality_assessment
            }
        else:
            self._quality_warnings = None
        
        # Validate skills structure
        if not isinstance(data['skills'], list):
            raise ValueError("Skills field must be an array")
        
        logger.info(f"✅ JSON structure and Impact Formula validation passed ({bullets_with_quantification}/{total_bullets} bullets with quantification)")

        # Return assessment so callers can make decisions (e.g., retry to improve quantification)
        return quality_assessment
    
    def _add_correction_instructions(self, user_prompt: str, error_message: str, total_bullets: int = 0, bullets_with_quantification: int = 0, minimum_ratio: float = 0.5) -> str:
        """Add specific correction instructions based on validation failure"""
        
        correction = "\n\nCORRECTION REQUIRED - THIS IS CRITICAL:\n"
        
        if "quantification" in error_message.lower():
            # Extract which bullets are missing quantification
            missing_bullets = []
            for line in error_message.split('\n'):
                if 'Experience' in line and 'bullet' in line:
                    missing_bullets.append(line.strip())
            
            correction += f"""
FIX THESE SPECIFIC BULLETS - ADD NUMBERS TO EACH:
{chr(10).join(missing_bullets[:8])}

CRITICAL: You need {max(0, int(total_bullets * minimum_ratio) - bullets_with_quantification)} MORE bullets with numbers to pass minimum validation.

EASY FIXES - Add these types of numbers:
• DATA SCALE: "analyzed 10K+ records", "processed 500+ files", "handled 50+ requests"  
• TIME SAVED: "reduced time by 40%", "improved speed by 2x", "completed in 30% less time"
• TEAM SIZE: "led 5-person team", "trained 15+ users", "supported 20+ stakeholders"
• FREQUENCY: "daily reports", "weekly analysis", "monthly presentations"
• SIMPLE COUNTS: "created 8 dashboards", "automated 12 processes", "identified 5 issues"

TRANSFORM THESE EXACT PATTERNS:
• "Python for analysis" → "Python to analyze 1K+ datasets" 
• "created dashboards" → "created 6 interactive dashboards"
• "improved efficiency" → "improved efficiency by 35%"
• "supported teams" → "supported 3 cross-functional teams"
• "data preprocessing" → "preprocessed 50K+ records"

JUST ADD REALISTIC NUMBERS TO EXISTING BULLETS - Don't change the core meaning!
"""
        
        if "keyword" in error_message.lower():
            correction += """
FIX: You MUST add ALL missing keywords!
- Look at critical_gaps list
- For EACH keyword, find a bullet and ADD it naturally
- Example: Add "fundraising" to a data analysis bullet
- Example: Add "international aid" to a project management bullet  
"""
        
        if "json" in error_message.lower():
            correction += """
FIX: Output ONLY valid JSON!
- Start with {
- End with }
- NO markdown, NO ```, NO explanations
- ONLY the JSON structure
"""
        
        return user_prompt + correction
    
    def _validate_real_cv_data_used(self, tailored_data: Dict[str, Any], original_cv: OriginalCV) -> None:
        """Skip placeholder-specific checks (e.g., 'John Doe') and allow generation to proceed."""
        logger.info("ℹ️ Skipping placeholder checks; proceeding with generated data as-is.")
    
    def _validate_keyword_integration(self, tailored_data: Dict[str, Any], recommendations: RecommendationAnalysis, request_id: str = 'debug') -> None:
        """Validate that critical missing keywords from recommendations are integrated"""
        # Log validation start
        logger.info(f"[{request_id}] 🔍 Starting keyword integration validation")
        
        # Get all text content from the tailored CV
        cv_text = ""
        
        # Add experience bullets with logging
        logger.info(f"[{request_id}] Scanning experience bullets:")
        for i, exp in enumerate(tailored_data.get('experience', [])):
            bullets = exp.get('bullets', [])
            logger.info(f"[{request_id}] - Experience {i+1}: {len(bullets)} bullets")
            cv_text += " ".join(bullets)
        
        # Add skills text with logging
        logger.info(f"[{request_id}] Scanning skills:")
        for i, skill_cat in enumerate(tailored_data.get('skills', [])):
            skills = skill_cat.get('skills', [])
            logger.info(f"[{request_id}] - Category {i+1}: {len(skills)} skills")
            cv_text += " ".join(skills)
        
        # Convert to lowercase for case-insensitive matching
        cv_text_lower = cv_text.lower()
        
        # Define keyword variations
        keyword_variations = {
            'results-driven': ['results driven', 'results-driven', 'results oriented', 'results-oriented', 'drive results'],
            'analytical': ['analysis', 'analytics', 'analyze', 'analytical'],
            'innovative': ['innovation', 'innovate', 'innovating'],
            'strategic': ['strategy', 'strategies', 'strategically'],
            'leadership': ['leader', 'led', 'leading'],
            'collaborative': ['collaboration', 'collaborate', 'collaborating', 'team'],
            'customer-focused': ['customer focused', 'customer-focused', 'customer centric', 'customer-centric'],
        }
        
        # Filter out non-keyword entries from critical_gaps
        valid_keywords = []
        for keyword in recommendations.critical_gaps[:10]:
            # Skip entries that look like category labels or statistics
            if '(' in keyword and '%' in keyword:
                logger.debug(f"Skipping non-keyword entry in critical_gaps: {keyword}")
                continue
            # Skip entries that are too long to be keywords
            if len(keyword) > 50:
                logger.debug(f"Skipping overly long entry in critical_gaps: {keyword[:50]}...")
                continue
            # Skip entries that contain special chars
            if any(c in keyword for c in [':', '=', '\n']):
                logger.debug(f"Skipping non-keyword with special chars: {keyword}")
                continue
            valid_keywords.append(keyword)
        
        # Only validate if we have actual keywords to check
        if not valid_keywords:
            logger.warning("⚠️ No valid keywords found in critical_gaps - using fallback keyword list")
            # Use the actual missing keywords from the recommendations
            valid_keywords = (recommendations.missing_keywords + 
                            recommendations.missing_technical_skills + 
                            recommendations.missing_soft_skills)[:5]
        
        # Check for critical missing keywords with variations
        missing_keywords = []
        for keyword in valid_keywords:
            keyword_lower = keyword.lower()
            
            # Check for keyword and its variations
            found = False
            
            # Direct match
            if keyword_lower in cv_text_lower:
                found = True
                continue
            
            # Check variations if available
            for base_keyword, variations in keyword_variations.items():
                if keyword_lower.replace('-', ' ') in variations:
                    # If the keyword is a known type, check all its variations
                    if any(var in cv_text_lower for var in variations):
                        found = True
                        break
            
            # Handle compound keywords (e.g., "data analysis")
            if not found and ' ' in keyword_lower:
                parts = keyword_lower.split()
                if all(part in cv_text_lower for part in parts):
                    found = True
            
            if not found:
                # Add to missing only if no variations were found
                missing_keywords.append(keyword)
        
        # Only fail if more than 50% of keywords are missing
        if missing_keywords and len(missing_keywords) > len(valid_keywords) * 0.5:
            missing_list = ", ".join(missing_keywords)
            raise ValueError(f"Critical keyword integration failure. Missing keywords: {missing_list}. These MUST be integrated into experience bullets or skills section.")
        elif missing_keywords:
            # Just warn if some keywords are missing but not too many
            logger.warning(f"⚠️ Some keywords not found but within acceptable range: {', '.join(missing_keywords)}")
        
        logger.info(f"✅ Keyword integration validation passed - {len(valid_keywords) - len(missing_keywords)}/{len(valid_keywords)} critical keywords found")
        
        logger.info(f"✅ Keyword integration validation passed - {len(valid_keywords)} critical keywords found")
    
    def _get_quality_grade(self, quantification_ratio: float) -> str:
        """Get quality grade based on quantification ratio"""
        if quantification_ratio >= 0.85:
            return "EXCELLENT (A+)"
        elif quantification_ratio >= 0.75:
            return "VERY GOOD (A)"
        elif quantification_ratio >= 0.65:
            return "GOOD (B+)"
        elif quantification_ratio >= 0.55:
            return "ACCEPTABLE (B)"
        elif quantification_ratio >= 0.45:
            return "BELOW AVERAGE (C)"
        elif quantification_ratio >= 0.35:
            return "POOR (D)"
        else:
            return "VERY POOR (F)"
    
    def _get_model_recommendation(self, quantification_ratio: float) -> str:
        """Get AI model recommendation based on performance"""
        if quantification_ratio >= 0.75:
            return "✅ Current AI model performing well! Continue using for consistent results."
        elif quantification_ratio >= 0.60:
            return "⚠️ Consider switching to GPT-4o Mini or Claude 3.5 Sonnet for better quantification."
        elif quantification_ratio >= 0.45:
            return "🔄 Strongly recommend switching to GPT-4o Mini for optimal CV quality and ATS performance."
        else:
            return "🚨 Current model not suitable for CV generation. Switch to GPT-4o Mini immediately for professional results."
    
    # Fallback CV creation removed - now raises errors for better debugging
    
    async def _estimate_ats_score(
        self,
        tailored_cv: TailoredCV,
        recommendations: RecommendationAnalysis,
        user_data: Any
    ) -> int:
        """
        Estimate ATS score for the tailored CV
        
        Args:
            tailored_cv: The tailored CV
            recommendations: Original recommendations
            
        Returns:
            Estimated ATS score (0-100)
        """
        try:
            # Use AI to estimate ATS score
            system_prompt = """You are an ATS (Applicant Tracking System) analyzer. 
            Analyze the provided CV and estimate its ATS score (0-100) based on:
            1. Keyword density and relevance
            2. Skills alignment with requirements
            3. Experience relevance
            4. Quantified achievements
            5. Professional formatting compatibility
            
            Respond with only a number between 0-100."""
            
            cv_text = self._convert_cv_to_text(tailored_cv)
            prompt = f"Analyze this CV for ATS score:\n\n{cv_text}"
            
            response = await ai_service.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                user=user_data,
                temperature=0.0,
                max_tokens=10
            )
            
            # Extract score from response
            score_text = response.content.strip()
            score = int(''.join(filter(str.isdigit, score_text)))
            return min(100, max(0, score))  # Ensure score is between 0-100
            
        except Exception as e:
            logger.error(f"Failed to estimate ATS score: {e}")
            raise Exception(f"ATS score estimation failed: {str(e)}")
    
    def _convert_cv_to_text(self, cv: TailoredCV) -> str:
        """Convert TailoredCV to plain text for analysis"""
        text_parts = []
        
        # Contact
        text_parts.append(f"{cv.contact.name}")
        text_parts.append(f"{cv.contact.email}")
        
        # Experience
        for exp in cv.experience:
            text_parts.append(f"{exp.company} - {exp.title}")
            text_parts.extend(exp.bullets)
        
        # Skills
        for skill_cat in cv.skills:
            text_parts.append(f"{skill_cat.category}: {', '.join(skill_cat.skills)}")
        
        # Projects
        if cv.projects:
            for proj in cv.projects:
                text_parts.append(f"Project: {proj.name}")
                text_parts.extend(proj.bullets)
        
        return "\n".join(text_parts)
    
    def _generate_processing_summary(
        self,
        original_cv: OriginalCV,
        tailored_cv: TailoredCV,
        recommendations: RecommendationAnalysis
    ) -> Dict[str, Any]:
        """Generate processing summary with statistics"""
        
        original_bullet_count = sum(len(exp.bullets) for exp in original_cv.experience)
        tailored_bullet_count = sum(len(exp.bullets) for exp in tailored_cv.experience)
        
        original_skills_count = sum(len(cat.skills) for cat in original_cv.skills)
        tailored_skills_count = sum(len(cat.skills) for cat in tailored_cv.skills)
        
        return {
            "processing_timestamp": datetime.utcnow().isoformat(),
            "target_company": recommendations.company,
            "target_role": recommendations.job_title,
            "original_bullet_points": original_bullet_count,
            "tailored_bullet_points": tailored_bullet_count,
            "original_skills_count": original_skills_count,
            "tailored_skills_count": tailored_skills_count,
            "keywords_integrated": len(tailored_cv.keywords_integrated),
            "critical_gaps_addressed": len([gap for gap in recommendations.critical_gaps if gap in str(tailored_cv.model_dump())]),
            "framework_version": tailored_cv.framework_version,
            "optimization_strategy": tailored_cv.optimization_strategy.education_strategy,
            "estimated_ats_improvement": (tailored_cv.estimated_ats_score or 80) - (recommendations.match_score or 60)
        }
    
    def _extract_applied_recommendations(self, tailored_cv: TailoredCV) -> List[str]:
        """Extract list of applied recommendations from tailored CV"""
        applied = []
        
        # Check enhancements applied
        if tailored_cv.enhancements_applied:
            applied.extend([f"Enhancement: {k}" for k in tailored_cv.enhancements_applied.keys()])
        
        # Check keyword integration
        if tailored_cv.keywords_integrated:
            applied.append(f"Keywords integrated: {len(tailored_cv.keywords_integrated)}")
        
        # Check quantifications
        if tailored_cv.quantifications_added:
            applied.append(f"Quantifications added: {len(tailored_cv.quantifications_added)}")
        
        return applied
    
    # Utility methods for file operations
    
    def save_tailored_cv(self, tailored_cv: TailoredCV, company_folder: str) -> str:
        """
        Save tailored CV to company-specific folder (both JSON and TXT formats)
        
        Args:
            tailored_cv: The tailored CV to save
            company_folder: Company folder path
            
        Returns:
            File path where CV was saved (JSON file)
        """
        try:
            company_path = Path(company_folder)
            company_path.mkdir(parents=True, exist_ok=True)
            
            # Extract company name from path
            company_name = company_path.name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_filename = f"{company_name}_tailored_cv_{timestamp}.json"
            txt_filename = f"{company_name}_tailored_cv_{timestamp}.txt"
            
            json_file_path = company_path / json_filename
            txt_file_path = company_path / txt_filename
            
            # Save JSON file
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(tailored_cv.model_dump(), f, indent=2, default=str)
            
            # Convert to text and save TXT file
            text_content = self._convert_tailored_cv_to_text(tailored_cv)
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"✅ Saved tailored CV to {json_file_path}")
            logger.info(f"✅ Saved tailored CV text to {txt_file_path}")

            # Register files in DB (best-effort)
            try:
                from app.database import SessionLocal
                from app.services.file_registry_service import FileRegistryService
                db = SessionLocal()
                try:
                    registry = FileRegistryService.from_email(db, self.user_email)
                    company_id = registry.upsert_company(company, display_name=company.replace('_', ' '))
                    file_id = registry.register_file(company_id, "tailored_cv", json_file_path, timestamp=timestamp)
                    registry.set_cv_pointer(company_id, "tailored", file_id)
                    registry.record_analysis_run(company_id, kind="tailoring", output_file_id=file_id)
                    db.commit()
                finally:
                    db.close()
            except Exception as reg_err:
                logger.warning(f"⚠️ [DB] Failed to register tailored CV: {reg_err}")
            return str(json_file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save tailored CV: {e}")
            raise
    
    def _convert_tailored_cv_to_text(self, tailored_cv: TailoredCV) -> str:
        """
        Convert tailored CV JSON to readable text format matching original CV format
        
        Args:
            tailored_cv: The tailored CV object
            
        Returns:
            Formatted text content matching original CV format
        """
        try:
            lines = []
            
            # No header - start directly with contact information like original CV
            
            # Contact Information - Single line format like original
            if tailored_cv.contact:
                contact_parts = []
                if tailored_cv.contact.name:
                    contact_parts.append(tailored_cv.contact.name)
                if tailored_cv.contact.phone:
                    contact_parts.append(tailored_cv.contact.phone)
                if tailored_cv.contact.email:
                    contact_parts.append(tailored_cv.contact.email)
                if tailored_cv.contact.linkedin:
                    contact_parts.append("LinkedIn")
                if tailored_cv.contact.location:
                    contact_parts.append(tailored_cv.contact.location)
                
                lines.append("  | ".join(contact_parts))
                lines.append("")
            
            # Professional Summary (if available in the model)
            # Note: This field might not exist in the current TailoredCV model
            # if hasattr(tailored_cv, 'professional_summary') and tailored_cv.professional_summary:
            #     lines.append("PROFESSIONAL SUMMARY")
            #     lines.append("-" * 20)
            #     lines.append(tailored_cv.professional_summary)
            #     lines.append("")
            
            # Skills - Format with categories to match JSON structure
            if tailored_cv.skills:
                lines.append("TECHNICAL SKILLS")
                for skill_category in tailored_cv.skills:
                    if skill_category.category and skill_category.skills:
                        lines.append(f"  {skill_category.category}:")
                        lines.append("  • " + ", ".join(skill_category.skills))
                lines.append("")
            
            # Experience - Format like original CV
            if tailored_cv.experience:
                lines.append("EXPERIENCE")
                for exp in tailored_cv.experience:
                    # Format: Title + Duration on same line
                    duration_str = f"{exp.start_date} – {exp.end_date}" if exp.start_date and exp.end_date else ""
                    lines.append(f"{exp.title}         {duration_str}")
                    
                    # Company and location on next line
                    if exp.company and exp.location:
                        lines.append(f"{exp.company}, {exp.location}")
                    elif exp.company:
                        lines.append(exp.company)
                    
                    lines.append("")
                    
                    # Bullets (sanitize to avoid double bullet prefixes)
                    if exp.bullets:
                        import re as _re
                        for bullet in exp.bullets:
                            try:
                                clean_bullet = _re.sub(r'^\s*[•*\-–—]+\s*', '', str(bullet))
                            except Exception:
                                clean_bullet = str(bullet)
                            lines.append(f"• {clean_bullet}")
                        lines.append("")
            
            # Education - Format like original CV with all data
            if tailored_cv.education:
                lines.append("EDUCATION")
                for edu in tailored_cv.education:
                    # Format: Degree on first line
                    lines.append(edu.degree)
                    
                    # Institution, location, GPA, and date on second line
                    edu_parts = []
                    if edu.institution:
                        edu_parts.append(edu.institution)
                    if edu.location:
                        edu_parts.append(edu.location)
                    if edu.gpa:
                        edu_parts.append(f"GPA {edu.gpa}")
                    if edu.graduation_date:
                        edu_parts.append(edu.graduation_date)
                    
                    if edu_parts:
                        lines.append(", ".join(edu_parts))
                    
                    # Relevant coursework if available
                    if edu.relevant_coursework:
                        lines.append(f"Relevant Coursework: {', '.join(edu.relevant_coursework)}")
                    
                    # Honors if available
                    if edu.honors:
                        lines.append(f"Honors: {', '.join(edu.honors)}")
                    
                    lines.append("")
            
            # Projects - Format like original CV
            if tailored_cv.projects:
                lines.append("PROJECTS")
                for project in tailored_cv.projects:
                    lines.append(f"{project.name}")
                    if project.context:
                        lines.append(f"{project.context}")
                    if project.technologies:
                        lines.append(f"Technologies: {', '.join(project.technologies)}")
                    if project.bullets:
                        import re as _re
                        for bullet in project.bullets:
                            try:
                                clean_bullet = _re.sub(r'^\s*[•*\-–—]+\s*', '', str(bullet))
                            except Exception:
                                clean_bullet = str(bullet)
                            lines.append(f"• {clean_bullet}")
                    lines.append("")
            
            # Note: Certifications and Languages are not part of the current TailoredCV model
            # If needed, they can be added to the model and uncommented here
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"❌ Failed to convert tailored CV to text: {e}")
            return f"Error converting CV to text: {str(e)}"
    
    def load_recommendation_file(self, company_folder: str) -> RecommendationAnalysis:
        """
        Load recommendation file from company folder
        
        Args:
            company_folder: Path to company folder
            
        Returns:
            RecommendationAnalysis object
        """
        try:
            # Strict selection: require a timestamped AI recommendation file for the company
            company_dir = Path(company_folder)
            from app.utils.timestamp_utils import TimestampUtils
            latest_file = TimestampUtils.find_latest_timestamped_file(
                company_dir, f"{company_dir.name}_ai_recommendation", "json"
            )
            if not latest_file:
                # No fallbacks: fail fast to surface the issue
                raise FileNotFoundError(
                    f"No timestamped AI recommendation found for {company_dir.name} in {company_folder}"
                )
            
            # Parse the recommendation file using our parser
            parsed_data = RecommendationParser.parse_recommendation_file(str(latest_file))
            
            return RecommendationAnalysis(**parsed_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to load recommendation file: {e}")
            raise
    
    def save_tailored_cv_to_analysis_folder(self, tailored_cv: TailoredCV, company: str) -> str:
        """
        Save tailored CV to the per-user cvs/tailored folder in cv-analysis with proper naming
        
        Args:
            tailored_cv: The tailored CV to save
            company: Company name for folder and file naming
            
        Returns:
            File path where CV was saved (JSON file)
        """
        try:
            # Path to cv-analysis/cvs/tailored folder (per-user location)
            tailored_folder = self.cv_analysis_path / "cvs" / "tailored"
            tailored_folder.mkdir(parents=True, exist_ok=True)
            
            # Use company-specific naming pattern with consistent timestamp format
            timestamp = TimestampUtils.get_timestamp()
            json_filename = f"{company}_tailored_cv_{timestamp}.json"
            txt_filename = f"{company}_tailored_cv_{timestamp}.txt"
            
            json_file_path = tailored_folder / json_filename
            txt_file_path = tailored_folder / txt_filename
            
            # Create clean version without metadata
            clean_cv = self._create_clean_tailored_cv(tailored_cv)
            
            # Save clean JSON file (without metadata)
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(clean_cv.model_dump(), f, indent=2, default=str)
            
            # Convert to text and save TXT file
            text_content = self._convert_tailored_cv_to_text(tailored_cv)
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # Generate PDF immediately after JSON/TXT creation
            try:
                from app.tailored_cv.services.pdf_export_service import export_tailored_cv_pdf
                from pathlib import Path
                
                # Create PDF export directory (company-specific)
                pdf_export_dir = self.cv_analysis_path / "cvs" / "pdf_cvs"
                pdf_export_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate PDF using the same JSON file
                pdf_path = export_tailored_cv_pdf(self.user_email, company, pdf_export_dir)
                
                logger.info(f"✅ Generated tailored CV PDF: {pdf_path}")
                
            except Exception as pdf_error:
                logger.warning(f"⚠️ Failed to generate PDF during CV save: {pdf_error}")
                # Don't fail the entire process if PDF generation fails
            
            logger.info(f"✅ Saved tailored CV to {json_file_path}")
            logger.info(f"✅ Saved tailored CV text to {txt_file_path}")
            return str(json_file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save tailored CV to analysis folder: {e}")
            raise
    
    def load_real_cv_and_recommendation(self, company: str) -> Tuple[OriginalCV, RecommendationAnalysis]:
        """
        Load the real CV and recommendation data for a company
        
        Args:
            company: Company name (e.g., "Australia_for_UNHCR", "Google", etc.)
            
        Returns:
            Tuple of (OriginalCV, RecommendationAnalysis)
        """
        try:
            # Paths
            company_folder = self.cv_analysis_path / "applied_companies" / company

            logger.info(f"Loading real data for {company}")
            logger.info(f"Company folder: {company_folder}")

            # Use user-specific unified latest file selector to choose the latest CV across tailored+original
            try:
                from app.unified_latest_file_selector import get_selector_for_user
                user_selector = get_selector_for_user(self.user_email)
                cv_ctx = user_selector.get_latest_cv_across_all(company)
                if not cv_ctx.exists:
                    raise FileNotFoundError("No CV file found via unified selector")
                # Prefer TXT file if JSON is empty, otherwise use JSON
                if cv_ctx.json_path and cv_ctx.json_path.exists() and cv_ctx.json_path.stat().st_size > 1000:
                    selected_cv_path = str(cv_ctx.json_path)
                elif cv_ctx.txt_path and cv_ctx.txt_path.exists():
                    selected_cv_path = str(cv_ctx.txt_path)
                else:
                    selected_cv_path = str(cv_ctx.json_path or cv_ctx.txt_path)
                logger.info(
                    f"📄 [TAILORING] Using latest CV via unified selector → type={cv_ctx.file_type}, ts={cv_ctx.timestamp}, path={selected_cv_path}"
                )
            except Exception as sel_err:
                # Fallback to original JSON path if selector fails
                logger.warning(f"⚠️ [TAILORING] Unified selector failed: {sel_err}. Falling back to original CV path")
                selected_cv_path = str(self.cv_analysis_path / "cvs" / "original" / "original_cv.json")

            # Debug logging for CV loading
            try:
                logger.info(f"🔍 [DEBUG] Loading CV from {selected_cv_path}")
                # Try to peek if it's json
                try:
                    with open(selected_cv_path, 'r', encoding='utf-8') as f:
                        peek = f.read(200)
                    logger.info(f"- First 200 chars: {peek.replace(chr(10),' ')[:200]}")
                except Exception:
                    pass
            except Exception:
                pass

            # Parse CV (RecommendationParser handles json/txt)
            cv_data = RecommendationParser.load_original_cv(selected_cv_path)
            logger.info(f"- Parsed CV data keys: {list(cv_data.keys() if isinstance(cv_data, dict) else [])}")
            
            # Check if CV data is empty and fall back to original_text if available
            if (isinstance(cv_data, dict) and 
                (not cv_data.get('contact', {}).get('name') or 
                 not cv_data.get('contact', {}).get('email') or
                 not cv_data.get('experience') or
                 not cv_data.get('skills'))):
                
                logger.warning("⚠️ [TAILORING] CV data is empty, checking for original_text fallback")
                
                # Try to load the JSON file and extract original_text
                if selected_cv_path.endswith('.json'):
                    try:
                        with open(selected_cv_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                        
                        if 'original_text' in json_data and json_data['original_text']:
                            logger.info("📄 [TAILORING] Found original_text, parsing as raw text")
                            # Parse the original_text as raw text
                            cv_data = RecommendationParser._parse_cv_text(json_data['original_text'])
                            logger.info(f"- Re-parsed CV data keys: {list(cv_data.keys() if isinstance(cv_data, dict) else [])}")
                    except Exception as e:
                        logger.warning(f"⚠️ [TAILORING] Failed to parse original_text: {e}")
            
            # Convert skills format if needed (from List[str] to List[SkillCategory])
            if isinstance(cv_data, dict) and 'skills' in cv_data:
                skills_data = cv_data['skills']
                if isinstance(skills_data, list) and len(skills_data) > 0:
                    # Check if skills are strings (need conversion) or already SkillCategory objects
                    if isinstance(skills_data[0], str):
                        logger.info("🔄 Converting skills from List[str] to List[SkillCategory]")
                        # Convert List[str] to List[SkillCategory]
                        from app.tailored_cv.models.cv_models import SkillCategory
                        cv_data['skills'] = [SkillCategory(category="Technical Skills", skills=skills_data)]
                    elif isinstance(skills_data[0], dict) and 'skills' in skills_data[0]:
                        # Already in SkillCategory format
                        logger.info("✅ Skills already in SkillCategory format")
                    else:
                        logger.warning(f"⚠️ Unknown skills format: {type(skills_data[0])}")
            
            # Validate CV data completeness and fallback to original CV if needed
            if isinstance(cv_data, dict):
                # Check if CV data is incomplete (missing essential fields)
                is_incomplete = (
                    not cv_data.get('contact', {}).get('name') or 
                    not cv_data.get('contact', {}).get('email') or
                    not cv_data.get('experience') or
                    not cv_data.get('skills')
                )
                
                if is_incomplete:
                    logger.warning("⚠️ [TAILORING] CV data is incomplete, falling back to original CV")
                    # Try to load the original CV as fallback
                    original_cv_path = self.cv_analysis_path / "cvs" / "original" / "original_cv.json"
                    if original_cv_path.exists() and str(original_cv_path) != selected_cv_path:
                        logger.info(f"📄 [TAILORING] Loading original CV as fallback: {original_cv_path}")
                        try:
                            cv_data = RecommendationParser.load_original_cv(str(original_cv_path))
                            logger.info("✅ [TAILORING] Successfully loaded original CV as fallback")
                            
                            # Re-apply skills conversion if needed
                            if isinstance(cv_data, dict) and 'skills' in cv_data:
                                skills_data = cv_data['skills']
                                if isinstance(skills_data, list) and len(skills_data) > 0 and isinstance(skills_data[0], str):
                                    from app.tailored_cv.models.cv_models import SkillCategory
                                    cv_data['skills'] = [SkillCategory(category="Technical Skills", skills=skills_data)]
                        except Exception as fallback_err:
                            logger.error(f"❌ [TAILORING] Failed to load original CV fallback: {fallback_err}")
            
            original_cv = OriginalCV(**cv_data)
            logger.info(f"- Final CV object attributes: {dir(original_cv)}")
            
            # Load recommendation
            if not company_folder.exists():
                raise FileNotFoundError(f"Company folder not found: {company_folder}. Available companies: {self.list_available_companies()}")
            
            recommendation = self.load_recommendation_file(str(company_folder))
            
            logger.info(f"✅ Loaded real CV and recommendation for {company}")
            return original_cv, recommendation
            
        except Exception as e:
            logger.error(f"❌ Failed to load real data for {company}: {e}")
            raise
    
    def list_available_companies(self) -> List[str]:
        """
        List all companies that have AI recommendation files
        
        Returns:
            List of company names that have recommendation files
        """
        try:
            companies = []
            
            if self.cv_analysis_path.exists():
                applied_companies_dir = self.cv_analysis_path / "applied_companies"
                if applied_companies_dir.exists():
                    for company_dir in applied_companies_dir.iterdir():
                        if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                            # Look for any AI recommendation file (with timestamp)
                            ai_files = list(company_dir.glob(f"{company_dir.name}_ai_recommendation_*.json"))
                            if ai_files:
                                companies.append(company_dir.name)
            
            return companies
            
        except Exception as e:
            logger.error(f"❌ Failed to list available companies: {e}")
            return []
    
    def _extract_skills_from_experience(self, experience_entries: List) -> List[str]:
        """
        Extract skills mentioned in experience bullets
        
        Args:
            experience_entries: List of ExperienceEntry objects
            
        Returns:
            List of extracted skills
        """
        extracted_skills = []
        
        # Common technical skills to look for
        skill_keywords = [
            'Python', 'SQL', 'Tableau', 'Power BI', 'Excel', 'Docker', 'Git', 'GitHub',
            'PostgreSQL', 'MySQL', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
            'Machine Learning', 'Data Analysis', 'Analytics', 'Visualization',
            'Dashboard', 'Reporting', 'Automation', 'ETL', 'Data Pipeline',
            'Statistics', 'Modeling', 'Forecasting', 'Segmentation'
        ]
        
        for entry in experience_entries:
            # Use object attribute instead of .get() since these are Pydantic objects
            bullets = entry.bullets if hasattr(entry, 'bullets') else []
            for bullet in bullets:
                if isinstance(bullet, str):
                    bullet_lower = bullet.lower()
                    for skill in skill_keywords:
                        if skill.lower() in bullet_lower and skill not in extracted_skills:
                            extracted_skills.append(skill)
        
        return extracted_skills


# Global instance removed - service now requires user_email parameter
# Create instances per request with proper user context