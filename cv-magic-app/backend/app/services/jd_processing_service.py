"""
JD Processing Service

This service integrates the universal JD processing pipeline into the main application.
It processes job descriptions into structured JSON format and provides utilities
to convert processed JDs back to text when needed for AI operations.
"""

import json
import logging
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
        self.user_email = user_email
        self.base_path = get_user_base_path(user_email)
    
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
                    text_parts.append(f"{section_name}\n" + "\n".join(f"- {item}" if item else "" for item in content))
                elif isinstance(content, str):
                    text_parts.append(f"{section_name}\n{content}")
        
        # Add any additional sections not in standard order
        for section_name, content in sections.items():
            if section_name not in section_order:
                if isinstance(content, list):
                    text_parts.append(f"{section_name}\n" + "\n".join(f"- {item}" if item else "" for item in content))
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
        if prefer_processed:
            # Try processed JD first
            logger.debug(f"🔍 [JD_PROCESSING] Checking for processed JD: {company_name}")
            processed_jd = self.get_processed_jd(company_name)
            if processed_jd:
                processed_text = self.processed_jd_to_text(processed_jd)
                processing_mode = processed_jd.get('processing_mode', 'unknown')
                sections_count = len(processed_jd.get('sections', {}))
                logger.info(f"✅ [JD_PROCESSING] Using PROCESSED JD for {company_name} | "
                           f"Mode: {processing_mode} | Sections: {sections_count} | "
                           f"Length: {len(processed_text)} chars")
                return processed_text
            else:
                logger.debug(f"⚠️ [JD_PROCESSING] No processed JD found for {company_name}, trying original JD")
        
        # Fallback to original JD
        logger.debug(f"🔍 [JD_PROCESSING] Loading original JD: {company_name}")
        original_text = self.get_original_jd_text(company_name)
        if original_text:
            logger.info(f"📄 [JD_PROCESSING] Using LEGACY (original) JD for {company_name} | "
                       f"Length: {len(original_text)} chars | "
                       f"Reason: {'prefer_processed=False' if not prefer_processed else 'processed JD not available'}")
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
        logger.info(f"🔍 [JD_PROCESSING] process_jd_if_needed called for {company_name} | "
                   f"JD length: {len(jd_text)} chars | User: {user.email if user else 'None'}")
        
        # Check if already processed
        if self.has_processed_jd(company_name):
            logger.info(f"♻️ [JD_PROCESSING] Processed JD already exists for {company_name}, skipping processing")
            return self.get_processed_jd(company_name)
        
        if not user:
            logger.warning(f"⚠️ [JD_PROCESSING] No user provided for JD processing, skipping for {company_name}")
            return None
        
        if not jd_text or len(jd_text.strip()) == 0:
            logger.warning(f"⚠️ [JD_PROCESSING] Empty JD text provided for {company_name}, skipping processing")
            return None
        
        try:
            logger.info(f"🔄 [JD_PROCESSING] Starting JD processing for {company_name} | "
                       f"Original length: {len(jd_text)} chars")
            
            # Initialize AI service for user
            ai_service.initialize_for_user(user)
            logger.debug(f"🔧 [JD_PROCESSING] AI service initialized for user: {user.email}")
            
            # Process JD using the universal prompt
            optimizer = JDOptimizer(ai_service=ai_service)
            
            job_info = {
                "company_name": company_name,
                "job_title": job_title or "Unknown",
                "job_url": job_url,
                "user": user,  # Pass user for AI service
            }
            
            logger.info(f"🤖 [JD_PROCESSING] Calling universal_jd_processing for {company_name}...")
            processed_data = await optimizer.universal_jd_processing(jd_text, job_info)
            
            if not processed_data:
                logger.error(f"❌ [JD_PROCESSING] universal_jd_processing returned None for {company_name}")
                return None
            
            # Save processed JD
            company_dir = self.base_path / "applied_companies" / company_name
            company_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_file = company_dir / f"jd_processed_{timestamp}.json"
            
            sections = processed_data.get("sections", {})
            additional_sections = processed_data.get("additional_sections", {})
            sections_count = len(sections) + len(additional_sections)
            
            # Create serializable payload (exclude user object which can't be JSON serialized)
            processed_payload = {
                "company_name": job_info.get("company_name"),
                "job_title": job_info.get("job_title"),
                "job_url": job_info.get("job_url"),
                "length_chars": len(jd_text),
                "processing_mode": "universal_ai" if optimizer.using_real_ai else "mock_fallback",
                "sections": sections,
                "additional_sections": additional_sections,
                "processed_at": datetime.now().isoformat(),
            }
            
            with open(processed_file, "w", encoding="utf-8") as f:
                json.dump(processed_payload, f, ensure_ascii=False, indent=2)
            
            # Calculate reduction
            processed_text = self.processed_jd_to_text(processed_payload)
            reduction = len(jd_text) - len(processed_text)
            reduction_pct = round((reduction / len(jd_text)) * 100, 1) if len(jd_text) > 0 else 0
            
            logger.info(f"✅ [JD_PROCESSING] JD processed successfully for {company_name} | "
                       f"File: {processed_file.name} | "
                       f"Mode: {processed_payload['processing_mode']} | "
                       f"Sections: {sections_count} | "
                       f"Reduction: {len(jd_text)} → {len(processed_text)} chars ({reduction_pct}%)")
            
            return processed_payload
                
        except Exception as e:
            import traceback
            logger.error(f"❌ [JD_PROCESSING] Failed to process JD for {company_name}: {e}")
            logger.error(f"❌ [JD_PROCESSING] Traceback: {traceback.format_exc()}")
            # Don't raise - allow fallback to original JD
            return None


# Convenience function
def get_jd_processing_service(user_email: str) -> JDProcessingService:
    """Get JD processing service for a user"""
    return JDProcessingService(user_email)

