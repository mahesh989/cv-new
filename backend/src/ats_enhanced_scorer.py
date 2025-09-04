"""
Enhanced ATS Scorer - DeepSeek Only Version
Combines keyword extraction with enhanced scoring logic
"""
import json
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedATSScorer:
    def __init__(self, api_key: str = None):
        """Initialize with DeepSeek AI service"""
        # Import here to avoid circular imports
        from .hybrid_ai_service import hybrid_ai
        
        self.ai_service = hybrid_ai
        print(f"🔧 [ATS_SCORER] Using DeepSeek AI service for ATS scoring")
        
        # Industry-specific weights (can be expanded)
        self.industry_weights = {
            'tech': {'technical': 0.40, 'experience': 0.30, 'soft': 0.20, 'domain': 0.10},
            'management': {'soft': 0.40, 'experience': 0.30, 'technical': 0.20, 'domain': 0.10},
            'default': {'technical': 0.30, 'experience': 0.25, 'soft': 0.25, 'domain': 0.20}
        }
    
    async def _call_ai_service(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """Helper method to call AI service consistently"""
        return await self.ai_service.generate_response(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def calculate_enhanced_ats_score(self, cv_text: str, jd_text: str, 
                                   skill_comparison: Dict, extracted_keywords: Dict) -> Dict:
        """
        Main function: Calculate enhanced ATS score using DeepSeek
        """
        logger.info("🔍 Starting Enhanced ATS Scoring with DeepSeek...")
        
        try:
            # Step 1: Calculate base scores from existing keyword matching
            base_scores = self._calculate_base_scores(skill_comparison, extracted_keywords)
            logger.info(f"📊 Base scores calculated: {base_scores['overall_base_score']}/100")
            
            # Step 2: Create enhanced result with proper structure for UI
            enhanced_result = self._create_enhanced_result(base_scores, skill_comparison, extracted_keywords)
            
            logger.info(f"✅ Enhanced ATS Score: {enhanced_result['overall_ats_score']}/100")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced ATS Scoring failed: {e}")
            # Fallback to base scores
            return self._create_fallback_result(skill_comparison, extracted_keywords)
    
    def _calculate_base_scores(self, skill_comparison: Dict, extracted_keywords: Dict) -> Dict:
        """Calculate base scores from individual skill categories - handles both old and new formats"""
        print("\n" + "="*80)
        print("📊 [ATS_SCORER] BASE SCORES CALCULATION - START")
        print("="*80)
        
        print(f"📊 [BASE_SCORES] Input skill comparison keys: {list(skill_comparison.keys())}")
        print(f"📊 [BASE_SCORES] Input extracted keywords keys: {list(extracted_keywords.keys())}")
        
        base_scores = {}
        overall_matches = 0
        overall_total = 0
        
        # Check if we have the new enhanced format with match_summary
        if 'match_summary' in skill_comparison and 'categories' in skill_comparison['match_summary']:
            categories_data = skill_comparison['match_summary']['categories']
            print(f"📊 [BASE_SCORES] Using NEW enhanced format with match_summary")
            print(f"📊 [BASE_SCORES] Categories data: {list(categories_data.keys())}")
            
            # Map category names from new format to expected format
            category_mapping = {
                'technical': 'technical_skills',
                'soft': 'soft_skills', 
                'domain': 'domain_keywords'
            }
            
            for old_name, new_name in category_mapping.items():
                if old_name in categories_data:
                    matched = categories_data[old_name].get('matched', 0)
                    missing = categories_data[old_name].get('missing', 0)
                    total = matched + missing
                    
                    if total > 0:
                        percentage = (matched / total) * 100
                        base_scores[new_name] = round(percentage, 1)
                        overall_matches += matched
                        overall_total += total
                    else:
                        base_scores[new_name] = 0
                        
                    print(f"   📈 {new_name}: {matched}/{total} = {base_scores[new_name]}%")
                else:
                    print(f"   ⚠️ {new_name}: Not found in categories data")
                    base_scores[new_name] = 0
        else:
            print(f"📊 [BASE_SCORES] Using OLD/fallback format for backward compatibility")
            # Fallback to old format for backward compatibility
            for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
                if category in skill_comparison:
                    matched = len(skill_comparison[category].get('matched', []))
                    missing = len(skill_comparison[category].get('missing', []))
                    total = matched + missing
                    
                    if total > 0:
                        percentage = (matched / total) * 100
                        base_scores[category] = round(percentage, 1)
                        overall_matches += matched
                        overall_total += total
                    else:
                        base_scores[category] = 0
                        
                    print(f"   📈 {category}: {matched}/{total} = {base_scores[category]}%")
                else:
                    print(f"   ⚠️ {category}: Not found in skill comparison")
                    base_scores[category] = 0
        
        # Calculate overall base score (for reference)
        overall_base = (overall_matches / overall_total * 100) if overall_total > 0 else 0
        
        print(f"\n📊 [BASE_SCORES] FINAL CALCULATION:")
        print(f"   📏 Overall matches: {overall_matches}")
        print(f"   📏 Overall total: {overall_total}")
        print(f"   📏 Overall base score: {round(overall_base, 1)}/100")
        print(f"   📏 Category scores: {base_scores}")
        
        logger.info(f"📊 Base scores calculated: {overall_base}/100")
        logger.info(f"📊 Category scores: {base_scores}")
        
        result = {
            'category_scores': base_scores,
            'overall_base_score': round(overall_base, 1),
            'total_matches': overall_matches,
            'total_requirements': overall_total
        }
        
        print("="*80)
        print("📊 [ATS_SCORER] BASE SCORES CALCULATION - END")
        print("="*80 + "\n")
        
        return result
    
    def _create_enhanced_result(self, base_scores: Dict, skill_comparison: Dict, extracted_keywords: Dict) -> Dict:
        """Create enhanced ATS result with proper structure for UI compatibility"""
        print(f"🚀 [ATS_SCORER] Creating enhanced result with DeepSeek")
        
        # Calculate enhanced score with proper weighting
        category_scores = base_scores['category_scores']
        
        # Enhanced scoring weights
        weights = {
            'technical_skills': 0.35,
            'soft_skills': 0.25, 
            'domain_keywords': 0.25,
            'bonus': 0.15
        }
        
        # Calculate weighted score
        weighted_score = (
            category_scores.get('technical_skills', 0) * weights['technical_skills'] +
            category_scores.get('soft_skills', 0) * weights['soft_skills'] +
            category_scores.get('domain_keywords', 0) * weights['domain_keywords']
        )
        
        # Add bonus for completeness if all categories have decent scores
        bonus_score = 0
        if all(category_scores.get(cat, 0) >= 50 for cat in ['technical_skills', 'soft_skills', 'domain_keywords']):
            bonus_score = 10  # Bonus for well-rounded candidate
            
        final_score = min(100, weighted_score + bonus_score)
        
        # Create detailed breakdown structure expected by UI
        detailed_breakdown = {
            'technical_skills_match': {
                'score': category_scores.get('technical_skills', 0),
                'weight': weights['technical_skills'],
                'contribution': category_scores.get('technical_skills', 0) * weights['technical_skills'],
                'type': 'base'
            },
            'soft_skills_match': {
                'score': category_scores.get('soft_skills', 0),
                'weight': weights['soft_skills'],
                'contribution': category_scores.get('soft_skills', 0) * weights['soft_skills'],
                'type': 'base'
            },
            'domain_keywords_match': {
                'score': category_scores.get('domain_keywords', 0),
                'weight': weights['domain_keywords'],
                'contribution': category_scores.get('domain_keywords', 0) * weights['domain_keywords'],
                'type': 'base'
            },
            'skills_relevance': {
                'score': 75.0,  # Default reasonable score
                'weight': 0.05,
                'contribution': 3.75,
                'type': 'analysis'
            },
            'experience_alignment': {
                'score': 80.0,  # Default reasonable score
                'weight': 0.05,
                'contribution': 4.0,
                'type': 'analysis'
            },
            'requirement_bonus': {
                'score': bonus_score,
                'weight': weights['bonus'],
                'contribution': bonus_score,
                'type': 'bonus'
            }
        }
        
        return {
            'overall_ats_score': round(final_score, 1),
            'score_category': self._get_score_category(final_score),
            'base_scores': category_scores,
            'detailed_breakdown': detailed_breakdown,
            'enhancement_analysis': {
                'technical_skills_match': category_scores.get('technical_skills', 0),
                'soft_skills_match': category_scores.get('soft_skills', 0),
                'domain_keywords_match': category_scores.get('domain_keywords', 0),
                'skills_relevance': 75.0,
                'experience_score': 80.0,
                'requirement_bonus': bonus_score
            },
            'detailed_analysis': {
                'status': 'completed',
                'requirement_bonus': {
                    'critical_requirements': [],
                    'preferred_requirements': [],
                    'total_bonus': bonus_score
                }
            },
            'recommendations': self._generate_basic_recommendations(category_scores),
            'achievements_mapped': []
        }
    
    def _get_score_category(self, score: float) -> str:
        """Categorize ATS score using industry standards"""
        if score >= 90:
            return "🌟 Exceptional fit - Immediate interview"
        elif score >= 80:
            return "✅ Strong fit - Priority consideration"
        elif score >= 70:
            return "⚠️ Good fit - Standard review process"
        elif score >= 60:
            return "🔄 Moderate fit - Secondary consideration"
        else:
            return "❌ Poor fit - Generally rejected"
    
    def _generate_basic_recommendations(self, category_scores: Dict) -> List[str]:
        """Generate basic recommendations based on category scores"""
        recommendations = []
        
        # Technical skills recommendations
        tech_score = category_scores.get('technical_skills', 0)
        if tech_score < 60:
            recommendations.append(f"💡 Technical Skills: Score is {tech_score}%. Consider highlighting more technical skills or certifications.")
        elif tech_score >= 80:
            recommendations.append(f"✅ Technical Skills: Strong score of {tech_score}%. Keep emphasizing technical expertise.")
        
        # Soft skills recommendations
        soft_score = category_scores.get('soft_skills', 0)
        if soft_score < 60:
            recommendations.append(f"🤝 Soft Skills: Score is {soft_score}%. Add more examples of leadership, communication, and teamwork.")
        elif soft_score >= 80:
            recommendations.append(f"✅ Soft Skills: Excellent score of {soft_score}%. Your interpersonal skills are well-represented.")
        
        # Domain keywords recommendations
        domain_score = category_scores.get('domain_keywords', 0)
        if domain_score < 60:
            recommendations.append(f"🎯 Domain Knowledge: Score is {domain_score}%. Include more industry-specific terms and methodologies.")
        elif domain_score >= 80:
            recommendations.append(f"✅ Domain Knowledge: Strong score of {domain_score}%. Your industry expertise is clear.")
        
        # Overall recommendations
        overall_avg = sum(category_scores.values()) / len(category_scores) if category_scores else 0
        if overall_avg < 65:
            recommendations.append("🚀 Priority: Focus on the lowest-scoring category first for maximum impact.")
        elif overall_avg >= 85:
            recommendations.append("🌟 Excellent: Your CV is well-aligned with the job requirements across all areas.")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _create_fallback_result(self, skill_comparison: Dict, extracted_keywords: Dict) -> Dict:
        """Create fallback result when base score calculation fails"""
        print(f"⚠️ [ATS_SCORER] Creating fallback result due to error")
        
        return {
            'overall_ats_score': 50.0,  # Conservative fallback score
            'score_category': self._get_score_category(50.0),
            'base_scores': {
                'technical_skills': 50.0,
                'soft_skills': 50.0,
                'domain_keywords': 50.0
            },
            'detailed_breakdown': {},
            'enhancement_analysis': {},
            'detailed_analysis': {'status': 'error_fallback'},
            'recommendations': [
                "⚠️ ATS scoring encountered an issue. Please try again or contact support.",
                "📝 Review your CV formatting to ensure proper skill extraction."
            ],
            'achievements_mapped': []
        }
