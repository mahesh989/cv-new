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
        }

        # Add timeout to prevent hanging requests
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Site-specific extraction
        if 'ethicaljobs.com.au' in url:
            return scrape_ethicaljobs(soup)
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
    
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'menu']):
        element.decompose()

    # Remove common navigation and UI elements
    for element in soup.find_all(class_=re.compile(r'(nav|menu|breadcrumb|sidebar|footer|header)', re.I)):
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
