"""
Unified Technical & Skills Analyzer

Consolidates TechnicalAnalyzer + SkillsAnalyzer into single comprehensive analysis
"""

import json
import logging
import re
from typing import Dict, Any, Optional

from app.ai.ai_service import ai_service
from prompt.unified_technical_skills_prompt import UNIFIED_TECHNICAL_SKILLS_PROMPT
from .standardized_config import STANDARD_AI_PARAMS

logger = logging.getLogger(__name__)


class TechnicalSkillsAnalyzer:
    """Unified analyzer for technical depth and skills relevance"""

    def __init__(self):
        self.prompt_template = UNIFIED_TECHNICAL_SKILLS_PROMPT

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
        
        logger.error("[TECH_SKILLS_ANALYZER] Failed to parse LLM response. Raw: %s", raw_response[:400])
        raise ValueError("Technical & Skills analysis response not valid JSON")

    async def analyze(
        self,
        cv_text: str,
        jd_text: str,
        matched_skills: str,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze technical capability and skills relevance.

        Args:
            cv_text: CV content (limited to 5000 chars)
            jd_text: Job description (limited to 3000 chars)
            matched_skills: Pre-matched skills from keyword analysis
            user_email: User email for API key context
            
        Returns:
            Dict containing technical & skills analysis results
        """
        prompt = self.prompt_template.format(
            cv_text=cv_text[:5000],
            jd_text=jd_text[:3000],
            matched_skills=matched_skills
        )

        logger.info("[TECH_SKILLS_ANALYZER] Requesting unified technical & skills analysis...")
        try:
            # Create user object from user_email
            from app.models.auth import UserData
            from datetime import datetime, timezone
            current_user = UserData(
                id="pipeline_user",
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
            validated_result = self._validate_result(result)
            
            logger.info("[TECH_SKILLS_ANALYZER] Analysis completed successfully")
            return validated_result
            
        except Exception as e:
            logger.error("[TECH_SKILLS_ANALYZER] Analysis failed: %s", str(e))
            raise ValueError(f"Technical & Skills analysis failed: {str(e)}")

    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure all required fields are present"""
        required_keys = [
            "technical_depth",
            "required_skills_coverage",
            "tech_stack_similarity",
            "business_readiness",
            "complexity_handling",
            "learning_adaptation"
        ]
        
        for key in required_keys:
            if key not in result:
                logger.warning(f"[TECH_SKILLS_ANALYZER] Missing key: {key}, adding default")
                result[key] = {
                    "score": 50,
                    "evidence": [],
                    "gaps": ["Analysis incomplete"],
                    "reasoning": "Default value due to parsing error"
                }
            
            # Validate score is present and in range
            if "score" not in result[key]:
                result[key]["score"] = 50
            
            # Ensure score is 0-100
            score = result[key]["score"]
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                logger.warning(f"[TECH_SKILLS_ANALYZER] Invalid score for {key}: {score}, capping to 0-100")
                result[key]["score"] = max(0, min(100, float(score)))
        
        return result

