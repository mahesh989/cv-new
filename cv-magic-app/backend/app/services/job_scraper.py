import requests
from bs4 import BeautifulSoup
import re
import asyncio
from typing import Optional

def scrape_job_description(url: str) -> str:
    """
    Scrape job description from a given URL.
    
    Args:
        url: The URL of the job posting
        
    Returns:
        Extracted job description text
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # Add Seek-specific headers
        if 'seek.com.au' in url:
            headers["Referer"] = "https://www.seek.com.au/"
            headers["Sec-Fetch-Dest"] = "document"
            headers["Sec-Fetch-Mode"] = "navigate"
            headers["Sec-Fetch-Site"] = "same-origin"

        # Add timeout to prevent hanging requests
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Site-specific extraction
        if 'ethicaljobs.com.au' in url:
            return scrape_ethicaljobs(soup)
        elif 'seek.com.au' in url:
            return scrape_seek(soup)
        else:
            return scrape_generic(soup)

    except requests.exceptions.Timeout:
        return f"Error: Request timed out while fetching job description from {url}"
    except requests.exceptions.ConnectionError:
        return f"Error: Connection failed while fetching job description from {url}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching job description: {str(e)}"
    except Exception as e:
        return f"Unexpected error while scraping job description: {str(e)}"


def scrape_seek(soup: BeautifulSoup) -> str:
    """Specialized scraper for Seek.com.au website"""
    
    # Check if job is expired/removed
    expired_indicators = [
        "This job is no longer advertised",
        "Jobs remain on SEEK for 30 days",
        "no longer advertised",
        "job is no longer available",
        "This job has been removed",
        "Job posting has expired"
    ]
    
    page_text = soup.get_text().lower()
    for indicator in expired_indicators:
        if indicator.lower() in page_text:
            return f"Error: Job posting has expired or been removed from Seek. The job is no longer available for application."
    
    # Remove unwanted elements
    unwanted_selectors = [
        'nav', 'header', 'footer', 'aside', 'menu',
        '[class*="navigation"]', '[class*="nav"]', '[class*="menu"]',
        '[class*="sidebar"]', '[class*="footer"]', '[class*="header"]',
        'form', 'button', '[class*="search"]', '[class*="filter"]',
        '[class*="breadcrumb"]', '[class*="pagination"]',
        'script', 'style', 'noscript',
        '[class*="advertisement"]', '[class*="ad"]',
        '[class*="cookie"]', '[class*="consent"]'
    ]
    
    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    # Look for Seek-specific job content selectors
    job_content_selectors = [
        '[data-automation-id="jobAdDetails"]',  # Main job description
        '[data-automation-id="jobAdDetails"] div',  # Job description content
        '[data-automation-id="jobDescription"]',  # Alternative selector
        '[data-automation-id="jobDescription"] div',  # Job description content
        '[class*="jobAdDetails"]',
        '[class*="job-description"]',
        '[class*="job-details"]',
        '[class*="job-content"]',
        '[class*="jobDescription"]',
        '[class*="jobAd"]',
        'main', 'article',
        '[data-testid*="job"]',  # Test ID selectors
        '[data-testid*="description"]',
        '[data-testid*="content"]'
    ]
    
    # Also try to extract from JSON data in the page
    json_data_selectors = [
        'script[type="application/json"]',
        'script[type="application/ld+json"]'
    ]
    
    job_text = ""
    
    # For Seek, try multiple extraction methods
    job_text = ""
    
    # Method 1: Try JSON-LD structured data first (most reliable for Seek)
    json_ld_scripts = soup.select('script[type="application/ld+json"]')
    for script in json_ld_scripts:
        try:
            import json
            data = json.loads(script.string)
            if isinstance(data, dict):
                job_content = _extract_job_from_json_ld(data)
                if job_content and len(job_content) > len(job_text):
                    job_text = job_content
        except (json.JSONDecodeError, AttributeError):
            continue
    
    # Method 2: Try JSON data extraction
    if not job_text or len(job_text) < 100:
        for selector in json_data_selectors:
            scripts = soup.select(selector)
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    # Look for job content in the JSON structure
                    if isinstance(data, dict):
                        job_content = _extract_job_from_json(data)
                        if job_content and len(job_content) > len(job_text):
                            job_text = job_content
                except (json.JSONDecodeError, AttributeError):
                    continue
    
    # Method 3: Try page source extraction
    if not job_text or len(job_text) < 100:
        page_source = str(soup)
        job_content = _extract_job_from_page_source(page_source)
        # Only use page source extraction if it finds substantial content (more than 500 chars)
        if job_content and len(job_content) > 500 and len(job_content) > len(job_text):
            job_text = job_content
    
    # Method 4: Try JavaScript script extraction
    if not job_text or len(job_text) < 100:
        all_scripts = soup.find_all('script')
        for script in all_scripts:
            if script.string and ('jobDetails' in script.string or 'content' in script.string):
                job_content = _extract_job_from_script(script.string)
                if job_content and len(job_content) > len(job_text):
                    job_text = job_content
    
    # If no JSON content found, try HTML selectors
    if not job_text or len(job_text) < 100:
        for selector in job_content_selectors:
            elements = soup.select(selector)
            if elements:
                # Get text from the first matching element
                job_text = elements[0].get_text(separator=' ', strip=True)
                job_text = re.sub(r'\s+', ' ', job_text).strip()
                if len(job_text) > 200:  # Ensure we have substantial content
                    break
    
    # If still no content, try to extract from sections (common in Seek)
    if not job_text or len(job_text) < 100:
        sections = soup.find_all('section')
        for i, section in enumerate(sections):
            section_text = section.get_text(separator=' ', strip=True)
            section_text = re.sub(r'\s+', ' ', section_text).strip()
            
            # Check if this section contains job-related content
            job_keywords = [
                'about the role', 'job description', 'position overview', 'key responsibilities',
                'requirements', 'qualifications', 'skills required', 'experience required',
                'what we offer', 'benefits', 'company culture', 'team', 'location', 'salary'
            ]
            
            found_keywords = [keyword for keyword in job_keywords if keyword in section_text.lower()]
            
            if found_keywords:
                # Prioritize job description content over company profile
                is_job_description = any(keyword in section_text.lower() for keyword in [
                    'about the role', 'job description', 'position overview', 'key responsibilities',
                    'what you', 'about you', 'requirements', 'qualifications'
                ])
                
                is_company_profile = any(keyword in section_text.lower() for keyword in [
                    'company profile', 'about ventura', 'since we first started', 'our commitment',
                    'diverse culture', 'innovative', 'brilliant benefits'
                ])
                
                # If it's job description content, prioritize it
                if is_job_description and not is_company_profile:
                    if len(section_text) > len(job_text):
                        job_text = section_text
                # If it contains both job description and company profile, extract just the job description part
                elif is_job_description and is_company_profile:
                    # Try to extract just the job description part
                    job_desc_start = section_text.lower().find('about the role')
                    if job_desc_start != -1:
                        # Find a good end point (before company profile content)
                        company_profile_start = section_text.lower().find('company profile')
                        if company_profile_start != -1 and company_profile_start > job_desc_start:
                            job_desc_text = section_text[job_desc_start:company_profile_start].strip()
                            if len(job_desc_text) > len(job_text):
                                job_text = job_desc_text
                        else:
                            # If no clear company profile start, take everything from "About the Role"
                            job_desc_text = section_text[job_desc_start:].strip()
                            if len(job_desc_text) > len(job_text):
                                job_text = job_desc_text
                # If it's company profile and we don't have job description yet, use it as fallback
                elif is_company_profile and not job_text:
                    if len(section_text) > len(job_text):
                        job_text = section_text
                # If we have no other content, use any job-related content
                elif not job_text:
                    if len(section_text) > len(job_text):
                        job_text = section_text
    
    # If no specific job content found, try to extract from the main content area
    if not job_text or len(job_text) < 100:
        # Look for main content containers
        main_containers = soup.find_all(['div', 'section'], class_=re.compile(r'(content|main|body)', re.I))
        for container in main_containers:
            text = container.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > len(job_text):
                job_text = text
    
    return final_cleanup(job_text)


def scrape_ethicaljobs(soup: BeautifulSoup) -> str:
    """Specialized scraper for EthicalJobs website"""
    
    # Remove all navigation, sidebar, and duplicate elements
    unwanted_selectors = [
        'nav', 'header', 'footer', 'aside', 'menu',
        '[class*="navigation"]', '[class*="nav"]', '[class*="menu"]',
        '[class*="sidebar"]', '[class*="footer"]', '[class*="header"]',
        'form', 'button', '[class*="search"]', '[class*="filter"]',
        '[class*="breadcrumb"]', '[class*="pagination"]',
        'script', 'style', 'noscript'
    ]
    
    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    # Look for job description content
    job_content_selectors = [
        '[class*="job-description"]',
        '[class*="job-details"]', 
        '[class*="job-content"]',
        '[class*="description"]',
        'main', 'article'
    ]
    
    job_text = ""
    for selector in job_content_selectors:
        elements = soup.select(selector)
        if elements:
            # Get text from the first matching element
            job_text = elements[0].get_text(separator=' ', strip=True)
            job_text = re.sub(r'\s+', ' ', job_text).strip()
            if len(job_text) > 200:  # Ensure we have substantial content
                break
    
    # If no specific job content found, try to extract from the main content area
    if not job_text or len(job_text) < 100:
        # Look for main content containers
        main_containers = soup.find_all(['div', 'section'], class_=re.compile(r'(content|main|body)', re.I))
        for container in main_containers:
            text = container.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > len(job_text):
                job_text = text
    
    return final_cleanup(job_text)


def scrape_generic(soup: BeautifulSoup) -> str:
    """Generic scraper for other job sites"""
    
    # Remove unwanted elements (but not body or html)
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'menu']):
        element.decompose()

    # Remove common navigation and UI elements (but not body or html)
    for element in soup.find_all(class_=re.compile(r'(nav|menu|breadcrumb|sidebar|footer|header)', re.I)):
        # Don't remove body or html elements as they contain the main content
        if element.name not in ['body', 'html']:
            element.decompose()

    # Try to find the main job description content
    priority_selectors = [
        'main', 'article',
        '[class*="job-description"]', '[class*="job-details"]', '[class*="job-content"]',
        '[class*="description"]', '[class*="details"]', '[class*="content"]'
    ]
    
    job_text = ""
    for selector in priority_selectors:
        containers = soup.select(selector)
        if containers:
            main_container = containers[0]
            job_text = main_container.get_text(separator=' ', strip=True)
            job_text = re.sub(r'\s+', ' ', job_text).strip()
            if len(job_text) > 200:
                break
    
    # Fallback to full page text
    if not job_text or len(job_text) < 100:
        job_text = soup.get_text(separator=' ', strip=True)
        job_text = re.sub(r'\s+', ' ', job_text).strip()

    return final_cleanup(job_text)


def _extract_job_from_json_ld(data: dict) -> str:
    """Extract job description from JSON-LD structured data"""
    try:
        job_content = ""
        
        # Check for @graph structure (common in JSON-LD)
        if '@graph' in data and isinstance(data['@graph'], list):
            for item in data['@graph']:
                if isinstance(item, dict):
                    # Look for job posting
                    if item.get('@type') == 'JobPosting':
                        for key in ['description', 'content', 'jobDescription', 'details']:
                            if key in item and isinstance(item[key], str):
                                if len(item[key]) > len(job_content):
                                    job_content = item[key]
        
        # Check for direct job posting
        if not job_content and data.get('@type') == 'JobPosting':
            for key in ['description', 'content', 'jobDescription', 'details']:
                if key in data and isinstance(data[key], str):
                    if len(data[key]) > len(job_content):
                        job_content = data[key]
        
        # Clean up HTML tags if present
        if job_content:
            import re
            # Remove HTML tags
            job_content = re.sub(r'<[^>]+>', ' ', job_content)
            # Decode HTML entities
            job_content = job_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            job_content = job_content.replace('&nbsp;', ' ').replace('&rsquo;', "'").replace('&ldquo;', '"').replace('&rdquo;', '"')
            job_content = job_content.replace('&bull;', '•').replace('&ndash;', '–').replace('&mdash;', '—')
            # Decode Unicode escapes
            job_content = job_content.replace('\\u003C', '<').replace('\\u003E', '>').replace('\\u002F', '/')
            job_content = job_content.replace('\\u0026', '&').replace('\\u0027', "'").replace('\\u0022', '"')
            # Additional HTML entity decoding
            job_content = job_content.replace('&quot;', '"').replace('&apos;', "'")
            # Clean up whitespace
            job_content = re.sub(r'\s+', ' ', job_content).strip()
        
        return job_content
        
    except Exception:
        return ""


def _extract_job_from_json(data: dict) -> str:
    """Extract job description from JSON data structure"""
    try:
        # Look for job content in various JSON structures
        job_content = ""
        
        # Check for job details in the data structure
        if 'jobDetails' in data and 'result' in data['jobDetails']:
            job_data = data['jobDetails']['result']
            if 'job' in job_data and 'content' in job_data['job']:
                job_content = job_data['job']['content']
        
        # Check for Seek-specific data structures
        if not job_content:
            # Look for Seek-specific job data
            if 'job' in data:
                job_data = data['job']
                for key in ['content', 'description', 'jobDescription', 'details', 'summary']:
                    if key in job_data and isinstance(job_data[key], str):
                        if len(job_data[key]) > len(job_content):
                            job_content = job_data[key]
            
            # Look for job posting data
            if 'jobPosting' in data:
                posting_data = data['jobPosting']
                for key in ['description', 'content', 'jobDescription', 'details']:
                    if key in posting_data and isinstance(posting_data[key], str):
                        if len(posting_data[key]) > len(job_content):
                            job_content = posting_data[key]
        
        # Check for job content in other possible locations
        if not job_content:
            # Look for content field in the data
            for key in ['content', 'description', 'jobDescription', 'job_content', 'details', 'summary']:
                if key in data and isinstance(data[key], str):
                    if len(data[key]) > len(job_content):
                        job_content = data[key]
        
        # Clean up HTML tags if present
        if job_content:
            import re
            # Remove HTML tags
            job_content = re.sub(r'<[^>]+>', ' ', job_content)
            # Decode HTML entities
            job_content = job_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            job_content = job_content.replace('&nbsp;', ' ').replace('&rsquo;', "'").replace('&ldquo;', '"').replace('&rdquo;', '"')
            job_content = job_content.replace('&bull;', '•').replace('&ndash;', '–').replace('&mdash;', '—')
            # Decode Unicode escapes
            job_content = job_content.replace('\\u003C', '<').replace('\\u003E', '>').replace('\\u002F', '/')
            job_content = job_content.replace('\\u0026', '&').replace('\\u0027', "'").replace('\\u0022', '"')
            # Additional HTML entity decoding
            job_content = job_content.replace('&quot;', '"').replace('&apos;', "'")
            # Clean up whitespace
            job_content = re.sub(r'\s+', ' ', job_content).strip()
        
        return job_content
        
    except Exception:
        return ""


def _extract_job_from_script(script_content: str) -> str:
    """Extract job content from JavaScript script content"""
    try:
        import re
        
        # Look for job content in JavaScript variables
        content_match = re.search(r'"content":"([^"]+)"', script_content)
        if content_match:
            content = content_match.group(1)
            # Decode Unicode escapes
            content = content.encode().decode('unicode_escape')
            # Clean up HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            content = content.replace('&nbsp;', ' ').replace('&rsquo;', "'").replace('&ldquo;', '"').replace('&rdquo;', '"')
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            return content
        
        return ""
        
    except Exception:
        return ""


def _extract_job_from_page_source(page_source: str) -> str:
    """Extract job content from page source using regex patterns"""
    try:
        import re
        
        # Look for job content patterns - more comprehensive for Seek
        job_patterns = [
            # Common job description sections
            r'About the Role[^<]*',
            r'What You.*?Be Doing[^<]*',
            r'About You[^<]*',
            r'Why Join Ventura[^<]*',
            r'Job Description[^<]*',
            r'Position Overview[^<]*',
            r'Role Description[^<]*',
            r'Key Responsibilities[^<]*',
            r'Requirements[^<]*',
            r'Qualifications[^<]*',
            r'Skills Required[^<]*',
            r'Experience Required[^<]*',
            r'What We Offer[^<]*',
            r'Benefits[^<]*',
            r'Company Culture[^<]*',
            r'Team[^<]*',
            r'Location[^<]*',
            r'Salary[^<]*',
            r'Employment Type[^<]*',
            r'Work Arrangement[^<]*'
        ]
        
        job_content = ""
        for pattern in job_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Clean up HTML tags and entities
                clean_match = re.sub(r'<[^>]+>', ' ', match)
                # Decode HTML entities
                clean_match = clean_match.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                clean_match = clean_match.replace('&nbsp;', ' ').replace('&rsquo;', "'").replace('&ldquo;', '"').replace('&rdquo;', '"')
                clean_match = clean_match.replace('&bull;', '•').replace('&ndash;', '–').replace('&mdash;', '—')
                # Decode Unicode escapes
                clean_match = clean_match.replace('\\u003C', '<').replace('\\u003E', '>').replace('\\u002F', '/')
                clean_match = clean_match.replace('\\u0026', '&').replace('\\u0027', "'").replace('\\u0022', '"')
                # Additional HTML entity decoding
                clean_match = clean_match.replace('&quot;', '"').replace('&apos;', "'")
                clean_match = re.sub(r'\s+', ' ', clean_match).strip()
                if len(clean_match) > len(job_content):
                    job_content = clean_match
        
        # If we found content, try to get a larger section
        if job_content and ('About the Role' in job_content or 'Job Description' in job_content):
            # Try to find the start of the job description
            start_markers = ['About the Role', 'Job Description', 'Position Overview', 'Role Description']
            end_markers = ['Ready to Apply', 'Apply Now', 'How to Apply', 'Application Process', 'Contact Us']
            
            for start_marker in start_markers:
                if start_marker in job_content:
                    start_idx = page_source.find(start_marker)
                    if start_idx != -1:
                        # Try to find a good end point
                        for end_marker in end_markers:
                            end_idx = page_source.find(end_marker, start_idx)
                            if end_idx != -1:
                                full_content = page_source[start_idx:end_idx + len(end_marker)]
                                # Clean up the full content
                                full_content = re.sub(r'<[^>]+>', ' ', full_content)
                                # Decode HTML entities
                                full_content = full_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                                full_content = full_content.replace('&nbsp;', ' ').replace('&rsquo;', "'").replace('&ldquo;', '"').replace('&rdquo;', '"')
                                full_content = full_content.replace('&bull;', '•').replace('&ndash;', '–').replace('&mdash;', '—')
                                # Decode Unicode escapes
                                full_content = full_content.replace('\\u003C', '<').replace('\\u003E', '>').replace('\\u002F', '/')
                                full_content = full_content.replace('\\u0026', '&').replace('\\u0027', "'").replace('\\u0022', '"')
                                # Additional HTML entity decoding
                                full_content = full_content.replace('&quot;', '"').replace('&apos;', "'")
                                full_content = re.sub(r'\s+', ' ', full_content).strip()
                                if len(full_content) > len(job_content):
                                    job_content = full_content
                                break
                        break
        
        # If still no good content, try to extract from JSON-LD structured data
        if not job_content or len(job_content) < 200:
            json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
            json_ld_matches = re.findall(json_ld_pattern, page_source, re.IGNORECASE | re.DOTALL)
            for json_content in json_ld_matches:
                try:
                    import json
                    data = json.loads(json_content)
                    if isinstance(data, dict) and 'description' in data:
                        description = data['description']
                        if isinstance(description, str) and len(description) > len(job_content):
                            job_content = description
                except:
                    continue
        
        # If still no content, try to extract from meta description or other meta tags
        if not job_content or len(job_content) < 200:
            meta_patterns = [
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
                r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']',
                r'<meta[^>]*name=["\']twitter:description["\'][^>]*content=["\']([^"\']*)["\']'
            ]
            for pattern in meta_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                for match in matches:
                    if len(match) > len(job_content):
                        job_content = match
        
        return job_content
        
    except Exception:
        return ""


def final_cleanup(text: str) -> str:
    """Final cleanup of extracted text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common unwanted patterns
    unwanted_patterns = [
        r'Cookie\s+Policy.*?(?=\n|$)',
        r'Privacy\s+Policy.*?(?=\n|$)',
        r'Terms\s+of\s+Service.*?(?=\n|$)',
        r'Subscribe\s+to\s+our\s+newsletter.*?(?=\n|$)',
        r'Follow\s+us\s+on.*?(?=\n|$)',
        r'Share\s+this\s+job.*?(?=\n|$)',
        r'Apply\s+now.*?(?=\n|$)',
        r'View\s+all\s+jobs.*?(?=\n|$)',
    ]
    
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up any remaining excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


async def scrape_job_description_async(url: str) -> str:
    """
    Async wrapper for job description scraping.
    
    Args:
        url: The URL of the job posting
        
    Returns:
        Extracted job description text
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, scrape_job_description, url)


def is_valid_job_url(url: str) -> bool:
    """
    Check if the URL appears to be a valid job posting URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if the URL appears to be a job posting
    """
    if not url or not isinstance(url, str):
        return False
    
    # Check if it's a valid URL format
    if not re.match(r'^https?://', url):
        return False
    
    # Check for common job site patterns
    job_site_patterns = [
        r'linkedin\.com.*jobs',
        r'indeed\.com',
        r'glassdoor\.com.*jobs',
        r'seek\.com\.au',
        r'ethicaljobs\.com\.au',
        r'careerone\.com\.au',
        r'jobsearch\.gov\.au',
        r'jobs\.gov\.au',
        r'ziprecruiter\.com',
        r'monster\.com',
        r'careerbuilder\.com',
    ]
    
    for pattern in job_site_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    return True
