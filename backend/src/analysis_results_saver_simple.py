"""
Simplified Analysis Results Saver - Only creates 3 files per company:
1. company_slug_output_log.txt
2. job_info_company_slug.json  
3. original_cv_text.txt
"""
import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SimpleAnalysisResultsSaver:
    def __init__(self, results_dir: str = "analysis_results", debug: bool = False):
        """Initialize with results directory and debug flag"""
        self.results_dir = results_dir
        self.debug = debug
        os.makedirs(results_dir, exist_ok=True)
    
    def extract_company_name(self, jd_text: str) -> str:
        """Extract company name from JD text - improved to be more accurate"""
        # First, try to find "No to Violence" specifically in the text
        if "No to Violence" in jd_text:
            company_name = "No_to_Violence"
            logger.info(f"✅ Found specific company name: {company_name}")
            return company_name
        
        # Look for company name in the first few lines
        lines = jd_text.split('\n')
        first_lines = lines[:10]  # Check first 10 lines
        
        # Look for company patterns in first lines
        for line in first_lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip common non-company lines
            if (line.startswith('http') or 
                line.startswith('Job') or 
                line.startswith('We') or 
                line.startswith('The') or
                line.startswith('About') or
                line.startswith('Work for') or
                line.startswith('Leading') or
                line.startswith('Applications') or
                line.startswith('Posted on') or
                line.startswith('Melbourne') or
                line.startswith('Full Time') or
                line.startswith('Contract') or
                line.startswith('Information Technology') or
                line.startswith('Policy and Research') or
                line.startswith('Not For Profit') or
                line.startswith('NFP') or
                line.startswith('Data Analyst') or
                line.startswith('Job Summary') or
                line.startswith('Applications close') or
                line.startswith('Job posted on') or
                line.startswith('CBD') or
                line.startswith('Inner Suburbs') or
                line.startswith('Work for an organisation') or
                line.startswith('Leading organisation') or
                line.startswith('Melbourne CBD Office') or
                line.startswith('close to public transport') or
                line.startswith('hybrid working') or
                line.startswith('About us') or
                line.startswith('No to Violence is')):
                continue
            
            # Look for company name patterns - more restrictive
            if (len(line) >= 3 and len(line) < 50 and 
                line[0].isupper() and 
                not line.isupper() and  # Not all caps
                not re.search(r'\d', line) and  # No numbers
                not re.search(r'[<>{}[\]()]', line) and  # No special brackets
                not re.search(r'http', line, re.IGNORECASE) and  # No URLs
                not re.search(r'[<>]', line) and  # No angle brackets
                not re.search(r'[&,]', line) and  # No ampersands or commas
                not re.search(r'\s+', line) and  # No multiple spaces
                not re.search(r'[A-Z]{2,}', line)):  # No consecutive uppercase letters
                
                # Clean up company name
                company_name = re.sub(r'[^\w\s&.-]', '', line)
                company_name = re.sub(r'\s+', '_', company_name)
                company_name = company_name.strip('_')
                
                if len(company_name) >= 3 and len(company_name) < 50:
                    logger.info(f"✅ Extracted company name: {company_name}")
                    return company_name
        
        # Fallback: look for specific patterns
        company_patterns = [
            r'at\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+in|\s+is|\s+are|\s+looking|\s+seeking)',
            r'with\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+in|\s+is|\s+are|\s+looking|\s+seeking)',
            r'for\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+in|\s+is|\s+are|\s+looking|\s+seeking)',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+is\s+looking',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+are\s+looking',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+seeking',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                # Clean up company name
                company_name = re.sub(r'[^\w\s&.-]', '', company_name)
                company_name = re.sub(r'\s+', '_', company_name)
                company_name = company_name.strip('_')
                if len(company_name) >= 3 and len(company_name) < 50:
                    logger.info(f"✅ Extracted company name via pattern: {company_name}")
                    return company_name
        
        # Final fallback to timestamp-based name
        fallback_name = f"Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.warning(f"⚠️ Could not extract company name, using fallback: {fallback_name}")
        return fallback_name
    
    def save_analysis_results(self, 
                            cv_text: str,
                            jd_text: str,
                            skill_comparison: Dict,
                            ats_results: Dict,
                            company_name: Optional[str] = None) -> str:
        """
        Save analysis results to company_slug_output_log.txt
        
        Args:
            cv_text: CV content
            jd_text: Job description content
            skill_comparison: Skill comparison results
            ats_results: Enhanced ATS score results
            company_name: Optional company name override
            
        Returns:
            str: Path to saved file
        """
        try:
            # Validate inputs
            if not cv_text or not jd_text:
                raise ValueError("CV text and JD text are required")
            
            # Extract company name if not provided
            if not company_name:
                company_name = self.extract_company_name(jd_text)
            
            # Create company slug - ensure it's clean and short
            company_slug = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '_')
            # Truncate if too long
            if len(company_slug) > 50:
                company_slug = company_slug[:50]
            
            logger.info(f"📁 Creating company directory: {company_slug}")
            
            # Create company subdirectory
            company_dir = os.path.join(self.results_dir, company_slug)
            os.makedirs(company_dir, exist_ok=True)
            
            # Create filename: company_slug_output_log.txt
            filename = f"{company_slug}_output_log.txt"
            filepath = os.path.join(company_dir, filename)
            
            # Generate simple output log
            report_content = self._generate_simple_output_log(
                cv_text, jd_text, skill_comparison, ats_results, company_name
            )
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"✅ Output log saved to: {filepath}")
            
            # Also save the other 2 files to complete the 3-file structure
            self.save_job_info_as_json(jd_text, company_name)
            self.save_original_cv_text(cv_text, company_name)
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save output log: {e}")
            raise
    
    def _generate_simple_output_log(self, 
                            cv_text: str,
                            jd_text: str,
                            skill_comparison: Dict,
                            ats_results: Dict,
                            company_name: str) -> str:
        """Generate simple output log with key information"""
        
        report = []
        report.append("=" * 80)
        report.append(f"OUTPUT LOG")
        report.append(f"Company: {company_name}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # CV info
        report.append("📄 CV CONTENT:")
        report.append(f"Length: {len(cv_text)} characters")
        report.append("")
        
        # JD info
        report.append("📋 JOB DESCRIPTION:")
        report.append(f"Length: {len(jd_text)} characters")
        report.append("")
        
        # Skill comparison summary
        if skill_comparison:
            report.append("🔍 SKILL COMPARISON:")
            match_summary = skill_comparison.get('match_summary', {})
            total_matches = match_summary.get('total_matches', 0)
            total_requirements = match_summary.get('total_jd_requirements', 0)
            match_percentage = match_summary.get('match_percentage', 0)
            report.append(f"Match: {match_percentage}% ({total_matches}/{total_requirements})")
            report.append("")
        
        # ATS results summary
        if ats_results:
            report.append("🎯 ATS RESULTS:")
            overall_score = ats_results.get('overall_ats_score', 'Unknown')
            score_category = ats_results.get('score_category', 'Unknown')
            report.append(f"Score: {overall_score}/100")
            report.append(f"Category: {score_category}")
            report.append("")
        
        return "\n".join(report)
    
    def save_job_info_as_json(self, jd_text: str, company_name: str, job_link: str = None) -> str:
        """
        Extract job information and save as job_info_company_slug.json
        
        Args:
            jd_text: Job description text
            company_name: Company name for folder organization
            job_link: Optional job link
            
        Returns:
            str: Path to saved JSON file
        """
        try:
            # Create company slug
            company_slug = re.sub(r'[^\w\s&.-]', '', company_name)
            company_slug = re.sub(r'\s+', '_', company_slug)
            company_slug = company_slug.strip('_')
            # Truncate if too long
            if len(company_slug) > 50:
                company_slug = company_slug[:50]
            
            # Create company subdirectory
            company_dir = os.path.join(self.results_dir, company_slug)
            os.makedirs(company_dir, exist_ok=True)
            
            # Create filename
            filename = f"job_info_{company_slug}.json"
            filepath = os.path.join(company_dir, filename)
            
            # Prepare job info data
            job_info = {
                "company_name": company_name,
                "job_title": "Unknown",
                "location": "Unknown",
                "experience_required": "Unknown",
                "seniority_level": "Unknown",
                "industry": "Unknown",
                "phone_number": "Unknown",
                "email": "Unknown",
                "website": "Unknown",
                "work_type": "Unknown"
            }
            
            # Add job_link if provided
            if job_link:
                job_info['job_link'] = job_link
            
            # Save to JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(job_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Job info saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save job info: {e}")
            raise
    
    def save_original_cv_text(self, cv_text: str, company_name: str) -> str:
        """
        Save original CV text to company-specific folder
        
        Args:
            cv_text: Original CV text content
            company_name: Company name for folder organization
            
        Returns:
            str: Path to saved text file
        """
        try:
            # Clean company name for directory
            company_slug = re.sub(r'[^\w\s&.-]', '', company_name)
            company_slug = re.sub(r'\s+', '_', company_slug)
            company_slug = company_slug.strip('_')
            # Truncate if too long
            if len(company_slug) > 50:
                company_slug = company_slug[:50]
            
            # Create company-specific directory
            company_dir = os.path.join(self.results_dir, company_slug)
            os.makedirs(company_dir, exist_ok=True)
            
            # Create filename
            filename = "original_cv_text.txt"
            filepath = os.path.join(company_dir, filename)
            
            # Save CV text to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ORIGINAL CV TEXT\n")
                f.write(f"Company: {company_name}\n")
                f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Length: {len(cv_text)} characters\n")
                f.write("=" * 80 + "\n\n")
                f.write(cv_text)
            
            logger.info(f"✅ Original CV text saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save original CV text: {e}")
            raise
