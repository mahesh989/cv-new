"""
Role Seniority Analyzer

Handles LLM-based role seniority analysis for ATS scoring.
"""

import json
import logging
import re
from typing import Dict, Any

from app.ai.ai_service import ai_service
from app.prompt.ats_seniority_prompt import ROLE_SENIORITY_PROMPT
from .standardized_config import STANDARD_AI_PARAMS, validate_analysis_result

logger = logging.getLogger(__name__)


class SeniorityAnalyzer:
    """Analyzes role seniority using centralized AI service."""

    def __init__(self):
        self.prompt_template = ROLE_SENIORITY_PROMPT

    def _clean_llm_response(self, content: str) -> str:
        """Conservative cleaner: strip code fences and slice to outermost braces only."""
        content = content.strip()
        content = re.sub(r"```(?:json)?\s*", "", content)
        content = re.sub(r"```\s*$", "", content)
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return content[start_idx:end_idx + 1]
        return content

    def _extract_json_objects(self, content: str) -> list:
        """Extract JSON object strings from arbitrary text by brace balancing."""
        objs = []
        depth = 0
        start = None
        for i, ch in enumerate(content):
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start is not None:
                        objs.append(content[start:i+1])
                        start = None
        return objs

    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse LLM response with multiple fallback strategies."""
        cleaned = self._clean_llm_response(raw_response)
        
        # Strategy 1: direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: extract first balanced object
        objs = self._extract_json_objects(raw_response)
        for obj in objs:
            try:
                return json.loads(obj)
            except json.JSONDecodeError:
                continue
        
        # Strategy 3: wrap key-value if missing outer braces
        m = re.search(r'("[\w_]+"\s*:\s*\{[\s\S]*\})', raw_response)
        if m:
            candidate = '{' + m.group(1) + '}'
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        logger.error("[SENIORITY] Failed to parse LLM response. Raw: %s", raw_response[:400])
        raise ValueError("Seniority analysis response not valid JSON")

    async def analyze(self, cv_text: str, jd_text: str, user_email: str = None) -> Dict[str, Any]:
        """
        Analyze role seniority using LLM.
        
        Args:
            cv_text: CV content
            jd_text: Job description content
            user_email: User email for API key context
            
        Returns:
            Dict containing seniority analysis results
        """
        # Validate CV content first
        from app.services.cv_content_validator import cv_content_validator
        validation_result = cv_content_validator.validate_cv_content(cv_text)
        
        # Add content constraints to prompt
        constraints = validation_result.get('analysis_constraints', {})
        max_seniority = constraints.get('max_seniority_score', 100)
        requires_evidence = constraints.get('requires_explicit_evidence', True)
        
        # Modify prompt with constraints
        constrained_prompt = self.prompt_template.format(
            cv_text=cv_text[:5000],
            jd_text=jd_text[:3000]
        )
        
        # Add constraint instructions
        constraint_instructions = f"""
        
## CONTENT VALIDATION CONSTRAINTS:
- Maximum seniority score: {max_seniority}/100
- Requires explicit evidence: {requires_evidence}
- CV content length: {len(cv_text)} characters
- Available sections: {validation_result.get('available_sections', [])}
- Experience years: {validation_result.get('experience_info', {}).get('explicit_years', 0)}

## MANDATORY SCORING LIMITS:
- If CV lacks experience details, seniority_score MUST be ≤ {max_seniority}
- If CV lacks leadership evidence, leadership scores MUST be ≤ 20
- If CV lacks management experience, management scores MUST be ≤ 15
- DO NOT exceed these limits regardless of assumptions
"""
        
        prompt = constrained_prompt + constraint_instructions

        logger.info("[SENIORITY] Requesting role seniority analysis...")
        try:
            # Create user object from user_email
            from app.models.auth import UserData
            from datetime import datetime, timezone
            current_user = UserData(
                id="pipeline_user",  # Use a placeholder ID for pipeline operations
                email=user_email or "pipeline@system.com",
                name=(user_email or "pipeline").split("@")[0],
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            response = await ai_service.generate_response(
                prompt=prompt, 
                user=current_user,
                temperature=STANDARD_AI_PARAMS["temperature"], 
                max_tokens=STANDARD_AI_PARAMS["max_tokens"],
                system_prompt=STANDARD_AI_PARAMS["system_prompt"]
            )
            
            result = self._parse_response(response.content.strip())
            
            # Validate required fields
            if "seniority_analysis" not in result:
                raise ValueError("Missing seniority_analysis in response")
            
            seniority_analysis = result["seniority_analysis"]
            if "seniority_score" not in seniority_analysis:
                raise ValueError("Missing seniority_score in seniority_analysis")
            
            score = float(seniority_analysis["seniority_score"])
            if not 0 <= score <= 100:
                raise ValueError(f"Seniority score {score} out of range [0, 100]")
            
            logger.info("[SENIORITY] Analysis completed. Score: %.1f", score)
            return result
            
        except Exception as e:
            logger.error("[SENIORITY] Analysis failed: %s", str(e))
            raise ValueError(f"Seniority analysis failed: {str(e)}")
