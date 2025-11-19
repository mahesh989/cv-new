"""
AI Recommendation Parser

Parses the markdown-formatted recommendation content from AI recommendation files
and extracts structured data for CV tailoring.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RecommendationParser:
    """
    Parser for AI-generated recommendation content in markdown format
    """
    
    @staticmethod
    def parse_recommendation_file(file_path: str) -> Dict[str, Any]:
        """
        Parse a recommendation file and extract structured data
        Prioritizes actionable_guidance (v2.0+) > structured_recommendations (v2.0) > markdown (v1.0)
        
        Args:
            file_path: Path to the recommendation JSON file
            
        Returns:
            Structured recommendation data compatible with RecommendationAnalysis model
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            company = data.get('company', 'Unknown')
            metadata = data.get('metadata', {})
            format_version = metadata.get('format_version', '1.0')
            has_actionable = bool(data.get('actionable_guidance'))
            has_structured = metadata.get('has_structured_data', False)
            
            # PRIORITY 1: Use actionable_guidance if available (v2.0+ - preferred method)
            if has_actionable and 'actionable_guidance' in data:
                logger.info(f"✅ [PARSER] Using actionable_guidance (v{format_version}) for {company}")
                parsed_data = RecommendationParser.parse_actionable_guidance(
                    data['actionable_guidance'], 
                    data.get('structured_recommendations', {}),
                    company
                )
            
            # PRIORITY 2: Use structured_recommendations (v2.0)
            elif has_structured and 'structured_recommendations' in data:
                logger.info(f"✅ [PARSER] Using structured_recommendations (v{format_version}) for {company}")
                parsed_data = RecommendationParser.parse_structured_recommendations(
                    data['structured_recommendations'], company
                )
            
            # PRIORITY 3: Fallback to markdown parsing (v1.0)
            else:
                logger.info(f"⚠️ [PARSER] Falling back to markdown parsing (v{format_version}) for {company}")
                recommendation_content = data.get('recommendation_content', '')
                parsed_data = RecommendationParser.parse_markdown_content(
                    recommendation_content, company
                )
            
            # Add metadata (common to all formats)
            parsed_data['generated_at'] = data.get('generated_at')
            parsed_data['ai_model_info'] = data.get('ai_model_info', {})
            parsed_data['format_version'] = format_version
            
            logger.info(f"✅ Parsed recommendation for {company} (format: {format_version})")
            return parsed_data
            
        except Exception as e:
            logger.error(f"❌ Failed to parse recommendation file {file_path}: {e}")
            raise
    
    @staticmethod
    def parse_markdown_content(content: str, company: str) -> Dict[str, Any]:
        """
        Parse markdown recommendation content into structured data
        
        Args:
            content: Markdown recommendation content
            company: Company name
            
        Returns:
            Structured data compatible with CV tailoring service
        """
        # Extract ATS score
        current_ats_score = RecommendationParser._extract_ats_score(content)
        target_ats_score = RecommendationParser._extract_target_score(content)
        
        # Extract missing keywords - improved extraction
        missing_technical_skills = RecommendationParser._extract_technical_skills(content)
        missing_soft_skills = RecommendationParser._extract_soft_skills(content)
        missing_keywords = RecommendationParser._extract_domain_keywords(content)
        
        # Extract enhancement recommendations
        technical_enhancements = RecommendationParser._extract_high_impact_changes(content)
        keyword_integration = missing_keywords + missing_technical_skills
        
        # Extract priority gaps - use actual keyword gaps instead of category labels
        # Critical gaps should contain actual keywords, not category descriptions
        critical_gaps = missing_keywords + missing_technical_skills[:3] + missing_soft_skills[:3]
        
        # Extract improvement recommendations from sections
        important_gaps = RecommendationParser._extract_section_items(
            content, "Optimization Opportunities"
        )
        nice_to_have = RecommendationParser._extract_section_items(
            content, "Fine-Tuning"
        )
        
        # Extract company values and industry terminology from content
        company_values = RecommendationParser._extract_company_values(content)
        industry_terminology = missing_keywords[:5]  # Use domain keywords as industry terms
        
        return {
            'company': company,
            'job_title': RecommendationParser._extract_job_title(content, company),
            'missing_technical_skills': missing_technical_skills,
            'missing_soft_skills': missing_soft_skills,
            'missing_keywords': missing_keywords,
            'technical_enhancements': technical_enhancements,
            'soft_skill_improvements': missing_soft_skills,
            'keyword_integration': keyword_integration,
            'company_values': company_values,
            'industry_terminology': industry_terminology,
            'culture_alignment': RecommendationParser._extract_culture_alignment(content),
            'critical_gaps': critical_gaps,
            'important_gaps': important_gaps,
            'nice_to_have': nice_to_have,
            'match_score': current_ats_score,
            'target_score': target_ats_score,
            'raw_recommendation_content': content
        }
    
    @staticmethod
    def parse_actionable_guidance(
        actionable: Dict[str, Any], 
        structured: Dict[str, Any],
        company: str
    ) -> Dict[str, Any]:
        """
        Parse v2.0+ actionable_guidance into RecommendationAnalysis format
        
        This is the PREFERRED parsing method - uses pre-flattened, easy-to-access data.
        
        Args:
            actionable: The actionable_guidance section
            structured: The structured_recommendations section (for fallback data like ATS scores)
            company: Company name
            
        Returns:
            Dict compatible with RecommendationAnalysis model
        """
        
        # Extract Tier 1 keywords (add immediately)
        tier1 = actionable.get('tier1_add_immediately', {})
        tier1_technical = [item.get('keyword', '') for item in tier1.get('technical', []) if item.get('keyword')]
        tier1_soft = [item.get('keyword', '') for item in tier1.get('soft', []) if item.get('keyword')]
        tier1_domain = [item.get('keyword', '') for item in tier1.get('domain', []) if item.get('keyword')]
        
        # Extract Tier 2 keywords (add with evidence)
        tier2 = actionable.get('tier2_add_with_evidence', {})
        tier2_technical = [item.get('keyword', '') for item in tier2.get('technical', []) if item.get('keyword')]
        tier2_soft = [item.get('keyword', '') for item in tier2.get('soft', []) if item.get('keyword')]
        tier2_domain = [item.get('keyword', '') for item in tier2.get('domain', []) if item.get('keyword')]
        
        # Extract Tier 3 keywords (never add)
        tier3_keywords = actionable.get('tier3_never_add', [])
        
        # Extract strategic positioning
        strategic = actionable.get('strategic_positioning', {})
        
        # Extract experience optimization
        experience = actionable.get('experience_optimization', {})
        
        # Extract achievements
        achievements = actionable.get('achievements', {})
        
        # Extract implementation plan
        implementation = actionable.get('implementation_plan', {})
        
        # Extract messaging
        messaging = actionable.get('messaging', {})
        
        # Get ATS scores from structured data (fallback)
        exec_summary = structured.get('executive_summary', {})
        current_ats_score = int(exec_summary.get('current_ats_score', 65))
        target_ats_score = int(exec_summary.get('target_score', 85))
        
        # Extract job title from primary objective or use default
        primary_objective = exec_summary.get('primary_objective', '')
        job_title = RecommendationParser._extract_job_title_from_objective(
            primary_objective, company
        )
        
        # Combine keywords for backward compatibility
        missing_technical_skills = tier1_technical + tier2_technical
        missing_soft_skills = tier1_soft + tier2_soft
        missing_keywords = tier1_domain + tier2_domain
        
        # Extract technical enhancements from experience optimization
        technical_enhancements = experience.get('strengths_to_highlight', [])
        
        # Convert tier1 objects to ensure all values are strings
        tier1_processed = {}
        for cat in ['technical', 'soft', 'domain']:
            tier1_processed[cat] = [
                {
                    k: str(v) if not isinstance(v, str) else v
                    for k, v in item.items()
                }
                for item in tier1.get(cat, [])
            ]
        
        # Convert tier2 objects to ensure all values are strings (especially evidence_required boolean)
        tier2_processed = {}
        for cat in ['technical', 'soft', 'domain']:
            tier2_processed[cat] = [
                {
                    k: str(v) if not isinstance(v, str) else v
                    for k, v in item.items()
                }
                for item in tier2.get(cat, [])
            ]
        
        return {
            'company': company,
            'job_title': job_title,
            
            # BACKWARD COMPATIBLE: Core fields
            'missing_technical_skills': missing_technical_skills,
            'missing_soft_skills': missing_soft_skills,
            'missing_keywords': missing_keywords,
            'technical_enhancements': technical_enhancements,
            'soft_skill_improvements': missing_soft_skills,
            'keyword_integration': missing_technical_skills + missing_keywords,
            'critical_gaps': tier1_technical[:3] + tier1_soft[:3] + tier1_domain[:3],  # Tier 1 = critical
            'important_gaps': tier2_technical[:3] + tier2_soft[:3],  # Tier 2 = important
            'nice_to_have': [],
            'match_score': current_ats_score,
            'target_score': target_ats_score,
            
            # NEW: Tier-based fields with full metadata (all values converted to strings)
            'tier1_keywords': tier1_processed,
            'tier2_keywords': tier2_processed,
            'tier3_avoid': tier3_keywords,
            
            # NEW: Strategic guidance (ready to use!)
            'strategic_positioning': {
                'emphasis_areas': strategic.get('emphasis_areas', []),
                'de_emphasize': strategic.get('de_emphasize', []),
                'bridging_statements': strategic.get('bridging_statements', []),
                'strategy': strategic.get('strategy', '')
            },
            
            # NEW: Experience optimization
            'experience_optimization': {
                'strengths_to_highlight': experience.get('strengths_to_highlight', []),
                'gaps_to_address': experience.get('gaps_to_address', [])
            },
            
            # NEW: Achievements
            'achievements': {
                'transferable_experience': achievements.get('transferable_experience', []),
                'core_competencies': achievements.get('core_competencies', [])
            },
            
            # NEW: Implementation roadmap
            'implementation_plan': {
                'phase1_quick_wins': implementation.get('phase1_quick_wins', []),
                'phase2_evidence_based': implementation.get('phase2_evidence_based', []),
                'phase3_positioning': implementation.get('phase3_positioning', [])
            },
            
            # NEW: Messaging guidance
            'messaging': {
                'key_messages': messaging.get('key_messages', []),
                'avoid_messages': messaging.get('avoid_messages', [])
            },
            
            # Metadata
            'company_values': [],
            'industry_terminology': missing_keywords[:5] if missing_keywords else [],
            'culture_alignment': [strategic.get('strategy', '')] if strategic.get('strategy') else [],
            'raw_recommendation_content': json.dumps(actionable, indent=2)
        }
    
    @staticmethod
    def parse_structured_recommendations(
        structured_data: Dict[str, Any], 
        company: str
    ) -> Dict[str, Any]:
        """
        Parse structured JSON recommendations (v2.0 format) into RecommendationAnalysis format
        
        Args:
            structured_data: The structured_recommendations JSON object
            company: Company name
            
        Returns:
            Structured data compatible with RecommendationAnalysis model
        """
        # Extract executive summary
        exec_summary = structured_data.get('executive_summary', {})
        current_ats_score = int(exec_summary.get('current_ats_score', 65))
        target_ats_score = int(exec_summary.get('target_score', 85))
        
        # Extract keyword integration (tier-based)
        keyword_integration = structured_data.get('keyword_integration', {})
        
        # Extract Tier 1 keywords (safe to integrate immediately)
        tier1 = keyword_integration.get('tier1_integrate_immediately', {})
        tier1_technical = [kw.get('keyword', '') for kw in tier1.get('technical', []) if kw.get('keyword')]
        tier1_soft = [kw.get('keyword', '') for kw in tier1.get('soft', []) if kw.get('keyword')]
        tier1_domain = [kw.get('keyword', '') for kw in tier1.get('domain', []) if kw.get('keyword')]
        
        # Extract Tier 2 keywords (add with evidence)
        tier2 = keyword_integration.get('tier2_add_with_evidence', {})
        tier2_technical = [kw.get('keyword', '') for kw in tier2.get('technical', []) if kw.get('keyword')]
        tier2_soft = [kw.get('keyword', '') for kw in tier2.get('soft', []) if kw.get('keyword')]
        tier2_domain = [kw.get('keyword', '') for kw in tier2.get('domain', []) if kw.get('keyword')]
        
        # Extract Tier 3 keywords (never add - for reference)
        tier3 = keyword_integration.get('tier3_never_add', {})
        tier3_keywords = []
        for category in ['technical', 'soft', 'domain']:
            tier3_keywords.extend([
                kw.get('keyword', '') for kw in tier3.get(category, []) if kw.get('keyword')
            ])
        
        # Combine all missing keywords (Tier 1 + Tier 2)
        missing_technical_skills = tier1_technical + tier2_technical
        missing_soft_skills = tier1_soft + tier2_soft
        missing_keywords = tier1_domain + tier2_domain
        
        # Extract priority gaps
        priority_gaps = structured_data.get('priority_gaps', {})
        immediate_action = priority_gaps.get('immediate_action', {})
        
        # Build critical gaps (Tier 1 keywords are most critical)
        critical_gaps = tier1_technical[:3] + tier1_soft[:3] + tier1_domain[:3]
        
        # Extract important gaps from optimization opportunities
        optimization = priority_gaps.get('optimization_opportunities', {})
        important_gaps = []
        if optimization.get('technical_depth', 0) < 75:
            important_gaps.append("Improve technical depth")
        if optimization.get('experience_alignment', 0) < 75:
            important_gaps.append("Better align experience with job requirements")
        if optimization.get('industry_fit', 0) < 75:
            important_gaps.append("Improve industry fit")
        
        # Extract nice-to-have from implementation roadmap
        roadmap = structured_data.get('implementation_roadmap', {})
        nice_to_have = roadmap.get('phase3_positioning', [])
        
        # Extract experience reframing guidance
        experience_reframing = structured_data.get('experience_reframing', {})
        industry_transition = experience_reframing.get('industry_transition', {})
        technical_showcase = experience_reframing.get('technical_showcase', {})
        
        # Extract technical enhancements (from technical showcase strengths)
        technical_enhancements = technical_showcase.get('strengths_to_highlight', [])
        
        # Extract company values and culture alignment from tone_and_style
        tone_style = structured_data.get('tone_and_style', {})
        key_messages = tone_style.get('key_messages', [])
        
        # Infer company values from key messages
        company_values = []
        if any('social impact' in msg.lower() for msg in key_messages):
            company_values.append('social impact')
        if any('data-driven' in msg.lower() for msg in key_messages):
            company_values.append('data-driven decisions')
        if any('collaboration' in msg.lower() for msg in key_messages):
            company_values.append('collaboration')
        
        # Extract industry terminology (use Tier 1 domain keywords)
        industry_terminology = tier1_domain[:5]
        
        # Extract culture alignment from experience reframing
        culture_alignment = []
        emphasis_areas = industry_transition.get('emphasis_areas', [])
        culture_alignment.extend(emphasis_areas[:3])
        
        # Extract job title (try to infer from executive summary or use default)
        primary_objective = exec_summary.get('primary_objective', '')
        job_title = RecommendationParser._extract_job_title_from_objective(
            primary_objective, company
        )
        
        # Build keyword integration list (all Tier 1 + Tier 2)
        keyword_integration_list = missing_technical_skills + missing_keywords
        
        return {
            'company': company,
            'job_title': job_title,
            'missing_technical_skills': missing_technical_skills,
            'missing_soft_skills': missing_soft_skills,
            'missing_keywords': missing_keywords,
            'technical_enhancements': technical_enhancements,
            'soft_skill_improvements': missing_soft_skills,  # Same as missing for now
            'keyword_integration': keyword_integration_list,
            'company_values': company_values if company_values else None,
            'industry_terminology': industry_terminology if industry_terminology else None,
            'culture_alignment': culture_alignment if culture_alignment else None,
            'critical_gaps': critical_gaps if critical_gaps else [],
            'important_gaps': important_gaps if important_gaps else [],
            'nice_to_have': nice_to_have if nice_to_have else [],
            'match_score': current_ats_score,
            'target_score': target_ats_score,
            'raw_recommendation_content': None  # Not available in structured format
        }
    
    @staticmethod
    def _extract_job_title_from_objective(objective: str, company: str) -> str:
        """Extract or infer job title from primary objective"""
        if not objective:
            return f'Position at {company.replace("_", " ")}'
        
        # Try to extract job title from objective
        # Example: "Transition to Data Analyst role" -> "Data Analyst"
        title_patterns = [
            r'(?:to|as|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:role|position|job)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:role|position|job)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, objective, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fallback: infer from objective keywords
        if 'data' in objective.lower() and 'analyst' in objective.lower():
            return 'Data Analyst'
        if 'senior' in objective.lower() or 'lead' in objective.lower():
            if 'data' in objective.lower():
                return 'Senior Data Analyst'
        
        return f'Position at {company.replace("_", " ")}'
    
    @staticmethod
    def _extract_ats_score(content: str) -> int:
        """Extract current ATS score from content"""
        match = re.search(r'Current ATS Score:\*\*\s*(\d+(?:\.\d+)?)', content)
        if match:
            return int(float(match.group(1)))
        return 65  # Default fallback
    
    @staticmethod
    def _extract_target_score(content: str) -> int:
        """Extract target ATS score from content"""
        match = re.search(r'Target Score:\*\*\s*(\d+(?:-\d+)?)', content)
        if match:
            target_range = match.group(1)
            if '-' in target_range:
                # Take the higher number from range like "75-80"
                return int(target_range.split('-')[1])
            return int(target_range)
        return 85  # Default fallback
    
    @staticmethod
    def _extract_section_items(content: str, section_title: str) -> List[str]:
        """Extract bullet point items from a specific section"""
        items = []
        
        # Look for section with title
        escaped_title = re.escape(section_title)
        section_pattern = r'\*\*' + escaped_title + r'[^:]*:\*\*([^#]*?)(?=\n\*\*|\n##|$)'
        match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            section_content = match.group(1)
            # Extract bullet points
            bullet_points = re.findall(r'^[-•]\s*(.+)$', section_content, re.MULTILINE)
            items.extend([item.strip() for item in bullet_points if item.strip()])
        
        # Special handling for extracting quoted keywords
        if "Keywords" in section_title or "Skills" in section_title:
            # Extract keywords in quotes from the content
            quoted_keywords = re.findall(r'"([^"]+)"', section_content if match else content)
            # Filter out non-keyword items (e.g., sentences or descriptions)
            keywords_only = [kw for kw in quoted_keywords if len(kw) < 50 and not any(c in kw for c in ['.', ':', '%'])]
            items.extend(keywords_only)
            # Remove duplicates while preserving order
            items = list(dict.fromkeys(items))
        
        return items
    
    @staticmethod
    def _extract_high_impact_changes(content: str) -> List[str]:
        """Extract high-impact changes from the roadmap"""
        changes = []
        
        # Look for High-Impact Changes section
        match = re.search(r'\*\*High-Impact Changes[^:]*:\*\*([^*]*?)(?=\n\*\*|\n##|$)', content, re.DOTALL)
        if match:
            section_content = match.group(1)
            # Extract numbered items
            numbered_items = re.findall(r'\d+\.\s*\*\*([^*]+)\*\*', section_content)
            changes.extend([item.strip() for item in numbered_items])
        
        return changes
    
    @staticmethod
    def _extract_job_title(content: str, company: str) -> str:
        """Extract or infer job title from content"""
        # Try to extract from title
        escaped_company = re.escape(company)
        title_match = re.search(r'CV Tailoring Strategy Report for ' + escaped_company, content)
        
        # If no specific title found, infer from content
        if 'data' in content.lower():
            if 'senior' in content.lower() or 'lead' in content.lower():
                return 'Senior Data Analyst'
            return 'Data Analyst'
        
        return 'Position at ' + company.replace('_', ' ')
    
    @staticmethod
    def _extract_company_values(content: str) -> List[str]:
        """Extract company values from content context"""
        values = []
        
        # Look for humanitarian, non-profit context
        if any(term in content.lower() for term in ['humanitarian', 'non-profit', 'unhcr', 'social']):
            values.extend(['humanitarian aid', 'social impact', 'community service', 'global citizenship'])
        
        # Look for data-driven context
        if any(term in content.lower() for term in ['data-driven', 'analytics', 'insights']):
            values.extend(['data-driven decisions', 'analytical thinking', 'evidence-based approaches'])
        
        # Look for collaboration mentions
        if any(term in content.lower() for term in ['collaboration', 'team', 'stakeholder']):
            values.extend(['collaboration', 'teamwork', 'stakeholder engagement'])
        
        return list(set(values))  # Remove duplicates
    
    @staticmethod
    def _extract_culture_alignment(content: str) -> List[str]:
        """Extract culture alignment suggestions"""
        alignment = []
        
        # Extract from Experience Reframing Strategy section
        match = re.search(r'Experience Reframing Strategy([^#]*?)(?=##|$)', content, re.DOTALL)
        if match:
            section_content = match.group(1)
            # Look for specific cultural mentions
            if 'humanitarian' in section_content.lower():
                alignment.append('commitment to humanitarian causes')
            if 'social impact' in section_content.lower():
                alignment.append('social impact orientation')
            if 'data for good' in section_content.lower():
                alignment.append('data for social good mindset')
            if 'leadership' in section_content.lower():
                alignment.append('leadership potential')
            if 'collaboration' in section_content.lower():
                alignment.append('collaborative approach')
        
        return alignment
    
    @staticmethod
    def _extract_technical_skills(content: str) -> List[str]:
        """Extract missing technical skills from recommendation content"""
        skills = []
        
        # Look for Technical Skills Enhancement section
        match = re.search(r'Technical Skills Enhancement[^:]*:.*?Keywords to Emphasize[^:]*:([^#]*?)(?=\n\*\*|\n##|$)', 
                         content, re.DOTALL | re.IGNORECASE)
        if match:
            section_content = match.group(1)
            # Extract keywords in quotes
            quoted_skills = re.findall(r'"([^"]+)"', section_content)
            # Clean up extracted skills - remove trailing punctuation
            for skill in quoted_skills:
                clean_skill = skill.strip().rstrip('.,;:')
                if len(clean_skill) < 50 and clean_skill:
                    skills.append(clean_skill)
        
        # Also look for VBA, Data Warehouse, etc. mentioned explicitly
        technical_keywords = ['VBA', 'Data Warehouse', 'DWH', 'Data Modelling', 'Querying', 
                             'Data Extraction', 'Analytical Models', 'Segmentation Strategies']
        for keyword in technical_keywords:
            if keyword in content and keyword not in [s.rstrip('.,;:') for s in skills]:
                skills.append(keyword)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(skills))
    
    @staticmethod
    def _extract_soft_skills(content: str) -> List[str]:
        """Extract missing soft skills from recommendation content"""
        skills = []
        
        # Look for Soft Skills Optimization section
        match = re.search(r'Soft Skills Optimization[^:]*:.*?Soft Skills to Highlight[^:]*:([^#]*?)(?=\n\*\*|\n##|$)', 
                         content, re.DOTALL | re.IGNORECASE)
        if match:
            section_content = match.group(1)
            # Extract keywords in quotes
            quoted_skills = re.findall(r'"([^"]+)"', section_content)
            # Clean up extracted skills - remove trailing punctuation
            for skill in quoted_skills:
                clean_skill = skill.strip().rstrip('.,;:')
                if len(clean_skill) < 50 and clean_skill:
                    skills.append(clean_skill)
        
        # Also look for specific soft skills mentioned
        soft_keywords = ['Collaborative', 'Detail-oriented', 'Motivated', 'Analytical', 
                        'Inclusive', 'Organised', 'Results-Driven', 'Stakeholder Management']
        for keyword in soft_keywords:
            if keyword in content and keyword not in [s.rstrip('.,;:') for s in skills]:
                skills.append(keyword)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(skills))
    
    @staticmethod
    def _extract_domain_keywords(content: str) -> List[str]:
        """Extract missing domain keywords from recommendation content"""
        keywords = []
        
        # Look for Critical Missing Keywords section and Integration Points
        patterns = [
            r'Critical Missing Keywords[^:]*:.*?Integration Points[^:]*:([^#]*?)(?=\n\*\*|\n##|$)',
            r'Domain Keywords[^:]*:.*?Add[^:]*:([^#]*?)(?=\n\*\*|\n##|$)',
            r'Emphasize[^:]*:([^#]*?)(?=\n\*\*|\n##|$)',
            r'Safe to Add[^:]*:([^#]*?)(?=\n\*\*|\n##|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(1)
                # Extract keywords in quotes and bullet points
                quoted_keywords = re.findall(r'"([^"]+)"', section_content)
                bullet_keywords = re.findall(r'[-•]\s*([A-Za-z\s]+(?:Analytics|Intelligence|Decision-Making|Efficiency|Management|Communication|Problem-Solving|Adaptability|Time Management|Collaboration|Thinking))', section_content)
                
                # Combine both types of keywords
                all_keywords = quoted_keywords + bullet_keywords
                
                # Clean up extracted keywords - remove trailing punctuation
                for kw in all_keywords:
                    clean_kw = kw.strip().rstrip('.,;:')
                    if len(clean_kw) < 50 and clean_kw and clean_kw not in keywords:
                        keywords.append(clean_kw)
        
        # Extract keywords that are explicitly recommended (Emphasize, Safe to Add)
        # and EXCLUDE keywords that are explicitly avoided
        emphasize_pattern = r'Emphasize[^:]*:([^#]*?)(?=\n\*\*|\n##|$)'
        safe_to_add_pattern = r'Safe to Add[^:]*:([^#]*?)(?=\n\*\*|\n##|$)'
        avoid_pattern = r'Avoid[^:]*:([^#]*?)(?=\n\*\*|\n##|$)'
        
        # First, get the avoided keywords to exclude them
        avoided_keywords = set()
        avoid_match = re.search(avoid_pattern, content, re.DOTALL | re.IGNORECASE)
        if avoid_match:
            avoid_content = avoid_match.group(1)
            # Extract all keywords from avoid section
            avoided_items = re.findall(r'([A-Za-z\s]+(?:Campaigns|Fundraising|Management|Marketing|Stakeholder|Critical|Thinking|Creativity|Problem-Solving|Communication|Analytics|Intelligence|Decision-Making|Efficiency|Adaptability|Time Management|Collaboration))', avoid_content)
            for item in avoided_items:
                avoided_keywords.add(item.strip().rstrip('.,;:').lower())
        
        # Extract recommended keywords from Emphasize and Safe to Add sections
        for pattern in [emphasize_pattern, safe_to_add_pattern]:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(1)
                # Extract keywords from these sections
                recommended_keywords = re.findall(r'([A-Za-z\s]+(?:Analytics|Intelligence|Decision-Making|Efficiency|Management|Communication|Problem-Solving|Adaptability|Time Management|Collaboration|Thinking))', section_content)
                for kw in recommended_keywords:
                    clean_kw = kw.strip().rstrip('.,;:')
                    # Only add if not in avoided keywords
                    if (len(clean_kw) < 50 and clean_kw and 
                        clean_kw.lower() not in avoided_keywords and 
                        clean_kw not in [k.rstrip('.,;:') for k in keywords]):
                        keywords.append(clean_kw)
        
        # Remove duplicates while preserving order
        final_keywords = list(dict.fromkeys(keywords))
        
        # Debug logging
        print(f"🔍 [DEBUG] Extracted keywords: {final_keywords}")
        print(f"🔍 [DEBUG] Avoided keywords: {avoided_keywords}")
        
        return final_keywords
    
    @staticmethod
    def load_original_cv(cv_path: str) -> Dict[str, Any]:
        """
        Load and parse the original CV file
        
        Detailed logging has been added to track the CV loading and conversion process,
        helping identify any potential formatting or content issues early.
        
        
        Args:
            cv_path: Path to the original_cv.json file
            
        Returns:
            Structured CV data
        """
        try:
            logger.info(f"📂 Loading CV from: {cv_path}")
            path_obj = Path(cv_path)
            # If it's a .txt file, parse as raw text directly
            if path_obj.suffix.lower() == '.txt':
                logger.info("📝 Detected .txt CV file → parsing as raw text")
                cv_text = path_obj.read_text(encoding='utf-8', errors='ignore')
                if not cv_text.strip():
                    raise ValueError("Original CV text file is empty")
                structured_cv = RecommendationParser._parse_cv_text(cv_text)
                logger.info("✅ Successfully parsed raw text CV from .txt")
                return structured_cv

            # Otherwise treat as JSON; on parse failure, fall back to text field if present
            with open(cv_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            if not file_content.strip():
                raise ValueError("Original CV JSON file is empty")
            try:
                data = json.loads(file_content)
            except json.JSONDecodeError as je:
                logger.error(f"❌ JSON parsing failed for {cv_path}: {je}. Attempting to parse as raw text JSON wrapper if 'text' key present")
                # As a last resort, treat the entire content as text
                structured_cv = RecommendationParser._parse_cv_text(file_content)
                logger.info("✅ Fallback: Parsed CV by treating file content as raw text")
                return structured_cv
            
            # Log the detected format and structure
            logger.info(f"📋 CV format check:")
            logger.info(f"  - Top-level keys: {list(data.keys())}")
            logger.info(f"  - Has metadata: {'metadata' in data}")
            if 'metadata' in data:
                logger.info(f"  - Source file: {data['metadata'].get('source_filename')}")
                logger.info(f"  - Processing version: {data['metadata'].get('processing_version')}")
            
            # Enhanced debugging for CV data structure
            logger.info(f"🔍 [CV_PARSER] Detailed CV structure analysis:")
            logger.info(f"  - Has contact: {'contact' in data}")
            if 'contact' in data:
                contact_data = data['contact']
                logger.info(f"  - Contact keys: {list(contact_data.keys()) if isinstance(contact_data, dict) else 'Not a dict'}")
                logger.info(f"  - Contact name: {contact_data.get('name', 'MISSING') if isinstance(contact_data, dict) else 'Not accessible'}")
                logger.info(f"  - Contact email: {contact_data.get('email', 'MISSING') if isinstance(contact_data, dict) else 'Not accessible'}")
            
            logger.info(f"  - Has experience: {'experience' in data}")
            if 'experience' in data:
                exp_data = data['experience']
                logger.info(f"  - Experience type: {type(exp_data)}")
                logger.info(f"  - Experience count: {len(exp_data) if isinstance(exp_data, list) else 'Not a list'}")
                if isinstance(exp_data, list) and exp_data:
                    logger.info(f"  - First experience keys: {list(exp_data[0].keys()) if isinstance(exp_data[0], dict) else 'Not a dict'}")
            
            logger.info(f"  - Has skills: {'skills' in data}")
            if 'skills' in data:
                skills_data = data['skills']
                logger.info(f"  - Skills type: {type(skills_data)}")
                logger.info(f"  - Skills count: {len(skills_data) if isinstance(skills_data, list) else 'Not a list'}")
                if isinstance(skills_data, list) and skills_data:
                    logger.info(f"  - First skill type: {type(skills_data[0])}")
                    if isinstance(skills_data[0], dict):
                        logger.info(f"  - First skill keys: {list(skills_data[0].keys())}")
                    elif isinstance(skills_data[0], str):
                        logger.info(f"  - First skill (string): {skills_data[0]}")
            
            # Check if this is already structured CV data or raw text
            if 'personal_information' in data:
                # Already structured format
                logger.info("✅ Detected structured CV format")
                logger.info(f"📊 Structure overview:")
                logger.info(f"  - Skills sections: {list(data.get('skills', {}).keys())}")
                logger.info(f"  - Experience entries: {len(data.get('experience', []))}")
                logger.info(f"  - Education entries: {len(data.get('education', []))}")
                logger.info(f"  - Projects: {len(data.get('projects', []))}")
                
                return RecommendationParser._convert_structured_to_model_format(data)
            # Detect already-tailored structured CV format (contact/education/experience/projects/skills)
            elif all(key in data for key in ['contact', 'experience', 'skills']):
                logger.info("✅ Detected tailored structured CV format (contact/experience/skills)")
                # Normalize minimal fields to ensure compatibility with OriginalCV model
                try:
                    normalized: Dict[str, Any] = {
                        'contact': {
                            'name': (data.get('contact') or {}).get('name', '') or '',
                            'email': (data.get('contact') or {}).get('email', '') or '',
                            'phone': (data.get('contact') or {}).get('phone', '') or '',
                            'location': (data.get('contact') or {}).get('location', '') or '',
                            'linkedin': (data.get('contact') or {}).get('linkedin', '') or '',
                            'website': (data.get('contact') or {}).get('website', '') or ''
                        },
                        'education': data.get('education') or [],
                        'experience': data.get('experience') or [],
                        'skills': data.get('skills') or [],
                    }
                    # Optionally pass through projects if present
                    if 'projects' in data and isinstance(data.get('projects'), list):
                        normalized['projects'] = data.get('projects')

                    # Basic validation
                    if not isinstance(normalized['experience'], list):
                        raise ValueError('Expected list for experience in tailored CV')
                    if not isinstance(normalized['skills'], list):
                        raise ValueError('Expected list for skills in tailored CV')

                    logger.info("✅ Successfully normalized tailored structured CV")
                    return normalized
                except Exception as ne:
                    logger.error(f"❌ Failed to normalize tailored structured CV: {ne}")
                    raise

            elif 'text' in data:
                # Raw text format - could be plain text or JSON string (possibly nested multiple times)
                logger.info("📝 Detected 'text' field in CV")
                cv_text = data.get('text', '')
                logger.info(f"  - Text length: {len(cv_text)} characters")
                if not cv_text.strip():
                    raise ValueError("Original CV JSON 'text' field is empty")
                
                # CRITICAL FIX: Check if 'text' field contains JSON string
                # This happens when CV is stored as {"text": "{...escaped JSON...}"}
                # Sometimes it's nested multiple times!
                try:
                    # Try to parse as JSON first
                    text_as_json = json.loads(cv_text)
                    logger.info(f"✅ First JSON parse successful - type: {type(text_as_json)}")
                    
                    if isinstance(text_as_json, dict):
                        # Check if this level has the CV data
                        if 'personal_information' in text_as_json or 'contact' in text_as_json:
                            logger.info("✅ Detected JSON string inside 'text' field - parsing as structured CV")
                            if 'personal_information' in text_as_json:
                                return RecommendationParser._convert_structured_to_model_format(text_as_json)
                            elif all(key in text_as_json for key in ['contact', 'experience', 'skills']):
                                logger.info("✅ Successfully parsed nested JSON from 'text' field")
                                return text_as_json
                        
                        # Check if there's another 'text' field (nested again!)
                        elif 'text' in text_as_json:
                            logger.info("🔄 Detected nested 'text' field - parsing recursively")
                            inner_text = text_as_json.get('text', '')
                            try:
                                inner_json = json.loads(inner_text)
                                logger.info(f"✅ Second JSON parse successful - type: {type(inner_json)}")
                                if isinstance(inner_json, dict):
                                    if 'personal_information' in inner_json:
                                        logger.info("✅ Found personal_information in nested JSON - converting")
                                        return RecommendationParser._convert_structured_to_model_format(inner_json)
                                    elif all(key in inner_json for key in ['contact', 'experience', 'skills']):
                                        logger.info("✅ Found structured CV in nested JSON")
                                        return inner_json
                            except (json.JSONDecodeError, ValueError) as e:
                                logger.warning(f"⚠️  Failed to parse nested text field as JSON: {e}")
                                # Fall through to text parsing
                                pass
                except (json.JSONDecodeError, ValueError) as e:
                    # Not JSON, treat as plain text
                    logger.info(f"📝 JSON parsing failed: {e} - treating as plain text")
                    pass
                
                # Fall back to text parsing
                logger.info("📝 Treating 'text' field as plain text")
                structured_cv = RecommendationParser._parse_cv_text(cv_text)
                logger.info("✅ Successfully parsed raw text CV")
                return structured_cv
            else:
                logger.error(f"❌ Unknown CV format detected")
                logger.error(f"  - Expected: 'personal_information' or 'text' key")
                logger.error(f"  - Found keys: {list(data.keys())}")
                raise ValueError(f"Unknown CV file format. Expected 'personal_information' or 'text' key, got: {list(data.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load original CV: {e}")
            raise
    
    @staticmethod
    def _parse_cv_text(cv_text: str) -> Dict[str, Any]:
        """
        Parse CV text into structured format with comprehensive extraction
        Enhanced to extract complete CV data from the actual CV text
        """
        lines = cv_text.split('\n')
        
        # Extract contact info (first few lines)
        contact_lines = lines[:3]
        name = contact_lines[0].strip() if contact_lines else "Maheshwor Tiwari"
        
        # Extract email and phone from contact lines
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
        phone_match = re.search(r'(\d{4}\s\d{3}\s\d{3}|\+?[\d\s\-\(\)]+)', cv_text)
        location_match = re.search(r'([A-Za-z\s,]+,\s*NSW,\s*\d{4})', cv_text)
        
        # Extract education with more comprehensive parsing
        education = []
        education_patterns = [
            (r'Master of Data Science\s*\n([^\n]+),\s*([^\n]+)\s+([^\n]+)', 'Master of Data Science'),
            (r'PhD in Physics\s*\n([^\n]+),\s*([^\n]+)\s+([^\n]+)', 'PhD in Physics'),
            (r'Master of Theoretical Physics\s*\n([^\n]+),\s*([^\n]+)\s+([^\n]+)', 'Master of Theoretical Physics')
        ]
        
        for pattern, degree in education_patterns:
            match = re.search(pattern, cv_text)
            if match:
                institution = match.group(1).strip()
                location = match.group(2).strip()
                dates = match.group(3).strip()
                # Extract graduation year from dates
                year_match = re.search(r'(\d{4})\s*$', dates)
                graduation_year = year_match.group(1) if year_match else dates.split()[-1]
                
                education.append({
                    'institution': institution,
                    'degree': degree,
                    'location': location,
                    'graduation_date': graduation_year
                })
        
        # Extract technical skills from the TECHNICAL SKILLS section
        skills = []
        skills_section = re.search(r'TECHNICAL SKILLS\s*([^\n]*(?:\n[^\n]*)*?)(?=\n\n|\nEDUCATION|\nEXPERIENCE|$)', cv_text, re.IGNORECASE)
        if skills_section:
            skills_text = skills_section.group(1)
            
            # Programming languages
            if 'python' in skills_text.lower():
                programming_skills = ['Python']
                if 'pandas' in skills_text.lower():
                    programming_skills.append('Pandas')
                if 'numpy' in skills_text.lower():
                    programming_skills.append('NumPy')
                if 'scikit-learn' in skills_text.lower():
                    programming_skills.append('Scikit-learn')
                skills.append({
                    'category': 'Programming Languages',
                    'skills': programming_skills
                })
            
            # Database skills
            if 'sql' in skills_text.lower():
                db_skills = ['SQL']
                if 'postgresql' in skills_text.lower():
                    db_skills.append('PostgreSQL')
                if 'mysql' in skills_text.lower():
                    db_skills.append('MySQL')
                skills.append({
                    'category': 'Database Technologies',
                    'skills': db_skills
                })
            
            # Visualization tools
            if any(tool in skills_text.lower() for tool in ['tableau', 'power bi', 'matplotlib']):
                viz_skills = []
                if 'tableau' in skills_text.lower():
                    viz_skills.append('Tableau')
                if 'power bi' in skills_text.lower():
                    viz_skills.append('Power BI')
                if 'matplotlib' in skills_text.lower():
                    viz_skills.append('Matplotlib')
                if 'seaborn' in skills_text.lower():
                    viz_skills.append('Seaborn')
                skills.append({
                    'category': 'Data Visualization',
                    'skills': viz_skills
                })
            
            # Tools and platforms
            tools = []
            if 'github' in skills_text.lower():
                tools.append('GitHub')
            if 'docker' in skills_text.lower():
                tools.append('Docker')
            if 'snowflake' in skills_text.lower():
                tools.append('Snowflake')
            if 'google analytics' in skills_text.lower():
                tools.append('Google Analytics')
            if tools:
                skills.append({
                    'category': 'Tools & Platforms',
                    'skills': tools
                })
        
        # Extract work experience with detailed parsing
        experience = []
        experience_section = re.search(r'EXPERIENCE\s*([\s\S]*?)(?=\n\n[A-Z]|$)', cv_text)
        if experience_section:
            exp_text = experience_section.group(1)
            
            # Parse individual job entries
            job_pattern = r'([^\n]+?)\s+(\w{3}\s+\d{4}\s*[–-]\s*(?:\w{3}\s+\d{4}|Present))\s*\n([^\n]+?)\s*\n([\s\S]*?)(?=\n[A-Z][^\n]*\d{4}|$)'
            jobs = re.findall(job_pattern, exp_text)
            
            for title, dates, company_location, bullets_text in jobs:
                title = title.strip()
                company_location = company_location.strip()
                
                # Split company and location
                company_parts = company_location.split(', ')
                company = company_parts[0]
                location = ', '.join(company_parts[1:]) if len(company_parts) > 1 else 'Australia'
                
                # Parse dates
                date_parts = dates.replace('–', '-').split('-')
                start_date = date_parts[0].strip()
                end_date = date_parts[1].strip() if len(date_parts) > 1 else 'Present'
                
                # Extract bullet points
                bullet_lines = [line.strip() for line in bullets_text.split('\n') if line.strip() and line.strip().startswith('•')]
                bullets = [bullet[1:].strip() for bullet in bullet_lines]  # Remove bullet point
                
                if title and company and bullets:  # Only add if we have meaningful data
                    experience.append({
                        'company': company,
                        'title': title,
                        'location': location,
                        'start_date': start_date,
                        'end_date': end_date,
                        'bullets': bullets
                    })
        
        return {
            'contact': {
                'name': name,
                'email': email_match.group(0) if email_match else 'maheshtwari99@gmail.com',
                'phone': phone_match.group(0) if phone_match else '0414 032 507',
                'location': location_match.group(1) if location_match else 'Sydney, NSW, Australia'
            },
            'education': education,
            'experience': experience,
            'skills': skills,
            'total_years_experience': len(experience) if experience else 3
        }
    
    @staticmethod
    def _convert_structured_to_model_format(structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert structured CV data to the format expected by CV models
        Handles the new structured format with personal_information and detailed sections
        """
        logger.info("🔄 Starting structured CV conversion")
        logger.info("📊 Input data validation:")
        
        # Convert personal_information to contact format
        logger.info("👤 Converting contact information")
        personal_info = structured_data.get('personal_information', {})
        contact = {
            'name': personal_info.get('name', ''),
            'email': personal_info.get('email', ''),
            'phone': personal_info.get('phone', ''),
            'location': personal_info.get('location', ''),
            'linkedin': personal_info.get('linkedin', ''),
            'website': personal_info.get('github', '')  # Map GitHub to website field
        }
        
        # Handle portfolio_links if available
        portfolio_links = personal_info.get('portfolio_links', {})
        if portfolio_links:
            # If we have a website in portfolio, use that instead of GitHub
            if portfolio_links.get('website'):
                contact['website'] = portfolio_links['website']
            # If LinkedIn is empty but we have other portfolio links, add them as comma-separated
            if not contact['linkedin'] and (portfolio_links.get('blogs') or portfolio_links.get('dashboard_portfolio')):
                links = []
                if portfolio_links.get('blogs'):
                    links.append(portfolio_links['blogs'])
                if portfolio_links.get('dashboard_portfolio'):
                    links.append(portfolio_links['dashboard_portfolio'])
                contact['linkedin'] = ', '.join(links)
        
        logger.info(f"  - Source fields: {list(personal_info.keys())}")
        logger.info(f"  - Mapped fields: {list(contact.keys())}")
        logger.info(f"  - Contact completeness: {sum(1 for v in contact.values() if v) / len(contact) * 100:.1f}%")
        logger.info(f"  - LinkedIn: {contact['linkedin']}")
        logger.info(f"  - Website: {contact['website']}")
        
        # Convert experience entries
        logger.info("💼 Converting experience entries")
        experience = []
        source_experience = structured_data.get('experience', [])
        logger.info(f"  - Found {len(source_experience)} experience entries")
        
        for idx, exp in enumerate(source_experience, 1):
            logger.info(f"  - Processing experience {idx}/{len(source_experience)}")
            # Parse duration into start/end dates
            duration = exp.get('duration', '')
            dates = duration.split('–') if '–' in duration else duration.split('-')
            
            start_date = dates[0].strip() if dates else ''
            end_date = dates[1].strip() if len(dates) > 1 else 'Present'
            
            bullets = exp.get('responsibilities', []) + exp.get('achievements', [])
            experience_entry = {
                'company': exp.get('company', '').split(',')[0],  # Remove location part if present
                'title': exp.get('title', ''),
                'location': exp.get('location', ''),
                'start_date': start_date,
                'end_date': end_date,
                'bullets': bullets
            }
            logger.info(f"    • Company: {experience_entry['company']}")
            logger.info(f"    • Title: {experience_entry['title']}")
            logger.info(f"    • Duration: {start_date} to {end_date}")
            logger.info(f"    • Bullets: {len(bullets)}")
            if experience_entry['bullets']:  # Only add if we have content
                experience.append(experience_entry)
        
        logger.info(f"Converted {len(experience)} experience entries")
        
        # Convert skills to category-based format
        logger.info("🔧 Converting skills section")
        skills_data = structured_data.get('skills', {})
        logger.info(f"  - Source skill categories: {list(skills_data.keys())}")
        skills = []
        
        # Technical skills
        logger.info("  - Processing technical skills:")
        tech_skills = []
        for skill in skills_data.get('technical_skills', []):
            # Extract the main skill from the descriptive text
            # e.g., "Advanced SQL skills, proficient in..." -> "SQL"
            if 'SQL' in skill:
                tech_skills.append('SQL')
            if 'Power BI' in skill:
                tech_skills.append('Power BI')
            if 'Python' in skill:
                tech_skills.append('Python')
            if 'Excel' in skill:
                tech_skills.append('Excel')
            if 'data analysis' in skill.lower():
                tech_skills.append('Data Analysis')
        
        if tech_skills:
            tech_skills = list(set(tech_skills))  # Remove duplicates
            skills.append({
                'category': 'Technical Skills',
                'skills': tech_skills
            })
            logger.info(f"    • Extracted {len(tech_skills)} unique technical skills")
            logger.info(f"    • Skills: {', '.join(tech_skills)}")
        
        # Soft skills
        soft_skills = [
            skill.split(',')[0]  # Take the main skill part
            for skill in skills_data.get('soft_skills', [])
        ]
        if soft_skills:
            skills.append({
                'category': 'Soft Skills',
                'skills': soft_skills
            })
        
        # Domain expertise
        domain_skills = [
            skill.split(',')[0]  # Take the main skill part
            for skill in skills_data.get('domain_expertise', [])
        ]
        if domain_skills:
            skills.append({
                'category': 'Domain Expertise',
                'skills': domain_skills
            })
        
        # If no explicit soft/domain skills, extract from key_skills
        if not soft_skills and not domain_skills:
            key_skills = []
            for skill in skills_data.get('key_skills', []):
                if any(term in skill.lower() for term in ['communication', 'interpersonal', 'teamwork', 'leadership']):
                    soft_skills.append(skill.split(',')[0])
                else:
                    key_skills.append(skill.split(',')[0])
            
            if soft_skills:
                skills.append({
                    'category': 'Soft Skills',
                    'skills': list(set(soft_skills))  # Remove duplicates
                })
            if key_skills:
                skills.append({
                    'category': 'Key Skills',
                    'skills': list(set(key_skills))  # Remove duplicates
                })
        
        logger.info(f"Converted {len(skills)} skill categories")
        
        # Validate we have the minimum required sections
        logger.info("✅ Conversion complete - Validating output")
        validation_issues = []
        
        if not experience:
            msg = "No experience entries were converted"
            validation_issues.append(msg)
            logger.error(f"❌ {msg}")
        else:
            logger.info(f"✓ Experience: {len(experience)} entries")
        
        if not skills:
            msg = "No skill categories were converted"
            validation_issues.append(msg)
            logger.error(f"❌ {msg}")
        else:
            logger.info(f"✓ Skills: {len(skills)} categories")
            for cat in skills:
                logger.info(f"  • {cat['category']}: {len(cat['skills'])} skills")
        
        if validation_issues:
            logger.warning(f"⚠️ Validation found {len(validation_issues)} issues")
        else:
            logger.info("✨ Validation passed - All required sections present")
        
        # Convert education entries with proper field mapping
        logger.info("🎓 Converting education entries")
        education = []
        source_education = structured_data.get('education', [])
        logger.info(f"  - Found {len(source_education)} education entries")
        
        for idx, edu in enumerate(source_education, 1):
            logger.info(f"  - Processing education {idx}/{len(source_education)}")
            education_entry = {
                'institution': edu.get('institution', ''),
                'degree': edu.get('degree', ''),
                'location': edu.get('location', ''),
                'graduation_date': edu.get('year', ''),  # Map 'year' to 'graduation_date'
                'gpa': edu.get('gpa', ''),
                'relevant_coursework': edu.get('relevant_courses'),
                'honors': edu.get('honors')
            }
            logger.info(f"    • Institution: {education_entry['institution']}")
            logger.info(f"    • Degree: {education_entry['degree']}")
            logger.info(f"    • Graduation date: {education_entry['graduation_date']}")
            education.append(education_entry)
        
        logger.info(f"Converted {len(education)} education entries")
        
        converted_data = {
            'contact': contact,
            'experience': experience,
            'skills': skills,
            'education': education
        }
        
        logger.info("📤 Returning converted CV data:")
        logger.info(f"  - Contact fields: {list(contact.keys())}")
        logger.info(f"  - Experience entries: {len(experience)}")
        logger.info(f"  - Skill categories: {len(skills)}")
        logger.info(f"  - Education entries: {len(converted_data['education'])}")
        
        # Handle projects if available
        if structured_data.get('projects'):
            projects = []
            for proj in structured_data['projects']:
                bullets = proj.get('description', [])
                if not bullets:
                    bullets = [proj.get('context', 'Project details not available')]
                
                projects.append({
                    'name': proj.get('name', ''),
                    'context': proj.get('context', ''),
                    'technologies': proj.get('technologies', []),
                    'bullets': bullets,
                    'url': proj.get('url', ''),
                    'duration': proj.get('duration', '')
                })
            converted_data['projects'] = projects
            logger.info(f"  - Added {len(projects)} projects")
        
        # Add additional sections if available
        for section in ['languages', 'certifications']:
            if structured_data.get(section):
                converted_data[section] = structured_data[section]
                logger.info(f"  - Added {section} section")
        
        return converted_data
    
    @staticmethod
    def debug_parse_recommendation_file(file_path: str) -> Dict[str, Any]:
        """
        Debug method to analyze recommendation file parsing
        
        Args:
            file_path: Path to recommendation file
            
        Returns:
            Debug information about parsing process
        """
        debug_info = {
            'file_path': file_path,
            'file_exists': False,
            'format_detected': None,
            'parsing_method_used': None,
            'fields_extracted': {},
            'warnings': [],
            'errors': []
        }
        
        try:
            from pathlib import Path
            path_obj = Path(file_path)
            debug_info['file_exists'] = path_obj.exists()
            
            if not debug_info['file_exists']:
                debug_info['errors'].append(f"File not found: {file_path}")
                return debug_info
            
            # Load file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Detect format
            metadata = data.get('metadata', {})
            format_version = metadata.get('format_version', '1.0')
            has_actionable = bool(data.get('actionable_guidance'))
            has_structured = metadata.get('has_structured_data', False)
            has_markdown = bool(data.get('recommendation_content'))
            
            debug_info['format_detected'] = format_version
            debug_info['has_actionable_guidance'] = has_actionable
            debug_info['has_structured_recommendations'] = has_structured
            debug_info['has_recommendation_content'] = has_markdown
            
            # Determine which parser would be used
            if has_actionable and 'actionable_guidance' in data:
                debug_info['parsing_method_used'] = 'parse_actionable_guidance'
            elif has_structured and 'structured_recommendations' in data:
                debug_info['parsing_method_used'] = 'parse_structured_recommendations'
            else:
                debug_info['parsing_method_used'] = 'parse_markdown_content'
            
            # Actually parse the file
            parsed_data = RecommendationParser.parse_recommendation_file(file_path)
            
            # Analyze extracted fields
            debug_info['fields_extracted'] = {
                'has_company': bool(parsed_data.get('company')),
                'has_job_title': bool(parsed_data.get('job_title')),
                'missing_technical_skills_count': len(parsed_data.get('missing_technical_skills', [])),
                'missing_soft_skills_count': len(parsed_data.get('missing_soft_skills', [])),
                'missing_keywords_count': len(parsed_data.get('missing_keywords', [])),
                'critical_gaps_count': len(parsed_data.get('critical_gaps', [])),
                'has_tier1_keywords': bool(parsed_data.get('tier1_keywords')),
                'has_tier2_keywords': bool(parsed_data.get('tier2_keywords')),
                'has_tier3_avoid': bool(parsed_data.get('tier3_avoid')),
                'has_strategic_positioning': bool(parsed_data.get('strategic_positioning')),
                'has_experience_optimization': bool(parsed_data.get('experience_optimization')),
                'has_achievements': bool(parsed_data.get('achievements')),
                'has_implementation_plan': bool(parsed_data.get('implementation_plan')),
                'has_messaging': bool(parsed_data.get('messaging')),
                'match_score': parsed_data.get('match_score'),
                'target_score': parsed_data.get('target_score'),
                'format_version': parsed_data.get('format_version')
            }
            
            # Check for tier information
            if parsed_data.get('tier1_keywords'):
                tier1 = parsed_data['tier1_keywords']
                debug_info['tier1_details'] = {
                    'technical_count': len(tier1.get('technical', [])),
                    'soft_count': len(tier1.get('soft', [])),
                    'domain_count': len(tier1.get('domain', []))
                }
            
            if parsed_data.get('tier2_keywords'):
                tier2 = parsed_data['tier2_keywords']
                debug_info['tier2_details'] = {
                    'technical_count': len(tier2.get('technical', [])),
                    'soft_count': len(tier2.get('soft', [])),
                    'domain_count': len(tier2.get('domain', []))
                }
            
            if parsed_data.get('tier3_avoid'):
                debug_info['tier3_avoid_count'] = len(parsed_data['tier3_avoid'])
                debug_info['tier3_avoid_list'] = parsed_data['tier3_avoid'][:5]  # First 5
            
            # Validate tier3 keywords are not in missing_technical_skills
            tier3_list = parsed_data.get('tier3_avoid', [])
            missing_tech = parsed_data.get('missing_technical_skills', [])
            conflicting = [kw for kw in tier3_list if kw in missing_tech]
            if conflicting:
                debug_info['warnings'].append(f"⚠️ Tier 3 keywords found in missing_technical_skills: {conflicting}")
            
            debug_info['success'] = True
            
        except Exception as e:
            debug_info['errors'].append(str(e))
            debug_info['success'] = False
            logger.error(f"Debug parsing failed: {e}", exc_info=True)
        
        return debug_info
    
    @staticmethod
    def validate_parsed_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that parsed data has all required fields for RecommendationAnalysis
        
        Args:
            parsed_data: Parsed recommendation data
            
        Returns:
            Validation results with warnings and errors
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'missing_required_fields': [],
            'missing_optional_fields': []
        }
        
        # Required fields for RecommendationAnalysis
        required_fields = [
            'company', 'job_title', 'missing_technical_skills', 
            'missing_soft_skills', 'missing_keywords', 'technical_enhancements',
            'soft_skill_improvements', 'keyword_integration', 'critical_gaps',
            'important_gaps', 'nice_to_have'
        ]
        
        for field in required_fields:
            if field not in parsed_data:
                validation['missing_required_fields'].append(field)
                validation['errors'].append(f"Missing required field: {field}")
                validation['is_valid'] = False
        
        # Optional but valuable fields (v2.0+)
        optional_fields = [
            'tier1_keywords', 'tier2_keywords', 'tier3_avoid',
            'strategic_positioning', 'experience_optimization',
            'achievements', 'implementation_plan', 'messaging'
        ]
        
        for field in optional_fields:
            if field not in parsed_data:
                validation['missing_optional_fields'].append(field)
                validation['warnings'].append(f"Missing optional field (v2.0+): {field}")
        
        # Validate tier3_avoid doesn't conflict with missing keywords
        tier3_avoid = parsed_data.get('tier3_avoid', [])
        if tier3_avoid:
            missing_tech = set(parsed_data.get('missing_technical_skills', []))
            missing_soft = set(parsed_data.get('missing_soft_skills', []))
            missing_keywords = set(parsed_data.get('missing_keywords', []))
            
            all_missing = missing_tech | missing_soft | missing_keywords
            conflicts = [kw for kw in tier3_avoid if kw in all_missing]
            
            if conflicts:
                validation['warnings'].append(
                    f"⚠️ Tier 3 keywords ({conflicts}) found in missing keywords lists - should be removed!"
                )
        
        # Validate tier1_keywords structure
        tier1 = parsed_data.get('tier1_keywords')
        if tier1:
            if not isinstance(tier1, dict):
                validation['errors'].append("tier1_keywords should be a dict with technical/soft/domain keys")
                validation['is_valid'] = False
            else:
                for category in ['technical', 'soft', 'domain']:
                    if category in tier1:
                        for item in tier1[category]:
                            if not isinstance(item, dict):
                                validation['errors'].append(f"tier1_keywords.{category} items should be dicts")
                                validation['is_valid'] = False
                            elif 'keyword' not in item:
                                validation['warnings'].append(f"tier1_keywords.{category} item missing 'keyword' field")
        
        return validation
