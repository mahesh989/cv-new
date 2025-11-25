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
        # Categorized structure (from AI response)
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
        
        # Merge categories into flat keyword lists for backward compatibility
        # This ensures required_keywords and preferred_keywords are populated immediately
        merged_required = []
        for category, skills in self.required_skills.items():
            if isinstance(skills, list):
                merged_required.extend(skills)
        
        merged_preferred = []
        for category, skills in self.preferred_skills.items():
            if isinstance(skills, list):
                merged_preferred.extend(skills)
        
        # Core analysis results (merged from categories)
        # Use merged lists if top-level keys don't exist (for backward compatibility)
        self.required_keywords: List[str] = data.get('required_keywords') if 'required_keywords' in data else merged_required
        self.preferred_keywords: List[str] = data.get('preferred_keywords') if 'preferred_keywords' in data else merged_preferred
        self.all_keywords: List[str] = data.get('all_keywords') if 'all_keywords' in data else (merged_required + merged_preferred)
        self.experience_years: Optional[int] = data.get('experience_years')
        
        # Metadata
        self.analysis_timestamp: str = data.get('analysis_timestamp', datetime.now().isoformat())
        self.ai_model_used: Optional[str] = data.get('ai_model_used')
        self.processing_status: str = data.get('processing_status', "completed")
        self.company_name: Optional[str] = data.get('company_name')
        self.metadata: Dict[str, Any] = data.get('metadata', {})
        
        # ⭐ DEBUG: Log keyword counts for troubleshooting
        logger.debug(f"🔍 [JDAnalysisResult] Initialized with {len(self.required_keywords)} required and {len(self.preferred_keywords)} preferred keywords")
        logger.debug(f"🔍 [JDAnalysisResult] Required categories: {list(self.required_skills.keys())}")
        logger.debug(f"🔍 [JDAnalysisResult] Preferred categories: {list(self.preferred_skills.keys())}")
        if len(self.required_keywords) == 0 and len(merged_required) > 0:
            logger.warning(f"⚠️ [JDAnalysisResult] WARNING: Merged {len(merged_required)} required keywords but required_keywords is empty!")
            print(f"⚠️ [JDAnalysisResult] WARNING: Merged {len(merged_required)} required keywords but required_keywords is empty!")
        if len(self.required_keywords) > 0 or len(self.preferred_keywords) > 0:
            logger.info(f"✅ [JDAnalysisResult] Successfully extracted {len(self.required_keywords)} required and {len(self.preferred_keywords)} preferred keywords")
            print(f"✅ [JDAnalysisResult] Successfully extracted {len(self.required_keywords)} required and {len(self.preferred_keywords)} preferred keywords")
    
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
            'metadata': self.metadata or {}  # ⭐ Ensure metadata is always a dict, never None
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
    
    def __init__(self, user_email: str):
        self.ai_service = ai_service
        self.user_email = user_email
        from app.utils.user_path_utils import get_user_base_path
        self.base_analysis_path = get_user_base_path(user_email)
        self.requirements_extractor = RequirementsExtractor()
    
    def _read_jd_file(self, file_path: Union[str, Path]) -> str:
        """
        Read job description from file - NOW WITH PROCESSED JD SUPPORT
        
        Tries processed JD first (if available), falls back to original JD file.
        This ensures better AI analysis results while maintaining backward compatibility.
        
        Args:
            file_path: Path to the job description file
            
        Returns:
            Job description text (processed if available, otherwise original)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        path = Path(file_path)
        
        # ⭐ NEW: Try processed JD first (with fallback)
        try:
            # Extract company name from file path
            # Path format: .../applied_companies/{company_name}/jd_original_{timestamp}.json
            company_name = None
            path_parts = path.parts
            if 'applied_companies' in path_parts:
                idx = path_parts.index('applied_companies')
                if idx + 1 < len(path_parts):
                    company_name = path_parts[idx + 1]
            
            if company_name and self.user_email:
                logger.info(f"🔍 [JD_ANALYZER] Attempting to use processed JD for {company_name}")
                print(f"🔍 [JD_ANALYZER] Attempting to use processed JD for {company_name}")
                from app.services.jd_processing_service import get_jd_processing_service
                jd_service = get_jd_processing_service(self.user_email)
                processed_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
                if processed_text:
                    logger.info(f"✅ [JD_ANALYZER] ✅ Using PROCESSED JD for {company_name} | "
                               f"Source: jd_processing_service | Length: {len(processed_text)} chars")
                    
                    # ⭐ PRINT FULL PROCESSED JD TEXT BEING SENT TO AI FOR JD ANALYSIS
                    logger.info(f"📋 [JD_ANALYZER] ========== FULL PROCESSED JD TEXT FOR JD ANALYSIS ==========")
                    logger.info(f"📋 [JD_ANALYZER] Company: {company_name}")
                    logger.info(f"📋 [JD_ANALYZER] Total length: {len(processed_text)} characters")
                    logger.info(f"📋 [JD_ANALYZER] This processed JD text will be sent to AI for keyword extraction:")
                    logger.info(f"📋 [JD_ANALYZER] Full processed JD text:\n{processed_text}")
                    logger.info(f"📋 [JD_ANALYZER] ========== END OF PROCESSED JD TEXT FOR JD ANALYSIS ==========")
                    print(f"✅ [JD_ANALYZER] ✅ Using PROCESSED JD for {company_name} | "
                          f"Length: {len(processed_text)} chars")
                    print(f"📋 [JD_ANALYZER] FULL PROCESSED JD TEXT FOR JD ANALYSIS ({len(processed_text)} chars):\n{processed_text}")
                    return processed_text
                else:
                    logger.info(f"📄 [JD_ANALYZER] Processed JD not available for {company_name}, "
                               f"falling back to LEGACY file: {path.name}")
                    print(f"📄 [JD_ANALYZER] Processed JD not available for {company_name}, "
                          f"falling back to LEGACY file: {path.name}")
            else:
                if not company_name:
                    logger.warning(f"⚠️ [JD_ANALYZER] Cannot use processed JD: company_name not extracted from path {path}")
                    print(f"⚠️ [JD_ANALYZER] Cannot use processed JD: company_name not extracted from path {path}")
                if not self.user_email:
                    logger.warning(f"⚠️ [JD_ANALYZER] Cannot use processed JD: user_email not available")
                    print(f"⚠️ [JD_ANALYZER] Cannot use processed JD: user_email not available")
                logger.debug(f"📄 [JD_ANALYZER] Falling back to LEGACY file")
        except Exception as e:
            logger.warning(f"⚠️ [JD_ANALYZER] Error attempting processed JD, falling back to LEGACY file: {e}")
            # Continue with original file reading
        
        # ✅ FALLBACK: Original legacy behavior (unchanged)
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
            logger.info(f"📄 [JD_ANALYZER] Using LEGACY (original) JD file | "
                       f"Path: {path.name} | Length: {len(content)} chars | "
                       f"Reason: Processed JD not available or error occurred")
            print(f"📄 [JD_ANALYZER] Using LEGACY (original) JD file | "
                  f"Path: {path.name} | Length: {len(content)} chars")
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
            
            # ⭐ DEBUG: Log raw response for troubleshooting
            logger.debug(f"🔍 [JD_ANALYZER] Raw AI response (first 500 chars): {content[:500]}")
            logger.debug(f"🔍 [JD_ANALYZER] Raw AI response length: {len(content)} chars")
            print(f"🔍 [JD_ANALYZER] Raw AI response (first 500 chars): {content[:500]}")
            print(f"🔍 [JD_ANALYZER] Raw AI response length: {len(content)} chars")
            
            # Handle cases where AI might wrap JSON in markdown code blocks
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
                logger.debug(f"🔍 [JD_ANALYZER] Removed ```json markdown fences")
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
                logger.debug(f"🔍 [JD_ANALYZER] Removed ``` markdown fences")
            
            data = json.loads(content)
            
            # ⭐ DEBUG: Log parsed data structure
            logger.debug(f"🔍 [JD_ANALYZER] Parsed JSON keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            if isinstance(data, dict):
                required_skills = data.get('required_skills', {})
                preferred_skills = data.get('preferred_skills', {})
                logger.debug(f"🔍 [JD_ANALYZER] Required skills structure: {list(required_skills.keys()) if isinstance(required_skills, dict) else type(required_skills)}")
                logger.debug(f"🔍 [JD_ANALYZER] Preferred skills structure: {list(preferred_skills.keys()) if isinstance(preferred_skills, dict) else type(preferred_skills)}")
                if isinstance(required_skills, dict):
                    for category, skills in required_skills.items():
                        logger.debug(f"🔍 [JD_ANALYZER] Required {category}: {len(skills) if isinstance(skills, list) else 'N/A'} items")
                if isinstance(preferred_skills, dict):
                    for category, skills in preferred_skills.items():
                        logger.debug(f"🔍 [JD_ANALYZER] Preferred {category}: {len(skills) if isinstance(skills, list) else 'N/A'} items")
            print(f"🔍 [JD_ANALYZER] Parsed JSON keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
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
            company_dir = self.base_analysis_path / "applied_companies" / company_name
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # ⭐ CACHE INVALIDATION: Check if we should update existing file or create new one
            # If re-analyzing with processed JD, update existing file to mark it as using processed JD
            existing = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_name}_jd_analysis", "json")
            if existing and existing.exists():
                # Check if this result has processed JD metadata
                result_dict = result.to_dict()
                used_processed_jd = (result_dict.get('metadata', {}) or {}).get('used_processed_jd', False)
                
                if used_processed_jd:
                    # Update existing file with processed JD metadata
                    logger.info(f"🔄 [JD_ANALYZER] Updating existing analysis file with processed JD metadata: {existing}")
                    with open(existing, 'w', encoding='utf-8') as f:
                        json.dump(result_dict, f, indent=2, ensure_ascii=False)
                    logger.info(f"✅ [JD_ANALYZER] Updated analysis file with processed JD flag")
                    return str(existing)
                else:
                    # Reuse existing file if not using processed JD
                    logger.info(f"♻️ JD analysis already exists, reusing: {existing}")
                    return str(existing)

            # Otherwise save analysis result with timestamp
            timestamp = TimestampUtils.get_timestamp()
            analysis_file = company_dir / f"{company_name}_jd_analysis_{timestamp}.json"

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
        
        ⚠️ IMPORTANT: This method checks if processed JD exists and is newer than the analysis.
        If processed JD is newer, returns None to force re-analysis with processed JD.
        
        Args:
            company_name: Company name to load analysis for
            
        Returns:
            JDAnalysisResult if found and still valid, None otherwise (to force re-analysis)
        """
        try:
            company_dir = self.base_analysis_path / "applied_companies" / company_name
            analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_name}_jd_analysis", "json")
            
            if not analysis_file or not analysis_file.exists():
                logger.debug(f"📂 [JD_ANALYZER] No existing JD analysis found for {company_name}")
                return None
            
            # ⭐ CACHE INVALIDATION: Check if processed JD exists
            # If processed JD exists, invalidate cache to force re-analysis with processed JD
            if self.user_email:
                try:
                    from app.services.jd_processing_service import get_jd_processing_service
                    jd_service = get_jd_processing_service(self.user_email)
                    processed_jd_path = jd_service._get_processed_jd_path(company_name)
                    
                    if processed_jd_path and processed_jd_path.exists():
                        # ⭐ AGGRESSIVE CACHE INVALIDATION: Always invalidate if processed JD exists
                        # This ensures we always use processed JD when available, even if cached analysis exists
                        analysis_mtime = analysis_file.stat().st_mtime
                        processed_mtime = processed_jd_path.stat().st_mtime
                        
                        # Check if processed JD is newer OR if analysis doesn't have processed JD metadata
                        should_invalidate = False
                        reason = ""
                        
                        if processed_mtime > analysis_mtime:
                            should_invalidate = True
                            reason = f"Processed JD is newer (processed: {processed_mtime}, analysis: {analysis_mtime})"
                        else:
                            # Even if processed JD is older, check if analysis was based on processed JD
                            # If analysis metadata doesn't indicate processed JD was used, invalidate
                            try:
                                with open(analysis_file, 'r', encoding='utf-8') as f:
                                    analysis_data = json.load(f)
                                analysis_metadata = analysis_data.get('metadata', {})
                                used_processed_jd = analysis_metadata.get('used_processed_jd', False)
                                
                                if not used_processed_jd:
                                    should_invalidate = True
                                    reason = "Cached analysis was not based on processed JD (metadata missing 'used_processed_jd' flag)"
                            except Exception:
                                # If we can't read metadata, assume it's not based on processed JD
                                should_invalidate = True
                                reason = "Cannot verify if cached analysis used processed JD (metadata read failed)"
                        
                        if should_invalidate:
                            logger.info(f"🔄 [JD_ANALYZER] 🔄 CACHE INVALIDATED: {reason}")
                            logger.info(f"🔄 [JD_ANALYZER] Forcing re-analysis with processed JD for {company_name}")
                            logger.info(f"🔄 [JD_ANALYZER] Cached analysis file: {analysis_file}")
                            logger.info(f"🔄 [JD_ANALYZER] Processed JD file: {processed_jd_path}")
                            print(f"🔄 [JD_ANALYZER] 🔄 CACHE INVALIDATED: {reason}")
                            print(f"🔄 [JD_ANALYZER] Forcing re-analysis with processed JD for {company_name}")
                            return None  # Force re-analysis
                        else:
                            logger.debug(f"📂 [JD_ANALYZER] Analysis is up-to-date and based on processed JD "
                                        f"(analysis: {analysis_mtime}, processed: {processed_mtime})")
                except Exception as e:
                    logger.warning(f"⚠️ [JD_ANALYZER] Could not check processed JD for cache invalidation: {e}")
                    # Continue with loading existing analysis if check fails
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ⭐ CACHE-HIT LOGGING: Check if cached analysis was based on processed JD
            analysis_metadata = data.get('metadata', {}) or {}
            used_processed_jd = analysis_metadata.get('used_processed_jd', False)
            cached_keywords = data.get('required_keywords', []) + data.get('preferred_keywords', [])
            
            logger.info(f"📂 [JD_ANALYZER] Loaded existing JD analysis from: {analysis_file}")
            logger.info(f"📂 [JD_ANALYZER] Cached analysis contains {len(cached_keywords)} keywords")
            logger.info(f"📋 [JD_ANALYZER] ⚡ USING CACHED ANALYSIS (based on processed JD: {used_processed_jd})")
            logger.info(f"📋 [JD_ANALYZER] Cached JD source: {'PROCESSED' if used_processed_jd else 'RAW'}")
            print(f"📋 [JD_ANALYZER] ⚡ USING CACHED ANALYSIS (based on processed JD: {used_processed_jd})")
            print(f"📋 [JD_ANALYZER] Cached JD source: {'PROCESSED' if used_processed_jd else 'RAW'}")
            
            # Check if processed JD exists to compare
            if self.user_email:
                try:
                    from app.services.jd_processing_service import get_jd_processing_service
                    jd_service = get_jd_processing_service(self.user_email)
                    processed_jd_path = jd_service._get_processed_jd_path(company_name)
                    
                    if processed_jd_path and processed_jd_path.exists():
                        # Load processed JD to show what SHOULD be used
                        processed_jd = jd_service.get_processed_jd(company_name)
                        if processed_jd:
                            processed_text = jd_service.processed_jd_to_text(processed_jd)
                            logger.warning(f"⚠️ [JD_ANALYZER] ⚠️⚠️⚠️ USING CACHED ANALYSIS (may be based on OLD/RAW JD)")
                            logger.warning(f"⚠️ [JD_ANALYZER] Processed JD exists ({len(processed_text)} chars) but cached analysis is being reused")
                            logger.warning(f"⚠️ [JD_ANALYZER] Cached analysis file: {analysis_file}")
                            logger.warning(f"⚠️ [JD_ANALYZER] Processed JD file: {processed_jd_path}")
                            logger.warning(f"⚠️ [JD_ANALYZER] To use processed JD, delete cached analysis or force re-analysis")
                            print(f"⚠️ [JD_ANALYZER] ⚠️⚠️⚠️ USING CACHED ANALYSIS - Processed JD exists but not being used!")
                            print(f"⚠️ [JD_ANALYZER] Cached: {analysis_file}")
                            print(f"⚠️ [JD_ANALYZER] Processed JD available: {processed_jd_path}")
                except Exception as e:
                    logger.debug(f"⚠️ [JD_ANALYZER] Could not check processed JD for cached analysis warning: {e}")
            
            logger.warning(f"⚠️ [JD_ANALYZER] Using cached analysis - processed JD check was not performed. "
                          f"Analysis may be based on original JD, not processed JD.")
            return JDAnalysisResult(data)
            
        except Exception as e:
            logger.warning(f"Failed to load existing analysis for {company_name}: {e}")
            return None
    
    async def analyze_jd_text(self, jd_text: str, temperature: float = 0.0) -> JDAnalysisResult:
        """
        Analyze job description text and extract keywords
        
        Args:
            jd_text: Job description text to analyze
            temperature: AI temperature for consistency (default: 0.0)
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            Exception: If analysis fails
        """
        try:
            # ⭐ LOG THE JD TEXT BEING SENT TO AI FOR KEYWORD EXTRACTION
            has_sections = any(section in jd_text for section in [
                "ROLE OVERVIEW", "KEY RESPONSIBILITIES", "TECHNICAL REQUIREMENTS"
            ])
            jd_preview = jd_text[:300].replace('\n', ' ')
            
            logger.info(f"📋 [JD_ANALYZER] ========== JD TEXT FOR KEYWORD EXTRACTION ==========")
            logger.info(f"📋 [JD_ANALYZER] JD text length: {len(jd_text)} characters")
            logger.info(f"📋 [JD_ANALYZER] Has sections format (processed JD): {has_sections}")
            logger.info(f"📋 [JD_ANALYZER] JD preview (first 300 chars): {jd_preview}")
            logger.info(f"📋 [JD_ANALYZER] Full JD text being sent to AI for keyword extraction:")
            logger.info(f"📋 [JD_ANALYZER] {jd_text}")
            logger.info(f"📋 [JD_ANALYZER] ========== END OF JD TEXT FOR KEYWORD EXTRACTION ==========")
            print(f"📋 [JD_ANALYZER] JD TEXT FOR KEYWORD EXTRACTION ({len(jd_text)} chars, has_sections={has_sections}):\n{jd_text}")
            
            system_prompt, user_prompt = get_jd_analysis_prompts(jd_text)
            
            # Get actual user from database to get real user ID (required for API key lookup)
            from app.models.auth import UserData
            from app.models.user import User
            from app.database import get_database
            from datetime import datetime, timezone
            
            # Query database for user record
            user_record = None
            for db in get_database():
                user_record = db.query(User).filter(User.email == self.user_email).first()
                break
            
            if not user_record:
                raise ValueError(f"User {self.user_email} not found in database. Cannot retrieve API keys.")
            
            # Create UserData with REAL user ID (converted to string as expected by UserData model)
            current_user = UserData(
                id=str(user_record.id),  # Convert INTEGER to string for UserData model
                email=user_record.email,
                name=user_record.full_name or user_record.username or "User",
                created_at=user_record.created_at.replace(tzinfo=timezone.utc) if user_record.created_at.tzinfo is None else user_record.created_at,
                is_active=user_record.is_active
            )
            
            logger.info(f"🔧 [JD_ANALYZER] Retrieved user from database: {current_user.email} (ID: {current_user.id})")
            
            # Initialize AI service for this user to load their API keys and providers
            logger.info(f"🔧 [JD_ANALYZER] Initializing AI service for user: {current_user.email}")
            self.ai_service.initialize_for_user(current_user)
            logger.info(f"✅ [JD_ANALYZER] AI service initialized with providers: {list(self.ai_service._providers.keys())}")
            
            # Check if user has any API keys configured
            if not self.ai_service._providers:
                from app.exceptions.cv_exceptions import APIKeyNotFoundError
                logger.error(f"❌ [JD_ANALYZER] No API keys configured for user {current_user.email}")
                raise APIKeyNotFoundError("any", current_user.email)
            
            # Check if current provider is available
            current_provider = self.ai_service.get_current_provider()
            if not current_provider:
                from app.exceptions.cv_exceptions import APIKeyNotFoundError
                logger.error(f"❌ [JD_ANALYZER] No provider selected for user {current_user.email}")
                raise APIKeyNotFoundError("any", current_user.email)
            
            response = await self.ai_service.generate_response(
                prompt=user_prompt,
                user=current_user,
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
            # Check if it's an API key error and preserve the original message
            from app.exceptions.cv_exceptions import APIKeyNotFoundError, APIKeyError
            if isinstance(e, (APIKeyNotFoundError, APIKeyError)):
                raise
            raise Exception(f"Failed to analyze job description: {e}")
    
    async def analyze_jd_file(self, file_path: Union[str, Path], temperature: float = 0.0) -> JDAnalysisResult:
        """
        Analyze job description from file
        
        Args:
            file_path: Path to job description file
            temperature: AI temperature for consistency (default: 0.0)
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If analysis fails
        """
        try:
            jd_text = self._read_jd_file(file_path)
            logger.info(f"📄 [JD_ANALYZER] Analyzing JD file: {file_path}")
            logger.info(f"📄 [JD_ANALYZER] JD text loaded from file (length: {len(jd_text)} chars)")
            logger.info(f"📄 [JD_ANALYZER] JD text will be passed to analyze_jd_text() which will log full content")
            
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
                                temperature: float = 0.0, force_processed_jd: bool = False) -> JDAnalysisResult:
        """
        Analyze job description using company name pattern
        
        Args:
            company_name: Company name (e.g., "Australia_for_UNHCR")
            base_path: Base path for JD files (optional, uses default if not provided)
            temperature: AI temperature for consistency (default: 0.0)
            force_processed_jd: If True, force use of processed JD even if cached analysis exists
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            FileNotFoundError: If JD file doesn't exist
            Exception: If analysis fails
        """
        # ⭐ CACHE INVALIDATION: Check if processed JD exists and should invalidate cache
        if self.user_email and not force_processed_jd:
            try:
                from app.services.jd_processing_service import get_jd_processing_service
                jd_service = get_jd_processing_service(self.user_email)
                if jd_service.has_processed_jd(company_name):
                    # Check if cached analysis exists and if it was based on processed JD
                    company_dir = Path(base_path or str(self.base_analysis_path)) / "applied_companies" / company_name
                    analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_name}_jd_analysis", "json")
                    
                    if analysis_file and analysis_file.exists():
                        try:
                            with open(analysis_file, 'r', encoding='utf-8') as f:
                                analysis_data = json.load(f)
                            analysis_metadata = analysis_data.get('metadata', {})
                            used_processed_jd = analysis_metadata.get('used_processed_jd', False)
                            
                            if not used_processed_jd:
                                logger.info(f"🔄 [JD_ANALYZER] Processed JD exists but cached analysis wasn't based on it. "
                                           f"Cache will be invalidated by _load_analysis_result()")
                        except Exception:
                            pass  # If we can't check, let _load_analysis_result() handle it
            except Exception as e:
                logger.debug(f"⚠️ [JD_ANALYZER] Could not check processed JD before analysis: {e}")
        
        if not base_path:
            base_path = str(self.base_analysis_path)
        
        company_dir = Path(base_path) / "applied_companies" / company_name
        jd_file_path = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
        
        # Fallback to non-timestamped file if no timestamped file exists
        if not jd_file_path:
            jd_file_path = company_dir / "jd_original.json"
        
        return await self.analyze_jd_file(jd_file_path, temperature)
    
    async def analyze_and_save_company_jd(self, company_name: str, force_refresh: bool = False,
                                        temperature: float = 0.0, base_path: Optional[str] = None) -> JDAnalysisResult:
        """
        Analyze company JD and save result with caching logic
        
        Args:
            company_name: Company name (e.g., "Australia_for_UNHCR")
            force_refresh: Force re-analysis even if cached result exists
            temperature: AI temperature for consistency (default: 0.0)
            
        Returns:
            JDAnalysisResult with extracted keywords
            
        Raises:
            FileNotFoundError: If JD file doesn't exist
            Exception: If analysis fails
        """
        try:
            # ⭐ FIX: Track if cache should be invalidated due to processed JD
            cache_invalidated_for_processed_jd = False
            
            # Check for existing analysis unless force refresh
            if not force_refresh:
                cached_result = self._load_analysis_result(company_name)
                if cached_result:
                    # If we can compute the current JD hash, only reuse cache if hashes match
                    try:
                        company_dir = self.base_analysis_path / "applied_companies" / company_name
                        jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json") or (company_dir / "jd_original.json")
                        # ⭐ Use _read_jd_file which automatically tries processed JD first
                        current_text = self._read_jd_file(jd_file) if jd_file and jd_file.exists() else None
                        current_hash = self._compute_jd_hash(current_text) if current_text else None
                        cached_hash = (cached_result.metadata or {}).get('jd_hash') if hasattr(cached_result, 'metadata') else None
                        cached_used_processed = (cached_result.metadata or {}).get('used_processed_jd', False) if hasattr(cached_result, 'metadata') else False
                        
                        # ⭐ CACHE VALIDATION: Check both hash AND processed JD usage
                        if current_hash and cached_hash and current_hash == cached_hash:
                            # Hash matches, but also check if processed JD was used
                            if self.user_email:
                                try:
                                    from app.services.jd_processing_service import get_jd_processing_service
                                    jd_service = get_jd_processing_service(self.user_email)
                                    processed_jd_exists = jd_service.has_processed_jd(company_name)
                                    
                                    if processed_jd_exists and not cached_used_processed:
                                        # Processed JD exists but cache wasn't based on it - INVALIDATE!
                                        logger.info(f"🔄 [JD_ANALYZER] Hash matches but cache wasn't based on processed JD. "
                                                   f"INVALIDATING cache to use processed JD.")
                                        print(f"🔄 [JD_ANALYZER] CACHE INVALIDATED: processed JD exists but cache wasn't based on it")
                                        cache_invalidated_for_processed_jd = True
                                        # Don't return cached_result, continue to re-analysis
                                    elif processed_jd_exists and cached_used_processed:
                                        # Both hash matches AND cache was based on processed JD - valid cache
                                        logger.info(f"📂 [JD_ANALYZER] Using cached analysis for {company_name} "
                                                   f"(JD hash matched AND was based on processed JD)")
                                        return cached_result
                                    elif not processed_jd_exists:
                                        # No processed JD exists, hash matches - valid cache
                                        logger.info(f"📂 [JD_ANALYZER] Using cached analysis for {company_name} (JD hash matched)")
                                        return cached_result
                                except Exception as e:
                                    logger.debug(f"⚠️ [JD_ANALYZER] Could not check processed JD for cache validation: {e}")
                                    # ⭐ FIX: Only use cached if we haven't marked for invalidation
                                    if not cache_invalidated_for_processed_jd:
                                        logger.info(f"📂 [JD_ANALYZER] Using cached analysis for {company_name} (JD hash matched, processed JD check failed)")
                                        return cached_result
                            else:
                                # No user_email, can't check processed JD - use cache if hash matches
                                logger.info(f"📂 [JD_ANALYZER] Using cached analysis for {company_name} (JD hash matched)")
                                return cached_result
                        else:
                            logger.info(f"🔁 Cached JD analysis exists but hash changed or missing; re-analyzing")
                    except Exception:
                        # If any issue computing hash, fall back to previous guard below
                        pass
                
                # ⭐ FIX: Skip secondary guard if cache was invalidated for processed JD
                if cache_invalidated_for_processed_jd:
                    logger.info(f"🔄 [JD_ANALYZER] Skipping secondary cache check - cache was invalidated for processed JD")
                else:
                    # If a JD original already exists in the company folder and an analysis file also exists,
                    # avoid re-running analysis again. This is a defensive guard against duplicate runs.
                    company_dir = self.base_analysis_path / "applied_companies" / company_name
                    try:
                        jd_original = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json") or (company_dir / "jd_original.json" if (company_dir / "jd_original.json").exists() else None)
                        jd_analysis = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_name}_jd_analysis", "json") or (company_dir / f"{company_name}_jd_analysis.json" if (company_dir / f"{company_name}_jd_analysis.json").exists() else None)
                        if jd_original and jd_analysis and jd_analysis.exists():
                            # If hash matches, reuse; else proceed to fresh analysis
                            try:
                                # ⭐ Use _read_jd_file which automatically tries processed JD first
                                current_text = self._read_jd_file(jd_original)
                                current_hash = self._compute_jd_hash(current_text)
                                with open(jd_analysis, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                cached_hash = data.get('metadata', {}).get('jd_hash') if isinstance(data, dict) else None
                                cached_used_processed = data.get('metadata', {}).get('used_processed_jd', False) if isinstance(data, dict) else False
                                
                                if isinstance(data, dict) and cached_hash == current_hash:
                                    # Hash matches, but also check if processed JD was used
                                    if self.user_email:
                                        try:
                                            from app.services.jd_processing_service import get_jd_processing_service
                                            jd_service = get_jd_processing_service(self.user_email)
                                            processed_jd_exists = jd_service.has_processed_jd(company_name)
                                            
                                            if processed_jd_exists and not cached_used_processed:
                                                # Processed JD exists but cache wasn't based on it - INVALIDATE!
                                                logger.info(f"🔄 [JD_ANALYZER] (Guard) Hash matches but cache wasn't based on processed JD. "
                                                           f"INVALIDATING cache to use processed JD.")
                                                print(f"🔄 [JD_ANALYZER] (Guard) CACHE INVALIDATED: processed JD exists but cache wasn't based on it")
                                                cache_invalidated_for_processed_jd = True
                                                # Don't return, continue to re-analysis
                                            elif processed_jd_exists and cached_used_processed:
                                                # Both hash matches AND cache was based on processed JD - valid cache
                                                logger.info(f"♻️ [JD_ANALYZER] JD original and matching analysis already present for {company_name} "
                                                           f"(hash matched AND was based on processed JD); skipping re-analysis")
                                                return JDAnalysisResult(data)
                                            elif not processed_jd_exists:
                                                # No processed JD exists, hash matches - valid cache
                                                logger.info(f"♻️ [JD_ANALYZER] JD original and matching analysis already present for {company_name}; skipping re-analysis")
                                                return JDAnalysisResult(data)
                                        except Exception as e:
                                            logger.debug(f"⚠️ [JD_ANALYZER] Could not check processed JD for guard validation: {e}")
                                            # ⭐ FIX: Only use cached if we haven't marked for invalidation
                                            if not cache_invalidated_for_processed_jd:
                                                logger.info(f"♻️ [JD_ANALYZER] JD original and matching analysis already present for {company_name}; skipping re-analysis")
                                                return JDAnalysisResult(data)
                                    else:
                                        # No user_email, can't check processed JD - use cache if hash matches
                                        logger.info(f"♻️ [JD_ANALYZER] JD original and matching analysis already present for {company_name}; skipping re-analysis")
                                        return JDAnalysisResult(data)
                                # ⭐ FIX: Don't return if cache was invalidated for processed JD
                                if not cache_invalidated_for_processed_jd:
                                    return JDAnalysisResult(data)
                            except Exception:
                                logger.debug("Hash comparison failed; continuing with fresh analysis")
                except Exception as guard_err:
                    logger.debug(f"Guard check for existing JD files failed (continuing with analysis): {guard_err}")
            
            # Perform fresh analysis
            logger.info(f"🔄 [JD_ANALYZER] 🔄 PERFORMING NEW ANALYSIS with processed JD for {company_name} (force_refresh={force_refresh})")
            print(f"🔄 [JD_ANALYZER] 🔄 PERFORMING NEW ANALYSIS with processed JD for {company_name} (force_refresh={force_refresh})")
            result = await self.analyze_company_jd(company_name, base_path=base_path, temperature=temperature)
            
            # Set company name and metadata
            result.company_name = company_name
            
            # ⭐ MARK METADATA: Indicate that this analysis used processed JD (if available)
            if self.user_email:
                try:
                    from app.services.jd_processing_service import get_jd_processing_service
                    jd_service = get_jd_processing_service(self.user_email)
                    if jd_service.has_processed_jd(company_name):
                        result.metadata = result.metadata or {}
                        result.metadata['used_processed_jd'] = True
                        processed_jd = jd_service.get_processed_jd(company_name)
                        if processed_jd:
                            processed_text = jd_service.processed_jd_to_text(processed_jd)
                            result.metadata['jd_source'] = 'processed'
                            result.metadata['processed_jd_length'] = len(processed_text)
                            result.metadata['timestamp'] = datetime.now().isoformat()
                        logger.info(f"✅ [JD_ANALYZER] Marked analysis as using processed JD for {company_name}")
                        logger.info(f"✅ [JD_ANALYZER] Cache metadata: jd_source=processed, length={result.metadata.get('processed_jd_length')}")
                except Exception as e:
                    logger.debug(f"⚠️ [JD_ANALYZER] Could not mark processed JD usage in metadata: {e}")
            
            # Ensure base path is user-scoped when saving if provided
            if base_path:
                self.base_analysis_path = Path(base_path)
            # Save result
            saved_path = self._save_analysis_result(company_name, result)
            # ⭐ FIX: Preserve existing metadata and ADD saved_path (don't overwrite!)
            if result.metadata is None:
                result.metadata = {}
            result.metadata["saved_path"] = saved_path
            
            # Log final metadata for verification
            logger.info(f"📋 [JD_ANALYZER] Final analysis metadata: used_processed_jd={result.metadata.get('used_processed_jd')}, "
                       f"jd_source={result.metadata.get('jd_source')}, saved_path={saved_path}")
            
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
async def analyze_jd_text(jd_text: str, temperature: float = 0.0) -> JDAnalysisResult:
    """Convenience function to analyze JD text"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_jd_text(jd_text, temperature)


async def analyze_jd_file(file_path: Union[str, Path], temperature: float = 0.0) -> JDAnalysisResult:
    """Convenience function to analyze JD file"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_jd_file(file_path, temperature)


async def analyze_company_jd(company_name: str, base_path: Optional[str] = None, 
                           temperature: float = 0.0) -> JDAnalysisResult:
    """Convenience function to analyze company JD using naming pattern"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_company_jd(company_name, base_path, temperature)


async def analyze_and_save_company_jd(company_name: str, force_refresh: bool = False,
                                    temperature: float = 0.0) -> JDAnalysisResult:
    """Convenience function to analyze and save company JD"""
    analyzer = JDAnalyzer()
    return await analyzer.analyze_and_save_company_jd(company_name, force_refresh, temperature)


def load_jd_analysis(company_name: str) -> Optional[JDAnalysisResult]:
    """Convenience function to load saved JD analysis"""
    analyzer = JDAnalyzer()
    return analyzer.load_jd_analysis(company_name)
