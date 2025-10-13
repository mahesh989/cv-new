"""
Skills Relevance Analyzer

Handles LLM-based skills relevance analysis for ATS scoring.
"""

import json
import logging
import re
from typing import Dict, Any, Optional

from app.ai.ai_service import ai_service
from prompt.ats_skills_relevance_prompt import SKILLS_RELEVANCE_PROMPT
from .standardized_config import STANDARD_AI_PARAMS, validate_analysis_result

logger = logging.getLogger(__name__)


class SkillsAnalyzer:
    """Analyzes skills relevance using centralized AI service."""

    def __init__(self):
        self.prompt_template = SKILLS_RELEVANCE_PROMPT

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
        logger.info("[SKILLS] Raw response length: %d", len(raw_response))
        logger.info("[SKILLS] Raw response preview: %s", raw_response[:200])
        
        cleaned = self._clean_llm_response(raw_response)
        logger.info("[SKILLS] Cleaned response: %s", cleaned[:200])
        
        # Strategy 1: direct parse
        try:
            result = json.loads(cleaned)
            logger.info("[SKILLS] Direct parse successful")
            return result
        except json.JSONDecodeError as e:
            logger.warning("[SKILLS] Direct parse failed: %s", str(e))
        
        # Strategy 2: extract first balanced object
        objs = self._extract_json_objects(raw_response)
        logger.info("[SKILLS] Found %d JSON objects", len(objs))
        for i, obj in enumerate(objs):
            try:
                result = json.loads(obj)
                logger.info("[SKILLS] Object %d parse successful", i)
                return result
            except json.JSONDecodeError as e:
                logger.warning("[SKILLS] Object %d parse failed: %s", i, str(e))
                continue
        
        # Strategy 3: wrap key-value if missing outer braces
        m = re.search(r'("[\w_]+"\s*:\s*\{[\s\S]*\})', raw_response)
        if m:
            candidate = '{' + m.group(1) + '}'
            try:
                result = json.loads(candidate)
                logger.info("[SKILLS] Wrapped parse successful")
                return result
            except json.JSONDecodeError as e:
                logger.warning("[SKILLS] Wrapped parse failed: %s", str(e))
        
        # Strategy 4: Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw_response)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                logger.info("[SKILLS] Markdown extraction successful")
                return result
            except json.JSONDecodeError as e:
                logger.warning("[SKILLS] Markdown extraction failed: %s", str(e))
        
        # Strategy 5: Try to find any JSON-like structure
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, raw_response, re.DOTALL)
        for i, match in enumerate(matches):
            try:
                result = json.loads(match)
                logger.info("[SKILLS] Pattern match %d successful", i)
                return result
            except json.JSONDecodeError:
                continue
        
        # Strategy 6: Provide fallback response if all parsing fails
        logger.warning("[SKILLS] All parsing strategies failed, providing fallback response")
        logger.error("[SKILLS] Raw response: %s", raw_response[:800])
        
        # Create a fallback response with reasonable defaults
        fallback_response = {
            "skills_analysis": [],
            "overall_skills_score": 50.0,  # Neutral score
            "corporate_skills_strength": "Unable to analyze due to response format",
            "academic_skills_discount": "Analysis failed",
            "business_readiness_score": 50.0,
            "skill_development_timeline": "Unknown",
            "strength_areas": ["Analysis failed"],
            "critical_gaps": ["Unable to determine"],
            "training_investment_needed": ["Analysis failed"],
            "immediate_value_skills": ["Unable to determine"],
            "risky_transition_skills": ["Unable to determine"],
            "parsing_error": True,
            "raw_response_preview": raw_response[:200]
        }
        
        logger.warning("[SKILLS] Using fallback response due to parsing failure")
        return fallback_response

    async def analyze(self, cv_text: str, jd_text: str, matched_skills: str, user_email: str = None) -> Dict[str, Any]:
        """
        Analyze skills relevance using LLM.
        
        Args:
            cv_text: CV content
            jd_text: Job description content
            matched_skills: JSON string of matched skills
            user_email: User email for API key context
            
        Returns:
            Dict containing skills analysis results
        """
        prompt = self.prompt_template.format(
            cv_text=cv_text[:5000],  # Limit to avoid token overflow
            jd_text=jd_text[:3000],
            matched_skills=matched_skills
        )

        logger.info("[SKILLS] Requesting skills relevance analysis...")
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
            if "overall_skills_score" not in result:
                raise ValueError("Missing overall_skills_score in response")
            
            score = float(result["overall_skills_score"])
            if not 0 <= score <= 100:
                raise ValueError(f"Skills score {score} out of range [0, 100]")
            
            logger.info("[SKILLS] Analysis completed. Score: %.1f", score)
            return result
            
        except Exception as e:
            logger.error("[SKILLS] Analysis failed: %s", str(e))
            # Provide a fallback response instead of raising an error
            fallback_response = {
                "skills_analysis": [],
                "overall_skills_score": 50.0,
                "corporate_skills_strength": "Analysis failed due to error",
                "academic_skills_discount": "Analysis failed",
                "business_readiness_score": 50.0,
                "skill_development_timeline": "Unknown",
                "strength_areas": ["Analysis failed"],
                "critical_gaps": ["Unable to determine"],
                "training_investment_needed": ["Analysis failed"],
                "immediate_value_skills": ["Unable to determine"],
                "risky_transition_skills": ["Unable to determine"],
                "analysis_error": True,
                "error_message": str(e)
            }
            logger.warning("[SKILLS] Returning fallback response due to analysis error")
            return fallback_response
