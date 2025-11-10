"""
Unified Experience, Seniority & Industry Fit Analyzer
Consolidates ExperienceAnalyzer + SeniorityAnalyzer + IndustryAnalyzer
"""

import json
import logging
import re
from typing import Dict, Any, Optional

from app.ai.ai_service import ai_service
from prompt.unified_experience_fit_prompt import UNIFIED_EXPERIENCE_FIT_PROMPT
from app.services.ats.components.standardized_config import STANDARD_AI_PARAMS

logger = logging.getLogger(__name__)


class ExperienceFitAnalyzer:
    """Unified analyzer for experience, seniority, and industry fit"""

    def __init__(self):
        self.prompt_template = UNIFIED_EXPERIENCE_FIT_PROMPT

    def _clean_llm_response(self, response: str) -> str:
        """Clean LLM response to extract JSON"""
        content = response.strip()
        content = re.sub(r"```(?:json)?\s*", "", content)
        content = re.sub(r"```\s*$", "", content)
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            return content[start : end + 1]
        return content

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response with fallback strategies"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(response[start:end])
            except Exception:
                pass
        logger.error("[EXP_FIT_ANALYZER] Failed to parse LLM response. Raw: %s", response[:400])
        raise ValueError("Unified experience & fit analysis JSON parsing failed")

    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure all required fields are present"""
        required_keys = [
            "experience_alignment",
            "role_similarity",
            "seniority_match",
            "leadership_readiness",
            "industry_transition_fit",
        ]
        for key in required_keys:
            if key not in result:
                logger.warning("[EXP_FIT_ANALYZER] Missing key: %s, adding default", key)
                result[key] = {"score": 50}
            score = result[key].get("score", 50)
            try:
                score_num = float(score)
            except Exception:
                score_num = 50.0
            result[key]["score"] = max(0.0, min(100.0, score_num))
        return result

    async def analyze(
        self,
        cv_text: str,
        jd_text: str,
        user_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze experience alignment, seniority match, and industry fit.
        """
        try:
            logger.info("[EXP_FIT_ANALYZER] Starting unified experience & fit analysis")
            cv_text_truncated = cv_text[:5000] if cv_text else ""
            jd_text_truncated = jd_text[:3000] if jd_text else ""

            formatted_prompt = self.prompt_template.format(cv_text=cv_text_truncated, jd_text=jd_text_truncated)

            # Build user identity for provider routing
            from app.models.auth import UserData
            from datetime import datetime, timezone

            current_user = UserData(
                id="pipeline_user",
                email=user_email or "pipeline@system.com",
                name=(user_email or "pipeline").split("@")[0],
                created_at=datetime.now(timezone.utc),
                is_active=True,
            )

            response = await ai_service.generate_response(
                prompt=formatted_prompt,
                user=current_user,
                temperature=STANDARD_AI_PARAMS["temperature"],
                max_tokens=STANDARD_AI_PARAMS["max_tokens"],
                system_prompt=STANDARD_AI_PARAMS["system_prompt"],
            )

            response_text = getattr(response, "content", "") or ""
            cleaned = self._clean_llm_response(response_text)
            parsed = self._parse_response(cleaned)
            validated = self._validate_result(parsed)
            logger.info("[EXP_FIT_ANALYZER] Analysis completed successfully")
            return validated
        except Exception as e:
            logger.error("[EXP_FIT_ANALYZER] Analysis failed: %s", str(e), exc_info=True)
            raise


