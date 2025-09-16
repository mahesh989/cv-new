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

logger = logging.getLogger(__name__)


class AIRecommendationGenerator:
    """Service for generating AI-based CV optimization recommendations"""
    
    def __init__(self):
        self.base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
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
            
            # Check if output file already exists
            output_file = self._get_output_file_path(company)
            if output_file.exists() and not force_regenerate:
                logger.info(f"AI recommendation file already exists for {company}, skipping")
                return True
            
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
            
            return success
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error generating AI recommendation for {company}: {e}")
            return False
    
    def _get_output_file_path(self, company: str) -> Path:
        """Get the output file path for AI recommendation"""
        company_dir = self.base_dir / company
        return company_dir / f"{company}_ai_recommendation.json"
    
    def _load_ai_prompt(self, company: str) -> Optional[str]:
        """
        Load the AI prompt for a company
        
        Args:
            company: Company name
            
        Returns:
            Prompt content or None if not found
        """
        try:
            prompt_file = self.prompt_dir / f"{company}_prompt_recommendation.py"
            
            if not prompt_file.exists():
                logger.error(f"Prompt file not found: {prompt_file}")
                return None
            
            # Import the prompt module dynamically
            import sys
            import importlib.util
            
            # Add the prompt directory to Python path
            if str(self.prompt_dir) not in sys.path:
                sys.path.append(str(self.prompt_dir))
            
            # Load the module
            spec = importlib.util.spec_from_file_location(f"{company}_prompt_recommendation", prompt_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the prompt content
            if hasattr(module, 'get_prompt'):
                prompt_content = module.get_prompt()
                logger.info(f"📋 [AI GENERATOR] Loaded AI prompt for {company} ({len(prompt_content)} characters)")
                return prompt_content
            else:
                logger.error(f"Prompt module for {company} does not have get_prompt() function")
                return None
                
        except Exception as e:
            logger.error(f"Error loading AI prompt for {company}: {e}")
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
            # Use the centralized AI service to generate response
            response = await ai_service.generate_response(
                prompt=prompt_content,
                system_prompt="You are an expert CV strategist and career consultant. Provide detailed, actionable recommendations in the exact format requested.",
                temperature=0.7,  # Balanced creativity and consistency
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
            company_dir = self.base_dir / company
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON file
            output_file = company_dir / f"{company}_ai_recommendation.json"
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
        return self._get_output_file_path(company).exists()
    
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
                    ai_file = company_dir / f"{company_dir.name}_ai_recommendation.json"
                    if ai_file.exists():
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
            company_dir = self.base_dir / company
            txt_file = company_dir / f"{company}_ai_recommendation.txt"
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
                    txt_file = company_dir / f"{company_dir.name}_ai_recommendation.txt"
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


# Global instance
ai_recommendation_generator = AIRecommendationGenerator()
