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
        
        Args:
            file_path: Path to the recommendation JSON file
            
        Returns:
            Structured recommendation data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            company = data.get('company', 'Unknown')
            recommendation_content = data.get('recommendation_content', '')
            
            parsed_data = RecommendationParser.parse_markdown_content(
                recommendation_content, company
            )
            
            # Add metadata
            parsed_data['generated_at'] = data.get('generated_at')
            parsed_data['ai_model_info'] = data.get('ai_model_info', {})
            
            logger.info(f"✅ Parsed recommendation for {company}")
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
        
        # Extract missing keywords
        missing_technical_skills = RecommendationParser._extract_section_items(
            content, "Technical Skills Enhancement"
        )
        missing_soft_skills = RecommendationParser._extract_section_items(
            content, "Soft Skills Optimization"
        )
        missing_keywords = RecommendationParser._extract_section_items(
            content, "Critical Missing Keywords"
        )
        
        # Extract enhancement recommendations
        technical_enhancements = RecommendationParser._extract_high_impact_changes(content)
        keyword_integration = missing_keywords + missing_technical_skills
        
        # Extract priority gaps
        critical_gaps = RecommendationParser._extract_section_items(
            content, "Immediate Action Required"
        )
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
    def load_original_cv(cv_path: str) -> Dict[str, Any]:
        """
        Load and parse the original CV file
        
        Args:
            cv_path: Path to the original_cv.json file
            
        Returns:
            Structured CV data
        """
        try:
            with open(cv_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if this is already structured CV data or raw text
            if 'personal_information' in data:
                # Already structured format
                logger.info("✅ Loaded structured CV data")
                return RecommendationParser._convert_structured_to_model_format(data)
            elif 'text' in data:
                # Raw text format - parse it
                cv_text = data.get('text', '')
                structured_cv = RecommendationParser._parse_cv_text(cv_text)
                logger.info("✅ Loaded and parsed raw text CV")
                return structured_cv
            else:
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
        """
        personal_info = structured_data.get('personal_information', {})
        
        # Convert contact information
        contact = {
            'name': personal_info.get('name', ''),
            'email': personal_info.get('email', ''),
            'phone': personal_info.get('phone', ''),
            'location': personal_info.get('location', '')
        }
        
        # Convert education
        education = []
        for edu in structured_data.get('education', []):
            education.append({
                'institution': edu.get('institution', ''),
                'degree': edu.get('degree', ''),
                'location': edu.get('location', ''),
                'graduation_date': edu.get('duration', '').split(' - ')[-1] if edu.get('duration') else ''
            })
        
        # Convert experience
        experience = []
        for exp in structured_data.get('experience', []):
            # Convert achievements to bullets format
            bullets = exp.get('achievements', []) + exp.get('responsibilities', [])
            
            experience.append({
                'company': exp.get('company', ''),
                'title': exp.get('position', ''),
                'location': exp.get('location', ''),
                'start_date': exp.get('duration', '').split(' – ')[0] if ' – ' in exp.get('duration', '') else exp.get('duration', ''),
                'end_date': exp.get('duration', '').split(' – ')[1] if ' – ' in exp.get('duration', '') else 'Present',
                'bullets': bullets
            })
        
        # Convert skills
        skills = []
        technical_skills = structured_data.get('technical_skills', [])
        if technical_skills:
            # Group technical skills into categories
            skills.append({
                'category': 'Technical Skills',
                'skills': [skill.replace('Advanced ', '').replace('Strong experience in ', '').replace('Proficient in ', '').split(' for ')[0].split(' and ')[0] for skill in technical_skills[:5]]
            })
        
        return {
            'contact': contact,
            'education': education,
            'experience': experience,
            'skills': skills,
            'total_years_experience': len(experience)
        }
