"""
Batched ATS Component Analyzer

Handles multiple ATS component analyses in a single LLM call for improved performance.
"""

import asyncio
import json
import logging
import re
from typing import Dict, Any, Optional

from app.ai.ai_service import ai_service
from .standardized_config import STANDARD_AI_PARAMS

logger = logging.getLogger(__name__)


class BatchedAnalyzer:
    """Analyzes multiple ATS components in a single LLM call for better performance."""

    def __init__(self):
        self.batch_1_prompt = self._get_batch_1_prompt()  # Skills + Experience
        self.batch_2_prompt = self._get_batch_2_prompt()  # Industry + Seniority + Technical

    def _get_batch_1_prompt(self) -> str:
        """Combined prompt for Skills Relevance and Experience Alignment analysis."""
        return """
You are an expert ATS (Applicant Tracking System) analyst. Analyze the CV and Job Description for Skills Relevance and Experience Alignment.

CV TEXT:
{cv_text}

JOB DESCRIPTION:
{jd_text}

MATCHED SKILLS:
{matched_skills}

Provide a comprehensive analysis in the following JSON format:

{{
  "skills_analysis": {{
    "skills_relevance_score": <score 0-100>,
    "matched_skills_analysis": "<detailed analysis of matched skills>",
    "missing_skills_analysis": "<analysis of missing critical skills>",
    "skills_gap_assessment": "<overall skills gap assessment>",
    "recommendations": "<specific recommendations for improvement>"
  }},
  "experience_analysis": {{
    "experience_alignment_score": <score 0-100>,
    "years_experience_match": "<analysis of years of experience match>",
    "role_progression_analysis": "<analysis of career progression>",
    "relevant_experience_highlights": "<key relevant experience points>",
    "experience_gaps": "<identified experience gaps>",
    "recommendations": "<recommendations for experience improvement>"
  }}
}}

Guidelines:
- Be thorough but concise in your analysis
- Focus on actionable insights
- Provide specific examples from the CV and JD
- Ensure scores are realistic and well-justified
"""

    def _get_batch_2_prompt(self) -> str:
        """Combined prompt for Industry Fit, Role Seniority, and Technical Depth analysis."""
        return """
You are an expert ATS (Applicant Tracking System) analyst. Analyze the CV and Job Description for Industry Fit, Role Seniority, and Technical Depth.

CV TEXT:
{cv_text}

JOB DESCRIPTION:
{jd_text}

Provide a comprehensive analysis in the following JSON format:

{{
  "industry_analysis": {{
    "industry_alignment_score": <score 0-100>,
    "industry_experience_match": "<analysis of industry experience>",
    "domain_knowledge_assessment": "<assessment of domain knowledge>",
    "industry_networking": "<analysis of industry connections/networking>",
    "recommendations": "<recommendations for industry alignment>"
  }},
  "seniority_analysis": {{
    "seniority_score": <score 0-100>,
    "leadership_experience": "<analysis of leadership experience>",
    "management_skills": "<assessment of management capabilities>",
    "strategic_thinking": "<evaluation of strategic thinking>",
    "team_leadership": "<analysis of team leadership>",
    "recommendations": "<recommendations for seniority development>"
  }},
  "technical_analysis": {{
    "technical_depth_score": <score 0-100>,
    "jd_problem_complexity": <complexity level 1-10>,
    "technical_expertise_match": "<analysis of technical expertise>",
    "problem_solving_approach": "<evaluation of problem-solving approach>",
    "innovation_capability": "<assessment of innovation capability>",
    "technical_recommendations": "<technical development recommendations>"
  }}
}}

Guidelines:
- Be thorough but concise in your analysis
- Focus on actionable insights
- Provide specific examples from the CV and JD
- Ensure scores are realistic and well-justified
- For jd_problem_complexity, rate 1-10 based on technical complexity of the role
"""

    def _clean_llm_response(self, content: str) -> str:
        """Conservative cleaner: strip code fences and slice to outermost braces only."""
        content = content.strip()
        content = re.sub(r"```(?:json)?\s*", "", content)
        content = re.sub(r"```\s*$", "", content)
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            return content
        
        return content[start_idx:end_idx + 1]

    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response with robust error handling."""
        try:
            cleaned_content = self._clean_llm_response(content)
            return json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            logger.error(f"[BATCHED] JSON parsing failed: {e}")
            logger.error(f"[BATCHED] Content: {content[:500]}...")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")

    async def analyze_batch_1(self, cv_text: str, jd_text: str, matched_skills: str) -> Dict[str, Any]:
        """Analyze Skills Relevance and Experience Alignment in a single call."""
        logger.info("[BATCHED] Requesting batch 1 analysis (Skills + Experience)...")
        
        try:
            prompt = self.batch_1_prompt.format(
                cv_text=cv_text,
                jd_text=jd_text,
                matched_skills=matched_skills
            )
            
            response = await ai_service.generate_response(
                prompt=prompt,
                system_prompt=STANDARD_AI_PARAMS["system_prompt"],
                temperature=STANDARD_AI_PARAMS["temperature"],
                max_tokens=STANDARD_AI_PARAMS["max_tokens"]
            )
            
            result = self._parse_llm_response(response.content)
            
            # Extract scores for logging
            skills_score = result.get("skills_analysis", {}).get("skills_relevance_score", 0)
            experience_score = result.get("experience_analysis", {}).get("experience_alignment_score", 0)
            
            logger.info(f"[BATCHED] Batch 1 analysis completed. Skills: {skills_score}, Experience: {experience_score}")
            return result
            
        except Exception as e:
            logger.error(f"[BATCHED] Batch 1 analysis failed: {e}")
            raise ValueError(f"Batch 1 analysis failed: {str(e)}")

    async def analyze_batch_2(self, cv_text: str, jd_text: str) -> Dict[str, Any]:
        """Analyze Industry Fit, Role Seniority, and Technical Depth in a single call."""
        logger.info("[BATCHED] Requesting batch 2 analysis (Industry + Seniority + Technical)...")
        
        try:
            prompt = self.batch_2_prompt.format(
                cv_text=cv_text,
                jd_text=jd_text
            )
            
            response = await ai_service.generate_response(
                prompt=prompt,
                system_prompt=STANDARD_AI_PARAMS["system_prompt"],
                temperature=STANDARD_AI_PARAMS["temperature"],
                max_tokens=STANDARD_AI_PARAMS["max_tokens"]
            )
            
            result = self._parse_llm_response(response.content)
            
            # Extract scores for logging
            industry_score = result.get("industry_analysis", {}).get("industry_alignment_score", 0)
            seniority_score = result.get("seniority_analysis", {}).get("seniority_score", 0)
            technical_score = result.get("technical_analysis", {}).get("technical_depth_score", 0)
            
            logger.info(f"[BATCHED] Batch 2 analysis completed. Industry: {industry_score}, Seniority: {seniority_score}, Technical: {technical_score}")
            return result
            
        except Exception as e:
            logger.error(f"[BATCHED] Batch 2 analysis failed: {e}")
            raise ValueError(f"Batch 2 analysis failed: {str(e)}")

    async def analyze_all_batched(self, cv_text: str, jd_text: str, matched_skills: str) -> Dict[str, Any]:
        """Analyze all components using batched approach (2 LLM calls instead of 5)."""
        logger.info("[BATCHED] Starting batched analysis (2 calls instead of 5)...")
        
        try:
            # Run both batches in parallel
            batch_1_task = self.analyze_batch_1(cv_text, jd_text, matched_skills)
            batch_2_task = self.analyze_batch_2(cv_text, jd_text)
            
            batch_1_result, batch_2_result = await asyncio.gather(
                batch_1_task, batch_2_task, return_exceptions=True
            )
            
            # Check for exceptions
            if isinstance(batch_1_result, Exception):
                raise batch_1_result
            if isinstance(batch_2_result, Exception):
                raise batch_2_result
            
            # Combine results
            combined_result = {
                "skills": batch_1_result,
                "experience": batch_1_result,
                "industry": batch_2_result,
                "seniority": batch_2_result,
                "technical": batch_2_result
            }
            
            logger.info("[BATCHED] All batched analyses completed successfully")
            return combined_result
            
        except Exception as e:
            logger.error(f"[BATCHED] Batched analysis failed: {e}")
            raise ValueError(f"Batched analysis failed: {str(e)}")
