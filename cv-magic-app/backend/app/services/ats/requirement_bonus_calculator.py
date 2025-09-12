"""
Requirement Bonus Calculator

Implements the requirement bonus rules for ATS scoring based on required and
preferred keyword matches. This module performs pure computation with input
validation and returns a detailed breakdown suitable for logging and JSON
appends.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class RequirementBonusCalculator:
    """Calculate bonus points from required and preferred keyword matching."""

    def calculate(self, match_counts: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate requirement bonus from match counts.

        Args:
            match_counts: Dict with keys:
                - total_required_keywords: int
                - total_preferred_keywords: int
                - matched_required_count: int
                - matched_preferred_count: int

        Returns:
            Dict with match_counts (including missing counts), bonus_breakdown,
            and coverage metrics.

        Raises:
            ValueError: on invalid inputs (missing keys or negative values).
        """
        required_total = match_counts.get("total_required_keywords")
        preferred_total = match_counts.get("total_preferred_keywords")
        matched_required = match_counts.get("matched_required_count")
        matched_preferred = match_counts.get("matched_preferred_count")

        # Validate presence
        missing_keys = [
            k for k in [
                "total_required_keywords",
                "total_preferred_keywords",
                "matched_required_count",
                "matched_preferred_count",
            ]
            if k not in match_counts
        ]
        if missing_keys:
            raise ValueError(f"Missing keys in match_counts: {missing_keys}")

        # Validate non-negative ints
        for name, value in [
            ("total_required_keywords", required_total),
            ("total_preferred_keywords", preferred_total),
            ("matched_required_count", matched_required),
            ("matched_preferred_count", matched_preferred),
        ]:
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Invalid value for {name}: {value}")

        if matched_required > required_total or matched_preferred > preferred_total:
            raise ValueError(
                "Matched counts cannot exceed totals (required or preferred)."
            )

        missing_required = max(0, required_total - matched_required)
        missing_preferred = max(0, preferred_total - matched_preferred)

        # Required bonus
        required_bonus = 0.0
        if matched_required > 0:
            if matched_required <= 5:
                required_bonus = 0.5 * matched_required
            else:
                required_bonus = 3.0

        # Required penalty
        if missing_required <= 1:
            required_penalty = 0.0
        elif 2 <= missing_required <= 4:
            required_penalty = -1.5
        else:
            required_penalty = -4.0

        # Preferred bonus and penalty (only if preferred exist)
        preferred_bonus = 0.0
        preferred_penalty = 0.0
        if preferred_total > 0:
            preferred_bonus = 0.2 * matched_preferred if matched_preferred > 0 else 0.0
            preferred_penalty = -0.15 * missing_preferred

        total_bonus = required_bonus + required_penalty + preferred_bonus + preferred_penalty

        # Coverage
        required_cov = (matched_required / required_total * 100.0) if required_total > 0 else 100.0
        preferred_cov = (matched_preferred / preferred_total * 100.0) if preferred_total > 0 else 100.0

        logger.info(
            "[ATS][BONUS] required_total=%s matched_required=%s missing_required=%s "
            "required_bonus=%.2f required_penalty=%.2f preferred_total=%s matched_preferred=%s "
            "missing_preferred=%s preferred_bonus=%.2f preferred_penalty=%.2f total_bonus=%.2f",
            required_total,
            matched_required,
            missing_required,
            required_bonus,
            required_penalty,
            preferred_total,
            matched_preferred,
            missing_preferred,
            preferred_bonus,
            preferred_penalty,
            total_bonus,
        )

        return {
            "match_counts": {
                "total_required_keywords": required_total,
                "total_preferred_keywords": preferred_total,
                "matched_required_count": matched_required,
                "matched_preferred_count": matched_preferred,
                "missing_required": missing_required,
                "missing_preferred": missing_preferred,
            },
            "bonus_breakdown": {
                "required_bonus": round(required_bonus, 2),
                "required_penalty": round(required_penalty, 2),
                "preferred_bonus": round(preferred_bonus, 2),
                "preferred_penalty": round(preferred_penalty, 2),
                "total_bonus": round(total_bonus, 2),
            },
            "coverage_metrics": {
                "required_coverage": round(required_cov, 2),
                "preferred_coverage": round(preferred_cov, 2),
            },
        }


