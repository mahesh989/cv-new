#!/usr/bin/env python3
"""
Generate markdown files for each unique company from skill analysis results.
Extracts the latest skill analysis for each company across all users.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def find_latest_analysis_per_company(base_path: Path) -> Dict[str, Tuple[Path, str]]:
    """
    Find the latest skills analysis file for each unique company.
    
    Returns:
        Dict mapping company_name -> (file_path, timestamp)
    """
    company_files = defaultdict(list)
    
    # Find all skills analysis files
    skills_files = list(base_path.rglob('*_skills_analysis_*.json'))
    
    for file_path in skills_files:
        # Extract company name from path
        # Format: .../applied_companies/{company}/{company}_skills_analysis_{timestamp}.json
        parts = file_path.parts
        if 'applied_companies' in parts:
            company_idx = parts.index('applied_companies')
            if company_idx + 1 < len(parts):
                company_name = parts[company_idx + 1]
                # Extract timestamp from filename
                match = re.search(r'(\d{8}_\d{6})', file_path.name)
                if match:
                    timestamp = match.group(1)
                    company_files[company_name].append((timestamp, file_path))
    
    # Get latest file for each company
    latest_per_company = {}
    for company, files in company_files.items():
        if files:
            # Sort by timestamp (descending) and get the latest
            files.sort(key=lambda x: x[0], reverse=True)
            latest_per_company[company] = files[0]
    
    return latest_per_company

def load_analysis_data(file_path: Path) -> Optional[Dict]:
    """Load and parse skills analysis JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def find_job_description(file_path: Path) -> Optional[str]:
    """Find and load job description text from JD original file."""
    try:
        # JD original files are in the same directory as skills analysis
        company_dir = file_path.parent
        
        # Find the latest JD original file (should match timestamp with skills analysis)
        jd_files = list(company_dir.glob('jd_original_*.json'))
        if not jd_files:
            return None
        
        # Get the latest JD file (sorted by filename which includes timestamp)
        latest_jd = sorted(jd_files, key=lambda x: x.name, reverse=True)[0]
        
        with open(latest_jd, 'r', encoding='utf-8') as f:
            jd_data = json.load(f)
        
        # Extract job description text
        jd_text = jd_data.get('text', '')
        if jd_text:
            return jd_text.strip()
        
        return None
    except Exception as e:
        print(f"Error loading job description: {e}")
        return None

def format_ats_score(ats_data: Dict) -> str:
    """Format ATS score information."""
    if not ats_data:
        return "N/A"
    
    final_score = ats_data.get('final_ats_score', 'N/A')
    breakdown = ats_data.get('breakdown', {})
    
    lines = [f"**Final ATS Score: {final_score}/100**\n"]
    
    if breakdown:
        category1 = breakdown.get('category1', {})
        category2 = breakdown.get('category2', {})
        bonus = breakdown.get('bonus_points', 0)
        
        if category1:
            lines.append(f"- **Category 1 (Keyword Matching):** {category1.get('score', 0)}/65")
            lines.append(f"  - Technical Skills: {category1.get('technical_points', 0)}/40")
            lines.append(f"  - Domain Keywords: {category1.get('domain_points', 0)}/10")
            lines.append(f"  - Soft Skills: {category1.get('soft_points', 0)}/15")
        
        if category2:
            lines.append(f"- **Category 2 (AI Component Analysis):** {category2.get('score', 0)}/35")
            tech_comp = category2.get('technical_skills_component', {})
            exp_comp = category2.get('experience_fit_component', {})
            if tech_comp:
                lines.append(f"  - Technical & Skills Component: {tech_comp.get('score', 0)}/22")
            if exp_comp:
                lines.append(f"  - Experience & Fit Component: {exp_comp.get('score', 0)}/13")
        
        if bonus:
            lines.append(f"- **Bonus Points:** {bonus}/10")
    
    return "\n".join(lines)

def format_skills_comparison(cv_skills: Dict, jd_skills: Dict) -> str:
    """Format skills comparison data from cv_skills and jd_skills."""
    if not cv_skills or not jd_skills:
        return "N/A"
    
    lines = []
    
    # Technical Skills
    cv_tech = set(cv_skills.get('technical_skills', []))
    jd_tech = set(jd_skills.get('technical_skills', []))
    matched_tech = cv_tech & jd_tech
    tech_match_rate = (len(matched_tech) / len(jd_tech) * 100) if jd_tech else 0
    
    lines.append(f"### Technical Skills")
    lines.append(f"- **CV Skills:** {len(cv_tech)}")
    lines.append(f"- **JD Requirements:** {len(jd_tech)}")
    lines.append(f"- **Matched:** {len(matched_tech)}")
    lines.append(f"- **Match Rate:** {tech_match_rate:.1f}%")
    if matched_tech:
        lines.append(f"- **Matched Skills:** {', '.join(sorted(matched_tech))}")
    if jd_tech - cv_tech:
        lines.append(f"- **Missing Skills:** {', '.join(sorted(jd_tech - cv_tech))}")
    lines.append("")
    
    # Soft Skills
    cv_soft = set(cv_skills.get('soft_skills', []))
    jd_soft = set(jd_skills.get('soft_skills', []))
    matched_soft = cv_soft & jd_soft
    soft_match_rate = (len(matched_soft) / len(jd_soft) * 100) if jd_soft else 0
    
    lines.append(f"### Soft Skills")
    lines.append(f"- **CV Skills:** {len(cv_soft)}")
    lines.append(f"- **JD Requirements:** {len(jd_soft)}")
    lines.append(f"- **Matched:** {len(matched_soft)}")
    lines.append(f"- **Match Rate:** {soft_match_rate:.1f}%")
    if matched_soft:
        lines.append(f"- **Matched Skills:** {', '.join(sorted(matched_soft))}")
    if jd_soft - cv_soft:
        lines.append(f"- **Missing Skills:** {', '.join(sorted(jd_soft - cv_soft))}")
    lines.append("")
    
    # Domain Keywords
    cv_domain = set(cv_skills.get('domain_keywords', []))
    jd_domain = set(jd_skills.get('domain_keywords', []))
    matched_domain = cv_domain & jd_domain
    domain_match_rate = (len(matched_domain) / len(jd_domain) * 100) if jd_domain else 0
    
    lines.append(f"### Domain Keywords")
    lines.append(f"- **CV Keywords:** {len(cv_domain)}")
    lines.append(f"- **JD Keywords:** {len(jd_domain)}")
    lines.append(f"- **Matched:** {len(matched_domain)}")
    lines.append(f"- **Match Rate:** {domain_match_rate:.1f}%")
    if matched_domain:
        lines.append(f"- **Matched Keywords:** {', '.join(sorted(matched_domain))}")
    if jd_domain - cv_domain:
        lines.append(f"- **Missing Keywords:** {', '.join(sorted(jd_domain - cv_domain))}")
    
    return "\n".join(lines)

def format_component_analysis(components: Dict) -> str:
    """Format component analysis data."""
    if not components:
        return "N/A"
    
    lines = []
    
    components_list = [
        ('skills_relevance', 'Skills Relevance'),
        ('experience_alignment', 'Experience Alignment'),
        ('industry_fit', 'Industry Fit'),
        ('role_seniority', 'Role Seniority'),
        ('technical_depth', 'Technical Depth'),
    ]
    
    for key, label in components_list:
        comp = components.get(key, {})
        if comp:
            score = comp.get('score', 0)
            analysis = comp.get('analysis', '')
            lines.append(f"### {label}: {score}/100")
            if analysis:
                lines.append(f"{analysis}\n")
    
    return "\n".join(lines)

def generate_markdown(company_name: str, analysis_data: Dict, file_path: Path, timestamp: str, job_description: Optional[str] = None) -> str:
    """Generate markdown content for a company."""
    lines = []
    
    # Header
    lines.append(f"# {company_name.replace('_', ' ')} - Skills Analysis Report")
    lines.append("")
    
    # Metadata
    lines.append("## Analysis Metadata")
    lines.append(f"- **Analysis Date:** {timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}")
    lines.append(f"- **Source File:** `{file_path.name}`")
    lines.append(f"- **User:** {file_path.parts[file_path.parts.index('user') + 1]}")
    lines.append("")
    
    # Job Description
    if job_description:
        lines.append("## Job Description")
        lines.append("")
        # Format the job description with proper line breaks
        jd_formatted = job_description.replace('\n\n', '\n\n').replace('\n', '  \n')
        lines.append(jd_formatted)
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # ATS Score
    ats_data = analysis_data.get('ats_score', {})
    if ats_data:
        lines.append("## ATS Score")
        lines.append(format_ats_score(ats_data))
        lines.append("")
    
    # JD Skills Details (keep this section)
    cv_skills = analysis_data.get('cv_skills', {})
    jd_skills = analysis_data.get('jd_skills', {})
    if jd_skills:
        lines.append("## Job Description Requirements")
        if jd_skills.get('technical_skills'):
            lines.append(f"### Required Technical Skills ({len(jd_skills['technical_skills'])}):")
            lines.append(", ".join(jd_skills['technical_skills']))
            lines.append("")
        if jd_skills.get('soft_skills'):
            lines.append(f"### Required Soft Skills ({len(jd_skills['soft_skills'])}):")
            lines.append(", ".join(jd_skills['soft_skills']))
            lines.append("")
        if jd_skills.get('domain_keywords'):
            lines.append(f"### Required Domain Keywords ({len(jd_skills['domain_keywords'])}):")
            lines.append(", ".join(jd_skills['domain_keywords']))
            lines.append("")
    
    # Component Analysis (keep this if exists)
    components = analysis_data.get('component_analysis', {})
    if components:
        lines.append("## Component Analysis")
        lines.append(format_component_analysis(components))
        lines.append("")
    
    return "\n".join(lines)

def main():
    # Base path in Docker container
    base_path = Path('/app/user')
    output_dir = Path('/tmp/company_analyses')
    output_dir.mkdir(exist_ok=True)
    
    print("Finding latest analysis files for each company...")
    latest_files = find_latest_analysis_per_company(base_path)
    
    print(f"\nFound {len(latest_files)} unique companies:")
    for company in sorted(latest_files.keys()):
        timestamp, file_path = latest_files[company]
        print(f"  - {company}: {file_path.name}")
    
    print("\nGenerating markdown files...")
    for company, (timestamp, file_path) in latest_files.items():
        analysis_data = load_analysis_data(file_path)
        if analysis_data:
            # Find job description
            job_description = find_job_description(file_path)
            if job_description:
                print(f"  ✓ Found job description for {company} ({len(job_description)} chars)")
            else:
                print(f"  ⚠ No job description found for {company}")
            
            md_content = generate_markdown(company, analysis_data, file_path, timestamp, job_description)
            output_file = output_dir / f"{company}_analysis.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"  ✓ Generated: {output_file.name}")
        else:
            print(f"  ✗ Failed to load: {file_path}")
    
    print(f"\n✅ Generated {len(latest_files)} markdown files in {output_dir}")
    print(f"\nTo download files, run:")
    print(f"  docker cp cv_backend:{output_dir} ./company_analyses")

if __name__ == '__main__':
    main()

