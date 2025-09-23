"""
Job Description Analyzer

This module provides functionality to analyze job descriptions and extract
required and preferred keywords using the centralized AI system.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import hashlib

from app.ai.ai_service import ai_service
from app.ai.base_provider import AIResponse
from app.utils.timestamp_utils import TimestampUtils
from .jd_analysis_prompt import get_jd_analysis_prompts

logger = logging.getLogger(__name__)


class JDAnalysisResult:
    """Container for job description analysis results"""
    
    def __init__(self, data: Dict[str, Any]):
        # Core analysis results (these will be merged from categories in to_dict())
        self.required_keywords: List[str] = data.get('required_keywords', [])
        self.preferred_keywords: List[str] = data.get('preferred_keywords', [])
        self.all_keywords: List[str] = data.get('all_keywords', [])
        self.experience_years: Optional[int] = data.get('experience_years')
        
        # Categorized structure
        self.required_skills: Dict[str, List[str]] = data.get('required_skills', {
            'technical': [],
            'soft_skills': [],
            'experience': [],
            'domain_knowledge': []
        })
        self.preferred_skills: Dict[str, List[str]] = data.get('preferred_skills', {
            'technical': [],
            'soft_skills': [],
            'experience': [],
            'domain_knowledge': []
        })
        
        # Metadata
        self.analysis_timestamp: str = datetime.now().isoformat()
        self.ai_model_used: Optional[str] = None
        self.processing_status: str = "completed"
        self.company_name: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format with merged keywords from categories"""
        # Merge all categories into required_keywords and preferred_keywords
        merged_required = []
        merged_preferred = []
        
        # Merge from required_skills
        for category, skills in self.required_skills.items():
            merged_required.extend(skills)
        
        # Merge from preferred_skills
        for category, skills in self.preferred_skills.items():
            merged_preferred.extend(skills)
        
        return {
            'experience_years': self.experience_years,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'required_keywords': merged_required,
            'preferred_keywords': merged_preferred,
            'analysis_timestamp': self.analysis_timestamp,
            'ai_model_used': self.ai_model_used,
            'processing_status': self.processing_status,
            'company_name': self.company_name,
            'metadata': self.metadata
        }
    
    def get_all_keywords_set(self) -> set:
        """Get all keywords as a set for easy matching operations"""
        return set(keyword.lower() for keyword in self.all_keywords)
    
    def get_required_keywords_set(self) -> set:
        """Get required keywords as a set for easy matching operations"""
        return set(keyword.lower() for keyword in self.required_keywords)
    
    def get_preferred_keywords_set(self) -> set:
        """Get preferred keywords as a set for easy matching operations"""
        return set(keyword.lower() for keyword in self.preferred_keywords)
    
    # Enhanced categorized access methods
    def get_technical_skills(self, required_only: bool = False) -> List[str]:
        """Get technical skills (required, preferred, or both)"""
        skills = []
        if required_only:
            skills.extend(self.required_skills.get('technical', []))
        else:
            skills.extend(self.required_skills.get('technical', []))
            skills.extend(self.preferred_skills.get('technical', []))
        return list(set(skills))  # Remove duplicates
    
    def get_soft_skills(self, required_only: bool = False) -> List[str]:
        """Get soft skills (required, preferred, or both)"""
        skills = []
        if required_only:
            skills.extend(self.required_skills.get('soft_skills', []))
        else:
            skills.extend(self.required_skills.get('soft_skills', []))
            skills.extend(self.preferred_skills.get('soft_skills', []))
        return list(set(skills))  # Remove duplicates
    
    def get_experience_requirements(self, required_only: bool = False) -> List[str]:
        """Get experience requirements (required, preferred, or both)"""
        experience = []
        if required_only:
            experience.extend(self.required_skills.get('experience', []))
        else:
            experience.extend(self.required_skills.get('experience', []))
            experience.extend(self.preferred_skills.get('experience', []))
        return list(set(experience))  # Remove duplicates
    
    def get_domain_knowledge(self, required_only: bool = False) -> List[str]:
        """Get domain knowledge (required, preferred, or both)"""
        knowledge = []
        if required_only:
            knowledge.extend(self.required_skills.get('domain_knowledge', []))
        else:
            knowledge.extend(self.required_skills.get('domain_knowledge', []))
            knowledge.extend(self.preferred_skills.get('domain_knowledge', []))
        return list(set(knowledge))  # Remove duplicates
    
    def get_skills_by_category(self, category: str, required_only: bool = False) -> List[str]:
        """Get skills by specific category (technical, soft_skills, experience, domain_knowledge)"""
        if category not in ['technical', 'soft_skills', 'experience', 'domain_knowledge']:
            raise ValueError(f"Invalid category: {category}. Must be one of: technical, soft_skills, experience, domain_knowledge")
        
        skills = []
        if required_only:
            skills.extend(self.required_skills.get(category, []))
        else:
            skills.extend(self.required_skills.get(category, []))
            skills.extend(self.preferred_skills.get(category, []))
        return list(set(skills))  # Remove duplicates
    
    def get_all_categorized_skills(self) -> Dict[str, Dict[str, List[str]]]:
        """Get all skills organized by category and requirement level"""
        return {
            'required': self.required_skills,
            'preferred': self.preferred_skills
        }
    
    def get_skill_summary(self) -> Dict[str, int]:
        """Get summary count of skills by category"""
        return {
            'total_required': sum(len(skills) for skills in self.required_skills.values()),
            'total_preferred': sum(len(skills) for skills in self.preferred_skills.values()),
            'required_technical': len(self.required_skills.get('technical', [])),
            'required_soft_skills': len(self.required_skills.get('soft_skills', [])),
            'required_experience': len(self.required_skills.get('experience', [])),
            'required_domain_knowledge': len(self.required_skills.get('domain_knowledge', [])),
            'preferred_technical': len(self.preferred_skills.get('technical', [])),
            'preferred_soft_skills': len(self.preferred_skills.get('soft_skills', [])),
            'preferred_experience': len(self.preferred_skills.get('experience', [])),
            'preferred_domain_knowledge': len(self.preferred_skills.get('domain_knowledge', []))
        }


class RequirementsExtractor:
    """Centralized requirements extractor for consistent counting across all analysis components"""
    
    def __init__(self):
        self.REQUIREMENT_INDICATORS = {
            "required": [
                "required", "must have", "essential", "mandatory", 
                "minimum", "necessary", "needed", "expect", "strong",
                "experience in", "experience with", "proficient", "skilled"
            ],
            "preferred": [
                "preferred", "desirable", "nice to have", "bonus",
                "advantage", "plus", "ideal", "would be great",
                "knowledge of", "appreciation of", "understanding of",
                "familiarity with"
            ]
        }
    
    def get_unified_requirement_counts(self, jd_analysis_result: 'JDAnalysisResult') -> Dict[str, int]:
        """Get consistent requirement counts from JD analysis result"""
        if not jd_analysis_result:
            return {"total_required": 0, "total_preferred": 0}
            
        # Count from the merged keyword lists (which come from categories)
        required_count = len(jd_analysis_result.required_keywords)
        preferred_count = len(jd_analysis_result.preferred_keywords)
        
        logger.info(f"[REQUIREMENTS] Unified counts - Required: {required_count}, Preferred: {preferred_count}")
        
        return {
            "total_required": required_count,
            "total_preferred": preferred_count,
            "breakdown": {
                "required_technical": len(jd_analysis_result.required_skills.get('technical', [])),
                "required_soft": len(jd_analysis_result.required_skills.get('soft_skills', [])),
                "required_domain": len(jd_analysis_result.required_skills.get('domain_knowledge', [])),
                "preferred_technical": len(jd_analysis_result.preferred_skills.get('technical', [])),
                "preferred_soft": len(jd_analysis_result.preferred_skills.get('soft_skills', [])),
                "preferred_domain": len(jd_analysis_result.preferred_skills.get('domain_knowledge', []))
            }
        }
    
    def validate_consistency(self, jd_analysis_result: 'JDAnalysisResult', match_counts: Dict[str, int]) -> bool:
        """Validate that match counts are consistent with JD analysis"""
        unified_counts = self.get_unified_requirement_counts(jd_analysis_result)
        
        jd_required = unified_counts["total_required"]
        jd_preferred = unified_counts["total_preferred"]
        
        match_required = match_counts.get("total_required_keywords", 0)
        match_preferred = match_counts.get("total_preferred_keywords", 0)
        
        if jd_required != match_required or jd_preferred != match_preferred:
            logger.warning(
                f"[REQUIREMENTS] Inconsistency detected! "
                f"JD Analysis: {jd_required}R/{jd_preferred}P, "
                f"Match Counts: {match_required}R/{match_preferred}P"
            )
            return False
        
        return True


class JDAnalyzer:
    """Job Description Analyzer using centralized AI system"""
    
    def __init__(self):
        self.ai_service = ai_service
        self.base_analysis_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        self.requirements_extractor = RequirementsExtractor()
    
    def _read_jd_file(self, file_path: Union[str, Path]) -> str:
        """
        Read job description from file
        
        Args:
            file_path: Path to the job description file
            
        Returns:
            Job description text
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Job description file not found: {path}")
        
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
                raise ValueError(f"Job description file is empty: {path}")
            return content
            
        except Exception as e:
            logger.error(f"Error reading JD file {path}: {e}")
            raise IOError(f"Failed to read job description file: {e}")

    def _compute_jd_hash(self, text: str) -> str:
        """Compute a stable hash for JD text to de-duplicate analyses."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _parse_ai_response(self, response: AIResponse) -> JDAnalysisResult:
        """
        Parse AI response into structured result
        
        Args:
            response: AI response containing JSON analysis
            
        Returns:
            JDAnalysisResult object
            
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
            
            # Ensure categorized structure exists with proper defaults
            if 'required_skills' not in data:
                data['required_skills'] = {
                    'technical': [],
                    'soft_skills': [],
                    'experience': [],
                    'domain_knowledge': []
                }
            
            if 'preferred_skills' not in data:
                data['preferred_skills'] = {
                    'technical': [],
                    'soft_skills': [],
                    'experience': [],
                    'domain_knowledge': []
                }
            
            # Ensure all category keys exist
            for category in ['technical', 'soft_skills', 'experience', 'domain_knowledge']:
                if category not in data['required_skills']:
                    data['required_skills'][category] = []
                if category not in data['preferred_skills']:
                    data['preferred_skills'][category] = []
            
            # The flat keyword lists will be generated in to_dict() method from categories
            # So we don't need to set them here
            
            result = JDAnalysisResult(data)
            result.ai_model_used = f"{response.provider}/{response.model}"
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response content: {response.content}")
            raise ValueError(f"AI response is not valid JSON: {e}")
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            raise ValueError(f"Failed to parse analysis result: {e}")
    
    def _save_analysis_result(self, company_name: str, result: JDAnalysisResult) -> str:
        """
        Save analysis result to JSON file
        
        Args:
            company_name: Company name for file organization
            result: Analysis result to save
            
        Returns:
            Path to saved file
            
        Raises:
            IOError: If file can't be saved
        """
        try:
            # Create company directory if it doesn't exist
            company_dir = self.base_analysis_path / company_name
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Reuse existing analysis file if present to avoid duplicates for same JD URL/text
            existing = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_analysis", "json")
            if existing and existing.exists():
                logger.info(f"♻️ JD analysis already exists, reusing: {existing}")
                return str(existing)

            # Otherwise save analysis result with timestamp
            timestamp = TimestampUtils.get_timestamp()
            analysis_file = company_dir / f"jd_analysis_{timestamp}.json"

            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Analysis result saved to: {analysis_file}")
            return str(analysis_file)
            
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            raise IOError(f"Failed to save analysis result: {e}")
    
    def _load_analysis_result(self, company_name: str) -> Optional[JDAnalysisResult]:
        """
        Load existing analysis result from JSON file
        
        Args:
            company_name: Company name to load analysis for
            
        Returns:
            JDAnalysisResult if found, None otherwise
        """
        try:
            company_dir = self.base_analysis_path / company_name
            analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_analysis", "json")
            
            if not analysis_file or not analysis_file.exists():
                return None
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"📂 Loaded existing JD analysis from: {analysis_file}")
            return JDAnalysisResult(data)
            
        except Exception as e:
            logger.warning(f"Failed to load existing analysis for {company_name}: {e}")
            return None
    
    async def analyze_jd_text(self, jd_text: str, temperature: float = 0.3) -> JDAnalysisResult:
        """
        Analyze job description text and extract keywords
        
        Args:
            jd_text: Job description text to analyze
            temperature: AI temperature for consistency (default: 0.3)
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            Exception: If analysis fails
        """
        try:
            system_prompt, user_prompt = get_jd_analysis_prompts(jd_text)
            
            response = await self.ai_service.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=2000
            )
            
            result = self._parse_ai_response(response)
            
            logger.info(f"✅ JD analysis completed. Found {len(result.required_keywords)} required "
                       f"and {len(result.preferred_keywords)} preferred keywords")
            
            return result
            
        except Exception as e:
            logger.error(f"JD analysis failed: {e}")
            raise Exception(f"Failed to analyze job description: {e}")
    
    async def analyze_jd_file(self, file_path: Union[str, Path], temperature: float = 0.3) -> JDAnalysisResult:
        """
        Analyze job description from file
        
        Args:
            file_path: Path to job description file
            temperature: AI temperature for consistency (default: 0.3)
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If analysis fails
        """
        try:
            jd_text = self._read_jd_file(file_path)
            logger.info(f"📄 Analyzing JD file: {file_path}")
            
            result = await self.analyze_jd_text(jd_text, temperature)
            # Attach JD hash to metadata for de-duplication
            try:
                result.metadata = result.metadata or {}
                result.metadata['jd_hash'] = self._compute_jd_hash(jd_text)
            except Exception:
                pass
            
            return result
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to analyze JD file {file_path}: {e}")
            raise Exception(f"Failed to analyze job description file: {e}")
    
    async def analyze_company_jd(self, company_name: str, base_path: Optional[str] = None, 
                                temperature: float = 0.3) -> JDAnalysisResult:
        """
        Analyze job description using company name pattern
        
        Args:
            company_name: Company name (e.g., "Australia_for_UNHCR")
            base_path: Base path for JD files (optional, uses default if not provided)
            temperature: AI temperature for consistency (default: 0.3)
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            FileNotFoundError: If JD file doesn't exist
            Exception: If analysis fails
        """
        if not base_path:
            base_path = str(self.base_analysis_path)
        
        company_dir = Path(base_path) / company_name
        jd_file_path = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
        
        # Fallback to non-timestamped file if no timestamped file exists
        if not jd_file_path:
            jd_file_path = company_dir / "jd_original.json"
        
        return await self.analyze_jd_file(jd_file_path, temperature)
    
    async def analyze_and_save_company_jd(self, company_name: str, force_refresh: bool = False,
                                        temperature: float = 0.3) -> JDAnalysisResult:
        """
        Analyze company JD and save result with caching logic
        
        Args:
            company_name: Company name (e.g., "Australia_for_UNHCR")
            force_refresh: Force re-analysis even if cached result exists
            temperature: AI temperature for consistency (default: 0.3)
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            FileNotFoundError: If JD file doesn't exist
            Exception: If analysis fails
        """
        try:
            # Check for existing analysis unless force refresh
            if not force_refresh:
                cached_result = self._load_analysis_result(company_name)
                if cached_result:
                    # If we can compute the current JD hash, only reuse cache if hashes match
                    try:
                        company_dir = self.base_analysis_path / company_name
                        jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json") or (company_dir / "jd_original.json")
                        current_text = self._read_jd_file(jd_file) if jd_file and jd_file.exists() else None
                        current_hash = self._compute_jd_hash(current_text) if current_text else None
                        cached_hash = (cached_result.metadata or {}).get('jd_hash') if hasattr(cached_result, 'metadata') else None
                        if current_hash and cached_hash and current_hash == cached_hash:
                            logger.info(f"📂 Using cached analysis for {company_name} (JD hash matched)")
                            return cached_result
                        else:
                            logger.info(f"🔁 Cached JD analysis exists but hash changed or missing; re-analyzing")
                    except Exception:
                        # If any issue computing hash, fall back to previous guard below
                        pass
                # If a JD original already exists in the company folder and an analysis file also exists,
                # avoid re-running analysis again. This is a defensive guard against duplicate runs.
                company_dir = self.base_analysis_path / company_name
                try:
                    jd_original = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json") or (company_dir / "jd_original.json" if (company_dir / "jd_original.json").exists() else None)
                    jd_analysis = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_analysis", "json") or (company_dir / "jd_analysis.json" if (company_dir / "jd_analysis.json").exists() else None)
                    if jd_original and jd_analysis and jd_analysis.exists():
                        # If hash matches, reuse; else proceed to fresh analysis
                        try:
                            current_text = self._read_jd_file(jd_original)
                            current_hash = self._compute_jd_hash(current_text)
                            with open(jd_analysis, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if isinstance(data, dict) and data.get('metadata', {}).get('jd_hash') == current_hash:
                                logger.info(f"♻️ JD original and matching analysis already present for {company_name}; skipping re-analysis")
                                return JDAnalysisResult(data)
                        except Exception:
                            logger.debug("Hash comparison failed; continuing with fresh analysis")
                except Exception as guard_err:
                    logger.debug(f"Guard check for existing JD files failed (continuing with analysis): {guard_err}")
            
            # Perform fresh analysis
            logger.info(f"🔄 Analyzing JD for {company_name} (force_refresh={force_refresh})")
            result = await self.analyze_company_jd(company_name, temperature=temperature)
            
            # Set company name and metadata
            result.company_name = company_name
            
            # Save result
            saved_path = self._save_analysis_result(company_name, result)
            result.metadata = {"saved_path": saved_path}
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze and save company JD {company_name}: {e}")
            raise
    
    def load_jd_analysis(self, company_name: str) -> Optional[JDAnalysisResult]:
        """
        Load saved JD analysis result
        
        Args:
            company_name: Company name to load analysis for
            
        Returns:
            JDAnalysisResult if found, None otherwise
        """
        return self._load_analysis_result(company_name)
    
    def get_ai_service_status(self) -> Dict[str, Any]:
        """Get current AI service status"""
        return self.ai_service.get_current_status()


# Convenience functions for easy usage
async def analyze_jd_text(jd_text: str, temperature: float = 0.3) -> JDAnalysisResult:
    """Convenience function to analyze JD text"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_jd_text(jd_text, temperature)


async def analyze_jd_file(file_path: Union[str, Path], temperature: float = 0.3) -> JDAnalysisResult:
    """Convenience function to analyze JD file"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_jd_file(file_path, temperature)


async def analyze_company_jd(company_name: str, base_path: Optional[str] = None, 
                           temperature: float = 0.3) -> JDAnalysisResult:
    """Convenience function to analyze company JD using naming pattern"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_company_jd(company_name, base_path, temperature)


async def analyze_and_save_company_jd(company_name: str, force_refresh: bool = False,
                                    temperature: float = 0.3) -> JDAnalysisResult:
    """Convenience function to analyze and save company JD"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_and_save_company_jd(company_name, force_refresh, temperature)


def load_jd_analysis(company_name: str) -> Optional[JDAnalysisResult]:
    """Convenience function to load saved JD analysis"""
    analyzer = JDAnalyzer()
    return analyzer.load_jd_analysis(company_name)
