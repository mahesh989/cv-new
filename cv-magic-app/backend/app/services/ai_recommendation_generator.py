"""
AI Recommendation Generator Service

This service executes AI recommendation prompts using the centralized AI system
and saves the generated recommendations as structured JSON files.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from app.ai.ai_service import ai_service
from app.ai.base_provider import AIResponse
from app.utils.timestamp_utils import TimestampUtils

# Import CV tailoring service with conditional import to avoid circular dependencies
try:
    from app.tailored_cv.services.cv_tailoring_service import cv_tailoring_service
    CV_TAILORING_AVAILABLE = True
except ImportError:
    CV_TAILORING_AVAILABLE = False
    cv_tailoring_service = None

logger = logging.getLogger(__name__)


class AIRecommendationGenerator:
    """Service for generating AI-based CV optimization recommendations"""
    
    def __init__(self):
        from app.utils.user_path_utils import get_user_base_path
        # get_user_base_path already returns the per-user cv-analysis directory
        # Avoid duplicating "cv-analysis" in the path
        self.base_dir = get_user_base_path("admin@admin.com")
        self.prompt_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/prompt")
    
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
            
            # Check recency between latest input recommendation and latest AI recommendation
            output_file = self._get_output_file_path(company)
            if not force_regenerate:
                try:
                    company_dir = self.base_dir / "applied_companies" / company
                    # Find latest input recommendation (timestamped preferred)
                    latest_input = TimestampUtils.find_latest_timestamped_file(
                        company_dir, f"{company}_input_recommendation", "json"
                    ) or (company_dir / f"{company}_input_recommendation.json")

                    # Find latest AI recommendation (timestamped preferred)
                    latest_ai = TimestampUtils.find_latest_timestamped_file(
                        company_dir, f"{company}_ai_recommendation", "json"
                    ) or (company_dir / f"{company}_ai_recommendation.json")

                    latest_input_mtime = latest_input.stat().st_mtime if latest_input and latest_input.exists() else 0
                    latest_ai_mtime = latest_ai.stat().st_mtime if latest_ai and latest_ai.exists() else 0

                    # If an AI file exists and is newer or equal to input, we can skip;
                    # otherwise we must regenerate to reflect the latest input recommendations.
                    if latest_ai.exists() and latest_ai_mtime >= latest_input_mtime:
                        logger.info(
                            f"🟢 [AI GENERATOR] Latest AI recommendation ({latest_ai.name}) is up-to-date vs input ({latest_input.name if latest_input else 'N/A'}); skipping regeneration"
                        )
                        return True
                    else:
                        logger.info(
                            f"🟡 [AI GENERATOR] Input recommendation is newer (ai_mtime={latest_ai_mtime}, input_mtime={latest_input_mtime}); regenerating AI recommendation"
                        )
                except Exception as time_err:
                    # If any error during timestamp checks, fall back to default existence check
                    logger.warning(f"⚠️ [AI GENERATOR] Timestamp check failed, proceeding with generation: {time_err}")
            
            # Check if CV has been updated since input recommendation was generated
            if not self._check_cv_freshness(company):
                logger.warning(f"⚠️ [AI GENERATOR] CV has been updated since input recommendation was generated")
                logger.warning(f"⚠️ [AI GENERATOR] Input recommendation may be outdated - consider regenerating input recommendation first")
            
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
                logger.info(f"📄 File: {output_file}")
                logger.info(f"💰 Cost: ${ai_response.cost:.4f}")
                logger.info(f"🔤 Tokens: {ai_response.tokens_used}")
                
                # Automatically trigger CV tailoring after successful AI recommendation generation
                try:
                    cv_success = await self._trigger_cv_tailoring(company)
                    if cv_success:
                        logger.info(f"🎯 [AI GENERATOR] CV tailoring completed automatically for {company}")
                    else:
                        logger.warning(f"⚠️ [AI GENERATOR] CV tailoring failed for {company}")
                except Exception as cv_error:
                    logger.error(f"❌ [AI GENERATOR] CV tailoring error for {company}: {cv_error}")
                    # Don't fail the AI recommendation generation if CV tailoring fails
            
            return success
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error generating AI recommendation for {company}: {e}")
            return False
    
    def _get_output_file_path(self, company: str) -> Path:
        """Get the latest output file path for AI recommendation"""
        company_dir = self.base_dir / "applied_companies" / company
        latest_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "json")
        if latest_file:
            return latest_file
        # Return expected path for new file (without timestamp - will be added during save)
        return company_dir / f"{company}_ai_recommendation.json"
    
    def _get_input_recommendation_file_path(self, company: str) -> Path:
        """Get the input recommendation file path for a company"""
        company_dir = self.base_dir / "applied_companies" / company
        
        # Use timestamped file with fallback
        from app.utils.timestamp_utils import TimestampUtils
        input_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_input_recommendation", "json")
        if not input_file:
            input_file = company_dir / f"{company}_input_recommendation.json"
        
        return input_file
    
    def _check_cv_freshness(self, company: str) -> bool:
        """
        Check if the CV has been updated since the input recommendation was generated
        
        Args:
            company: Company name
            
        Returns:
            True if CV is fresh (not updated since input recommendation), False otherwise
        """
        try:
            from app.unified_latest_file_selector import unified_selector
            
            # Get the latest CV context
            cv_context = unified_selector.get_latest_cv_across_all(company)
            if not cv_context.exists:
                logger.warning(f"⚠️ [AI GENERATOR] No CV found for {company}")
                return True  # Assume fresh if no CV found
            
            # Get the input recommendation file
            input_file = self._get_input_recommendation_file_path(company)
            if not input_file.exists():
                logger.warning(f"⚠️ [AI GENERATOR] No input recommendation file found for {company}")
                return True  # Assume fresh if no input recommendation found
            
            # Compare timestamps
            cv_mtime = cv_context.timestamp.timestamp() if cv_context.timestamp else 0
            input_mtime = input_file.stat().st_mtime
            
            if cv_mtime > input_mtime:
                logger.warning(f"⚠️ [AI GENERATOR] CV is newer than input recommendation")
                logger.warning(f"   CV timestamp: {cv_context.timestamp}")
                logger.warning(f"   Input recommendation timestamp: {input_mtime}")
                return False
            
            logger.info(f"✅ [AI GENERATOR] CV is fresh - no updates since input recommendation")
            return True
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error checking CV freshness: {e}")
            return True  # Assume fresh on error to avoid blocking generation
    
    def _load_ai_prompt(self, company: str) -> Optional[str]:
        """
        Generate AI prompt using the centralized template with company analysis data
        
        Args:
            company: Company name
            
        Returns:
            Generated prompt content or None if data not found
        """
        try:
            # Load the input recommendation data for the company
            input_file = self._get_input_recommendation_file_path(company)
            if not input_file.exists():
                logger.error(f"Input recommendation file not found: {input_file}")
                return None
            
            # Load analysis data
            with open(input_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Import the centralized prompt template using absolute path
            import sys
            import importlib.util
            
            template_path = self.prompt_dir / "ai_recommendation_prompt_template.py"
            if not template_path.exists():
                logger.error(f"AI recommendation template not found: {template_path}")
                return None
            
            # Load the template module
            spec = importlib.util.spec_from_file_location("ai_recommendation_prompt_template", template_path)
            template_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_module)
            
            # Generate the prompt using the template
            prompt_content = template_module.generate_ai_recommendation_prompt(company, analysis_data)
            
            logger.info(f"📋 [AI GENERATOR] Generated AI prompt for {company} using centralized template ({len(prompt_content)} characters)")
            return prompt_content
                
        except Exception as e:
            logger.error(f"Error generating AI prompt for {company}: {e}")
            return None
    
    async def _execute_ai_prompt(self, prompt_content: str) -> Optional[AIResponse]:
        """
        Execute the AI prompt using the centralized AI system
        
        Args:
            prompt_content: The prompt to execute
            
        Returns:
            AIResponse object or None if failed
        """
        try:
            # Use the enhanced AI service with API key validation
            from app.services.enhanced_ai_service import enhanced_ai_service
            
            response = await enhanced_ai_service.generate_response_with_validation(
                prompt=prompt_content,
                system_prompt="You are an expert CV strategist and career consultant. Provide detailed, actionable recommendations in the exact format requested.",
                temperature=0.0,  # Zero temperature for maximum consistency
                max_tokens=4000   # Allow for detailed responses
            )
            
            logger.info(f"🧠 [AI GENERATOR] AI response generated - Provider: {response.provider}, Model: {response.model}")
            logger.info(f"💰 [AI GENERATOR] Cost: ${response.cost:.4f}, Tokens: {response.tokens_used}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing AI prompt: {e}")
            return None
    
    def _structure_ai_response(self, ai_response: AIResponse, company: str) -> Dict[str, Any]:
        """
        Structure the AI response as JSON data
        
        Args:
            ai_response: Raw AI response
            company: Company name
            
        Returns:
            Structured JSON data with recommendation content and metadata
        """
        return {
            "company": company,
            "generated_at": datetime.now().isoformat(),
            "recommendation_content": ai_response.content,
            "ai_model_info": {
                "provider": ai_response.provider,
                "model": ai_response.model,
                "cost": ai_response.cost,
                "tokens_used": ai_response.tokens_used
            },
            "metadata": {
                "content_length": len(ai_response.content),
                "format_version": "1.0"
            }
        }
    
    def _save_ai_recommendation(self, company: str, recommendation_data: Dict[str, Any]) -> bool:
        """
        Save the AI recommendation data as JSON file
        
        Args:
            company: Company name
            recommendation_data: The structured recommendation data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure company directory exists
            company_dir = self.base_dir / "applied_companies" / company
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON file with timestamp
            timestamp = TimestampUtils.get_timestamp()
            output_file = company_dir / f"{company}_ai_recommendation_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(recommendation_data, f, indent=2, ensure_ascii=False)
            
            file_size = output_file.stat().st_size / 1024
            logger.info(f"💾 [AI GENERATOR] Saved AI recommendation: {output_file} ({file_size:.1f}KB)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving AI recommendation for {company}: {e}")
            return False
    
    def get_ai_recommendation_path(self, company: str) -> Path:
        """Get the path to AI recommendation file"""
        return self._get_output_file_path(company)
    
    def check_ai_recommendation_exists(self, company: str) -> bool:
        """Check if AI recommendation file exists"""
        company_dir = self.base_dir / "applied_companies" / company
        latest_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "json")
        return latest_file is not None and latest_file.exists()
    
    def list_companies_with_ai_recommendations(self) -> List[str]:
        """
        List all companies that have AI recommendation files
        
        Returns:
            List of company names
        """
        companies = []
        
        try:
            if not self.base_dir.exists():
                return companies
            
            for company_dir in self.base_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    # Check for timestamped AI recommendation files
                    latest_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_ai_recommendation", "json")
                    if latest_file and latest_file.exists():
                        companies.append(company_dir.name)
            
            logger.info(f"Found {len(companies)} companies with AI recommendations")
            return companies
            
        except Exception as e:
            logger.error(f"Error listing companies with AI recommendations: {e}")
            return companies
    
    async def batch_generate_recommendations(
        self, 
        companies: Optional[List[str]] = None, 
        force_regenerate: bool = False,
        max_concurrent: int = 3
    ) -> Dict[str, bool]:
        """
        Generate AI recommendations for multiple companies in batch
        
        Args:
            companies: List of company names (if None, process all with prompts)
            force_regenerate: Force regeneration even if files exist
            max_concurrent: Maximum concurrent AI requests
            
        Returns:
            Dictionary mapping company names to success status
        """
        if companies is None:
            companies = self._find_companies_with_prompts()
        
        logger.info(f"🔄 [AI GENERATOR] Starting batch AI recommendation generation for {len(companies)} companies")
        
        # Create semaphore to limit concurrent AI requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(company: str) -> tuple[str, bool]:
            async with semaphore:
                success = await self.generate_ai_recommendation(company, force_regenerate)
                return company, success
        
        # Execute batch generation with concurrency control
        tasks = [generate_with_semaphore(company) for company in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch generation task failed: {result}")
                continue
            
            company, success = result
            final_results[company] = success
        
        successful_count = sum(1 for success in final_results.values() if success)
        logger.info(f"✅ [AI GENERATOR] Batch generation complete: {successful_count}/{len(companies)} successful")
        
        return final_results
    
    def _find_companies_with_prompts(self) -> List[str]:
        """Find all companies that have prompt files"""
        companies = []
        
        try:
            if not self.prompt_dir.exists():
                return companies
            
            for prompt_file in self.prompt_dir.glob("*_prompt_recommendation.py"):
                company_name = prompt_file.stem.replace("_prompt_recommendation", "")
                companies.append(company_name)
            
            return companies
            
        except Exception as e:
            logger.error(f"Error finding companies with prompts: {e}")
            return companies
    
    def get_ai_recommendation_info(self, company: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an AI recommendation file
        
        Args:
            company: Company name
            
        Returns:
            Information dictionary or None if not found
        """
        try:
            ai_file = self._get_output_file_path(company)
            
            if not ai_file.exists():
                return None
            
            # Get file stats
            stat_info = ai_file.stat()
            
            # Read content from JSON file
            with open(ai_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "company": company,
                "file_path": str(ai_file),
                "file_size": stat_info.st_size,
                "last_modified": stat_info.st_mtime,
                "content_length": len(data.get("recommendation_content", "")),
                "has_content": bool(data.get("recommendation_content", "").strip()),
                "generated_at": data.get("generated_at"),
                "ai_model": data.get("ai_model_info", {}).get("model")
            }
            
        except Exception as e:
            logger.error(f"Error getting AI recommendation info for {company}: {e}")
            return None


    def convert_txt_to_json(self, company: str) -> bool:
        """
        Convert existing TXT recommendation file to JSON format
        
        Args:
            company: Company name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            company_dir = self.base_dir / "applied_companies" / company
            
            # Use timestamped files with fallback
            from app.utils.timestamp_utils import TimestampUtils
            txt_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "txt")
            if not txt_file:
                txt_file = company_dir / f"{company}_ai_recommendation.txt"
            
            json_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "json")
            if not json_file:
                json_file = company_dir / f"{company}_ai_recommendation.json"
            
            if not txt_file.exists():
                logger.error(f"TXT file not found: {txt_file}")
                return False
            
            # Read the TXT content
            with open(txt_file, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            
            # Structure the data as JSON
            json_data = {
                "company": company,
                "generated_at": datetime.fromtimestamp(txt_file.stat().st_mtime).isoformat(),
                "recommendation_content": txt_content,
                "ai_model_info": {
                    "provider": "unknown",  # Not available from TXT file
                    "model": "unknown",     # Not available from TXT file
                    "cost": 0.0,           # Not available from TXT file
                    "tokens_used": 0       # Not available from TXT file
                },
                "metadata": {
                    "content_length": len(txt_content),
                    "format_version": "1.0",
                    "converted_from_txt": True
                }
            }
            
            # Save as JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            file_size = json_file.stat().st_size / 1024
            logger.info(f"✅ [AI GENERATOR] Converted TXT to JSON: {json_file} ({file_size:.1f}KB)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error converting TXT to JSON for {company}: {e}")
            return False
    
    def batch_convert_txt_to_json(self) -> Dict[str, bool]:
        """
        Convert all existing TXT recommendation files to JSON format
        
        Returns:
            Dictionary mapping company names to conversion success status
        """
        results = {}
        
        try:
            if not self.base_dir.exists():
                return results
            
            for company_dir in self.base_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    # Use timestamped files with fallback
                    from app.utils.timestamp_utils import TimestampUtils
                    txt_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_ai_recommendation", "txt")
                    if not txt_file:
                        txt_file = company_dir / f"{company_dir.name}_ai_recommendation.txt"
                    
                    json_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_ai_recommendation", "json")
                    if not json_file:
                        json_file = company_dir / f"{company_dir.name}_ai_recommendation.json"
                    
                    # Only convert if TXT exists and JSON doesn't exist (or is older)
                    if txt_file.exists():
                        should_convert = not json_file.exists()
                        if json_file.exists():
                            # Convert if TXT is newer than JSON
                            should_convert = txt_file.stat().st_mtime > json_file.stat().st_mtime
                        
                        if should_convert:
                            success = self.convert_txt_to_json(company_dir.name)
                            results[company_dir.name] = success
                        else:
                            logger.info(f"Skipping {company_dir.name} - JSON file is up to date")
            
            successful_count = sum(1 for success in results.values() if success)
            logger.info(f"✅ [AI GENERATOR] Batch TXT to JSON conversion complete: {successful_count}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch TXT to JSON conversion: {e}")
            return results
    
    async def _trigger_cv_tailoring(self, company: str) -> bool:
        """
        Automatically trigger CV tailoring after AI recommendations are generated
        
        Args:
            company: Company name that just had AI recommendations generated
            
        Returns:
            True if CV tailoring was successful, False otherwise
        """
        if not CV_TAILORING_AVAILABLE:
            logger.warning(f"⚠️ [AI GENERATOR] CV tailoring service not available for {company}")
            return False
        
        try:
            logger.info(f"🚀 [AI GENERATOR] Starting automatic CV tailoring for {company}")
            
            # Load the original CV and the recommendation we just generated
            original_cv, recommendation = cv_tailoring_service.load_real_cv_and_recommendation(company)
            
            # Import the required models here to avoid circular imports
            from app.tailored_cv.models.cv_models import CVTailoringRequest
            
            # Create tailoring request
            request = CVTailoringRequest(
                original_cv=original_cv,
                recommendations=recommendation,
                custom_instructions="Auto-generated after AI recommendations",
                company_folder=None  # We'll save manually
            )
            
            # Process the CV tailoring
            response = await cv_tailoring_service.tailor_cv(request)
            
            if response.success:
                # Save tailored CV to company-specific folder in applied_companies
                file_path = cv_tailoring_service.save_tailored_cv_to_analysis_folder(response.tailored_cv, company)
                logger.info(f"✅ [AI GENERATOR] Tailored CV saved automatically to {file_path}")
                logger.info(f"📊 [AI GENERATOR] Estimated ATS score: {response.tailored_cv.estimated_ats_score}")
                
                return True
            else:
                logger.error(f"❌ [AI GENERATOR] CV tailoring failed for {company}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error during automatic CV tailoring for {company}: {e}")
            return False


# Global instance
ai_recommendation_generator = AIRecommendationGenerator()
