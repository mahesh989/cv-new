"""
Enhanced Validation Logic for Tailored CV
Replaces 90% keyword match with quality-focused validation
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

from .enhanced_keyword_integrator import EnhancedKeywordIntegrator

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Structured validation result"""
    passed: bool
    score: float
    issues: List[str]
    warnings: List[str]
    quality_metrics: Dict[str, Any]

class EnhancedCVValidator:
    """Quality-focused CV validation (not just keyword matching)"""
    
    def __init__(self, request_id: str = 'debug'):
        self.min_quality_score = 70  # Changed from 90% keyword match
        self.request_id = request_id
        
        logger.info(f"🔍 [{request_id}] [ENHANCED_VALIDATOR] Initialized with quality score threshold: {self.min_quality_score}")
        
    def validate_tailored_cv(
        self, 
        cv_data: Dict[str, Any],
        original_cv: str,
        recommendations: Dict[str, Any]
    ) -> ValidationResult:
        """Comprehensive CV validation"""
        
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Starting comprehensive CV validation")
        
        issues = []
        warnings = []
        quality_metrics = {}
        
        # 1. Structure Validation
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating structure...")
        structure_score = self._validate_structure(cv_data, issues)
        quality_metrics['structure'] = structure_score
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Structure score: {structure_score:.1f}")
        
        # 2. Content Quality Validation
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating content quality...")
        content_score = self._validate_content_quality(cv_data, issues, warnings)
        quality_metrics['content'] = content_score
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Content score: {content_score:.1f}")
        
        # 3. Keyword Integration Quality (not just count)
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating keyword quality...")
        keyword_score = self._validate_keyword_quality(
            cv_data, 
            original_cv, 
            recommendations, 
            issues, 
            warnings
        )
        quality_metrics['keywords'] = keyword_score
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Keyword score: {keyword_score:.1f}")
        
        # 4. Interview Defensibility Check
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating interview defensibility...")
        defensibility_score = self._validate_defensibility(
            cv_data, 
            original_cv, 
            warnings
        )
        quality_metrics['defensibility'] = defensibility_score
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Defensibility score: {defensibility_score:.1f}")
        
        # 5. Education Selection Validation
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating education selection...")
        education_score = self._validate_education(cv_data, issues)
        quality_metrics['education'] = education_score
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Education score: {education_score:.1f}")
        
        # Calculate overall score (weighted average)
        overall_score = (
            structure_score * 0.20 +
            content_score * 0.25 +
            keyword_score * 0.25 +
            defensibility_score * 0.20 +
            education_score * 0.10
        )
        
        passed = overall_score >= self.min_quality_score and len(issues) == 0
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Overall validation results:")
        logger.info(f"   - Overall Score: {overall_score:.1f}/{100}")
        logger.info(f"   - Passed: {passed}")
        logger.info(f"   - Issues: {len(issues)}")
        logger.info(f"   - Warnings: {len(warnings)}")
        
        if issues:
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Issues found:")
            for issue in issues:
                logger.warning(f"   - {issue}")
        
        if warnings:
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Warnings:")
            for warning in warnings:
                logger.warning(f"   - {warning}")
        
        return ValidationResult(
            passed=passed,
            score=overall_score,
            issues=issues,
            warnings=warnings,
            quality_metrics=quality_metrics
        )
    
    def _validate_structure(self, cv_data: Dict[str, Any], issues: List[str]) -> float:
        """Validate CV structure and required sections"""
        score = 100.0
        
        logger.debug(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating structure...")
        
        # Check profile summary
        if 'profile_summary' not in cv_data or not cv_data['profile_summary']:
            issues.append("Missing profile summary")
            score -= 20
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Missing profile summary (-20 points)")
        elif len(cv_data['profile_summary'].split()) > 50:
            word_count = len(cv_data['profile_summary'].split())
            issues.append(f"Profile summary exceeds 50 words: {word_count} words")
            score -= 15
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Profile summary too long: {word_count} words (-15 points)")
        else:
            word_count = len(cv_data['profile_summary'].split())
            logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Profile summary OK: {word_count} words")
        
        # Check experience count (1-3)
        exp_count = len(cv_data.get('experience', []) or [] or [])
        if exp_count == 0:
            issues.append("No experience entries")
            score -= 30
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] No experience entries (-30 points)")
        elif exp_count > 3:
            issues.append(f"Too many experience entries: {exp_count} (max 3)")
            score -= 15
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Too many experience entries: {exp_count} (-15 points)")
        else:
            logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Experience count OK: {exp_count}")
        
        # Check bullet counts (2-3 per entry)
        for i, exp in enumerate(cv_data.get('experience', []) or [] or []):
            bullet_count = len(exp.get('bullets', []))
            if bullet_count < 2:
                issues.append(f"Experience {i+1} has only {bullet_count} bullets (min 2)")
                score -= 10
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Experience {i+1} insufficient bullets: {bullet_count} (-10 points)")
            elif bullet_count > 3:
                issues.append(f"Experience {i+1} has {bullet_count} bullets (max 3)")
                score -= 10
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Experience {i+1} too many bullets: {bullet_count} (-10 points)")
            else:
                logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Experience {i+1} bullets OK: {bullet_count}")
        
        # Check projects count (0-3)
        proj_count = len(cv_data.get('projects', []) or [] or [])
        if proj_count > 3:
            issues.append(f"Too many projects: {proj_count} (max 3)")
            score -= 10
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Too many projects: {proj_count} (-10 points)")
        else:
            logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Projects count OK: {proj_count}")
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Structure validation complete: {score:.1f}/100")
        return max(0, score)
    
    def _validate_content_quality(
        self, 
        cv_data: Dict[str, Any], 
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Validate content quality (metrics, verbosity, etc.)"""
        score = 100.0
        
        logger.debug(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating content quality...")
        
        # Check bullet quantification
        total_bullets = 0
        quantified_bullets = 0
        verbose_bullets = 0
        
        for exp in cv_data.get('experience', []) or []:
            for bullet in exp.get('bullets', []):
                total_bullets += 1
                
                # Check for metrics
                if self._has_metrics(bullet):
                    quantified_bullets += 1
                
                # Check for verbosity (>30 words)
                word_count = len(bullet.split())
                if word_count > 30:
                    verbose_bullets += 1
                    warnings.append(f"Verbose bullet ({word_count} words): {bullet[:50]}...")
                    logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Verbose bullet: {word_count} words")
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Content analysis: {total_bullets} bullets, {quantified_bullets} quantified, {verbose_bullets} verbose")
        
        # Quantification ratio (aim for 80%+)
        if total_bullets > 0:
            quantification_ratio = (quantified_bullets / total_bullets) * 100
            if quantification_ratio < 50:
                issues.append(f"Only {quantification_ratio:.0f}% of bullets have metrics (min 50%)")
                score -= 25
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Low quantification: {quantification_ratio:.0f}% (-25 points)")
            elif quantification_ratio < 80:
                warnings.append(f"Only {quantification_ratio:.0f}% of bullets have metrics (target 80%+)")
                score -= 10
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Moderate quantification: {quantification_ratio:.0f}% (-10 points)")
            else:
                logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Good quantification: {quantification_ratio:.0f}%")
        
        # Verbosity penalty
        if verbose_bullets > 0:
            verbosity_ratio = (verbose_bullets / total_bullets) * 100
            if verbosity_ratio > 30:
                score -= 15
                warnings.append(f"{verbosity_ratio:.0f}% of bullets are verbose (>30 words)")
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] High verbosity: {verbosity_ratio:.0f}% (-15 points)")
            else:
                logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Acceptable verbosity: {verbosity_ratio:.0f}%")
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Content quality validation complete: {score:.1f}/100")
        return max(0, score)
    
    def _validate_keyword_quality(
        self, 
        cv_data: Dict[str, Any],
        original_cv: str,
        recommendations: Dict[str, Any],
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Validate keyword integration QUALITY (not just presence)"""
        score = 100.0
        
        logger.debug(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating keyword quality...")
        
        # Get critical keywords
        critical_keywords = recommendations.get('critical_gaps', [])
        if not critical_keywords:
            logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] No critical keywords to validate")
            return score
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Validating {len(critical_keywords)} critical keywords")
        
        # Check for Tier 3 violations (should never happen)
        tier3_found = self._detect_tier3_keywords(cv_data, original_cv)
        if tier3_found:
            for kw in tier3_found:
                issues.append(f"Unverifiable keyword added: {kw}")
                score -= 20  # Heavy penalty
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Tier 3 keyword found: {kw} (-20 points)")
        
        # Check Tier 1/2 integration (quality-focused)
        cv_text = self._extract_cv_text(cv_data)
        
        tier1_integrated = 0
        tier1_total = 0
        tier2_integrated = 0
        tier2_total = 0
        
        integrator = EnhancedKeywordIntegrator(original_cv, self.request_id)
        
        for keyword in critical_keywords:
            classification = integrator.classify_keyword(keyword)
            
            if classification.tier == 1:
                tier1_total += 1
                if keyword.lower() in cv_text.lower():
                    tier1_integrated += 1
                    logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Tier 1 keyword integrated: {keyword}")
                else:
                    logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Tier 1 keyword missing: {keyword}")
            
            elif classification.tier == 2:
                tier2_total += 1
                if keyword.lower() in cv_text.lower():
                    tier2_integrated += 1
                    logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Tier 2 keyword integrated: {keyword}")
                else:
                    logger.info(f"ℹ️ [{self.request_id}] [ENHANCED_VALIDATOR] Tier 2 keyword not integrated: {keyword}")
        
        # Tier 1 should have high integration (80%+) - including adaptations
        if tier1_total > 0:
            tier1_rate = (tier1_integrated / tier1_total) * 100
            if tier1_rate < 80:
                warnings.append(f"Only {tier1_rate:.0f}% of Tier 1 keywords integrated (target 80%+)")
                score -= 15
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Low Tier 1 integration: {tier1_rate:.0f}% (-15 points)")
            else:
                logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Good Tier 1 integration: {tier1_rate:.0f}%")
        
        # Check for Tier 1 adaptations (modifications without evidence)
        tier1_adaptations = integrator.validate_keyword_integration(critical_keywords).get('tier1_adapt', [])
        if tier1_adaptations:
            logger.info(f"🔧 [{self.request_id}] [ENHANCED_VALIDATOR] Tier 1 adaptations available: {len(tier1_adaptations)} keywords")
            # Generate modifications for these keywords
            modifications = integrator.generate_tier1_modifications(tier1_adaptations)
            logger.info(f"🔧 [{self.request_id}] [ENHANCED_VALIDATOR] Generated {len(modifications)} Tier 1 modifications")
        
        # Tier 2 is optional (no penalty)
        if tier2_total > 0:
            tier2_rate = (tier2_integrated / tier2_total) * 100
            if tier2_rate < 50:
                warnings.append(f"Only {tier2_rate:.0f}% of Tier 2 keywords integrated")
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Low Tier 2 integration: {tier2_rate:.0f}%")
            else:
                logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Good Tier 2 integration: {tier2_rate:.0f}%")
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Keyword quality validation complete: {score:.1f}/100")
        return max(0, score)
    
    def _validate_defensibility(
        self, 
        cv_data: Dict[str, Any],
        original_cv: str,
        warnings: List[str]
    ) -> float:
        """Check if CV content is interview-defensible"""
        score = 100.0
        
        logger.debug(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating interview defensibility...")
        
        # Extract skills from tailored CV
        tailored_skills = set()
        for category_data in cv_data.get('skills', []) or []:
            tailored_skills.update([s.lower() for s in category_data.get('skills', [])])
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Found {len(tailored_skills)} skills in tailored CV")
        
        # Extract skills from original CV (basic keyword extraction)
        original_skills = set(re.findall(r'\b[a-z]+\b', original_cv.lower()))
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Found {len(original_skills)} skills in original CV")
        
        # Check for suspicious additions
        suspicious = []
        for skill in tailored_skills:
            # If skill not in original and looks specific
            if skill not in original_skills and len(skill) > 3:
                # Check if it's a specific tool
                if any(specific in skill for specific in [
                    'postgresql', 'mysql', 'mongodb', 
                    'kubernetes', 'terraform', 'ansible',
                    'power bi', 'tableau server'
                ]):
                    suspicious.append(skill)
        
        if suspicious:
            for skill in suspicious[:3]:  # Show first 3
                warnings.append(f"Potentially unverifiable skill: {skill}")
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Suspicious skill: {skill}")
            score -= min(30, len(suspicious) * 10)
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Found {len(suspicious)} suspicious skills (-{min(30, len(suspicious) * 10)} points)")
        else:
            logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] No suspicious skills found")
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Defensibility validation complete: {score:.1f}/100")
        return max(0, score)
    
    def _validate_education(self, cv_data: Dict[str, Any], issues: List[str]) -> float:
        """Validate education selection and overqualification"""
        score = 100.0
        
        logger.debug(f"🔍 [{self.request_id}] [ENHANCED_VALIDATOR] Validating education selection...")
        
        education = cv_data.get('education', []) or []
        education_count = len(education)
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Education count: {education_count}")
        
        if education_count > 3:
            issues.append(f"Too many education entries: {education_count} (max 3)")
            score -= 15
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Too many education entries: {education_count} (-15 points)")
        
        # Check for overqualification
        advanced_degrees = []
        for edu in education:
            degree = edu.get('degree', '').lower()
            if any(term in degree for term in ['phd', 'doctorate', 'master', 'mba']):
                advanced_degrees.append(degree)
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Advanced degrees found: {len(advanced_degrees)}")
        
        if len(advanced_degrees) > 2:
            issues.append(f"Multiple advanced degrees detected: {len(advanced_degrees)} (overqualification risk)")
            score -= 20
            logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_VALIDATOR] Overqualification risk: {len(advanced_degrees)} advanced degrees (-20 points)")
        else:
            logger.info(f"✅ [{self.request_id}] [ENHANCED_VALIDATOR] Education selection OK")
        
        logger.info(f"📊 [{self.request_id}] [ENHANCED_VALIDATOR] Education validation complete: {score:.1f}/100")
        return max(0, score)
    
    def _has_metrics(self, bullet: str) -> bool:
        """Check if bullet contains metrics"""
        # Look for numbers, percentages, dollar amounts, etc.
        metric_patterns = [
            r'\d+%',  # percentages
            r'\$\d+',  # dollar amounts
            r'\d+[KMB]',  # K, M, B suffixes
            r'\d+\.\d+',  # decimal numbers
            r'\d+',  # any number
        ]
        
        for pattern in metric_patterns:
            if re.search(pattern, bullet):
                return True
        return False
    
    def _detect_tier3_keywords(self, cv_data: Dict[str, Any], original_cv: str) -> List[str]:
        """Detect Tier 3 keywords that shouldn't be added"""
        tier3_keywords = []
        
        # Extract all text from CV
        cv_text = self._extract_cv_text(cv_data)
        cv_text_lower = cv_text.lower()
        
        # Check for specific Tier 3 patterns
        tier3_patterns = [
            'postgresql', 'mysql', 'oracle', 'mongodb',
            'kubernetes', 'terraform', 'ansible',
            'power bi', 'tableau server', 'databricks',
            'scrum master', 'pmp', 'safe'
        ]
        
        for pattern in tier3_patterns:
            if pattern in cv_text_lower and pattern not in original_cv.lower():
                tier3_keywords.append(pattern)
        
        return tier3_keywords
    
    def _extract_cv_text(self, cv_data: Dict[str, Any]) -> str:
        """Extract all text content from CV data"""
        text_parts = []
        
        # Extract from profile summary
        if cv_data.get('profile_summary'):
            text_parts.append(cv_data['profile_summary'])
        
        # Extract from experience bullets
        for exp in cv_data.get('experience', []) or []:
            for bullet in exp.get('bullets', []):
                text_parts.append(bullet)
        
        # Extract from project bullets
        for proj in cv_data.get('projects', []) or []:
            for bullet in proj.get('bullets', []):
                text_parts.append(bullet)
        
        # Extract from skills
        for skill_cat in cv_data.get('skills', []) or []:
            for skill in skill_cat.get('skills', []):
                text_parts.append(skill)
        
        return ' '.join(text_parts)
