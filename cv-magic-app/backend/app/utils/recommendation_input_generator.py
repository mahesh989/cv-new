"""
Recommendation Input Generator

Automatically creates streamlined recommendation input files from skills analysis results.
This file is triggered whenever ATS calculation is completed.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RecommendationInputGenerator:
    """Generates streamlined recommendation input files from skills analysis results"""
    
    def __init__(self, base_analysis_dir: str = "cv-analysis"):
        self.base_analysis_dir = Path(base_analysis_dir)
    
    def generate_recommendation_input(self, company_name: str, skills_analysis_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a streamlined recommendation input file from skills analysis data
        
        Args:
            company_name: Name of the company (used for folder structure)
            skills_analysis_data: Complete skills analysis data from the main analysis file
            
        Returns:
            Path to the generated recommendation input file, or None if failed
        """
        try:
            # Create company directory if it doesn't exist
            company_dir = self.base_analysis_dir / company_name
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract only the essential data for recommendations
            recommendation_data = self._extract_recommendation_data(skills_analysis_data)
            
            # Generate filename
            recommendation_filename = f"{company_name}_recommendation_input.json"
            recommendation_filepath = company_dir / recommendation_filename
            
            # Save the streamlined data
            with open(recommendation_filepath, 'w', encoding='utf-8') as f:
                json.dump(recommendation_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ [RECOMMENDATION_INPUT] Generated: {recommendation_filepath}")
            return str(recommendation_filepath)
            
        except Exception as e:
            logger.error(f"❌ [RECOMMENDATION_INPUT] Failed to generate for {company_name}: {e}")
            return None
    
    def _extract_recommendation_data(self, skills_analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract only the essential data needed for recommendations
        
        Args:
            skills_analysis_data: Complete skills analysis data
            
        Returns:
            Streamlined data structure for recommendations
        """
        recommendation_data = {}
        
        # Extract CV comprehensive analysis
        if 'cv_comprehensive_analysis' in skills_analysis_data:
            recommendation_data['cv_comprehensive_analysis'] = skills_analysis_data['cv_comprehensive_analysis']
        
        # Extract JD comprehensive analysis  
        if 'jd_comprehensive_analysis' in skills_analysis_data:
            recommendation_data['jd_comprehensive_analysis'] = skills_analysis_data['jd_comprehensive_analysis']
        
        # Extract analyze match entries (remove timestamps)
        if 'analyze_match_entries' in skills_analysis_data:
            match_entries = []
            for entry in skills_analysis_data['analyze_match_entries']:
                if isinstance(entry, dict) and 'content' in entry:
                    match_entries.append({
                        'content': entry['content']
                    })
            recommendation_data['analyze_match_entries'] = match_entries
        
        # Extract preextracted comparison entries (remove timestamps)
        if 'preextracted_comparison_entries' in skills_analysis_data:
            comparison_entries = []
            for entry in skills_analysis_data['preextracted_comparison_entries']:
                if isinstance(entry, dict) and 'content' in entry:
                    comparison_entries.append({
                        'content': entry['content']
                    })
            recommendation_data['preextracted_comparison_entries'] = comparison_entries
        
        # Extract component analysis entries (remove timestamps)
        if 'component_analysis_entries' in skills_analysis_data:
            component_entries = []
            for entry in skills_analysis_data['component_analysis_entries']:
                if isinstance(entry, dict):
                    # Remove timestamp and keep the rest
                    component_entry = {k: v for k, v in entry.items() if k != 'timestamp'}
                    component_entries.append(component_entry)
            recommendation_data['component_analysis_entries'] = component_entries
        
        # Extract ATS calculation entries (remove timestamps)
        if 'ats_calculation_entries' in skills_analysis_data:
            ats_entries = []
            for entry in skills_analysis_data['ats_calculation_entries']:
                if isinstance(entry, dict):
                    # Remove timestamp and keep the rest
                    ats_entry = {k: v for k, v in entry.items() if k != 'timestamp'}
                    ats_entries.append(ats_entry)
            recommendation_data['ats_calculation_entries'] = ats_entries
        
        return recommendation_data
    
    def generate_from_existing_analysis(self, company_name: str) -> Optional[str]:
        """
        Generate recommendation input from existing skills analysis file
        
        Args:
            company_name: Name of the company
            
        Returns:
            Path to the generated recommendation input file, or None if failed
        """
        try:
            # Find the skills analysis file
            company_dir = self.base_analysis_dir / company_name
            skills_analysis_file = company_dir / f"{company_name}_skills_analysis.json"
            
            if not skills_analysis_file.exists():
                logger.warning(f"⚠️ [RECOMMENDATION_INPUT] Skills analysis file not found: {skills_analysis_file}")
                return None
            
            # Load the skills analysis data
            with open(skills_analysis_file, 'r', encoding='utf-8') as f:
                skills_analysis_data = json.load(f)
            
            # Generate recommendation input
            return self.generate_recommendation_input(company_name, skills_analysis_data)
            
        except Exception as e:
            logger.error(f"❌ [RECOMMENDATION_INPUT] Failed to generate from existing analysis for {company_name}: {e}")
            return None


# Global instance for easy access
recommendation_input_generator = RecommendationInputGenerator()


def generate_recommendation_input_after_ats(company_name: str, skills_analysis_data: Dict[str, Any]) -> Optional[str]:
    """
    Convenience function to generate recommendation input after ATS calculation
    
    Args:
        company_name: Name of the company
        skills_analysis_data: Complete skills analysis data
        
    Returns:
        Path to the generated recommendation input file, or None if failed
    """
    return recommendation_input_generator.generate_recommendation_input(company_name, skills_analysis_data)


def generate_recommendation_input_from_file(company_name: str) -> Optional[str]:
    """
    Convenience function to generate recommendation input from existing analysis file
    
    Args:
        company_name: Name of the company
        
    Returns:
        Path to the generated recommendation input file, or None if failed
    """
    return recommendation_input_generator.generate_from_existing_analysis(company_name)
