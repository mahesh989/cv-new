"""
Job Description Extraction Service - Enhanced web scraping and text processing
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class JDExtractor:
    """Enhanced job description extraction from URLs and text processing"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
        })
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract job description from URL
        
        Returns:
        {
            'text': str,
            'success': bool,
            'processing_time': float,
            'metadata': dict,
            'error': Optional[str]
        }
        """
        start_time = time.time()
        
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'text': '',
                    'success': False,
                    'processing_time': time.time() - start_time,
                    'metadata': {},
                    'error': 'Invalid URL format'
                }
            
            # Fetch webpage
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                return {
                    'text': '',
                    'success': False,
                    'processing_time': time.time() - start_time,
                    'metadata': {},
                    'error': 'Request timed out'
                }
            except requests.exceptions.RequestException as e:
                return {
                    'text': '',
                    'success': False,
                    'processing_time': time.time() - start_time,
                    'metadata': {},
                    'error': f'Request failed: {str(e)}'
                }
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract based on domain
            domain = parsed_url.netloc.lower()
            if 'ethicaljobs.com.au' in domain:
                result = self._extract_from_ethicaljobs(soup)
            elif 'seek.com.au' in domain:
                result = self._extract_from_seek(soup)
            elif 'linkedin.com' in domain:
                result = self._extract_from_linkedin(soup)
            elif 'indeed.com' in domain:
                result = self._extract_from_indeed(soup)
            else:
                result = self._extract_generic(soup)
            
            processing_time = time.time() - start_time
            
            return {
                'text': result['text'],
                'content': result['text'],
                'success': True,
                'processing_time': processing_time,
                'metadata': {
                    'source_domain': domain,
                    'text_length': len(result['text']),
                    'word_count': len(result['text'].split()) if result['text'] else 0,
                    **result.get('metadata', {})
                },
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error extracting JD from {url}: {str(e)}")
            return {
                'text': '',
                'success': False,
                'processing_time': time.time() - start_time,
                'metadata': {},
                'error': str(e)
            }
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process and clean job description text
        
        Returns:
        {
            'text': str,
            'success': bool,
            'processing_time': float,
            'metadata': dict,
            'error': Optional[str]
        }
        """
        start_time = time.time()
        
        try:
            if not text or not text.strip():
                return {
                    'text': '',
                    'success': False,
                    'processing_time': time.time() - start_time,
                    'metadata': {},
                    'error': 'Empty text provided'
                }
            
            # Clean and process the text
            processed_text = self._clean_and_structure_text(text)
            
            processing_time = time.time() - start_time
            
            return {
                'text': processed_text,
                'content': processed_text,
                'success': True,
                'processing_time': processing_time,
                'metadata': {
                    'original_length': len(text),
                    'processed_length': len(processed_text),
                    'word_count': len(processed_text.split()) if processed_text else 0,
                },
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error processing JD text: {str(e)}")
            return {
                'text': '',
                'success': False,
                'processing_time': time.time() - start_time,
                'metadata': {},
                'error': str(e)
            }
    
    def _extract_from_ethicaljobs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract job description from EthicalJobs website"""
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)
        
        # Look for main content
        main_content = (soup.find('main') or 
                       soup.find('article') or
                       soup.find('div', class_=re.compile(r'content|main|job', re.I)))
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback to body content
            text = soup.get_text(separator='\n', strip=True)
        
        # Clean and structure the text
        cleaned_text = self._clean_and_structure_text(text)
        
        return {
            'text': cleaned_text,
            'metadata': {
                'extraction_method': 'ethicaljobs_specific',
                'has_main_content': main_content is not None
            }
        }
    
    def _extract_from_seek(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract job description from Seek website"""
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)
        
        # Look for job description specific elements
        job_content = (soup.find('div', {'data-automation': 'jobAdDetails'}) or
                      soup.find('div', class_=re.compile(r'job.*description', re.I)) or
                      soup.find('div', class_=re.compile(r'content', re.I)))
        
        if job_content:
            text = job_content.get_text(separator='\n', strip=True)
        else:
            text = self._extract_generic(soup)['text']
        
        cleaned_text = self._clean_and_structure_text(text)
        
        return {
            'text': cleaned_text,
            'metadata': {
                'extraction_method': 'seek_specific',
                'has_job_content': job_content is not None
            }
        }
    
    def _extract_from_linkedin(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract job description from LinkedIn"""
        # LinkedIn has specific structure
        self._remove_unwanted_elements(soup)
        
        job_description = soup.find('div', class_=re.compile(r'jobs-description', re.I))
        
        if job_description:
            text = job_description.get_text(separator='\n', strip=True)
        else:
            text = self._extract_generic(soup)['text']
        
        cleaned_text = self._clean_and_structure_text(text)
        
        return {
            'text': cleaned_text,
            'metadata': {
                'extraction_method': 'linkedin_specific',
                'has_job_description': job_description is not None
            }
        }
    
    def _extract_from_indeed(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract job description from Indeed"""
        self._remove_unwanted_elements(soup)
        
        job_content = (soup.find('div', {'id': 'jobDescriptionText'}) or
                      soup.find('div', class_=re.compile(r'jobsearch.*description', re.I)))
        
        if job_content:
            text = job_content.get_text(separator='\n', strip=True)
        else:
            text = self._extract_generic(soup)['text']
        
        cleaned_text = self._clean_and_structure_text(text)
        
        return {
            'text': cleaned_text,
            'metadata': {
                'extraction_method': 'indeed_specific',
                'has_job_content': job_content is not None
            }
        }
    
    def _extract_generic(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Generic extraction for unknown job sites"""
        self._remove_unwanted_elements(soup)
        
        # Try priority selectors
        priority_selectors = [
            'main', 'article',
            '[class*=\"job-description\"]', '[class*=\"job-details\"]', 
            '[class*=\"job-content\"]', '[class*=\"description\"]',
            '[class*=\"details\"]', '[class*=\"content\"]'
        ]
        
        text = ""
        extraction_method = "generic_fallback"
        
        for selector in priority_selectors:
            elements = soup.select(selector)
            if elements:
                # Take the largest element (most likely to contain job description)
                largest_element = max(elements, key=lambda x: len(x.get_text()))
                text = largest_element.get_text(separator='\n', strip=True)
                extraction_method = f"generic_{selector}"
                if len(text) > 200:  # If we got substantial content, use it
                    break
        
        # Fallback to full page
        if not text or len(text) < 100:
            text = soup.get_text(separator='\n', strip=True)
            extraction_method = "generic_full_page"
        
        cleaned_text = self._clean_and_structure_text(text)
        
        return {
            'text': cleaned_text,
            'metadata': {
                'extraction_method': extraction_method
            }
        }
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """Remove navigation, ads, and other unwanted elements"""
        unwanted_selectors = [
            'nav', 'header', 'footer', 'aside', 'menu', 'form',
            '[class*=\"nav\"]', '[class*=\"menu\"]', '[class*=\"sidebar\"]',
            '[class*=\"header\"]', '[class*=\"footer\"]', '[class*=\"breadcrumb\"]',
            '[class*=\"pagination\"]', '[class*=\"search\"]', '[class*=\"filter\"]',
            '[class*=\"ad\"]', '[class*=\"advertisement\"]', '[class*=\"cookie\"]',
            'script', 'style', 'noscript', 'button[class*=\"apply\"]',
            '[class*=\"social\"]', '[class*=\"share\"]'
        ]
        
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
    
    def _clean_and_structure_text(self, text: str) -> str:
        """Clean and structure job description text"""
        if not text:
            return ""
        
        # Split into lines and process
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and very short lines
            if not line or len(line) < 3:
                continue
            
            # Skip obvious navigation/UI elements
            if self._is_navigation_text(line):
                continue
            
            # Skip repetitive elements
            if self._is_repetitive_text(line, cleaned_lines):
                continue
            
            cleaned_lines.append(line)
        
        # Join lines and clean up
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\n\n+', '\n\n', cleaned_text)
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        # Add structure - identify sections
        cleaned_text = self._add_section_structure(cleaned_text)
        
        return cleaned_text.strip()
    
    def _is_navigation_text(self, text: str) -> bool:
        """Check if text looks like navigation/UI element"""
        text_lower = text.lower()
        
        # Common navigation patterns
        nav_patterns = [
            r'^(home|search|menu|back|next|apply now|sign in|join|subscribe)$',
            r'^(login|register|create account|forgot password)$',
            r'^(privacy policy|terms of service|cookie|contact us)$',
            r'^(facebook|twitter|linkedin|instagram|youtube)$',
            r'^(job alert|email alert|save job|share job)$',
            r'^(browse jobs|search jobs|post a job|employer)$',
        ]
        
        return any(re.match(pattern, text_lower) for pattern in nav_patterns)
    
    def _is_repetitive_text(self, text: str, existing_lines: list) -> bool:
        """Check if text is repetitive compared to existing lines"""
        if not existing_lines:
            return False
        
        # Check for exact duplicates
        if text in existing_lines:
            return True
        
        # Check for very similar lines (simple similarity check)
        text_words = set(text.lower().split())
        for line in existing_lines[-5:]:  # Check last 5 lines
            line_words = set(line.lower().split())
            if text_words and line_words:
                similarity = len(text_words & line_words) / len(text_words | line_words)
                if similarity > 0.8:  # 80% similarity threshold
                    return True
        
        return False
    
    def _add_section_structure(self, text: str) -> str:
        """Add better section structure to the text"""
        lines = text.split('\n')
        structured_lines = []
        
        # Common section headers
        section_patterns = [
            (r'^(about us|about the company|company)', 'ABOUT THE COMPANY'),
            (r'^(about the role|role|position|job summary)', 'ABOUT THE ROLE'),
            (r'^(responsibilities|key responsibilities|duties)', 'RESPONSIBILITIES'),
            (r'^(requirements|qualifications|skills|experience)', 'REQUIREMENTS'),
            (r'^(what we offer|benefits|perks|compensation)', 'WHAT WE OFFER'),
            (r'^(how to apply|application|apply)', 'HOW TO APPLY'),
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if this line is a section header
            section_added = False
            for pattern, header in section_patterns:
                if re.match(pattern, line_lower):
                    if structured_lines:  # Add spacing before new section
                        structured_lines.append('')
                    structured_lines.append(f"=== {header} ===")
                    structured_lines.append('')
                    section_added = True
                    break
            
            if not section_added:
                structured_lines.append(line)
        
        return '\n'.join(structured_lines)

    # Public wrapper for cleaning/structuring used by simple routes
    def clean_and_structure_text(self, text: str) -> str:
        """Public method to clean and structure JD text (compatibility)."""
        return self._clean_and_structure_text(text)
    
    def extract_key_info(self, text: str) -> Dict[str, Any]:
        """Extract key information from job description"""
        info = {
            'company_name': '',
            'job_title': '',
            'location': '',
            'salary_mentioned': False,
            'remote_work': False,
            'experience_level': '',
            'key_skills': []
        }
        
        text_lower = text.lower()
        
        # Check for remote work
        remote_keywords = ['remote', 'work from home', 'telecommute', 'distributed team']
        info['remote_work'] = any(keyword in text_lower for keyword in remote_keywords)
        
        # Check for salary mention
        salary_patterns = [r'\$[0-9,]+', r'salary', r'compensation', r'pay rate']
        info['salary_mentioned'] = any(re.search(pattern, text_lower) for pattern in salary_patterns)
        
        # Extract experience level
        if any(word in text_lower for word in ['senior', 'lead', 'principal', '5+ years', '7+ years']):
            info['experience_level'] = 'senior'
        elif any(word in text_lower for word in ['junior', 'entry level', 'graduate', '1-2 years']):
            info['experience_level'] = 'junior'
        else:
            info['experience_level'] = 'mid'
        
        return info
    
    def extract_key_information(self, text: str) -> Dict[str, Any]:
        """Enhanced key information extraction"""
        text_lower = text.lower()
        
        return {
            'has_requirements': any(word in text_lower for word in ['requirement', 'qualification', 'must have']),
            'has_skills': any(word in text_lower for word in ['skill', 'experience', 'proficient', 'knowledge']),
            'has_responsibilities': any(word in text_lower for word in ['responsible', 'duty', 'role', 'task']),
            'has_company_info': any(word in text_lower for word in ['company', 'organization', 'about us']),
            'has_job_title': any(word in text_lower for word in ['engineer', 'developer', 'analyst', 'manager', 'specialist']),
            'has_salary': any(word in text_lower for word in ['salary', 'compensation', '$', 'pay']),
            'has_benefits': any(word in text_lower for word in ['benefit', 'health', 'vacation', 'insurance']),
            'has_location': any(word in text_lower for word in ['location', 'office', 'remote', 'hybrid']),
            'remote_work': any(word in text_lower for word in ['remote', 'work from home', 'telecommute']),
            'technical_skills': self._extract_technical_skills(text),
            'soft_skills': self._extract_soft_skills(text)
        }
    
    def _extract_technical_skills(self, text: str) -> list:
        """Extract technical skills from text"""
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'html', 'css', 'typescript', 'php', 'c++', 'go'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def _extract_soft_skills(self, text: str) -> list:
        """Extract soft skills from text"""
        soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'creative', 'organized', 'time management'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in soft_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def get_supported_sites(self):
        """Get list of supported job posting sites"""
        return [
            {
                "name": "Seek.com.au",
                "domain": "seek.com.au",
                "confidence": "high",
                "features": ["job_title", "company", "location", "salary"]
            },
            {
                "name": "Indeed.com",
                "domain": "indeed.com",
                "confidence": "high", 
                "features": ["job_title", "company", "location"]
            },
            {
                "name": "LinkedIn",
                "domain": "linkedin.com",
                "confidence": "medium",
                "features": ["job_title", "company"]
            },
            {
                "name": "EthicalJobs.com.au",
                "domain": "ethicaljobs.com.au", 
                "confidence": "high",
                "features": ["job_title", "company", "location"]
            },
            {
                "name": "Generic Sites",
                "domain": "*",
                "confidence": "medium",
                "features": ["basic_extraction"]
            }
        ]
    
    def get_extraction_stats(self):
        """Get extraction statistics (placeholder)"""
        return {
            "total_extractions": 0,
            "success_rate": 0.85,
            "avg_extraction_time": 2.5,
            "popular_domains": ["seek.com.au", "indeed.com", "linkedin.com"],
            "common_errors": ["Connection timeout", "Content not found"]
        }
    
    def calculate_readability_score(self, text: str) -> float:
        """Calculate readability score"""
        if not text:
            return 0.0
        
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        
        if sentences == 0:
            return 0.0
        
        avg_words_per_sentence = words / sentences
        
        if avg_words_per_sentence < 15:
            return 85.0
        elif avg_words_per_sentence < 25:
            return 70.0
        else:
            return 50.0
    
    def calculate_completeness_score(self, key_info: dict) -> float:
        """Calculate completeness score"""
        required_elements = [
            'has_requirements', 'has_skills', 'has_responsibilities', 
            'has_company_info', 'has_job_title'
        ]
        
        present_elements = sum(1 for elem in required_elements if key_info.get(elem, False))
        return (present_elements / len(required_elements)) * 100
    
    def calculate_structure_score(self, text: str) -> float:
        """Calculate structure score"""
        if not text:
            return 0.0
        
        headers = len([line for line in text.split('\n') if line.isupper() and len(line) > 5])
        bullets = text.count('•') + text.count('-') + text.count('*')
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        
        score = 0
        if headers > 0: score += 30
        if bullets > 0: score += 30 
        if paragraphs > 2: score += 40
        
        return min(score, 100)
    
    def calculate_overall_quality(self, analysis: dict) -> str:
        """Calculate overall quality rating"""
        avg_score = (
            analysis.get('readability_score', 0) + 
            analysis.get('completeness_score', 0) + 
            analysis.get('structure_score', 0)
        ) / 3
        
        if avg_score >= 80: return "Excellent"
        elif avg_score >= 60: return "Good"
        elif avg_score >= 40: return "Fair"
        else: return "Poor"
    
    def generate_content_recommendations(self, analysis: dict, key_info: dict) -> list:
        """Generate recommendations"""
        recommendations = []
        
        if analysis.get('readability_score', 0) < 60:
            recommendations.append("Consider shortening sentences for better readability")
        
        if analysis.get('structure_score', 0) < 60:
            recommendations.append("Add section headers and bullet points")
        
        if not key_info.get('has_requirements', False):
            recommendations.append("Include clear job requirements section")
        
        return recommendations
    
    def identify_missing_elements(self, key_info: dict) -> list:
        """Identify missing elements"""
        missing = []
        
        if not key_info.get('has_job_title', False):
            missing.append('Job Title')
        if not key_info.get('has_requirements', False):
            missing.append('Job Requirements')
        if not key_info.get('has_skills', False):
            missing.append('Required Skills')
        
        return missing


# Global JD extractor instance
jd_extractor = JDExtractor()
