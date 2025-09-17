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
    
    def __init__(self):
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
            
            # Step 4: Post-process and validate results
            processing_summary = self._generate_processing_summary(
                request.original_cv,
                tailored_cv,
                request.recommendations
            )
            
            # Step 5: Estimate ATS score improvement
            estimated_score = await self._estimate_ats_score(tailored_cv, request.recommendations)
            tailored_cv.estimated_ats_score = estimated_score
            
            response = CVTailoringResponse(
                tailored_cv=tailored_cv,
                processing_summary=processing_summary,
                recommendations_applied=self._extract_applied_recommendations(tailored_cv),
                success=True
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
        errors = []
        warnings = []
        suggestions = []
        
        # Required fields validation
        if not cv.contact.name:
            errors.append(CVValidationError(field="contact.name", message="Name is required", severity="error"))
        
        if not cv.contact.email:
            errors.append(CVValidationError(field="contact.email", message="Email is required", severity="error"))
        
        if not cv.experience:
            errors.append(CVValidationError(field="experience", message="At least one experience entry is required", severity="error"))
        
        if not cv.skills:
            errors.append(CVValidationError(field="skills", message="Skills section is required", severity="error"))
        
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
        """
        Generate tailored CV using AI service
        
        Args:
            original_cv: Original CV data
            recommendations: Recommendation analysis
            strategy: Optimization strategy
            custom_instructions: Optional custom instructions
            
        Returns:
            TailoredCV with optimized content
        """
        # Prepare the comprehensive prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            original_cv, 
            recommendations, 
            strategy, 
            custom_instructions
        )
        
        # Generate response using AI service with retry logic
        logger.info("🤖 Generating tailored CV using AI service...")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1}/{max_attempts}")
            
            # Use lower temperature for more consistent results
            temperature = 0.2 if attempt == 0 else 0.1
            
            ai_response = await ai_service.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=4000
            )
            
            # Try to parse and validate
            try:
                tailored_data = self._extract_and_parse_json(ai_response.content)
                self._validate_tailored_json(tailored_data)
                self._validate_real_cv_data_used(tailored_data, original_cv)
                self._validate_keyword_integration(tailored_data, recommendations)
                
                # If we get here, validation passed
                logger.info(f"✅ AI generation successful on attempt {attempt + 1}")
                break
                
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Attempt {attempt + 1} failed validation: {e}")
                if attempt == max_attempts - 1:
                    raise Exception(f"AI failed to generate compliant CV after {max_attempts} attempts: {str(e)}")
                else:
                    # Add more specific instructions for next attempt
                    user_prompt = self._add_correction_instructions(user_prompt, str(e))
                    continue
        
        # Build tailored CV from validated data
        tailored_cv = self._construct_tailored_cv(
            original_cv,
            tailored_data,
            recommendations,
            strategy
        )
        return tailored_cv
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with framework content"""
        return """You are an expert CV optimization specialist. You MUST follow the STREAMLINED CV OPTIMIZATION FRAMEWORK exactly.

""" + self.framework_content + """

ABSOLUTE REQUIREMENTS - YOU MUST IMPLEMENT ALL OF THESE:

1. EVERY BULLET MUST HAVE NUMBERS:
   Transform EVERY bullet point to include quantification.
   
   BAD: "Improved data pipeline efficiency"
   GOOD: "Improved data pipeline efficiency by 35%, processing 2M records daily"
   
   BAD: "Led team to deliver projects"
   GOOD: "Led 8-person team to deliver 5 projects worth $1.2M in 6 months"

2. ALL KEYWORDS MUST APPEAR:
   If recommendations say "Fundraising" is missing - ADD IT to relevant bullets.
   If recommendations say "International Aid" is missing - ADD IT to relevant bullets.
   Every keyword in critical_gaps MUST appear in the final CV.

3. PRESERVE EXACT DATA:
   - Name: Use EXACT name from original CV
   - Email: Use EXACT email from original CV  
   - Phone: Use EXACT phone from original CV
   - Companies: Use EXACT company names
   - Dates: Use EXACT dates

4. JSON OUTPUT RULES:
   - Output ONLY valid JSON
   - NO markdown, NO explanations, NO comments
   - Start with { and end with }
   - Use proper JSON structure

VERIFY BEFORE RESPONDING:
✓ Count bullets - do they ALL have numbers?
✓ Search for keywords - are they ALL present?
✓ Check names/dates - are they EXACTLY preserved?
✓ Valid JSON - proper format with no extra text?

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
      "graduation_date": "EXACT date from provided CV"
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

1. ADD NUMBERS TO EVERY BULLET:
   Look at each bullet point. If it has no numbers, ADD THEM:
   
   Original: "Designed and implemented Python scripts for data cleaning"
   Transform to: "Designed and implemented 15+ Python scripts for data cleaning, processing 500K records daily, reducing errors by 45%"
   
   Original: "Developed machine learning models"
   Transform to: "Developed 5 machine learning models achieving 92% accuracy, predicting outcomes for 10K+ customers monthly"

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
- Use ONLY existing experiences - enhance and reframe, NEVER fabricate
- Every bullet must include quantified metrics
- Integrate all missing technical and soft skills naturally
- Maintain professional tone and authenticity
- Target 80+ ATS score optimization

Please provide the optimized CV in the requested JSON format."""
        
        return prompt
    
    def _construct_tailored_cv(
        self,
        original_cv: OriginalCV,
        ai_generated_data: Dict[str, Any],
        recommendations: RecommendationAnalysis,
        strategy: OptimizationStrategy
    ) -> TailoredCV:
        """Construct TailoredCV object from AI-generated content"""
        
        # Extract optimization notes and applied enhancements
        optimization_notes = ai_generated_data.get("optimization_notes", {})
        
        # Create the tailored CV
        tailored_cv = TailoredCV(
            contact=original_cv.contact.model_copy(update=ai_generated_data.get("contact", {})),
            education=original_cv.education,  # Will be enhanced by AI data
            experience=original_cv.experience,  # Will be enhanced by AI data
            projects=original_cv.projects,  # Will be enhanced by AI data
            skills=original_cv.skills,  # Will be enhanced by AI data
            
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
    
    def _validate_tailored_json(self, data: Dict[str, Any]) -> None:
        """Validate that parsed JSON has expected structure and content quality"""
        required_fields = ['contact', 'experience', 'skills']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' missing from AI response")
        
        # Validate contact structure
        if not isinstance(data['contact'], dict):
            raise ValueError("Contact field must be an object")
        
        # Validate experience structure
        if not isinstance(data['experience'], list) or not data['experience']:
            raise ValueError("Experience field must be a non-empty array")
        
        # CRITICAL: Validate Impact Statement Formula compliance
        quantification_failures = []
        for i, exp in enumerate(data['experience']):
            if not isinstance(exp, dict) or 'bullets' not in exp:
                raise ValueError("Each experience entry must have bullets array")
            
            for j, bullet in enumerate(exp.get('bullets', [])):
                # Check for quantification (numbers, percentages, dollar amounts)
                has_numbers = any(char.isdigit() for char in bullet)
                has_percentage = '%' in bullet
                has_dollar = '$' in bullet
                has_quantification = has_numbers or has_percentage or has_dollar
                
                if not has_quantification:
                    quantification_failures.append(f"Experience {i+1}, bullet {j+1}: '{bullet[:60]}...'")
        
        if quantification_failures:
            failure_summary = "\n".join(quantification_failures)
            raise ValueError(f"Impact Statement Formula violation - bullets missing quantification:\n{failure_summary}")
        
        # Validate skills structure
        if not isinstance(data['skills'], list):
            raise ValueError("Skills field must be an array")
        
        logger.info("✅ JSON structure and Impact Formula validation passed")
    
    def _add_correction_instructions(self, user_prompt: str, error_message: str) -> str:
        """Add specific correction instructions based on validation failure"""
        
        correction = "\n\nCORRECTION REQUIRED:\n"
        
        if "quantification" in error_message.lower():
            correction += """
FIX: You MUST add numbers to EVERY bullet point!
- Count each bullet
- If ANY bullet has no numbers, ADD THEM
- Use realistic numbers: 10+ items, 25% improvement, $500K value, 3 months, etc.
"""
        
        if "keyword" in error_message.lower():
            correction += """
FIX: You MUST add ALL missing keywords!
- Look at critical_gaps list
- For EACH keyword, find a bullet and ADD it
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
    
    def _validate_keyword_integration(self, tailored_data: Dict[str, Any], recommendations: RecommendationAnalysis) -> None:
        """Validate that critical missing keywords from recommendations are integrated"""
        # Get all text content from the tailored CV
        cv_text = ""
        
        # Add experience bullets
        for exp in tailored_data.get('experience', []):
            cv_text += " ".join(exp.get('bullets', []))
        
        # Add skills text
        for skill_cat in tailored_data.get('skills', []):
            cv_text += " ".join(skill_cat.get('skills', []))
        
        # Convert to lowercase for case-insensitive matching
        cv_text_lower = cv_text.lower()
        
        # Check for critical missing keywords
        missing_keywords = []
        critical_keywords = recommendations.critical_gaps[:5]  # Top 5 critical gaps
        
        for keyword in critical_keywords:
            if keyword.lower() not in cv_text_lower:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            missing_list = ", ".join(missing_keywords)
            raise ValueError(f"Critical keyword integration failure. Missing keywords: {missing_list}. These MUST be integrated into experience bullets or skills section.")
        
        logger.info(f"✅ Keyword integration validation passed - {len(critical_keywords)} critical keywords found")
    
    # Fallback CV creation removed - now raises errors for better debugging
    
    async def _estimate_ats_score(
        self,
        tailored_cv: TailoredCV,
        recommendations: RecommendationAnalysis
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
                temperature=0.1,
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
        Save tailored CV to company-specific folder
        
        Args:
            tailored_cv: The tailored CV to save
            company_folder: Company folder path
            
        Returns:
            File path where CV was saved
        """
        try:
            company_path = Path(company_folder)
            company_path.mkdir(parents=True, exist_ok=True)
            
            filename = f"tailored_cv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = company_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(tailored_cv.model_dump(), f, indent=2, default=str)
            
            logger.info(f"✅ Saved tailored CV to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save tailored CV: {e}")
            raise
    
    def load_recommendation_file(self, company_folder: str) -> RecommendationAnalysis:
        """
        Load recommendation file from company folder
        
        Args:
            company_folder: Path to company folder
            
        Returns:
            RecommendationAnalysis object
        """
        try:
            # Look for AI recommendation files
            recommendation_files = list(Path(company_folder).glob("*_ai_recommendation.json"))
            if not recommendation_files:
                # Fallback to any recommendation file
                recommendation_files = list(Path(company_folder).glob("*recommendation*.json"))
            
            if not recommendation_files:
                raise FileNotFoundError(f"No recommendation file found in {company_folder}")
            
            # Use the most recent recommendation file
            latest_file = max(recommendation_files, key=lambda p: p.stat().st_mtime)
            
            # Parse the recommendation file using our parser
            parsed_data = RecommendationParser.parse_recommendation_file(str(latest_file))
            
            return RecommendationAnalysis(**parsed_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to load recommendation file: {e}")
            raise
    
    def save_tailored_cv_to_analysis_folder(self, tailored_cv: TailoredCV) -> str:
        """
        Save tailored CV to the cv-analysis folder as tailored_cv.json
        
        Args:
            tailored_cv: The tailored CV to save
            
        Returns:
            File path where CV was saved
        """
        try:
            # Path to cv-analysis folder
            cv_analysis_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
            cv_analysis_path.mkdir(parents=True, exist_ok=True)
            
            file_path = cv_analysis_path / "tailored_cv.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(tailored_cv.model_dump(), f, indent=2, default=str)
            
            logger.info(f"✅ Saved tailored CV to {file_path}")
            return str(file_path)
            
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
            # Paths to the real files
            cv_analysis_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
            original_cv_path = cv_analysis_path / "original_cv.json"
            company_folder = cv_analysis_path / company
            
            logger.info(f"Loading real data for {company}")
            logger.info(f"CV path: {original_cv_path}")
            logger.info(f"Company folder: {company_folder}")
            
            # Load original CV
            if not original_cv_path.exists():
                raise FileNotFoundError(f"Original CV not found at {original_cv_path}")
            
            cv_data = RecommendationParser.load_original_cv(str(original_cv_path))
            original_cv = OriginalCV(**cv_data)
            
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
            cv_analysis_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
            companies = []
            
            if cv_analysis_path.exists():
                for company_dir in cv_analysis_path.iterdir():
                    if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                        ai_file = company_dir / f"{company_dir.name}_ai_recommendation.json"
                        if ai_file.exists():
                            companies.append(company_dir.name)
            
            return companies
            
        except Exception as e:
            logger.error(f"❌ Failed to list available companies: {e}")
            return []


# Create service instance
cv_tailoring_service = CVTailoringService()