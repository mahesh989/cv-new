"""
CV-JD Matcher

This module provides functionality to match CV content against job description keywords
using AI-powered smart matching logic.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
from app.ai.ai_service import ai_service
from app.ai.base_provider import AIResponse
from .cv_jd_matching_prompt import get_cv_jd_matching_prompts

logger = logging.getLogger(__name__)

class CVJDMatchResult:
    """Container for CV-JD matching results"""
    
    def __init__(self, data: Dict[str, Any]):
        # Core matching results
        self.matched_required_keywords: List[str] = data.get('matched_required_keywords', [])
        self.matched_preferred_keywords: List[str] = data.get('matched_preferred_keywords', [])
        self.missed_required_keywords: List[str] = data.get('missed_required_keywords', [])
        self.missed_preferred_keywords: List[str] = data.get('missed_preferred_keywords', [])
        
        # Match counts
        self.match_counts: Dict[str, int] = data.get('match_counts', {})
        
        # Additional analysis
        self.matching_notes: Dict[str, Any] = data.get('matching_notes', {})
        
        # Metadata
        self.analysis_timestamp: str = datetime.now().isoformat()
        self.ai_model_used: Optional[str] = None
        self.processing_status: str = "completed"
        self.company_name: Optional[str] = None
        self.cv_file_path: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format"""
        return {
            'company_name': self.company_name,
            'cv_analysis_timestamp': self.analysis_timestamp,
            'matched_required_keywords': self.matched_required_keywords,
            'matched_preferred_keywords': self.matched_preferred_keywords,
            'missed_required_keywords': self.missed_required_keywords,
            'missed_preferred_keywords': self.missed_preferred_keywords,
            'match_counts': self.match_counts,
            'matching_notes': self.matching_notes,
            'ai_model_used': self.ai_model_used,
            'processing_status': self.processing_status,
            'cv_file_path': self.cv_file_path,
            'metadata': self.metadata
        }
    
    def get_match_percentage(self) -> Dict[str, float]:
        """Calculate match percentages"""
        total_required = self.match_counts.get('total_required_keywords', 0)
        total_preferred = self.match_counts.get('total_preferred_keywords', 0)
        
        matched_required = self.match_counts.get('matched_required_count', 0)
        matched_preferred = self.match_counts.get('matched_preferred_count', 0)
        
        return {
            'required_match_percentage': (matched_required / total_required * 100) if total_required > 0 else 0.0,
            'preferred_match_percentage': (matched_preferred / total_preferred * 100) if total_preferred > 0 else 0.0,
            'overall_match_percentage': ((matched_required + matched_preferred) / (total_required + total_preferred) * 100) if (total_required + total_preferred) > 0 else 0.0
        }
    
    def get_all_matched_keywords(self) -> List[str]:
        """Get all matched keywords (required + preferred)"""
        return self.matched_required_keywords + self.matched_preferred_keywords
    
    def get_all_missed_keywords(self) -> List[str]:
        """Get all missed keywords (required + preferred)"""
        return self.missed_required_keywords + self.missed_preferred_keywords

class CVJDMatcher:
    """CV-JD Matcher using centralized AI system"""
    
    def __init__(self):
        self.ai_service = ai_service
    
    def _read_cv_file(self, file_path: Union[str, Path]) -> str:
        """
        Read CV content from file
        
        Args:
            file_path: Path to the CV file
            
        Returns:
            CV content text
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CV file not found: {path}")
        
        try:
            # Support JSON format with {"text": "..."}
            if str(path).endswith('.json'):
                import json
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                content = (data.get('text') or '').strip()
            else:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
            if not content:
                raise ValueError(f"CV file is empty: {path}")
            return content
        except Exception as e:
            logger.error(f"Error reading CV file {path}: {e}")
            raise IOError(f"Failed to read CV file: {e}")
    
    def _read_jd_analysis(self, company_name: str, base_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Read JD analysis results from file
        
        Args:
            company_name: Company name for the analysis
            base_path: Base path for analysis files
            
        Returns:
            JD analysis data
            
        Raises:
            FileNotFoundError: If analysis file doesn't exist
        """
        if not base_path:
            base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
        
        analysis_file = Path(base_path) / company_name / "jd_analysis.json"
        if not analysis_file.exists():
            raise FileNotFoundError(f"JD analysis file not found: {analysis_file}")
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Error reading JD analysis file {analysis_file}: {e}")
            raise IOError(f"Failed to read JD analysis file: {e}")
    
    
    def _parse_ai_response(self, response: AIResponse) -> CVJDMatchResult:
        """
        Parse AI response into structured result
        
        Args:
            response: AI response containing JSON analysis
            
        Returns:
            CVJDMatchResult object
            
        Raises:
            ValueError: If response can't be parsed
        """
        try:
            # Try to parse JSON from response content
            content = response.content.strip()
            
            # Handle cases where AI might wrap JSON in markdown code blocks
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
            
            data = json.loads(content)
            
            # Validate required fields
            if not isinstance(data, dict):
                raise ValueError("Response is not a valid JSON object")
            
            # Ensure all required fields exist
            required_fields = [
                'matched_required_keywords', 'matched_preferred_keywords',
                'missed_required_keywords', 'missed_preferred_keywords',
                'match_counts'
            ]
            
            for field in required_fields:
                if field not in data:
                    data[field] = [] if 'keywords' in field else {}
            
            result = CVJDMatchResult(data)
            result.ai_model_used = f"{response.provider}/{response.model}"
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ CRITICAL: AI returned invalid JSON that cannot be parsed")
            logger.error(f"❌ JSON Parse Error: {e}")
            logger.error(f"❌ Error Location: Line {getattr(e, 'lineno', '?')}, Column {getattr(e, 'colno', '?')}")
            logger.error(f"❌ AI Response Content:")
            logger.error(f"{response.content}")
            logger.error(f"❌ STOPPING PROCESS: No fallbacks - AI must return valid JSON")
            
            raise ValueError(
                f"CRITICAL FAILURE: AI returned malformed JSON. "
                f"Error: {e} at line {getattr(e, 'lineno', '?')}, column {getattr(e, 'colno', '?')}. "
                f"AI must be fixed to return proper JSON format. "
                f"Process terminated - no fallbacks allowed."
            )
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            raise ValueError(f"Failed to parse matching result: {e}")
    
    async def match_cv_against_jd(
        self, 
        company_name: str,
        cv_file_path: Optional[str] = None,
        jd_analysis_data: Optional[Dict[str, Any]] = None,
        temperature: float = 0.3,
        max_retries: int = 3
    ) -> CVJDMatchResult:
        """
        Match CV content against job description keywords
        
        Args:
            company_name: Company name for the analysis
            cv_file_path: Path to CV file (optional, uses default if not provided)
            jd_analysis_data: JD analysis data (optional, loads from file if not provided)
            temperature: AI temperature for consistency (default: 0.3)
            
        Returns:
            CVJDMatchResult with matching results
            
        Raises:
            FileNotFoundError: If required files don't exist
            Exception: If matching fails
        """
        try:
            # Read CV content
            if not cv_file_path:
                cv_file_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/original_cv.json"
            
            cv_content = self._read_cv_file(cv_file_path)
            logger.info(f"📄 Read CV content from: {cv_file_path}")
            
            # Get JD analysis data
            if not jd_analysis_data:
                jd_analysis_data = self._read_jd_analysis(company_name)
                logger.info(f"📊 Loaded JD analysis for: {company_name}")
            
            # Extract keywords from JD analysis
            required_keywords = jd_analysis_data.get('required_keywords', [])
            preferred_keywords = jd_analysis_data.get('preferred_keywords', [])
            
            if not required_keywords and not preferred_keywords:
                raise ValueError("No keywords found in JD analysis data")
            
            logger.info(f"🔍 Found {len(required_keywords)} required and {len(preferred_keywords)} preferred keywords")
            
            # Get prompts
            system_prompt, user_prompt = get_cv_jd_matching_prompts(
                cv_content=cv_content,
                required_keywords=required_keywords,
                preferred_keywords=preferred_keywords
            )
            
            # Retry logic for AI service calls
            last_error = None
            for attempt in range(max_retries):
                try:
                    # Call AI service
                    response = await self.ai_service.generate_response(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=3000
                    )
                    
                    # Parse response
                    result = self._parse_ai_response(response)
                    result.company_name = company_name
                    result.cv_file_path = cv_file_path
                    
                    logger.info(f"✅ CV-JD matching completed. Found {len(result.matched_required_keywords)} matched required keywords")
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ CRITICAL: JSON parsing failed immediately: {e}")
                    logger.error(f"❌ STOPPING PROCESS: No retries for JSON parsing errors")
                    # Re-raise the exception to trigger the main error handling
                    raise
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"⚠️ Attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        logger.info(f"🔄 Retrying CV-JD matching...")
                        await asyncio.sleep(1)  # Brief delay before retry
                    continue
            
            # If all retries failed, raise the last error
            raise Exception(f"Failed after {max_retries} attempts: {last_error}")
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"CV-JD matching failed: {e}")
            raise Exception(f"Failed to match CV against JD: {e}")
    
    def _save_match_result(self, result: CVJDMatchResult, company_name: str, base_path: Optional[str] = None) -> str:
        """
        Save matching result to file
        
        Args:
            result: CVJDMatchResult to save
            company_name: Company name for file naming
            base_path: Base path for saving files
            
        Returns:
            Path to saved file
        """
        if not base_path:
            base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
        
        # Create company directory if it doesn't exist
        company_dir = Path(base_path) / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Save result
        result_file = company_dir / "cv_jd_match_results.json"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as file:
                json.dump(result.to_dict(), file, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved CV-JD match results to: {result_file}")
            return str(result_file)
            
        except Exception as e:
            logger.error(f"Failed to save match results to {result_file}: {e}")
            raise IOError(f"Failed to save match results: {e}")
    
    def _load_match_result(self, company_name: str, base_path: Optional[str] = None) -> Optional[CVJDMatchResult]:
        """
        Load existing matching result from file
        
        Args:
            company_name: Company name for file naming
            base_path: Base path for loading files
            
        Returns:
            CVJDMatchResult if found, None otherwise
        """
        if not base_path:
            base_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
        
        result_file = Path(base_path) / company_name / "cv_jd_match_results.json"
        
        if not result_file.exists():
            return None
        
        try:
            with open(result_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            result = CVJDMatchResult(data)
            logger.info(f"📂 Loaded existing CV-JD match results from: {result_file}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load match results from {result_file}: {e}")
            return None

# Convenience functions for easy usage
async def match_cv_against_company_jd(
    company_name: str,
    cv_file_path: Optional[str] = None,
    force_refresh: bool = False,
    temperature: float = 0.3
) -> CVJDMatchResult:
    """Convenience function to match CV against company JD"""
    matcher = CVJDMatcher()
    return await matcher.match_cv_against_jd(company_name, cv_file_path, None, temperature)

async def match_and_save_cv_jd(
    company_name: str,
    cv_file_path: Optional[str] = None,
    force_refresh: bool = False,
    temperature: float = 0.3
) -> CVJDMatchResult:
    """Convenience function to match CV against JD and save results"""
    matcher = CVJDMatcher()
    
    # Check for existing results
    if not force_refresh:
        existing_result = matcher._load_match_result(company_name)
        if existing_result:
            logger.info(f"📦 Using cached CV-JD match results for {company_name}")
            return existing_result
    
    # Perform matching
    result = await matcher.match_cv_against_jd(company_name, cv_file_path, None, temperature)
    
    # Save results
    matcher._save_match_result(result, company_name)
    
    return result

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Example: Match CV against Australia for UNHCR JD
        try:
            result = await match_and_save_cv_jd("Australia_for_UNHCR")
            print("✅ CV-JD matching completed!")
            print(f"Company: {result.company_name}")
            print(f"Matched Required: {len(result.matched_required_keywords)}")
            print(f"Matched Preferred: {len(result.matched_preferred_keywords)}")
            print(f"Missed Required: {len(result.missed_required_keywords)}")
            print(f"Missed Preferred: {len(result.missed_preferred_keywords)}")
            
            # Show match percentages
            percentages = result.get_match_percentage()
            print(f"\n📊 Match Percentages:")
            print(f"Required: {percentages['required_match_percentage']:.1f}%")
            print(f"Preferred: {percentages['preferred_match_percentage']:.1f}%")
            print(f"Overall: {percentages['overall_match_percentage']:.1f}%")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    asyncio.run(main())
