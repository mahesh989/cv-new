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
            r'Domain Keywords[^:]*:.*?Add[^:]*:([^#]*?)(?=\n\*\*|\n##|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(1)
                # Extract keywords in quotes
                quoted_keywords = re.findall(r'"([^"]+)"', section_content)
                # Clean up extracted keywords - remove trailing punctuation
                for kw in quoted_keywords:
                    clean_kw = kw.strip().rstrip('.,;:')
                    if len(clean_kw) < 50 and clean_kw:
                        keywords.append(clean_kw)
        
        # Also look for specific domain keywords mentioned
        domain_keywords = ['International Aid', 'Fundraising', 'Not For Profit', 'NFP', 
                          'Humanitarian Aid', 'Business Intelligence', 'Direct Marketing Campaigns', 
                          'Donor-Centricity', 'Refugee Support']
        for keyword in domain_keywords:
            if keyword in content and keyword not in [k.rstrip('.,;:') for k in keywords]:
                keywords.append(keyword)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(keywords))
    
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
                # Raw text format - parse it
                logger.info("📝 Detected raw text format")
                cv_text = data.get('text', '')
                logger.info(f"  - Text length: {len(cv_text)} characters")
                if not cv_text.strip():
                    raise ValueError("Original CV JSON 'text' field is empty")
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
