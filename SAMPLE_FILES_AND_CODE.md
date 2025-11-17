# Sample Files and Key Code

## 1. CV-JD Matching File (The Smith Family)

**File:** `The_Smith_Family_cv_jd_matching_20251116_092507.json`

```json
{
    "company_name": "The_Smith_Family",
    "matched_required_keywords": [
        "SQL",
        "Power BI",
        "problem-solving",
        "stakeholder management",
        "data extraction",
        "data analysis"
    ],
    "matched_preferred_keywords": [],
    "missed_required_keywords": [
        "Microsoft Excel",      ← REQUIRED, MISSING
        "communication",        ← REQUIRED, MISSING  
        "business processes"    ← REQUIRED, MISSING
    ],
    "missed_preferred_keywords": [
        "curiosity",
        "continuous improvement mindset"
    ],
    "match_counts": {
        "total_required_keywords": 9,
        "total_preferred_keywords": 2,
        "matched_required_count": 6,
        "matched_preferred_count": 0
    }
}
```

**KEY INSIGHT:** CV-JD Matching correctly identifies 3 REQUIRED keywords that are MISSING!

---

## 2. Input Recommendation File (After Filtering)

**File:** `The_Smith_Family_input_recommendation_20251116_092517.json`

```json
{
    "metadata": {
        "company": "The_Smith_Family",
        "ats_score_current": 49.1,
        "match_rate_current": 35.29
    },
    "skills_extraction": {
        "cv": {
            "technical": ["APIs", "Python", "SQL", "Power BI", ...],
            "soft": ["Collaboration", "Problem-solving", "Stakeholder management"],
            "domain": ["AI engineering", ...]
        },
        "jd": {
            "technical": ["SQL", "Power BI", "Microsoft Excel", ...],
            "soft": ["Communication", "Problem-solving", "Collaboration", ...],
            "domain": [...]
        }
    },
    "keyword_integration_guidance": {
        "tier1_always_add": {
            "technical": [],
            "soft": [],
            "domain": []
        },
        "tier2_add_if_evidence": {
            "technical": [],
            "soft": [],
            "domain": ["Dashboard creation", "Data cleansing", ...]
        },
        "tier3_never_add": {
            "technical": [],
            "domain": [...]
        },
        "already_in_cv_filtered": [
            "Data analysis",
            "SQL",
            "Reporting",
            "Problem-solving",
            "AI engineering",
            "Stakeholder management",
            "Collaboration",
            "Power BI"
        ]
    }
}
```

**KEY INSIGHT:** 
- ✅ Keyword filtering IS working (8 keywords filtered)
- ❌ "Communication" is NOT in the filtered list (because it's not in CV)
- ❌ But the tiers are empty at this stage (populated by AI later)

---

## 3. AI Recommendation File (After AI Classification)

**File:** `The_Smith_Family_ai_recommendation_20251116_092538.json`

```json
{
    "structured_recommendations": {
        "priority_gaps": {
            "keyword_coverage_gaps": {
                "technical_gap_percentage": 100,
                "soft_gap_percentage": 100,
                "domain_gap_percentage": 100.0,
                "overall_keyword_gap": 64.71
            },
            "component_gaps": {
                "technical_depth_gap": 100,
                "experience_alignment_gap": 100,
                "industry_fit_gap": 100,
                "seniority_alignment_gap": 100
            },
            "immediate_action_items": {
                "category1_missing_counts": {
                    "technical": 6,
                    "soft": 2,
                    "domain": 3,
                    "total": 11
                }
            }
        },
        "keyword_integration": {
            "tier1_integrate_immediately": {
                "technical": [],
                "soft": [],
                "domain": [
                    {
                        "keyword": "Dashboard creation",
                        "basis": "Generic and transferable skill",
                        "integration": "Add to skills section...",
                        "risk": "low"
                    },
                    {
                        "keyword": "Data cleansing",
                        "basis": "Common data processing skill",
                        "risk": "low"
                    },
                    {
                        "keyword": "Data collection",
                        "basis": "Fundamental skill in data analysis",
                        "risk": "low"
                    }
                ]
            },
            "tier2_add_with_evidence": {
                "technical": [],
                "soft": [
                    {
                        "keyword": "Communication",     ← WRONG! Should be Tier 1
                        "basis": "If there is evidence...",
                        "risk": "medium"
                    }
                ],
                "domain": [
                    {
                        "keyword": "Microsoft Excel",   ← WRONG! Should be Tier 1
                        "basis": "If there is evidence...",
                        "risk": "medium"
                    },
                    {
                        "keyword": "Analytical skills",
                        "risk": "medium"
                    }
                ]
            },
            "tier3_never_add": {
                "domain": [
                    {"keyword": "Annual Impact Report", "risk": "high"},
                    {"keyword": "Education", "risk": "high"},
                    {"keyword": "Growing Careers Project", "risk": "high"},
                    {"keyword": "Poverty", "risk": "high"}
                ]
            }
        }
    }
}
```

**THE PROBLEM:**
- ❌ "Communication" is REQUIRED + MISSING but went to Tier 2
- ❌ "Microsoft Excel" is REQUIRED + MISSING but went to Tier 2
- ❌ "business processes" is REQUIRED + MISSING but not in any tier!

---

## 4. Phase 7 Code - Keyword Classification

**File:** `ats_recommendation_service.py`

### The _classify_keywords Method

```python
def _classify_keywords(self, missing_keywords: Dict[str, List[str]], 
                      cv_skills: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Classify missing keywords into tiers based on CV tailoring framework.
    NOW WITH PRE-FILTERING: Removes keywords already present in the latest CV.
    
    Tier 1: Always add (generic/transferable)
    Tier 2: Add if semantic evidence exists
    Tier 3: Never add (domain-specific/unverifiable)
    """
    # STEP 1: Extract existing keywords from latest CV (including tailored CV if it exists)
    existing_keywords_lower = self._extract_existing_cv_keywords()
    
    # STEP 2: Filter missing keywords to exclude those already in CV
    filtered_missing = {}
    already_present = {}
    
    for category, keywords in missing_keywords.items():
        filtered_missing[category] = []
        already_present[category] = []
        
        for keyword in keywords:
            if self._keyword_exists_in_cv(keyword, existing_keywords_lower):
                logger.info(f"⏭️  [KEYWORD_FILTER] Skipping '{keyword}' (already in CV)")
                already_present[category].append(keyword)
            else:
                filtered_missing[category].append(keyword)
    
    logger.info(f"🔍 [KEYWORD_FILTER] Original missing keywords: {sum(len(v) for v in missing_keywords.values())}")
    logger.info(f"✅ [KEYWORD_FILTER] Actually new keywords: {sum(len(v) for v in filtered_missing.values())}")
    logger.info(f"⏭️  [KEYWORD_FILTER] Already in CV (filtered): {sum(len(v) for v in already_present.values())}")
    
    # Flatten for already_in_cv_filtered list
    already_in_cv_list = []
    for category_keywords in already_present.values():
        already_in_cv_list.extend(category_keywords)
    
    # STEP 3: Return guidance with pre-filtered keywords
    # NOTE: Actual tier classification happens in AI recommendation generator
    # This just provides the FILTERED keywords for AI to classify
    return {
        "tier1_always_add": {
            "technical": [],
            "soft": [],
            "domain": []
        },
        "tier2_add_if_evidence": {
            "technical": filtered_missing.get("technical", []),
            "soft": filtered_missing.get("soft", []),
            "domain": filtered_missing.get("domain", [])
        },
        "tier3_never_add": {
            "technical": [],
            "domain": []
        },
        "already_in_cv_filtered": already_in_cv_list
    }
```

**KEY ISSUE:** This method only FILTERS keywords. It doesn't classify them into tiers based on REQUIRED/PREFERRED status!

### The _extract_existing_cv_keywords Method

```python
def _extract_existing_cv_keywords(self) -> List[str]:
    """
    Extract all keywords from the latest CV (tailored or original)
    to prevent recommending keywords that are already present.
    
    Returns:
        List of keywords (lowercase) already in the CV
    """
    from app.unified_latest_file_selector import get_selector_for_user
    from pathlib import Path
    import json
    
    try:
        # Get the latest CV (tailored if exists, otherwise original)
        selector = get_selector_for_user(self.user_email)
        cv_contexts = selector.get_all_cv_contexts()
        
        if not cv_contexts:
            logger.warning("⚠️ [KEYWORD_FILTER] No CV contexts found")
            return []
        
        # Get the latest tailored CV
        latest_cv_context = cv_contexts[0]
        cv_json_path = latest_cv_context.json_path
        
        if not cv_json_path or not cv_json_path.exists():
            logger.warning(f"⚠️ [KEYWORD_FILTER] CV JSON not found: {cv_json_path}")
            return []
        
        with open(cv_json_path, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
        
        keywords = set()
        
        # Extract from skills section
        for skill_cat in cv_data.get('skills', []):
            if isinstance(skill_cat, dict):
                for skill in skill_cat.get('skills', []):
                    skill_str = str(skill) if skill is not None else ""
                    if skill_str and len(skill_str.strip()) > 0:
                        keywords.add(skill_str.strip().lower())
        
        # Extract from experience bullets
        for exp in cv_data.get('experience', []):
            if isinstance(exp, dict):
                for bullet in exp.get('bullets', []):
                    bullet_str = str(bullet) if bullet is not None else ""
                    # Extract keywords from bullet text (simple word extraction)
                    words = bullet_str.split()
                    for word in words:
                        clean_word = word.strip('.,;:()[]{}').lower()
                        if len(clean_word) > 3:  # Only meaningful words
                            keywords.add(clean_word)
        
        logger.info(f"🔍 [KEYWORD_FILTER] Extracted {len(keywords)} keywords from latest tailored CV: {cv_json_path.name}")
        
        return list(keywords)
        
    except Exception as e:
        logger.error(f"❌ [KEYWORD_FILTER] Error extracting CV keywords: {e}")
        return []
```

**KEY INSIGHT:** This extracts keywords from the CV successfully!

---

## 5. Phase 8 Code - CV Tailoring

**File:** `cv_tailoring_service.py`

### Main tailor_cv Method

```python
async def tailor_cv(self, request: CVTailoringRequest) -> CVTailoringResponse:
    """
    Main method to tailor a CV based on recommendations
    
    Args:
        request: CVTailoringRequest containing original CV and recommendations
        
    Returns:
        CVTailoringResponse with tailored CV and processing details
    """
    try:
        logger.info(f"🎯 Starting CV tailoring for {request.recommendations.company}")
        
        # Store original CV content for semantic validation
        self._original_cv_content = self._extract_original_cv_text(request.original_cv)
        
        # Step 1: Validate input data
        validation_result = self._validate_cv_data(request.original_cv)
        if not validation_result.is_valid:
            raise ValueError(f"CV validation failed")
        
        # Step 2: Determine optimization strategy
        optimization_strategy = self._determine_optimization_strategy(
            request.original_cv, 
            request.recommendations
        )
        
        # Step 3: Generate tailored CV using AI
        tailored_cv = await self._generate_tailored_cv(
            request.original_cv,
            request.recommendations, 
            optimization_strategy,
            request.custom_instructions
        )
        
        # Step 4: Post-process and validate results
        processing_summary = self._generate_processing_summary(
            request.original_cv,
            tailored_cv,
            request.recommendations
        )
        
        # Step 5: Estimate ATS score improvement
        estimated_score = await self._estimate_ats_score(...)
        tailored_cv.estimated_ats_score = estimated_score
        
        response = CVTailoringResponse(
            tailored_cv=tailored_cv,
            processing_summary=processing_summary,
            recommendations_applied=self._extract_applied_recommendations(tailored_cv),
            success=True
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ CV tailoring failed: {e}")
        raise Exception(f"CV tailoring process failed: {str(e)}")
```

### The _generate_tailored_cv Method (Key Part)

```python
async def _generate_tailored_cv(
    self,
    original_cv: OriginalCV,
    recommendations: RecommendationAnalysis,
    strategy: OptimizationStrategy,
    custom_instructions: Optional[str]
) -> TailoredCV:
    """
    Generate tailored CV using AI based on framework and recommendations
    """
    try:
        # Build the prompt for AI
        user_prompt = self._build_user_prompt(
            original_cv,
            recommendations,
            strategy,
            custom_instructions
        )
        
        # Call AI to generate the tailored CV
        ai_response = await ai_service.generate_cv_json(
            user_data=...,
            system_prompt=self.framework_content,  # The framework.md
            user_prompt=user_prompt,
            model_preference=...
        )
        
        # Parse the JSON response
        tailored_cv_data = json.loads(ai_response.content)
        
        # Convert to TailoredCV model
        tailored_cv = TailoredCV(**tailored_cv_data)
        
        return tailored_cv
        
    except Exception as e:
        logger.error(f"❌ Failed to generate tailored CV: {e}")
        raise
```

### The _build_user_prompt Method (Simplified)

```python
def _build_user_prompt(
    self,
    original_cv: OriginalCV,
    recommendations: RecommendationAnalysis,
    strategy: OptimizationStrategy,
    custom_instructions: Optional[str]
) -> str:
    """
    Build the user prompt for AI CV generation
    """
    prompt_parts = []
    
    # Add CV context
    prompt_parts.append("# Original CV")
    prompt_parts.append(json.dumps(original_cv.model_dump(), indent=2))
    
    # Add recommendations
    prompt_parts.append("\n# Recommendations")
    prompt_parts.append(recommendations.model_dump_json(indent=2))
    
    # Add strategy
    prompt_parts.append("\n# Optimization Strategy")
    prompt_parts.append(f"- Target Industry: {strategy.target_industry}")
    prompt_parts.append(f"- Target Role: {strategy.target_role}")
    
    # Add Tier 1 keywords to integrate
    tier1_keywords = recommendations.tier1_keywords
    prompt_parts.append("\n# TIER 1 KEYWORDS TO INTEGRATE:")
    prompt_parts.append(json.dumps(tier1_keywords, indent=2))
    
    # Add instructions
    prompt_parts.append("\n# INSTRUCTIONS:")
    prompt_parts.append("1. Integrate ALL Tier 1 keywords naturally")
    prompt_parts.append("2. Preserve ALL existing content if this is a rerun")
    prompt_parts.append("3. Follow the framework guidelines")
    prompt_parts.append("4. Output VALID JSON only")
    
    if custom_instructions:
        prompt_parts.append(f"\n# CUSTOM INSTRUCTIONS:")
        prompt_parts.append(custom_instructions)
    
    return "\n".join(prompt_parts)
```
