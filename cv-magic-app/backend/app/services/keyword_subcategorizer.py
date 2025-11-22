"""
Keyword Subcategorizer - Categorizes keywords into subcategories within main categories

This module provides subcategory classification for missing keywords:
- Main Categories: technical, soft, domain
- Subcategories: 3 subcategories per main category
- Validation rules for each subcategory
"""

import logging
import re
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class KeywordSubcategorizer:
    """
    Classifies keywords into subcategories within main categories (technical, soft, domain)
    Each main category has 3 subcategories for better organization and validation
    """
    
    # Subcategory patterns for Technical keywords
    TECHNICAL_SUBCATEGORIES = {
        "programming_languages": {
            "patterns": [
                r"\bpython\b", r"\bjava\b", r"\bjavascript\b", r"\btypescript\b",
                r"\br\b", r"\bsql\b", r"\bscala\b", r"\bgo\b", r"\brust\b",
                r"\bc\+\+\b", r"\bc#\b", r"\bphp\b", r"\bruby\b", r"\bswift\b",
                r"\bkotlin\b", r"\bmatlab\b", r"\bsas\b", r"\bspss\b"
            ],
            "validation_rule": "Must have evidence of actual coding/programming experience",
            "risk_level": "medium"
        },
        "tools_frameworks": {
            "patterns": [
                r"\bpandas\b", r"\bnumpy\b", r"\bscikit-learn\b", r"\btensorflow\b",
                r"\bpytorch\b", r"\bkeras\b", r"\bspark\b", r"\bhadoop\b",
                r"\bdocker\b", r"\bkubernetes\b", r"\bgit\b", r"\bjenkins\b",
                r"\bairflow\b", r"\bflask\b", r"\bdjango\b", r"\bfastapi\b",
                r"\breact\b", r"\bangular\b", r"\bvue\b", r"\bnode\.js\b"
            ],
            "validation_rule": "Must have evidence of tool usage in projects or work experience",
            "risk_level": "medium"
        },
        "cloud_infrastructure": {
            "patterns": [
                r"\baws\b", r"\bazure\b", r"\bgcp\b", r"\bgoogle cloud\b",
                r"\bsnowflake\b", r"\bbigquery\b", r"\bredshift\b", r"\bs3\b",
                r"\bec2\b", r"\blambda\b", r"\bdatabricks\b", r"\bterraform\b",
                r"\bkubernetes\b", r"\bci/cd\b", r"\bdevops\b"
            ],
            "validation_rule": "Must have evidence of cloud platform usage or infrastructure management",
            "risk_level": "high"
        }
    }
    
    # Subcategory patterns for Soft Skills keywords
    SOFT_SUBCATEGORIES = {
        "leadership_management": {
            "patterns": [
                r"\bleadership\b", r"\bteam management\b", r"\bpeople management\b",
                r"\bproject management\b", r"\bmentoring\b", r"\bcoaching\b",
                r"\bteam leadership\b", r"\bmanaging\b", r"\bdelegation\b",
                r"\bstrategic planning\b", r"\bdecision making\b", r"\bdecision-making\b"
            ],
            "validation_rule": "Must have evidence of leading teams, projects, or initiatives",
            "risk_level": "low"
        },
        "communication_collaboration": {
            "patterns": [
                r"\bcommunication\b", r"\bpresentation\b", r"\bstakeholder management\b",
                r"\bcollaboration\b", r"\bteamwork\b", r"\binterpersonal\b",
                r"\bnegotiation\b", r"\bclient facing\b", r"\bclient-facing\b",
                r"\bcross-functional\b", r"\bwritten communication\b", r"\bverbal communication\b"
            ],
            "validation_rule": "Must have evidence of communication or collaboration in work experience",
            "risk_level": "low"
        },
        "analytical_problem_solving": {
            "patterns": [
                r"\banalytical\b", r"\bproblem solving\b", r"\bproblem-solving\b",
                r"\bcritical thinking\b", r"\bdata analysis\b", r"\bquantitative\b",
                r"\bqualitative\b", r"\bresearch\b", r"\btroubleshooting\b",
                r"\broot cause\b", r"\banalytical skills\b", r"\battention to detail\b"
            ],
            "validation_rule": "Must have evidence of analytical work or problem-solving in experience",
            "risk_level": "low"
        }
    }
    
    # Subcategory patterns for Domain keywords
    DOMAIN_SUBCATEGORIES = {
        "industry_specific": {
            "patterns": [
                r"\brefugee\b", r"\bhumanitarian\b", r"\bfundraising\b", r"\bdonor\b",
                r"\bcharity\b", r"\bnon-profit\b", r"\bnonprofit\b", r"\bnfp\b",
                r"\bnot for profit\b", r"\bcommunity engagement\b", r"\bsocial impact\b",
                r"\bfood relief\b", r"\bvolunteer\b", r"\bphilanthropy\b"
            ],
            "validation_rule": "NEVER add without direct industry experience - high risk of misrepresentation",
            "risk_level": "high"
        },
        "regulatory_compliance": {
            "patterns": [
                r"\bgdpr\b", r"\bhipaa\b", r"\bsox\b", r"\bcompliance\b",
                r"\bregulatory\b", r"\baudit\b", r"\brisk management\b",
                r"\bgovernance\b", r"\bdata privacy\b", r"\bsecurity compliance\b",
                r"\bfinancial regulation\b", r"\bregulatory reporting\b"
            ],
            "validation_rule": "Must have evidence of working with regulations or compliance frameworks",
            "risk_level": "high"
        },
        "business_domain": {
            "patterns": [
                r"\bfinance\b", r"\baccounting\b", r"\bmarketing\b", r"\bsales\b",
                r"\bhr\b", r"\bhuman resources\b", r"\boperations\b", r"\bsupply chain\b",
                r"\blogistics\b", r"\bretail\b", r"\be-commerce\b", r"\bhealthcare\b",
                r"\beducation\b", r"\bmanufacturing\b"
            ],
            "validation_rule": "Must have evidence of domain knowledge or business context in experience",
            "risk_level": "medium"
        }
    }
    
    def __init__(self):
        """Initialize the subcategorizer"""
        self.subcategory_maps = {
            "technical": self.TECHNICAL_SUBCATEGORIES,
            "soft": self.SOFT_SUBCATEGORIES,
            "domain": self.DOMAIN_SUBCATEGORIES
        }
    
    def classify_keyword_subcategory(
        self, 
        keyword: str, 
        main_category: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Classify a keyword into its subcategory within a main category
        
        Args:
            keyword: The keyword to classify
            main_category: Main category (technical, soft, or domain)
            
        Returns:
            Tuple of (subcategory_name, subcategory_info)
            Returns ("uncategorized", {}) if no match found
        """
        keyword_lower = keyword.lower()
        
        if main_category not in self.subcategory_maps:
            logger.warning(f"⚠️ [SUBCATEGORIZER] Unknown main category: {main_category}")
            return ("uncategorized", {})
        
        subcategories = self.subcategory_maps[main_category]
        
        # Check each subcategory's patterns
        for subcat_name, subcat_info in subcategories.items():
            patterns = subcat_info.get("patterns", [])
            for pattern in patterns:
                if re.search(pattern, keyword_lower, re.IGNORECASE):
                    logger.debug(
                        f"✅ [SUBCATEGORIZER] '{keyword}' → {main_category}/{subcat_name}"
                    )
                    return (subcat_name, subcat_info)
        
        # No match found
        logger.debug(
            f"⚠️ [SUBCATEGORIZER] '{keyword}' → {main_category}/uncategorized"
        )
        return ("uncategorized", {
            "validation_rule": "Review manually - no automatic classification available",
            "risk_level": "medium"
        })
    
    def categorize_keywords_with_subcategories(
        self, 
        classified_keywords: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Add subcategory classification to already-tiered keywords
        
        Args:
            classified_keywords: Dictionary with structure:
                {
                    "tier1_always_add": {"technical": [...], "soft": [...], "domain": [...]},
                    "tier2_add_if_evidence": {"technical": [...], "soft": [...], "domain": [...]},
                    "tier3_never_add": {"technical": [...], "soft": [...], "domain": [...]}
                }
        
        Returns:
            Enhanced structure with subcategories:
                {
                    "tier1_always_add": {
                        "technical": {
                            "programming_languages": [...],
                            "tools_frameworks": [...],
                            "cloud_infrastructure": [...],
                            "uncategorized": [...]
                        },
                        ...
                    },
                    ...
                    "subcategory_metadata": {
                        "technical": {
                            "programming_languages": {
                                "validation_rule": "...",
                                "risk_level": "...",
                                "count": 5
                            },
                            ...
                        },
                        ...
                    }
                }
        """
        result = {
            "tier1_always_add": {},
            "tier2_add_if_evidence": {},
            "tier3_never_add": {},
            "subcategory_metadata": {}
        }
        
        # Initialize subcategory structure for each tier and category
        for tier in ["tier1_always_add", "tier2_add_if_evidence", "tier3_never_add"]:
            result[tier] = {
                "technical": {
                    "programming_languages": [],
                    "tools_frameworks": [],
                    "cloud_infrastructure": [],
                    "uncategorized": []
                },
                "soft": {
                    "leadership_management": [],
                    "communication_collaboration": [],
                    "analytical_problem_solving": [],
                    "uncategorized": []
                },
                "domain": {
                    "industry_specific": [],
                    "regulatory_compliance": [],
                    "business_domain": [],
                    "uncategorized": []
                }
            }
        
        # Initialize metadata structure
        for main_cat in ["technical", "soft", "domain"]:
            result["subcategory_metadata"][main_cat] = {}
            subcats = self.subcategory_maps[main_cat]
            for subcat_name, subcat_info in subcats.items():
                result["subcategory_metadata"][main_cat][subcat_name] = {
                    "validation_rule": subcat_info.get("validation_rule", ""),
                    "risk_level": subcat_info.get("risk_level", "medium"),
                    "count": 0
                }
            result["subcategory_metadata"][main_cat]["uncategorized"] = {
                "validation_rule": "Review manually - no automatic classification available",
                "risk_level": "medium",
                "count": 0
            }
        
        # Classify keywords into subcategories
        for tier_name, tier_data in classified_keywords.items():
            if tier_name not in result:
                continue
                
            for main_category, keywords in tier_data.items():
                for keyword in keywords:
                    subcat_name, subcat_info = self.classify_keyword_subcategory(
                        keyword, main_category
                    )
                    
                    # Add to appropriate subcategory
                    result[tier_name][main_category][subcat_name].append(keyword)
                    
                    # Update metadata count
                    if subcat_name in result["subcategory_metadata"][main_category]:
                        result["subcategory_metadata"][main_category][subcat_name]["count"] += 1
        
        return result
    
    def get_validation_rules_summary(self, categorized_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate validation rules summary for all subcategories
        
        Args:
            categorized_data: Output from categorize_keywords_with_subcategories()
        
        Returns:
            Summary of validation rules organized by tier and category
        """
        summary = {
            "tier1_validation": {},
            "tier2_validation": {},
            "tier3_validation": {},
            "overall_guidance": {}
        }
        
        metadata = categorized_data.get("subcategory_metadata", {})
        
        for tier in ["tier1_always_add", "tier2_add_if_evidence", "tier3_never_add"]:
            tier_key = tier.replace("_", " ").title().replace(" ", "_").lower()
            summary[f"{tier_key}_validation"] = {}
            
            for main_cat in ["technical", "soft", "domain"]:
                summary[f"{tier_key}_validation"][main_cat] = {}
                
                tier_data = categorized_data.get(tier, {}).get(main_cat, {})
                for subcat_name, keywords in tier_data.items():
                    if keywords and subcat_name in metadata.get(main_cat, {}):
                        subcat_meta = metadata[main_cat][subcat_name]
                        summary[f"{tier_key}_validation"][main_cat][subcat_name] = {
                            "keywords": keywords,
                            "count": len(keywords),
                            "validation_rule": subcat_meta.get("validation_rule", ""),
                            "risk_level": subcat_meta.get("risk_level", "medium")
                        }
        
        # Overall guidance
        summary["overall_guidance"] = {
            "tier1": "Add all keywords immediately - low risk, high transferability",
            "tier2": "Add only with semantic evidence from CV experience - medium risk",
            "tier3": "Never add without direct experience - high risk of misrepresentation"
        }
        
        return summary


# Example usage and validation
if __name__ == "__main__":
    import json
    
    # Example classification
    subcategorizer = KeywordSubcategorizer()
    
    # Test keywords
    test_keywords = {
        "tier1_always_add": {
            "technical": ["Python", "data analysis", "project management"],
            "soft": ["leadership", "communication", "problem solving"],
            "domain": []
        },
        "tier2_add_if_evidence": {
            "technical": ["AWS", "Docker", "Kubernetes"],
            "soft": ["stakeholder management", "analytical thinking"],
            "domain": ["GDPR", "compliance"]
        },
        "tier3_never_add": {
            "technical": [],
            "soft": [],
            "domain": ["refugee", "humanitarian", "fundraising"]
        }
    }
    
    # Categorize with subcategories
    categorized = subcategorizer.categorize_keywords_with_subcategories(test_keywords)
    
    # Get validation rules
    validation_summary = subcategorizer.get_validation_rules_summary(categorized)
    
    print("Categorized Keywords:")
    print(json.dumps(categorized, indent=2))
    print("\nValidation Summary:")
    print(json.dumps(validation_summary, indent=2))

