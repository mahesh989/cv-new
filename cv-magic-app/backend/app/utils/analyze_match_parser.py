"""
Utility module for parsing analyze match decisions from AI responses

This module provides functions to extract structured decision data
from analyze match AI responses, supporting the cost-saving workflow
where expensive analysis steps are skipped if the match is poor.
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def parse_analyze_match_decision(content: str) -> Dict[str, Any]:
    """
    Parse analyze match decision from AI response content
    
    Expected format:
    DECISION: [PROCEED / MAYBE / DONT_PROCEED]
    CONFIDENCE: [0-100]
    MATCH_SCORE: [0-100]
    PRIMARY_REASON: [One clear sentence]
    CRITICAL_MISSING: [List skills that are deal-breakers, or "None"]
    IMPLICIT_LIKELY: [Skills CV probably has but didn't mention, or "None"]
    LEARNABLE_GAPS: [Adjacent skills that could be highlighted, or "None"]
    BLOCKER_FOUND: [Yes/No - if yes, specify which blocker]
    
    Args:
        content: Raw AI response content from analyze match prompt
        
    Returns:
        Dictionary with parsed decision data:
        {
            "decision": "PROCEED" | "MAYBE" | "DONT_PROCEED" | "UNKNOWN",
            "confidence": int (0-100),
            "match_score": int (0-100),
            "primary_reason": str,
            "critical_missing": List[str],
            "implicit_likely": List[str],
            "learnable_gaps": List[str],
            "blocker_found": bool,
            "should_proceed": bool,  # True if decision is PROCEED or MAYBE
            "raw_content": str  # Original content for reference
        }
    """
    if not content or not content.strip():
        return _default_decision()
    
    # Initialize with defaults
    decision_data = {
        "decision": "UNKNOWN",
        "confidence": 0,
        "match_score": 0,
        "primary_reason": "",
        "critical_missing": [],
        "implicit_likely": [],
        "learnable_gaps": [],
        "blocker_found": False,
        "should_proceed": False,
        "raw_content": content
    }
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        if line.startswith("DECISION:"):
            decision = line.split(":", 1)[1].strip().upper()
            decision_data["decision"] = decision
            # Determine if should proceed based on decision
            decision_data["should_proceed"] = decision in ["PROCEED", "MAYBE"]
            
        elif line.startswith("CONFIDENCE:"):
            try:
                decision_data["confidence"] = int(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
                
        elif line.startswith("MATCH_SCORE:"):
            try:
                decision_data["match_score"] = int(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
                
        elif line.startswith("PRIMARY_REASON:"):
            decision_data["primary_reason"] = line.split(":", 1)[1].strip()
            
        elif line.startswith("CRITICAL_MISSING:"):
            missing = line.split(":", 1)[1].strip()
            if missing and missing.lower() != "none":
                # Handle comma-separated or newline-separated lists
                if "," in missing:
                    decision_data["critical_missing"] = [m.strip() for m in missing.split(",")]
                else:
                    decision_data["critical_missing"] = [missing]
                    
        elif line.startswith("IMPLICIT_LIKELY:"):
            implicit = line.split(":", 1)[1].strip()
            if implicit and implicit.lower() != "none":
                if "," in implicit:
                    decision_data["implicit_likely"] = [i.strip() for i in implicit.split(",")]
                else:
                    decision_data["implicit_likely"] = [implicit]
                    
        elif line.startswith("LEARNABLE_GAPS:"):
            gaps = line.split(":", 1)[1].strip()
            if gaps and gaps.lower() != "none":
                if "," in gaps:
                    decision_data["learnable_gaps"] = [g.strip() for g in gaps.split(",")]
                else:
                    decision_data["learnable_gaps"] = [gaps]
                    
        elif line.startswith("BLOCKER_FOUND:"):
            blocker = line.split(":", 1)[1].strip()
            decision_data["blocker_found"] = blocker.lower() in ["yes", "true", "y"]
            
        elif line.startswith("---") or line.startswith("DETAILED_ANALYSIS:"):
            # Stop at detailed analysis section (we don't need verbose paragraphs)
            break
    
    # Fallback: Try to extract decision from content if not found explicitly
    if decision_data["decision"] == "UNKNOWN":
        decision_match = re.search(r'DECISION:\s*(PROCEED|MAYBE|DONT_PROCEED)', content, re.IGNORECASE)
        if decision_match:
            decision = decision_match.group(1).upper()
            decision_data["decision"] = decision
            decision_data["should_proceed"] = decision in ["PROCEED", "MAYBE"]
    
    logger.info(f"📊 [ANALYZE_MATCH_PARSER] Parsed decision: {decision_data['decision']}, "
                f"should_proceed: {decision_data['should_proceed']}, "
                f"match_score: {decision_data['match_score']}")
    
    return decision_data


def _default_decision() -> Dict[str, Any]:
    """Return default decision structure when parsing fails"""
    return {
        "decision": "UNKNOWN",
        "confidence": 0,
        "match_score": 0,
        "primary_reason": "Unable to parse analyze match response",
        "critical_missing": [],
        "implicit_likely": [],
        "learnable_gaps": [],
        "blocker_found": False,
        "should_proceed": False,
        "raw_content": ""
    }


def should_proceed_with_full_analysis(decision_data: Dict[str, Any]) -> bool:
    """
    Determine if full analysis should proceed based on decision data
    
    Args:
        decision_data: Parsed decision data from parse_analyze_match_decision()
        
    Returns:
        True if analysis should continue, False otherwise
    """
    decision = decision_data.get("decision", "UNKNOWN").upper()
    
    # Explicit decisions
    if decision == "PROCEED":
        return True
    elif decision == "DONT_PROCEED":
        return False
    elif decision == "MAYBE":
        # For MAYBE, check match score and confidence
        match_score = decision_data.get("match_score", 0)
        confidence = decision_data.get("confidence", 0)
        # Proceed if match score >= 60 and confidence >= 50
        return match_score >= 60 and confidence >= 50
    
    # Unknown decision - check match score as fallback
    match_score = decision_data.get("match_score", 0)
    return match_score >= 75

