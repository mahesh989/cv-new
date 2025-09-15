"""
Enhanced CV-JD Matcher with Robust JSON Parsing

Fixes the JSON parsing issues seen in the logs by implementing:
1. Better response format validation
2. Automatic JSON correction
3. Structured retry logic
4. Response format enforcement
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List
from app.ai.ai_service import ai_service

logger = logging.getLogger(__name__)


class EnhancedCVJDMatcher:
    """Enhanced CV-JD matching service with robust JSON handling"""
    
    def __init__(self):
        self.max_retries = 3
        self.temperature = 0.3  # Lower temperature for more consistent JSON
    
    def _create_strict_json_prompt(self, cv_text: str, jd_analysis: Dict[str, Any]) -> str:
        """Create a prompt that enforces strict JSON format"""
        required_keywords = jd_analysis.get("required_keywords", [])[:10]  # Limit for token efficiency
        preferred_keywords = jd_analysis.get("preferred_keywords", [])[:5]
        
        return f"""Analyze the CV against job requirements and return ONLY valid JSON.

CV Text:
{cv_text[:3000]}...

Required Keywords to Match: {required_keywords}
Preferred Keywords to Match: {preferred_keywords}

Return ONLY this JSON structure with NO additional text or comments:
{{
  "matched_required_keywords": ["keyword1", "keyword2"],
  "matched_preferred_keywords": ["keyword1"],
  "missed_required_keywords": ["keyword3", "keyword4"],
  "missed_preferred_keywords": ["keyword2"],
  "match_counts": {{
    "total_required_keywords": {len(required_keywords)},
    "total_preferred_keywords": {len(preferred_keywords)},
    "matched_required_count": 0,
    "matched_preferred_count": 0
  }},
  "matching_notes": {{
    "keyword1": "Brief explanation of match/miss"
  }}
}}

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown, no extra text
2. All strings in matching_notes must be properly quoted
3. No trailing commas
4. Use proper JSON boolean/number types"""
    
    def _fix_common_json_issues(self, response: str) -> str:
        """Fix common JSON formatting issues in AI responses"""
        try:
            # Remove markdown code blocks
            response = re.sub(r'```json\s*', '', response)
            response = re.sub(r'```\s*$', '', response)
            
            # Remove any text before first {
            first_brace = response.find('{')
            if first_brace > 0:
                response = response[first_brace:]
            
            # Remove any text after last }
            last_brace = response.rfind('}')
            if last_brace > 0:
                response = response[:last_brace + 1]
            
            # Fix common issues in matching_notes
            # Find matching_notes section and fix unquoted values
            notes_pattern = r'"matching_notes":\s*\{([^}]*)\}'
            match = re.search(notes_pattern, response, re.DOTALL)
            
            if match:
                notes_content = match.group(1)
                # Fix unquoted values like: "key": value -> "key": "value"
                fixed_notes = re.sub(
                    r'("[^"]+"):\s*([^",\n}]+)(?=\s*[,\n}])',
                    r'\1: "\2"',
                    notes_content
                )
                # Remove newlines and excessive spaces
                fixed_notes = re.sub(r'\n\s*', ' ', fixed_notes)
                fixed_notes = re.sub(r'\s+', ' ', fixed_notes)
                
                # Replace in original response
                response = re.sub(notes_pattern, f'"matching_notes": {{{fixed_notes}}}', response, flags=re.DOTALL)
            
            # Remove trailing commas
            response = re.sub(r',(\s*[}\]])', r'\1', response)
            
            return response.strip()
            
        except Exception as e:
            logger.warning(f"Error fixing JSON issues: {e}")
            return response
    
    def _validate_and_complete_response(self, response_data: Dict[str, Any], 
                                      required_keywords: List[str], 
                                      preferred_keywords: List[str]) -> Dict[str, Any]:
        """Validate and complete the response data"""
        
        # Ensure all required fields exist
        required_fields = [
            "matched_required_keywords", "matched_preferred_keywords",
            "missed_required_keywords", "missed_preferred_keywords",
            "match_counts", "matching_notes"
        ]
        
        for field in required_fields:
            if field not in response_data:
                response_data[field] = [] if field.endswith("keywords") else {}
        
        # Validate match_counts
        if "match_counts" not in response_data:
            response_data["match_counts"] = {}
            
        match_counts = response_data["match_counts"]
        
        # Calculate counts from keywords if missing
        matched_req = len(response_data.get("matched_required_keywords", []))
        matched_pref = len(response_data.get("matched_preferred_keywords", []))
        
        match_counts.update({
            "total_required_keywords": len(required_keywords),
            "total_preferred_keywords": len(preferred_keywords),
            "matched_required_count": matched_req,
            "matched_preferred_count": matched_pref
        })
        
        # Ensure matching_notes is a dict
        if not isinstance(response_data.get("matching_notes"), dict):
            response_data["matching_notes"] = {}
        
        return response_data
    
    async def match_cv_against_jd(self, cv_text: str, jd_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match CV against JD with robust error handling
        
        Args:
            cv_text: CV content
            jd_analysis: JD analysis containing required/preferred keywords
            
        Returns:
            Match results dictionary
        """
        required_keywords = jd_analysis.get("required_keywords", [])
        preferred_keywords = jd_analysis.get("preferred_keywords", [])
        
        logger.info(f"[ENHANCED_MATCHER] Starting CV-JD matching with {len(required_keywords)} required, {len(preferred_keywords)} preferred keywords")
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[ENHANCED_MATCHER] Attempt {attempt + 1}/{self.max_retries}")
                
                # Create strict JSON prompt
                prompt = self._create_strict_json_prompt(cv_text, jd_analysis)
                
                # Generate response with low temperature for consistency
                ai_response = await ai_service.generate_response(
                    prompt=prompt,
                    temperature=self.temperature,
                    max_tokens=2000  # Reduced token limit for focused response
                )
                
                response_text = ai_response.content.strip()
                logger.debug(f"[ENHANCED_MATCHER] Raw response: {response_text[:200]}...")
                
                # Fix common JSON issues
                fixed_response = self._fix_common_json_issues(response_text)
                logger.debug(f"[ENHANCED_MATCHER] Fixed response: {fixed_response[:200]}...")
                
                # Parse JSON
                try:
                    response_data = json.loads(fixed_response)
                except json.JSONDecodeError as json_error:
                    logger.warning(f"[ENHANCED_MATCHER] JSON parse failed on attempt {attempt + 1}: {json_error}")
                    logger.debug(f"[ENHANCED_MATCHER] Failed content: {fixed_response}")
                    last_error = json_error
                    continue
                
                # Validate and complete response
                validated_response = self._validate_and_complete_response(
                    response_data, required_keywords, preferred_keywords
                )
                
                matched_req_count = validated_response["match_counts"]["matched_required_count"]
                matched_pref_count = validated_response["match_counts"]["matched_preferred_count"]
                
                logger.info(f"[ENHANCED_MATCHER] ✅ Matching successful on attempt {attempt + 1}")
                logger.info(f"[ENHANCED_MATCHER] Results: {matched_req_count}/{len(required_keywords)} required, {matched_pref_count}/{len(preferred_keywords)} preferred")
                
                return validated_response
                
            except Exception as e:
                logger.error(f"[ENHANCED_MATCHER] Attempt {attempt + 1} failed: {e}")
                last_error = e
                continue
        
        # All attempts failed - create fallback response
        logger.error(f"[ENHANCED_MATCHER] ❌ All {self.max_retries} attempts failed. Last error: {last_error}")
        
        fallback_response = {
            "matched_required_keywords": [],
            "matched_preferred_keywords": [],
            "missed_required_keywords": required_keywords.copy(),
            "missed_preferred_keywords": preferred_keywords.copy(),
            "match_counts": {
                "total_required_keywords": len(required_keywords),
                "total_preferred_keywords": len(preferred_keywords),
                "matched_required_count": 0,
                "matched_preferred_count": 0
            },
            "matching_notes": {
                "error": f"Matching failed after {self.max_retries} attempts: {str(last_error)}"
            },
            "error": str(last_error)
        }
        
        logger.warning(f"[ENHANCED_MATCHER] Returning fallback response with 0 matches")
        return fallback_response


# Global instance
enhanced_cv_jd_matcher = EnhancedCVJDMatcher()