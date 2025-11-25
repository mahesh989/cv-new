"""
JD Processing Service

This service integrates the universal JD processing pipeline into the main application.
It processes job descriptions into structured JSON format and provides utilities
to convert processed JDs back to text when needed for AI operations.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

from app.utils.timestamp_utils import TimestampUtils
from app.utils.user_path_utils import get_user_base_path
from app.ai.ai_service import ai_service

logger = logging.getLogger(__name__)


def _extract_json_content(content: str) -> str:
    """Strip optional markdown fences and return raw JSON string."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines:
            lines = lines[1:]
        while lines and lines[-1].strip() == "":
            lines.pop()
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    return content


class JDOptimizer:
    """
    Universal JD optimizer that handles filtering + reorganization in one pass.
    Uses the app's AI service for processing.
    """
    
    def __init__(self, ai_service: Optional[Any] = None):
        self.ai_service = ai_service
        self.using_real_ai = ai_service is not None
    
    async def universal_jd_processing(self, jd_text: str, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Single AI call that handles filtering + reorganization for any JD format.
        """
        universal_prompt = f"""
        **ROLE**: You are an expert Job Description Processor with 10+ years experience in HR tech and recruitment.

        **TASK**: Process this job description through TWO phases:

        ---

        ### **PHASE 1: CONTENT PRESERVATION FILTERING**

        **REMOVE ONLY THESE ELEMENTS**:
        - Salary figures, compensation details, bonus structures
        - Specific employee benefits (health insurance, gym memberships, free meals, etc.)
        - Application instructions ("click apply", "send email", "submit resume")
        - Contact information (email addresses, phone numbers, physical addresses)
        - Equal employment opportunity statements (unless they specify role requirements)
        - Employee testimonials or satisfaction survey results
        - Company stock performance or growth metrics
        - Office amenities and physical workspace descriptions
        - Generic "about our culture" statements that don't relate to job performance
        - Repetitive company background information

        **PRESERVE EVERYTHING ELSE**:
        - All job responsibilities and daily tasks
        - All required/preferred skills (technical, soft, domain-specific)
        - All experience requirements (years, specific background, industries)
        - All educational qualifications and certifications
        - Reporting structure and team information
        - Work arrangement (remote, hybrid, office location)
        - Tools, technologies, and software requirements
        - Performance expectations and success metrics
        - Industry/domain knowledge requirements
        - Project examples or portfolio requirements
        - Travel requirements or physical demands
        - Security clearances or background check requirements
        - Language proficiency requirements

        ---

        ### **PHASE 2: INTELLIGENT REORGANIZATION**

        **REORGANIZE INTO THESE SECTIONS** (create only sections that have content):
        1. **ROLE OVERVIEW & CONTEXT**
        2. **KEY RESPONSIBILITIES**
        3. **TECHNICAL REQUIREMENTS**
        4. **EXPERIENCE REQUIREMENTS**
        5. **QUALIFICATIONS & EDUCATION**
        6. **SOFT SKILLS & COMPETENCIES**
        7. **DOMAIN KNOWLEDGE**
        8. **WORK ARRANGEMENT**

        ---

        **CRITICAL RULES**:
        1. **PRESERVE EXACT PHRASING** - Never paraphrase or summarize requirements
        2. **REMOVE ONLY VERBATIM DUPLICATES** - Keep similar concepts if phrased differently
        3. **MAINTAIN ORIGINAL INTENT** - Don't lose nuance in requirements
        4. **CREATE NEW SECTIONS** if content doesn't fit standard categories
        5. **WHEN IN DOUBT, KEEP IT** - Better to have extra content than lose requirements
        6. **RESPECT JD STRUCTURE** - If JD has unique sections, preserve their intent
        7. **MAINTAIN TECHNICAL PRECISION** - Especially for engineering/medical/legal roles

        ---

        **INPUT JOB DESCRIPTION**:
        {jd_text}

        ---

        **OUTPUT FORMAT**:
        Return ONLY a JSON object (no markdown fences) in this structure:
        {{
            "sections": {{
                "ROLE OVERVIEW & CONTEXT": ["paragraph 1", "paragraph 2"],
                "KEY RESPONSIBILITIES": ["- bullet 1", "- bullet 2"],
                ...
            }},
            "additional_sections": {{
                "CUSTOM SECTION NAME": ["items if any"]
            }}
        }}

        - Use arrays of strings for each section so content stays exactly as in the JD.
        - Omit empty sections entirely.
        """
        
        if self.ai_service:
            from app.models.auth import UserData
            # Get user from job_info if available, otherwise we need it passed
            user = job_info.get('user')
            if not user:
                raise ValueError("User object required for AI service")
            
            response = await self.ai_service.generate_response(
                prompt=universal_prompt,
                user=user,
                system_prompt=(
                    "You are a universal JD processor that handles any format, industry, or structure. "
                    "Your goal is to preserve all meaningful job requirements while removing only true noise. "
                    "Adapt to the input format rather than forcing a specific output structure."
                ),
                temperature=0.1,
                max_tokens=4000,
            )
            return self._parse_processed_response(response.content)
        
        # Fallback to simple structure if no AI service
        return {
            "sections": {
                "ROLE OVERVIEW & CONTEXT": [jd_text]
            }
        }
    
    def _parse_processed_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM response into structured sections."""
        raw = _extract_json_content(content)
        try:
            payload = json.loads(raw)
            if "sections" not in payload or not isinstance(payload["sections"], dict):
                raise ValueError("Missing sections key")
            return payload
        except Exception:
            # Fallback to wrapping raw text
            return {
                "sections": {
                    "RAW_OUTPUT": [content.strip()]
                }
            }


class JDProcessingService:
    """
    Service for processing job descriptions into structured format
    and managing processed JD files
    """
    
    def __init__(self, user_email: str):
        logger.info(f"🏗️ [JD_PROCESSING_SERVICE] ===== INITIALIZING SERVICE =====")
        logger.info(f"🏗️ [JD_PROCESSING_SERVICE] User email: {user_email}")
        self.user_email = user_email
        logger.info(f"🏗️ [JD_PROCESSING_SERVICE] Getting user base path...")
        self.base_path = get_user_base_path(user_email)
        logger.info(f"🏗️ [JD_PROCESSING_SERVICE] Base path: {self.base_path}")
        logger.info(f"🏗️ [JD_PROCESSING_SERVICE] Base path exists: {self.base_path.exists() if self.base_path else False}")
        logger.info(f"🏗️ [JD_PROCESSING_SERVICE] ✅ Service initialized successfully")
    
    def _get_processed_jd_path(self, company_name: str) -> Optional[Path]:
        """
        Get path to processed JD file for a company
        
        Args:
            company_name: Company name
            
        Returns:
            Path to processed JD file if exists, None otherwise
        """
        company_dir = self.base_path / "applied_companies" / company_name
        processed_file = TimestampUtils.find_latest_timestamped_file(
            company_dir, "jd_processed", "json"
        )
        if not processed_file:
            processed_file = company_dir / "jd_processed.json"
        return processed_file if processed_file.exists() else None
    
    def _get_original_jd_path(self, company_name: str) -> Optional[Path]:
        """
        Get path to original JD file for a company
        
        Args:
            company_name: Company name
            
        Returns:
            Path to original JD file if exists, None otherwise
        """
        company_dir = self.base_path / "applied_companies" / company_name
        original_file = TimestampUtils.find_latest_timestamped_file(
            company_dir, "jd_original", "json"
        )
        if not original_file:
            original_file = company_dir / "jd_original.json"
        return original_file if original_file.exists() else None
    
    def get_processed_jd(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Get processed JD data for a company
        
        Args:
            company_name: Company name
            
        Returns:
            Processed JD data (structured JSON) if exists, None otherwise
        """
        processed_path = self._get_processed_jd_path(company_name)
        if not processed_path:
            return None
        
        try:
            with open(processed_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read processed JD for {company_name}: {e}")
            return None
    
    def get_original_jd_text(self, company_name: str) -> Optional[str]:
        """
        Get original JD text for a company
        
        Args:
            company_name: Company name
            
        Returns:
            Original JD text if exists, None otherwise
        """
        original_path = self._get_original_jd_path(company_name)
        if not original_path:
            return None
        
        try:
            with open(original_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both {"text": "..."} and {"jd_text": "..."} formats
                return data.get('text') or data.get('jd_text') or ''
        except Exception as e:
            logger.error(f"Failed to read original JD for {company_name}: {e}")
            return None
    
    def processed_jd_to_text(self, processed_jd: Dict[str, Any]) -> str:
        """
        Convert processed JD (structured JSON) back to plain text for AI operations
        
        Args:
            processed_jd: Processed JD data with sections structure
            
        Returns:
            Plain text representation of the processed JD
        """
        sections = processed_jd.get('sections', {})
        if not sections:
            # Fallback: if no sections, try to get raw text
            return processed_jd.get('text', '')
        
        # Reconstruct text from sections
        text_parts = []
        
        # Standard section order for better readability
        section_order = [
            "ROLE OVERVIEW & CONTEXT",
            "KEY RESPONSIBILITIES",
            "TECHNICAL REQUIREMENTS",
            "EXPERIENCE REQUIREMENTS",
            "QUALIFICATIONS & EDUCATION",
            "SOFT SKILLS & COMPETENCIES",
            "DOMAIN KNOWLEDGE",
            "WORK ARRANGEMENT"
        ]
        
        # Add sections in order
        for section_name in section_order:
            if section_name in sections:
                content = sections[section_name]
                if isinstance(content, list):
                    # Check if items already have "- " prefix to avoid double dashes
                    formatted_items = []
                    for item in content:
                        if item:
                            # If item already starts with "- ", use it as-is; otherwise add "- "
                            if item.strip().startswith("- "):
                                formatted_items.append(item)
                            else:
                                formatted_items.append(f"- {item}")
                    text_parts.append(f"{section_name}\n" + "\n".join(formatted_items))
                elif isinstance(content, str):
                    text_parts.append(f"{section_name}\n{content}")
        
        # Add any additional sections not in standard order
        for section_name, content in sections.items():
            if section_name not in section_order:
                if isinstance(content, list):
                    # Check if items already have "- " prefix to avoid double dashes
                    formatted_items = []
                    for item in content:
                        if item:
                            # If item already starts with "- ", use it as-is; otherwise add "- "
                            if item.strip().startswith("- "):
                                formatted_items.append(item)
                            else:
                                formatted_items.append(f"- {item}")
                    text_parts.append(f"{section_name}\n" + "\n".join(formatted_items))
                elif isinstance(content, str):
                    text_parts.append(f"{section_name}\n{content}")
        
        return "\n\n".join(text_parts)
    
    def get_jd_text_for_ai(self, company_name: str, prefer_processed: bool = True) -> Optional[str]:
        """
        Get JD text optimized for AI operations (prefers processed JD)
        
        Args:
            company_name: Company name
            prefer_processed: If True, use processed JD if available; otherwise use original
            
        Returns:
            JD text optimized for AI, or None if no JD found
        """
        import time
        start_time = time.time()
        
        if prefer_processed:
            # Try processed JD first
            logger.debug(f"🔍 [JD_PROCESSING] Checking for processed JD: {company_name}")
            processed_jd = self.get_processed_jd(company_name)
            if processed_jd:
                processed_text = self.processed_jd_to_text(processed_jd)
                processing_mode = processed_jd.get('processing_mode', 'unknown')
                sections_count = len(processed_jd.get('sections', {}))
                load_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Calculate size reduction if original available for comparison
                size_reduction = ""
                try:
                    original_text = self.get_original_jd_text(company_name)
                    if original_text:
                        reduction_pct = round((1 - len(processed_text) / len(original_text)) * 100, 1) if len(original_text) > 0 else 0
                        size_reduction = f" | Reduction: {len(original_text)} → {len(processed_text)} chars ({reduction_pct}%)"
                except Exception:
                    pass
                
                logger.info(f"✅ [JD_PROCESSING] ✅ Using PROCESSED JD for {company_name} | "
                           f"Mode: {processing_mode} | Sections: {sections_count} | "
                           f"Length: {len(processed_text)} chars{size_reduction} | "
                           f"Load time: {load_time:.1f}ms")
                print(f"✅ [JD_PROCESSING] ✅ Using PROCESSED JD for {company_name} | "
                      f"Length: {len(processed_text)} chars{size_reduction}")
                return processed_text
            else:
                logger.debug(f"⚠️ [JD_PROCESSING] No processed JD found for {company_name}, trying original JD")
        
        # Fallback to original JD
        logger.debug(f"🔍 [JD_PROCESSING] Loading original JD: {company_name}")
        original_text = self.get_original_jd_text(company_name)
        if original_text:
            load_time = (time.time() - start_time) * 1000  # Convert to ms
            reason = 'prefer_processed=False' if not prefer_processed else 'processed JD not available'
            logger.info(f"📄 [JD_PROCESSING] ⚠️ Using LEGACY (original) JD for {company_name} | "
                       f"Length: {len(original_text)} chars | "
                       f"Reason: {reason} | "
                       f"Load time: {load_time:.1f}ms")
            print(f"📄 [JD_PROCESSING] ⚠️ Using LEGACY (original) JD for {company_name} | "
                  f"Length: {len(original_text)} chars | Reason: {reason}")
            return original_text
        
        logger.warning(f"❌ [JD_PROCESSING] No JD found (neither processed nor original) for {company_name}")
        return None
    
    def has_processed_jd(self, company_name: str) -> bool:
        """
        Check if processed JD exists for a company
        
        Args:
            company_name: Company name
            
        Returns:
            True if processed JD exists, False otherwise
        """
        return self._get_processed_jd_path(company_name) is not None
    
    async def process_jd_if_needed(
        self, 
        company_name: str, 
        jd_text: str,
        job_title: Optional[str] = None,
        job_url: Optional[str] = None,
        user: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process JD if not already processed using app's AI service
        
        Args:
            company_name: Company name
            jd_text: Original JD text
            job_title: Optional job title
            job_url: Optional job URL
            user: User object for AI service (required for API key access)
            
        Returns:
            Processed JD data if processing succeeds, None otherwise
        """
        logger.info(f"🔍 [JD_PROCESSING] ===== process_jd_if_needed ENTRY POINT =====")
        logger.info(f"🔍 [JD_PROCESSING] Company: {company_name}")
        logger.info(f"🔍 [JD_PROCESSING] JD length: {len(jd_text)} chars")
        logger.info(f"🔍 [JD_PROCESSING] User provided: {user is not None}")
        logger.info(f"🔍 [JD_PROCESSING] User email: {user.email if user else 'None'}")
        logger.info(f"🔍 [JD_PROCESSING] Job title: {job_title}")
        logger.info(f"🔍 [JD_PROCESSING] Job URL: {job_url}")
        logger.info(f"🔍 [JD_PROCESSING] Self user_email: {self.user_email}")
        logger.info(f"🔍 [JD_PROCESSING] Base path: {self.base_path}")
        
        # ⭐ Always create a new timestamped processed JD file
        # This ensures we always have a fresh processed JD, even if old ones exist
        logger.info(f"🔄 [JD_PROCESSING] Always creating new timestamped processed JD file (existing files won't block processing)")
        print(f"🔄 [JD_PROCESSING] Always creating new timestamped processed JD file (existing files won't block processing)")
        
        if not user:
            logger.warning(f"⚠️ [JD_PROCESSING] ❌ BLOCKER: No user provided for JD processing, skipping for {company_name}")
            return None
        
        if not jd_text or len(jd_text.strip()) == 0:
            logger.warning(f"⚠️ [JD_PROCESSING] ❌ BLOCKER: Empty JD text provided for {company_name}, skipping processing")
            logger.warning(f"⚠️ [JD_PROCESSING] JD text is None: {jd_text is None}")
            logger.warning(f"⚠️ [JD_PROCESSING] JD text length: {len(jd_text) if jd_text else 0}")
            return None
        
        try:
            logger.info(f"🔄 [JD_PROCESSING] ===== STARTING PROCESSING LOGIC =====")
            print(f"🔄 [JD_PROCESSING] ===== STARTING PROCESSING LOGIC =====")
            logger.info(f"🔄 [JD_PROCESSING] Company: {company_name}")
            print(f"🔄 [JD_PROCESSING] Company: {company_name}")
            logger.info(f"🔄 [JD_PROCESSING] Original JD length: {len(jd_text)} chars")
            print(f"🔄 [JD_PROCESSING] Original JD length: {len(jd_text)} chars")
            
            # Initialize AI service for user
            logger.info(f"🔧 [JD_PROCESSING] Initializing AI service for user: {user.email}")
            print(f"🔧 [JD_PROCESSING] Initializing AI service for user: {user.email}")
            try:
                ai_service.initialize_for_user(user)
                logger.info(f"✅ [JD_PROCESSING] AI service initialized successfully")
                print(f"✅ [JD_PROCESSING] AI service initialized successfully")
            except Exception as ai_init_err:
                logger.error(f"❌ [JD_PROCESSING] Failed to initialize AI service: {ai_init_err}")
                print(f"❌ [JD_PROCESSING] Failed to initialize AI service: {ai_init_err}")
                import traceback
                logger.error(f"❌ [JD_PROCESSING] AI init traceback: {traceback.format_exc()}")
                print(f"❌ [JD_PROCESSING] AI init traceback: {traceback.format_exc()}")
                raise
            
            # Process JD using the universal prompt
            logger.info(f"🔧 [JD_PROCESSING] Creating JDOptimizer instance...")
            optimizer = JDOptimizer(ai_service=ai_service)
            logger.info(f"✅ [JD_PROCESSING] JDOptimizer created | Using real AI: {optimizer.using_real_ai}")
            
            # Get actual AI provider name from ai_service (e.g., "openai", "anthropic", "deepseek")
            ai_provider_name = "unknown"
            if optimizer.using_real_ai:
                try:
                    current_provider = ai_service.get_current_provider()
                    if current_provider:
                        ai_provider_name = current_provider.provider_name
                        logger.info(f"🔍 [JD_PROCESSING] Using AI provider: {ai_provider_name}")
                        print(f"🔍 [JD_PROCESSING] Using AI provider: {ai_provider_name}")
                    else:
                        # Fallback to config provider name
                        provider_name = ai_service.config.get_current_provider()
                        if provider_name:
                            ai_provider_name = provider_name
                            logger.info(f"🔍 [JD_PROCESSING] Using AI provider from config: {ai_provider_name}")
                            print(f"🔍 [JD_PROCESSING] Using AI provider from config: {ai_provider_name}")
                except Exception as provider_err:
                    logger.warning(f"⚠️ [JD_PROCESSING] Could not get provider name: {provider_err}, using 'ai_service'")
                    print(f"⚠️ [JD_PROCESSING] Could not get provider name: {provider_err}, using 'ai_service'")
                    ai_provider_name = "ai_service"
            
            job_info = {
                "company_name": company_name,
                "job_title": job_title or "Unknown",
                "job_url": job_url,
                "user": user,  # Pass user for AI service
            }
            logger.info(f"📋 [JD_PROCESSING] Job info prepared: {list(job_info.keys())}")
            
            logger.info(f"🤖 [JD_PROCESSING] Calling universal_jd_processing for {company_name}...")
            print(f"🤖 [JD_PROCESSING] Calling universal_jd_processing for {company_name}...")
            logger.info(f"🤖 [JD_PROCESSING] JD text preview (first 200 chars): {jd_text[:200]}")
            print(f"🤖 [JD_PROCESSING] JD text preview (first 200 chars): {jd_text[:200]}")
            try:
                processed_data = await optimizer.universal_jd_processing(jd_text, job_info)
                logger.info(f"✅ [JD_PROCESSING] universal_jd_processing completed")
                print(f"✅ [JD_PROCESSING] universal_jd_processing completed")
                logger.info(f"📊 [JD_PROCESSING] Processed data type: {type(processed_data)}")
                logger.info(f"📊 [JD_PROCESSING] Processed data is None: {processed_data is None}")
                print(f"📊 [JD_PROCESSING] Processed data type: {type(processed_data)}")
                print(f"📊 [JD_PROCESSING] Processed data is None: {processed_data is None}")
            except Exception as processing_err:
                logger.error(f"❌ [JD_PROCESSING] Error in universal_jd_processing: {processing_err}")
                import traceback
                logger.error(f"❌ [JD_PROCESSING] Processing traceback: {traceback.format_exc()}")
                raise
            
            if not processed_data:
                logger.error(f"❌ [JD_PROCESSING] universal_jd_processing returned None for {company_name}")
                return None
            
            logger.info(f"📊 [JD_PROCESSING] Processed data keys: {list(processed_data.keys()) if isinstance(processed_data, dict) else 'N/A'}")
            
            # Save processed JD
            logger.info(f"📁 [JD_PROCESSING] Preparing to save processed JD...")
            company_dir = self.base_path / "applied_companies" / company_name
            logger.info(f"📁 [JD_PROCESSING] Company directory: {company_dir}")
            logger.info(f"📁 [JD_PROCESSING] Company directory exists: {company_dir.exists()}")
            logger.info(f"📁 [JD_PROCESSING] Creating company directory (parents=True, exist_ok=True)...")
            company_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 [JD_PROCESSING] Company directory created/verified: {company_dir.exists()}")
            logger.info(f"📁 [JD_PROCESSING] Directory writable: {os.access(company_dir, os.W_OK) if company_dir.exists() else False}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_file = company_dir / f"jd_processed_{timestamp}.json"
            logger.info(f"📁 [JD_PROCESSING] Target file: {processed_file}")
            logger.info(f"📁 [JD_PROCESSING] Target file absolute path: {processed_file.absolute()}")
            
            sections = processed_data.get("sections", {})
            additional_sections = processed_data.get("additional_sections", {})
            sections_count = len(sections) + len(additional_sections)
            
            # Create serializable payload with processed JD content (sections)
            # This is the processed JD file - contains only processed content, not job_info metadata
            # Use actual AI provider name (e.g., "openai", "anthropic", "deepseek") instead of generic "universal_ai"
            processing_mode = ai_provider_name if optimizer.using_real_ai else "mock_fallback"
            processed_payload = {
                "sections": sections,
                "additional_sections": additional_sections,
                "processing_mode": processing_mode,
                "processed_at": datetime.now().isoformat(),
            }
            
            # Calculate processed text length for stats
            processed_text = self.processed_jd_to_text(processed_payload)
            processed_payload["length_chars"] = len(processed_text)
            
            # Ensure file is written completely and atomically
            logger.info(f"💾 [JD_PROCESSING] Writing processed JD to file...")
            print(f"💾 [JD_PROCESSING] Writing processed JD to file...")
            logger.info(f"💾 [JD_PROCESSING] File path: {processed_file}")
            print(f"💾 [JD_PROCESSING] File path: {processed_file}")
            logger.info(f"💾 [JD_PROCESSING] Payload size: {len(json.dumps(processed_payload))} bytes")
            logger.info(f"💾 [JD_PROCESSING] Payload keys: {list(processed_payload.keys())}")
            print(f"💾 [JD_PROCESSING] Payload keys: {list(processed_payload.keys())}")
            try:
                with open(processed_file, "w", encoding="utf-8") as f:
                    logger.info(f"💾 [JD_PROCESSING] File handle opened, writing JSON...")
                    print(f"💾 [JD_PROCESSING] File handle opened, writing JSON...")
                    json.dump(processed_payload, f, ensure_ascii=False, indent=2)
                    logger.info(f"💾 [JD_PROCESSING] JSON written, flushing...")
                    print(f"💾 [JD_PROCESSING] JSON written, flushing...")
                    f.flush()  # Force write to disk
                    logger.info(f"💾 [JD_PROCESSING] Flushed, syncing to disk...")
                    print(f"💾 [JD_PROCESSING] Flushed, syncing to disk...")
                    os.fsync(f.fileno())  # Ensure data is written to disk
                    logger.info(f"💾 [JD_PROCESSING] File synced to disk")
                    print(f"💾 [JD_PROCESSING] File synced to disk")
                
                # Verify file was written
                if processed_file.exists():
                    file_size = processed_file.stat().st_size
                    logger.info(f"✅ [JD_PROCESSING] File written successfully: {processed_file}")
                    logger.info(f"✅ [JD_PROCESSING] File size: {file_size} bytes")
                    print(f"✅ [JD_PROCESSING] File written successfully: {processed_file}")
                    print(f"✅ [JD_PROCESSING] File size: {file_size} bytes")
                else:
                    logger.error(f"❌ [JD_PROCESSING] File does not exist after write: {processed_file}")
                    print(f"❌ [JD_PROCESSING] File does not exist after write: {processed_file}")
            except Exception as write_err:
                logger.error(f"❌ [JD_PROCESSING] Failed to write processed JD file: {write_err}")
                logger.error(f"❌ [JD_PROCESSING] Error type: {type(write_err).__name__}")
                import traceback
                logger.error(f"❌ [JD_PROCESSING] Write error traceback: {traceback.format_exc()}")
                raise
            
            # Calculate reduction (processed_text already calculated above)
            reduction = len(jd_text) - len(processed_text)
            reduction_pct = round((reduction / len(jd_text)) * 100, 1) if len(jd_text) > 0 else 0
            
            logger.info(f"✅ [JD_PROCESSING] JD processed successfully for {company_name} | "
                       f"File: {processed_file.name} | "
                       f"Mode: {processed_payload['processing_mode']} | "
                       f"Sections: {sections_count} | "
                       f"Reduction: {len(jd_text)} → {len(processed_text)} chars ({reduction_pct}%)")
            print(f"✅ [JD_PROCESSING] JD processed successfully for {company_name} | "
                  f"File: {processed_file.name} | "
                  f"Mode: {processed_payload['processing_mode']} | "
                  f"Sections: {sections_count} | "
                  f"Reduction: {len(jd_text)} → {len(processed_text)} chars ({reduction_pct}%)")
            
            return processed_payload
                
        except Exception as e:
            import traceback
            logger.error(f"❌ [JD_PROCESSING] ===== EXCEPTION IN process_jd_if_needed =====")
            logger.error(f"❌ [JD_PROCESSING] Company: {company_name}")
            logger.error(f"❌ [JD_PROCESSING] Error: {e}")
            logger.error(f"❌ [JD_PROCESSING] Error type: {type(e).__name__}")
            logger.error(f"❌ [JD_PROCESSING] Error message: {str(e)}")
            logger.error(f"❌ [JD_PROCESSING] Full traceback:")
            logger.error(traceback.format_exc())
            # Don't raise - allow fallback to original JD
            logger.error(f"❌ [JD_PROCESSING] Returning None (allowing fallback to original JD)")
            return None


# Convenience function
def get_jd_processing_service(user_email: str) -> JDProcessingService:
    """Get JD processing service for a user"""
    logger.info(f"🏭 [JD_PROCESSING_FACTORY] Creating JDProcessingService for user: {user_email}")
    try:
        service = JDProcessingService(user_email)
        logger.info(f"✅ [JD_PROCESSING_FACTORY] Service created successfully")
        return service
    except Exception as e:
        logger.error(f"❌ [JD_PROCESSING_FACTORY] Failed to create service: {e}")
        import traceback
        logger.error(f"❌ [JD_PROCESSING_FACTORY] Traceback: {traceback.format_exc()}")
        raise

