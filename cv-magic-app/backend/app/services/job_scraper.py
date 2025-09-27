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
        '[class*="jobAdDetails"]',
        '[class*="job-description"]',
        '[class*="job-details"]',
        'main', 'article'
    ]
    
    # Also try to extract from JSON data in the page
    json_data_selectors = [
        'script[type="application/json"]',
        'script[type="application/ld+json"]'
    ]
    
    job_text = ""
    
    # For Seek, prioritize page source extraction as it's most reliable
    page_source = str(soup)
    job_content = _extract_job_from_page_source(page_source)
    if job_content and len(job_content) > 100:
        job_text = job_content
    else:
        # Fallback to JSON data extraction
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
        
        # Also try to extract from JavaScript scripts
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
        
        # Check for job content in other possible locations
        if not job_content:
            # Look for content field in the data
            for key in ['content', 'description', 'jobDescription', 'job_content']:
                if key in data:
                    job_content = data[key]
                    break
        
        # Clean up HTML tags if present
        if job_content:
            import re
            # Remove HTML tags
            job_content = re.sub(r'<[^>]+>', ' ', job_content)
            # Decode HTML entities
            job_content = job_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            job_content = job_content.replace('&nbsp;', ' ').replace('&rsquo;', "'").replace('&ldquo;', '"').replace('&rdquo;', '"')
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
        
        # Look for job content patterns
        job_patterns = [
            r'About the Role[^<]*',
            r'What You.*?Be Doing[^<]*',
            r'About You[^<]*',
            r'Why Join Ventura[^<]*'
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
        if job_content and 'About the Role' in job_content:
            start_marker = 'About the Role'
            end_marker = 'Ready to Apply'
            start_idx = page_source.find(start_marker)
            if start_idx != -1:
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
