"""
Integration Example: How to add subcategorization to recommendation generation

This file shows code snippets for integrating keyword subcategorization
into the existing recommendation generation flow.
"""

# ============================================================================
# SNIPPET 1: Integration in ATSRecommendationService._classify_keywords()
# ============================================================================

def _classify_keywords_with_subcategories(
    self, 
    missing_keywords: Dict[str, List[str]], 
    cv_skills: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Enhanced version of _classify_keywords() with subcategory classification
    
    Returns structure with subcategories:
    {
        "tier1_always_add": {
            "technical": {
                "programming_languages": [...],
                "tools_frameworks": [...],
                "cloud_infrastructure": [...],
                "uncategorized": [...]
            },
            "soft": {...},
            "domain": {...}
        },
        "tier2_add_if_evidence": {...},
        "tier3_never_add": {...},
        "subcategory_metadata": {...},
        "validation_rules": {...}
    }
    """
    from app.services.keyword_subcategorizer import KeywordSubcategorizer
    
    # STEP 1: Original classification (existing logic)
    classified = {
        "tier1_always_add": {"technical": [], "soft": [], "domain": []},
        "tier2_add_if_evidence": {"technical": [], "soft": [], "domain": []},
        "tier3_never_add": {"technical": [], "soft": [], "domain": []},
        "already_in_cv_filtered": []
    }
    
    # ... existing classification logic ...
    # (filter keywords, apply tier patterns, etc.)
    
    # STEP 2: Add subcategory classification
    subcategorizer = KeywordSubcategorizer()
    categorized_with_subcats = subcategorizer.categorize_keywords_with_subcategories(classified)
    
    # STEP 3: Add validation rules summary
    validation_summary = subcategorizer.get_validation_rules_summary(categorized_with_subcats)
    
    # STEP 4: Merge results
    result = {
        **categorized_with_subcats,
        "validation_rules": validation_summary,
        "already_in_cv_filtered": classified.get("already_in_cv_filtered", []),
        "integration_instructions": (
            "Tier 1: Integrate ALL keywords into skills section and relevant bullets. "
            "Tier 2: Integrate ONLY if semantic evidence exists in CV experience. "
            "Tier 3: DO NOT add - domain-specific, unverifiable, or lacks evidence. "
            "Subcategories help organize keywords and apply category-specific validation rules."
        )
    }
    
    return result


# ============================================================================
# SNIPPET 2: Integration in AIRecommendationGenerator._extract_actionable_guidance()
# ============================================================================

def _extract_actionable_guidance_with_subcategories(
    self, 
    json_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhanced version that includes subcategory information
    """
    from app.services.keyword_subcategorizer import KeywordSubcategorizer
    
    keyword_integration = json_data.get('keyword_integration', {})
    
    # Extract tier data (existing logic)
    tier1 = keyword_integration.get('tier1_integrate_immediately', {})
    tier2 = keyword_integration.get('tier2_add_with_evidence', {})
    tier3 = keyword_integration.get('tier3_never_add', {})
    
    # Convert to format expected by subcategorizer
    classified_format = {
        "tier1_always_add": {
            "technical": [item.get('keyword') for item in tier1.get('technical', [])],
            "soft": [item.get('keyword') for item in tier1.get('soft', [])],
            "domain": [item.get('keyword') for item in tier1.get('domain', [])]
        },
        "tier2_add_if_evidence": {
            "technical": [item.get('keyword') for item in tier2.get('technical', [])],
            "soft": [item.get('keyword') for item in tier2.get('soft', [])],
            "domain": [item.get('keyword') for item in tier2.get('domain', [])]
        },
        "tier3_never_add": {
            "technical": [item.get('keyword') for item in tier3.get('technical', [])],
            "soft": [item.get('keyword') for item in tier3.get('soft', [])],
            "domain": [item.get('keyword') for item in tier3.get('domain', [])]
        }
    }
    
    # Apply subcategorization
    subcategorizer = KeywordSubcategorizer()
    categorized = subcategorizer.categorize_keywords_with_subcategories(classified_format)
    
    # Build enhanced actionable guidance
    enhanced_guidance = {
        "tier1_add_immediately": self._build_subcategorized_tier(
            tier1, categorized["tier1_always_add"]
        ),
        "tier2_add_with_evidence": self._build_subcategorized_tier(
            tier2, categorized["tier2_add_if_evidence"]
        ),
        "tier3_never_add": categorized["tier3_never_add"],
        "subcategory_metadata": categorized["subcategory_metadata"],
        "validation_rules": subcategorizer.get_validation_rules_summary(categorized)
    }
    
    return enhanced_guidance


def _build_subcategorized_tier(
    self, 
    tier_data: Dict[str, List[Dict]], 
    subcategorized: Dict[str, Dict[str, List[str]]]
) -> Dict[str, Any]:
    """
    Build tier structure with subcategories, preserving original metadata
    """
    result = {}
    
    for main_cat in ["technical", "soft", "domain"]:
        result[main_cat] = {}
        
        # Get subcategories for this main category
        subcats = subcategorized.get(main_cat, {})
        
        # Get original tier items with metadata
        original_items = {item.get('keyword'): item for item in tier_data.get(main_cat, [])}
        
        # Organize by subcategory
        for subcat_name, keywords in subcats.items():
            result[main_cat][subcat_name] = []
            
            for keyword in keywords:
                if keyword in original_items:
                    # Preserve original metadata (integration, validation, risk)
                    result[main_cat][subcat_name].append(original_items[keyword])
                else:
                    # Fallback if keyword not in original (shouldn't happen)
                    result[main_cat][subcat_name].append({
                        "keyword": keyword,
                        "integration": "Add to appropriate section",
                        "validation": "Review manually",
                        "risk": "medium"
                    })
    
    return result


# ============================================================================
# SNIPPET 3: Validation Rules Application
# ============================================================================

def apply_validation_rules(
    keyword: str,
    main_category: str,
    subcategory: str,
    subcategory_metadata: Dict[str, Any],
    cv_experience: str
) -> Dict[str, Any]:
    """
    Apply validation rules based on subcategory
    
    Returns:
        {
            "can_add": bool,
            "validation_status": str,
            "required_evidence": str,
            "risk_level": str,
            "recommendation": str
        }
    """
    metadata = subcategory_metadata.get(main_category, {}).get(subcategory, {})
    validation_rule = metadata.get("validation_rule", "")
    risk_level = metadata.get("risk_level", "medium")
    
    result = {
        "can_add": False,
        "validation_status": "pending",
        "required_evidence": validation_rule,
        "risk_level": risk_level,
        "recommendation": ""
    }
    
    # Apply validation based on risk level and subcategory
    if risk_level == "low":
        # Low risk: Can add with minimal evidence
        result["can_add"] = True
        result["validation_status"] = "approved"
        result["recommendation"] = f"Safe to add '{keyword}' - {validation_rule}"
    
    elif risk_level == "medium":
        # Medium risk: Need semantic evidence
        # Check if keyword or related terms appear in CV experience
        keyword_lower = keyword.lower()
        cv_lower = cv_experience.lower()
        
        # Simple semantic check (can be enhanced with NLP)
        if keyword_lower in cv_lower or any(
            word in cv_lower for word in keyword_lower.split()
        ):
            result["can_add"] = True
            result["validation_status"] = "approved_with_evidence"
            result["recommendation"] = f"Can add '{keyword}' - evidence found in CV"
        else:
            result["can_add"] = False
            result["validation_status"] = "requires_evidence"
            result["recommendation"] = f"Cannot add '{keyword}' - {validation_rule}"
    
    elif risk_level == "high":
        # High risk: Strong evidence required
        result["can_add"] = False
        result["validation_status"] = "requires_strong_evidence"
        result["recommendation"] = f"DO NOT add '{keyword}' - {validation_rule}"
    
    return result


# ============================================================================
# SNIPPET 4: Updated JSON Structure in Recommendation File
# ============================================================================

"""
Example output structure with subcategories:

{
    "company": "Example_Company",
    "generated_at": "2025-01-22T10:00:00",
    "structured_recommendations": {
        "keyword_integration": {
            "tier1_integrate_immediately": {
                "technical": {
                    "programming_languages": [
                        {
                            "keyword": "Python",
                            "basis": "Generic and widely applicable",
                            "integration": "Add to skills section",
                            "validation": "Discuss Python projects",
                            "risk": "low"
                        }
                    ],
                    "tools_frameworks": [...],
                    "cloud_infrastructure": [...],
                    "uncategorized": [...]
                },
                "soft": {
                    "leadership_management": [...],
                    "communication_collaboration": [...],
                    "analytical_problem_solving": [...],
                    "uncategorized": [...]
                },
                "domain": {
                    "industry_specific": [...],
                    "regulatory_compliance": [...],
                    "business_domain": [...],
                    "uncategorized": [...]
                }
            },
            "tier2_add_with_evidence": {...},
            "tier3_never_add": {...}
        },
        "subcategory_metadata": {
            "technical": {
                "programming_languages": {
                    "validation_rule": "Must have evidence of actual coding/programming experience",
                    "risk_level": "medium",
                    "count": 5
                },
                ...
            },
            "soft": {...},
            "domain": {...}
        },
        "validation_rules": {
            "tier1_validation": {...},
            "tier2_validation": {...},
            "tier3_validation": {...},
            "overall_guidance": {...}
        }
    },
    "actionable_guidance": {
        "tier1_add_immediately": {
            "technical": {
                "programming_languages": [...],
                "tools_frameworks": [...],
                "cloud_infrastructure": [...]
            },
            ...
        },
        ...
    }
}
"""

