"""
Technical Depth Analyzer

Handles LLM-based technical depth analysis for ATS scoring.
"""

import json
import logging
import re
from typing import Dict, Any

from app.ai.ai_service import ai_service
from prompt.ats_technical_prompt import TECHNICAL_DEPTH_PROMPT
from .standardized_config import STANDARD_AI_PARAMS, validate_analysis_result

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Analyzes technical depth using centralized AI service."""

    def __init__(self):
        self.prompt_template = TECHNICAL_DEPTH_PROMPT

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
        
        logger.error("[TECHNICAL] Failed to parse LLM response. Raw: %s", raw_response[:400])
        raise ValueError("Technical analysis response not valid JSON")

    async def analyze(self, cv_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Analyze technical depth using LLM.
        
        Args:
            cv_text: CV content
            jd_text: Job description content
            
        Returns:
            Dict containing technical analysis results
        """
        prompt = self.prompt_template.format(
            cv_text=cv_text[:5000],
            jd_text=jd_text[:3000]
        )

        logger.info("[TECHNICAL] Requesting technical depth analysis...")
        try:
            response = await ai_service.generate_response(
                prompt=prompt, 
                temperature=STANDARD_AI_PARAMS["temperature"], 
                max_tokens=STANDARD_AI_PARAMS["max_tokens"],
                system_prompt=STANDARD_AI_PARAMS["system_prompt"]
            )
            
            result = self._parse_response(response.content.strip())
            
            # Validate required fields
            if "technical_analysis" not in result:
                raise ValueError("Missing technical_analysis in response")
            
            technical_analysis = result["technical_analysis"]
            if "technical_depth_score" not in technical_analysis:
                raise ValueError("Missing technical_depth_score in technical_analysis")
            
            score = float(technical_analysis["technical_depth_score"])
            if not 0 <= score <= 100:
                raise ValueError(f"Technical score {score} out of range [0, 100]")
            
            logger.info("[TECHNICAL] Analysis completed. Score: %.1f", score)
            return result
            
        except Exception as e:
            logger.error("[TECHNICAL] Analysis failed: %s", str(e))
            raise ValueError(f"Technical analysis failed: {str(e)}")
