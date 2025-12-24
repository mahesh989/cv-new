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
from app.utils.timestamp_utils import TimestampUtils
from .cv_jd_matching_prompt import get_cv_jd_matching_prompts

logger = logging.getLogger(__name__)

class CVJDMatchResult:
    """Container for CV-JD matching results"""
    
    def __init__(self, data: Dict[str, Any], jd_analysis_data: Optional[Dict[str, Any]] = None):
        # Raw matching results (from AI - all keywords together)
        self.matched_keywords: List[str] = data.get('matched_keywords', [])
        self.missed_keywords: List[str] = data.get('missed_keywords', [])

        # Classified results (required/preferred split for backward compatibility)
        self.matched_required_keywords: List[str] = []
        self.matched_preferred_keywords: List[str] = []
        self.missed_required_keywords: List[str] = []
        self.missed_preferred_keywords: List[str] = []

        # Classify matched/missed keywords if JD analysis is provided
        if jd_analysis_data:
            self._classify_matched_keywords(jd_analysis_data)
        else:
            # Fallback: Use legacy format if provided, otherwise assume all are required
            self.matched_required_keywords = data.get('matched_required_keywords', self.matched_keywords)
            self.matched_preferred_keywords = data.get('matched_preferred_keywords', [])
            self.missed_required_keywords = data.get('missed_required_keywords', self.missed_keywords)
            self.missed_preferred_keywords = data.get('missed_preferred_keywords', [])
        
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
        
        # Validate and fix data consistency
        self._validate_and_fix()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format"""
        return {
            'company_name': self.company_name,
            'cv_analysis_timestamp': self.analysis_timestamp,
            # Raw results (from AI)
            'matched_keywords': self.matched_keywords,
            'missed_keywords': self.missed_keywords,
            # Classified results (for backward compatibility)
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
        # Use classified counts for backward compatibility
        total_required = len(self.matched_required_keywords) + len(self.missed_required_keywords)
        total_preferred = len(self.matched_preferred_keywords) + len(self.missed_preferred_keywords)

        matched_required = len(self.matched_required_keywords)
        matched_preferred = len(self.matched_preferred_keywords)

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
    
    def _validate_and_fix(self):
        """
        Validate consistency and auto-fix common issues in matching results.
        
        Fixes:
        - Counts that don't match actual list lengths
        - Duplicate keywords across matched/missed lists
        - Duplicate keywords within lists
        - Total counts that don't match matched + missed
        """
        # Remove duplicates within each list (preserve order)
        self.matched_keywords = list(dict.fromkeys(self.matched_keywords))
        self.missed_keywords = list(dict.fromkeys(self.missed_keywords))

        # Remove duplicates between matched and missed lists (trust matched more)
        matched_set = set(self.matched_keywords)
        missed_set = set(self.missed_keywords)
        duplicates = matched_set & missed_set

        if duplicates:
            logger.warning(f"⚠️ [VALIDATION] Found {len(duplicates)} keywords in both matched and missed: {duplicates}")
            self.missed_keywords = [k for k in self.missed_keywords if k not in duplicates]
            missed_set = set(self.missed_keywords)

        # Fix counts to match actual list lengths
        actual_matched = len(self.matched_keywords)
        actual_missed = len(self.missed_keywords)

        reported_matched = self.match_counts.get('matched_count', actual_matched)
        reported_missed = self.match_counts.get('missed_count', actual_missed)

        if reported_matched != actual_matched:
            logger.warning(f"⚠️ [VALIDATION] Fixing matched_count: {reported_matched} → {actual_matched}")
            self.match_counts['matched_count'] = actual_matched

        if reported_missed != actual_missed:
            logger.warning(f"⚠️ [VALIDATION] Fixing missed_count: {reported_missed} → {actual_missed}")
            self.match_counts['missed_count'] = actual_missed

        # Validate and fix total count
        # Total should equal matched + missed
        total_from_lists = actual_matched + actual_missed
        reported_total = self.match_counts.get('total_keywords', total_from_lists)

        if reported_total != total_from_lists:
            logger.warning(f"⚠️ [VALIDATION] Fixing total_keywords: {reported_total} → {total_from_lists} (matched={actual_matched} + missed={actual_missed})")
            self.match_counts['total_keywords'] = total_from_lists

        # Log validation summary
        if duplicates or reported_matched != actual_matched or reported_missed != actual_missed or reported_total != total_from_lists:
            logger.info(f"✅ [VALIDATION] Data consistency fixed. Final counts: {actual_matched}/{total_from_lists} matched, {actual_missed} missed")

    def _classify_matched_keywords(self, jd_analysis_data: Dict[str, Any]):
        """
        Classify matched/missed keywords back into required/preferred categories
        for backward compatibility with bonus calculator.
        """
        # Get original required/preferred keywords from JD analysis
        required_keywords = jd_analysis_data.get('required_keywords', [])
        preferred_keywords = jd_analysis_data.get('preferred_keywords', [])

        # Create sets for fast lookup
        required_set = set(required_keywords)
        preferred_set = set(preferred_keywords)

        # Classify matched keywords
        for keyword in self.matched_keywords:
            if keyword in required_set:
                self.matched_required_keywords.append(keyword)
            elif keyword in preferred_set:
                self.matched_preferred_keywords.append(keyword)
            else:
                # Keyword not in either category (shouldn't happen, but handle gracefully)
                logger.warning(f"⚠️ [CLASSIFICATION] Matched keyword '{keyword}' not found in required or preferred lists")
                self.matched_required_keywords.append(keyword)  # Default to required

        # Classify missed keywords
        for keyword in self.missed_keywords:
            if keyword in required_set:
                self.missed_required_keywords.append(keyword)
            elif keyword in preferred_set:
                self.missed_preferred_keywords.append(keyword)
            else:
                # Keyword not in either category
                logger.warning(f"⚠️ [CLASSIFICATION] Missed keyword '{keyword}' not found in required or preferred lists")
                self.missed_required_keywords.append(keyword)  # Default to required

        logger.info(f"✅ [CLASSIFICATION] Classified {len(self.matched_keywords)} matched and {len(self.missed_keywords)} missed keywords into required/preferred categories")

class CVJDMatcher:
    """CV-JD Matcher using centralized AI system"""
    
    def __init__(self, user_email: str):
        self.ai_service = ai_service
        self.user_email = user_email
    
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
            
            # Validate CV has matchable content
            self._validate_cv_content(content, path)
            
            return content
        except Exception as e:
            logger.error(f"Error reading CV file {path}: {e}")
            raise IOError(f"Failed to read CV file: {e}")
    
    def _validate_cv_content(self, content: str, file_path: Union[str, Path] = None) -> None:
        """
        Validate CV has sufficient matchable content.
        
        Args:
            content: CV content text
            file_path: Optional file path for error messages
            
        Raises:
            ValueError: If CV content is insufficient for matching
        """
        # Check minimum character count (excluding whitespace)
        clean_content = ''.join(content.split())
        if len(clean_content) < 200:  # Minimum 200 characters
            path_info = f" ({file_path})" if file_path else ""
            raise ValueError(f"CV content too short for matching{path_info}. Minimum 200 characters required, found {len(clean_content)}")
        
        # Check for skill-related sections (at least one should exist)
        content_lower = content.lower()
        skill_indicators = [
            'experience', 'skills', 'education', 'projects', 
            'work', 'employment', 'qualifications', 'summary',
            'objective', 'professional', 'career', 'background'
        ]
        has_sections = any(indicator in content_lower for indicator in skill_indicators)
        
        if not has_sections:
            logger.warning(f"⚠️ [VALIDATION] CV may be missing standard sections (experience, skills, etc.)")
            # Don't fail, just warn - some CVs might have non-standard formats
        
        # Additional check: ensure there's substantial text beyond just headers
        # Count non-empty lines that aren't just separators
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        # Filter out lines that are mostly separators or very short
        substantial_lines = [
            line for line in lines 
            if len(line) > 10 and not all(c in '=-_*# ' for c in line[:20])
        ]
        
        if len(substantial_lines) < 3:
            path_info = f" ({file_path})" if file_path else ""
            logger.warning(f"⚠️ [VALIDATION] CV has very few substantial lines{path_info}. May have limited matchable content.")
    
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
            from app.utils.user_path_utils import get_user_base_path
            base_path = get_user_base_path(self.user_email)
        
        company_dir = Path(base_path) / "applied_companies" / company_name
        # Try to find timestamped file with company name pattern first
        analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_name}_jd_analysis", "json")
        
        # Fallback to old pattern without company name if not found
        if not analysis_file:
            analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_analysis", "json")
        
        # Fallback to non-timestamped file if still not found
        if not analysis_file:
            analysis_file = company_dir / f"{company_name}_jd_analysis.json"
        
        if not analysis_file.exists():
            raise FileNotFoundError(f"JD analysis file not found: {analysis_file}")
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"📂 Loaded JD analysis from: {analysis_file}")
            
            # ⭐ JD SOURCE LOGGING: Check if analysis was based on processed JD
            analysis_metadata = data.get('metadata', {}) or {}
            used_processed_jd = analysis_metadata.get('used_processed_jd', False)
            required_keywords = data.get('required_keywords', [])
            preferred_keywords = data.get('preferred_keywords', [])
            
            logger.info(f"📋 [CV_JD_MATCHING] ========== JD ANALYSIS SOURCE ==========")
            logger.info(f"📋 [CV_JD_MATCHING] Using JD analysis created from: {'PROCESSED JD' if used_processed_jd else 'RAW JD'}")
            logger.info(f"📋 [CV_JD_MATCHING] Analysis file: {analysis_file}")
            logger.info(f"📋 [CV_JD_MATCHING] Keywords count: {len(required_keywords)} required, {len(preferred_keywords)} preferred")
            logger.info(f"📋 [CV_JD_MATCHING] Analysis metadata: used_processed_jd={used_processed_jd}")
            logger.info(f"📋 [CV_JD_MATCHING] ========== END JD ANALYSIS SOURCE ==========")
            print(f"📋 [CV_JD_MATCHING] Using JD analysis created from: {'PROCESSED JD' if used_processed_jd else 'RAW JD'}")
            
            return data
        except Exception as e:
            logger.error(f"Error reading JD analysis file {analysis_file}: {e}")
            raise IOError(f"Failed to read JD analysis file: {e}")
    
    
    def _parse_ai_response(self, response: AIResponse, jd_analysis_data: Optional[Dict[str, Any]] = None) -> CVJDMatchResult:
        """
        Parse AI response into structured result
        
        Args:
            response: AI response containing JSON analysis
            
        Returns:
            CVJDMatchResult object
            
        Raises:
            json.JSONDecodeError: If JSON parsing fails (cleanup handled in retry loop)
            ValueError: If response structure is invalid
        """
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
            'matched_keywords', 'missed_keywords',
            'match_counts'
        ]

        for field in required_fields:
            if field not in data:
                data[field] = [] if 'keywords' in field else {}
        
        result = CVJDMatchResult(data, jd_analysis_data)
        result.ai_model_used = f"{response.provider}/{response.model}"
        
        return result
    
    def _clean_json_response(self, content: str) -> str:
        """
        Clean and fix common JSON formatting issues in AI responses
        """
        import re
        
        # Remove any text before the first {
        content = re.sub(r'^[^{]*', '', content)
        
        # Remove any text after the last }
        content = re.sub(r'}[^}]*$', '}', content)
        
        # Fix common issues:
        # 1. Convert single quotes to double quotes for keys
        content = re.sub(r"'([^']*)':", r'"\1":', content)
        
        # 2. Convert single quotes to double quotes for string values
        content = re.sub(r":\s*'([^']*)'", r': "\1"', content)
        
        # 3. Convert single quotes to double quotes in arrays
        content = re.sub(r"\[\s*'([^']*)'", r'["\1"', content)
        content = re.sub(r",\s*'([^']*)'", r', "\1"', content)
        
        # 4. Fix unquoted string values in matching_notes
        # Handle cases like: "Excel": Matched as it is mentioned...
        def fix_matching_notes(match):
            key = match.group(1)
            value = match.group(2)
            # Escape any quotes in the value and wrap in quotes
            value = value.replace('"', '\\"')
            return f'"{key}": "{value}"'
        
        # Pattern to match "key": unquoted_value
        content = re.sub(r'"([^"]+)":\s*([^,}]+?)(?=\s*[,}])', fix_matching_notes, content)
        
        # 5. Remove trailing commas before closing braces/brackets
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        return content
    
    async def match_cv_against_jd(
        self, 
        company_name: str,
        cv_file_path: Optional[str] = None,
        jd_analysis_data: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_retries: int = 3
    ) -> CVJDMatchResult:
        """
        Match CV content against job description keywords
        
        Args:
            company_name: Company name for the analysis
            cv_file_path: Path to CV file (optional, uses default if not provided)
            jd_analysis_data: JD analysis data (optional, loads from file if not provided)
            temperature: AI temperature for consistency (default: 0.0 for deterministic matching)
            
        Returns:
            CVJDMatchResult with matching results
            
        Raises:
            FileNotFoundError: If required files don't exist
            Exception: If matching fails
        """
        try:
            # Read CV content using unified latest file selector
            if not cv_file_path:
                logger.info(f"🔍 [CV_JD_MATCHER] No explicit CV path provided, using unified selector for {company_name}")
                
                from app.unified_latest_file_selector import get_selector_for_user
                user_selector = get_selector_for_user(self.user_email)
                
                # CRITICAL: For CV-JD matching (especially during reruns), always use the latest CV across all
                # This ensures that when a tailored CV is generated, reruns will use it for matching
                # Preferring tailored CV if it exists and is newer than original CV
                cv_context = user_selector.get_latest_cv_across_all(company_name)
                
                if not cv_context.exists:
                    raise FileNotFoundError(f"No CV found for company: {company_name}")
                
                # Use TXT file if available, otherwise JSON
                cv_file_path = str(cv_context.txt_path) if cv_context.txt_path else str(cv_context.json_path)
                logger.info(
                    f"✅ [CV_JD_MATCHER] Selected CV → type={cv_context.file_type}, ts={cv_context.timestamp}, path={cv_file_path}"
                )
            else:
                logger.info(f"📄 [CV_JD_MATCHER] Using provided CV path: {cv_file_path}")
            
            cv_content = self._read_cv_file(cv_file_path)
            try:
                preview = (cv_content or "")[:400].replace('\n', ' ')
                logger.info(f"📄 [CV_JD_MATCHER] Read CV from: {cv_file_path}")
                logger.info(f"🧪 [CV_JD_MATCHER] CV content length={len(cv_content or '')}, preview='{preview}'")
            except Exception:
                logger.info(f"📄 [CV_JD_MATCHER] Read CV from: {cv_file_path}")
                logger.info(f"🧪 [CV_JD_MATCHER] CV content length={len(cv_content or '')}")
            
            # Get JD analysis data
            # ⭐ NOTE: JD analysis already uses processed JD (via jd_analyzer.py)
            # CV-JD matching benefits from processed JD indirectly through better keyword extraction
            if not jd_analysis_data:
                jd_analysis_data = self._read_jd_analysis(company_name)
                logger.info(f"📊 [CV_JD_MATCHER] Loaded JD analysis for: {company_name}")
                print(f"📊 [CV_JD_MATCHER] Loaded JD analysis for: {company_name}")
                logger.info(f"ℹ️ [CV_JD_MATCHER] JD analysis was created using processed JD (if available)")
                print(f"ℹ️ [CV_JD_MATCHER] JD analysis was created using processed JD (if available)")
            
            # Extract keywords from JD analysis - use three_section_skills as primary source
            all_keywords = jd_analysis_data.get('three_section_all_keywords', [])

            # Fallback: If no three_section_all_keywords, try to extract from three_section_skills directly
            if not all_keywords and 'three_section_skills' in jd_analysis_data:
                three_section = jd_analysis_data['three_section_skills']
                all_keywords.extend(three_section.get('technical_skills', []))
                all_keywords.extend(three_section.get('soft_skills', []))
                all_keywords.extend(three_section.get('domain_knowledge', []))

            # Final fallback: Use required/preferred keywords (for backward compatibility)
            if not all_keywords:
                required_keywords = jd_analysis_data.get('required_keywords', [])
                preferred_keywords = jd_analysis_data.get('preferred_keywords', [])
                all_keywords = required_keywords + preferred_keywords

            if not all_keywords:
                raise ValueError("No keywords found in JD analysis data")

            # Remove duplicates while preserving order
            all_keywords = list(dict.fromkeys(all_keywords))

            logger.info(f"🔍 Found {len(all_keywords)} keywords from three_section_skills for CV-JD matching")
            
            # Get prompts
            system_prompt, user_prompt = get_cv_jd_matching_prompts(
                cv_content=cv_content,
                all_keywords=all_keywords
            )
            
            # Determine if we can use structured outputs (JSON mode)
            # OpenAI supports response_format for JSON mode, which eliminates JSON parsing issues
            response_format_kwargs = {}
            
            # Check current provider to determine structured output support
            current_provider_name = self.ai_service.config.get_current_provider()
            if current_provider_name == "openai":
                # OpenAI JSON mode - forces valid JSON output, eliminating parsing issues
                # This allows the model to focus on matching quality rather than JSON formatting
                response_format_kwargs = {"response_format": {"type": "json_object"}}
                logger.info("✅ [CV_JD_MATCHER] Using OpenAI JSON mode for structured output")
            
            # Retry logic for AI service calls
            last_error = None
            for attempt in range(max_retries):
                try:
                    # Create user object from stored user_email
                    from app.models.auth import UserData
                    from datetime import datetime, timezone
                    current_user = UserData(
                        id="pipeline_user",  # Use a placeholder ID for pipeline operations
                        email=self.user_email,
                        name=self.user_email.split("@")[0] if self.user_email else "user",
                        created_at=datetime.now(timezone.utc),
                        is_active=True
                    )
                    
                    # Call AI service with structured output if supported
                    response = await self.ai_service.generate_response(
                        prompt=user_prompt,
                        user=current_user,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=3000,
                        **response_format_kwargs
                    )
                    
                    # Try parsing with cleanup on JSON errors
                    try:
                        result = self._parse_ai_response(response, jd_analysis_data)
                        result.company_name = company_name
                        result.cv_file_path = cv_file_path
                        
                        logger.info(f"✅ CV-JD matching completed. Found {len(result.matched_required_keywords)} matched required keywords")
                        
                        return result
                        
                    except json.JSONDecodeError as json_err:
                        # Try cleanup on first attempt before retrying with fresh API call
                        if attempt == 0:
                            try:
                                logger.warning(f"⚠️ JSON parsing failed, attempting cleanup...")
                                cleaned_content = self._clean_json_response(response.content)
                                data = json.loads(cleaned_content)
                                
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
                                result.company_name = company_name
                                result.cv_file_path = cv_file_path
                                
                                logger.info("✅ Successfully fixed and parsed malformed JSON response")
                                logger.info(f"✅ CV-JD matching completed. Found {len(result.matched_required_keywords)} matched required keywords")
                                
                                return result
                                
                            except Exception as cleanup_error:
                                logger.warning(f"⚠️ JSON cleanup failed: {cleanup_error}")
                                # Will continue to retry with fresh API call
                        
                        # If cleanup failed or not first attempt, continue to retry
                        last_error = json_err
                        logger.warning(f"⚠️ Attempt {attempt + 1}/{max_retries} - JSON parse failed: {json_err}")
                        if attempt < max_retries - 1:
                            logger.info(f"🔄 Retrying CV-JD matching with fresh API call...")
                            await asyncio.sleep(1)  # Brief delay before retry
                        continue
                    
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
            from app.utils.user_path_utils import get_user_base_path, get_user_company_analysis_paths, validate_company_name
            validate_company_name(company_name)
            base_path = get_user_base_path(self.user_email)
        
        # Get correct paths
        paths = get_user_company_analysis_paths(self.user_email, company_name)
        timestamp = TimestampUtils.get_timestamp()
        result_file = paths["cv_jd_matching"](timestamp)
        result_file.parent.mkdir(parents=True, exist_ok=True)
        
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
            from app.utils.user_path_utils import get_user_base_path
            base_path = get_user_base_path(self.user_email)
        
        company_dir = Path(base_path) / "applied_companies" / company_name
        result_file = TimestampUtils.find_latest_timestamped_file(company_dir, "cv_jd_match_results", "json")
        
        if not result_file or not result_file.exists():
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
    temperature: float = 0.0,
    user_email: str = None
) -> CVJDMatchResult:
    """Convenience function to match CV against company JD"""
    matcher = CVJDMatcher(user_email=user_email)
    return await matcher.match_cv_against_jd(company_name, cv_file_path, None, temperature)

async def match_and_save_cv_jd(
    company_name: str,
    cv_file_path: Optional[str] = None,
    force_refresh: bool = False,
    temperature: float = 0.0,
    jd_analysis_data: Optional[Dict[str, Any]] = None,
    user_email: str = None
) -> CVJDMatchResult:
    """Convenience function to match CV against JD and save results"""
    matcher = CVJDMatcher(user_email=user_email)
    
    # Check for existing results
    if not force_refresh:
        existing_result = matcher._load_match_result(company_name)
        if existing_result:
            logger.info(f"📦 Using cached CV-JD match results for {company_name}")
            return existing_result
    
            # Perform matching
    try:
        result = await matcher.match_cv_against_jd(company_name, cv_file_path, jd_analysis_data, temperature)
        
        # Save results
        matcher._save_match_result(result, company_name)
    except ValueError as ve:
        if "too short" in str(ve) or "insufficient content" in str(ve):
            logger.error(f"❌ CV file for {company_name} does not contain enough content for matching. Please ensure the CV includes relevant experience and skills.")
        elif "No keywords found" in str(ve):
            logger.error(f"❌ No keywords found in JD analysis for {company_name}. Please ensure the job description has been properly analyzed.")
        raise
    
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
