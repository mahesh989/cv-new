"""
Hybrid Skill Comparator

Combines the enhanced skill matcher with AI-powered analysis for optimal results.
This provides both deterministic skill matching and AI interpretation.
"""

import logging
from typing import Dict, List, Any, Optional
import json

from .enhanced_skill_matcher import enhanced_skill_matcher, SkillMatch
from .preextracted_comparator import build_json_prompt, _extract_json_from_text

logger = logging.getLogger(__name__)

class HybridSkillComparator:
    """Combines enhanced skill matching with AI analysis"""
    
    def __init__(self):
        self.skill_matcher = enhanced_skill_matcher
    
    async def compare_skills_hybrid(
        self,
        ai_service,
        cv_skills: Dict[str, list],
        jd_skills: Dict[str, list],
        temperature: float = 0.3,
        max_tokens: int = 3000
    ) -> Dict[str, Any]:
        """
        Perform hybrid skill comparison using both deterministic matching 
        and AI analysis for best results.
        """
        
        logger.info("🚀 Starting hybrid skill comparison...")
        
        # Step 1: Use enhanced skill matcher for deterministic matching
        deterministic_results = self._perform_deterministic_matching(cv_skills, jd_skills)
        
        # Step 2: Use AI for remaining unmatched skills and validation
        ai_results = await self._perform_ai_matching(
            ai_service, cv_skills, jd_skills, deterministic_results, temperature, max_tokens
        )
        
        # Step 3: Combine and optimize results
        final_results = self._combine_results(deterministic_results, ai_results, cv_skills, jd_skills)
        
        return final_results
    
    def _perform_deterministic_matching(self, cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> Dict[str, Any]:
        """Use enhanced skill matcher for high-confidence matches"""
        
        results = {
            'technical_skills': {'matched': [], 'missing': []},
            'soft_skills': {'matched': [], 'missing': []},
            'domain_keywords': {'matched': [], 'missing': []}
        }
        
        confidence_threshold = 0.8  # High confidence for deterministic matches
        
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            cv_category_skills = cv_skills.get(category, [])
            jd_category_skills = jd_skills.get(category, [])
            
            # Find matches for this category
            matches = self.skill_matcher.match_skills(cv_category_skills, jd_category_skills)
            
            matched_jd_skills = set()
            for match in matches:
                if match.confidence >= confidence_threshold:
                    results[category]['matched'].append({
                        'jd_skill': match.jd_skill,
                        'cv_equivalent': match.cv_skill,
                        'reasoning': f"{match.match_type.title()} match (confidence: {match.confidence:.2f}) - {match.reasoning}",
                        'confidence': match.confidence,
                        'match_source': 'deterministic'
                    })
                    matched_jd_skills.add(match.jd_skill)
            
            # Add unmatched skills to missing
            for jd_skill in jd_category_skills:
                if jd_skill not in matched_jd_skills:
                    results[category]['missing'].append({
                        'jd_skill': jd_skill,
                        'reasoning': 'No high-confidence deterministic match found',
                        'needs_ai_analysis': True
                    })
        
        logger.info(f"✅ Deterministic matching completed. Found {self._count_matches(results)} high-confidence matches.")
        return results
    
    async def _perform_ai_matching(
        self,
        ai_service,
        cv_skills: Dict[str, list],
        jd_skills: Dict[str, list],
        deterministic_results: Dict[str, Any],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Use AI to analyze remaining unmatched skills"""
        
        # Create a subset of skills that need AI analysis
        unmatched_jd_skills = {}
        
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            unmatched_skills = [
                item['jd_skill'] for item in deterministic_results[category]['missing']
                if item.get('needs_ai_analysis', False)
            ]
            if unmatched_skills:
                unmatched_jd_skills[category] = unmatched_skills
        
        if not any(unmatched_jd_skills.values()):
            logger.info("📝 No skills need AI analysis - all handled deterministically.")
            return {'technical_skills': {'matched': [], 'missing': []}, 'soft_skills': {'matched': [], 'missing': []}, 'domain_keywords': {'matched': [], 'missing': []}}
        
        logger.info(f"🤖 Using AI to analyze {sum(len(skills) for skills in unmatched_jd_skills.values())} remaining skills...")
        
        # Build focused prompt for unmatched skills
        focused_prompt = self._build_focused_ai_prompt(cv_skills, unmatched_jd_skills, deterministic_results)
        
        try:
            response = await ai_service.generate_response(
                prompt=focused_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            ai_results = _extract_json_from_text(response.content)
            logger.info("✅ AI analysis completed successfully.")
            return ai_results
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            # Return empty structure if AI fails
            return {'technical_skills': {'matched': [], 'missing': []}, 'soft_skills': {'matched': [], 'missing': []}, 'domain_keywords': {'matched': [], 'missing': []}}
    
    def _build_focused_ai_prompt(self, cv_skills: Dict[str, list], unmatched_jd_skills: Dict[str, list], deterministic_results: Dict[str, Any]) -> str:
        """Build a focused AI prompt for analyzing remaining unmatched skills"""
        
        # Get already matched CV skills to avoid double-counting
        used_cv_skills = set()
        for category in deterministic_results:
            for match in deterministic_results[category]['matched']:
                used_cv_skills.add(match['cv_equivalent'])
        
        # Create available CV skills (unused ones)
        available_cv_skills = {}
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            available_skills = [skill for skill in cv_skills.get(category, []) if skill not in used_cv_skills]
            if available_skills:
                available_cv_skills[category] = available_skills
        
        prompt = f"""
You are an expert skill analyst. High-confidence matches have already been found deterministically.
Your job is to analyze the REMAINING unmatched JD requirements against AVAILABLE CV skills.

AVAILABLE CV SKILLS (not yet matched):
{json.dumps(available_cv_skills, indent=2)}

REMAINING UNMATCHED JD REQUIREMENTS:
{json.dumps(unmatched_jd_skills, indent=2)}

INSTRUCTIONS:
- Use lower confidence thresholds since these are edge cases
- Look for semantic relationships, partial matches, transferable skills
- Be more liberal with matches but provide clear reasoning
- If truly no match exists, mark as missing with explanation

OUTPUT (JSON only):
{{
  "technical_skills": {{"matched": [], "missing": []}},
  "soft_skills": {{"matched": [], "missing": []}},
  "domain_keywords": {{"matched": [], "missing": []}}
}}

Each matched item: {{"jd_skill": "...", "cv_equivalent": "...", "reasoning": "..."}}
Each missing item: {{"jd_skill": "...", "reasoning": "..."}}
"""
        return prompt.strip()
    
    def _combine_results(self, deterministic_results: Dict[str, Any], ai_results: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> Dict[str, Any]:
        """Combine deterministic and AI results into final output"""
        
        combined_results = {
            'technical_skills': {'matched': [], 'missing': []},
            'soft_skills': {'matched': [], 'missing': []},
            'domain_keywords': {'matched': [], 'missing': []}
        }
        
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            # Add deterministic matches first (higher confidence)
            combined_results[category]['matched'].extend(deterministic_results[category]['matched'])
            
            # Add AI matches with source annotation
            for ai_match in ai_results.get(category, {}).get('matched', []):
                ai_match['match_source'] = 'ai_analysis'
                combined_results[category]['matched'].append(ai_match)
            
            # Combine missing skills
            # First get skills that were marked as missing by deterministic analysis
            deterministic_missing = {item['jd_skill'] for item in deterministic_results[category]['missing']}
            
            # Then get skills that AI also couldn't match
            ai_missing = {item['jd_skill'] for item in ai_results.get(category, {}).get('missing', [])}
            
            # Add final missing skills (those that neither system could match)
            final_missing = deterministic_missing.intersection(ai_missing)
            for jd_skill in final_missing:
                # Get the AI reasoning if available, otherwise use deterministic reasoning
                ai_missing_item = next((item for item in ai_results.get(category, {}).get('missing', []) if item['jd_skill'] == jd_skill), None)
                reasoning = ai_missing_item['reasoning'] if ai_missing_item else "No suitable CV equivalent found"
                
                combined_results[category]['missing'].append({
                    'jd_skill': jd_skill,
                    'reasoning': reasoning
                })
        
        # Add summary statistics
        total_matches = self._count_matches(combined_results)
        total_requirements = sum(len(jd_skills.get(cat, [])) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])
        total_missing = sum(len(combined_results[cat]['missing']) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])
        
        combined_results['summary'] = {
            'total_jd_requirements': total_requirements,
            'total_matches': total_matches,
            'total_missing': total_missing,
            'match_rate_percentage': round((total_matches / total_requirements * 100), 1) if total_requirements > 0 else 0,
            'deterministic_matches': self._count_matches(deterministic_results),
            'ai_matches': self._count_matches(ai_results)
        }
        
        logger.info(f"🎯 Hybrid comparison complete: {total_matches}/{total_requirements} matched ({combined_results['summary']['match_rate_percentage']}%)")
        
        return combined_results
    
    def _count_matches(self, results: Dict[str, Any]) -> int:
        """Count total matches across all categories"""
        return sum(
            len(results.get(category, {}).get('matched', []))
            for category in ['technical_skills', 'soft_skills', 'domain_keywords']
        )

# Global instance
hybrid_comparator = HybridSkillComparator()
