import requests
from bs4 import BeautifulSoup
import re

def scrape_job_description(url: str) -> str:
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
    
    # Extract the main job content
    job_sections = []
    
    # Look for the main job description sections
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main', re.I))
    
    if main_content:
        # Extract key sections in order
        sections_to_extract = [
            ('Job Title', r'(data analyst|software engineer|developer)', 'h1, h2, .job-title, [class*="title"]'),
            ('Company', r'(no to violence|company)', 'h2, h3, .company, [class*="company"]'),
            ('Job Summary', r'(job summary|summary)', '.summary, [class*="summary"]'),
            ('Job Description', r'(job description|description)', '.description, [class*="description"]'),
            ('About Us', r'(about us|about)', '.about, [class*="about"]'),
            ('About the Role', r'(about the role|role|responsibilities)', '.role, [class*="role"], [class*="responsibilities"]'),
            ('Requirements', r'(requirements|qualifications|skills)', '.requirements, [class*="requirements"], [class*="qualifications"]'),
            ('What We Offer', r'(what we offer|benefits|offer)', '.benefits, [class*="benefits"], [class*="offer"]'),
            ('How to Apply', r'(how to apply|apply)', '.apply, [class*="apply"]')
        ]
        
        extracted_content = []
        processed_text = set()  # Track processed content to avoid duplicates
        
        # Get all text content and process it
        all_text = main_content.get_text(separator='\n', strip=True)
        
        # Split into logical sections based on common patterns
        sections = re.split(r'\n(?=[A-Z][^a-z]*(?:\n|$))', all_text)
        
        for section in sections:
            section = section.strip()
            if not section or len(section) < 50:  # Skip very short sections
                continue
                
            # Clean the section
            cleaned_section = clean_section_text(section)
            
            # Skip if we've already processed this content
            section_key = cleaned_section[:100].lower()  # Use first 100 chars as key
            if section_key in processed_text:
                continue
                
            processed_text.add(section_key)
            
            # Only include sections that look like job content
            if is_job_content(cleaned_section):
                extracted_content.append(cleaned_section)
        
        # Join the extracted sections
        job_text = '\n\n'.join(extracted_content)
        
    else:
        # Fallback to generic extraction
        job_text = scrape_generic(soup)
    
    # Final cleanup
    job_text = final_cleanup(job_text)
    
    return job_text


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


def clean_section_text(text: str) -> str:
    """Clean individual section text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common navigation patterns
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip obvious navigation/UI elements
        if re.match(r'^(home|search|menu|back|next|apply now|sign in|join|subscribe)$', line, re.I):
            continue
            
        if len(line) < 5:  # Skip very short lines
            continue
            
        cleaned_lines.append(line)
    
    return ' '.join(cleaned_lines)


def is_job_content(text: str) -> bool:
    """Check if text section contains actual job content"""
    text_lower = text.lower()
    
    # Must contain job-related keywords
    job_keywords = [
        'role', 'position', 'responsibilities', 'requirements', 'qualifications',
        'experience', 'skills', 'analyst', 'developer', 'engineer', 'manager',
        'about us', 'company', 'organization', 'team', 'work', 'job',
        'benefits', 'offer', 'salary', 'apply', 'application'
    ]
    
    has_job_keywords = any(keyword in text_lower for keyword in job_keywords)
    
    # Must not be primarily navigation/UI
    navigation_keywords = [
        'cookie', 'privacy policy', 'terms of service', 'copyright',
        'facebook', 'twitter', 'linkedin', 'instagram', 'social media',
        'search jobs', 'browse jobs', 'job alerts', 'career advice',
        'employer login', 'post a job', 'pricing', 'contact us'
    ]
    
    is_navigation = any(keyword in text_lower for keyword in navigation_keywords)
    
    # Must have reasonable length
    has_reasonable_length = 30 < len(text) < 5000
    
    return has_job_keywords and not is_navigation and has_reasonable_length


def final_cleanup(text: str) -> str:
    """Final cleanup of scraped text"""
    
    # Remove duplicate sentences
    sentences = re.split(r'[.!?]+', text)
    unique_sentences = []
    seen_sentences = set()
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Normalize for comparison (remove extra spaces, convert to lowercase)
        normalized = re.sub(r'\s+', ' ', sentence.lower())
        
        if normalized not in seen_sentences and len(sentence) > 10:
            seen_sentences.add(normalized)
            unique_sentences.append(sentence)
    
    # Rejoin sentences
    clean_text = '. '.join(unique_sentences)
    
    # Final whitespace cleanup
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Add proper sentence endings
    if clean_text and not clean_text.endswith('.'):
        clean_text += '.'
    
    return clean_text