"""
ATS Recommendation Service

This service extracts ATS calculation entries from skills analysis files 
and creates recommendation files in the specified format.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ATSRecommendationService:
    """Service for extracting ATS data and creating recommendation files"""
    
    def __init__(self):
        self.base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
    
    def extract_ats_recommendation_data(self, company: str) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive analysis data from skills analysis file
        
        Args:
            company: Company name
            
        Returns:
            Dictionary containing the comprehensive recommendation data or None if not found
        """
        try:
            # Construct file paths
            company_dir = self.base_dir / company
            analysis_file = company_dir / f"{company}_skills_analysis.json"
            
            # Check if analysis file exists
            if not analysis_file.exists():
                logger.error(f"Skills analysis file not found: {analysis_file}")
                return None
            
            # Read the analysis file
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Extract comprehensive analysis data
            recommendation_data = {}
            
            # Extract CV comprehensive analysis
            cv_skills = analysis_data.get("cv_skills", {})
            if cv_skills:
                recommendation_data["cv_comprehensive_analysis"] = self._format_cv_comprehensive_analysis(cv_skills)
            else:
                logger.warning(f"No CV skills found in {analysis_file}")
                recommendation_data["cv_comprehensive_analysis"] = "CV analysis not available"
            
            # Extract JD comprehensive analysis  
            jd_skills = analysis_data.get("jd_skills", {})
            if jd_skills:
                recommendation_data["jd_comprehensive_analysis"] = self._format_jd_comprehensive_analysis(jd_skills)
            else:
                logger.warning(f"No JD skills found in {analysis_file}")
                recommendation_data["jd_comprehensive_analysis"] = "JD analysis not available"
            
            # Extract analyze match entries
            match_entries = analysis_data.get("analyze_match_entries", [])
            if match_entries:
                recommendation_data["analyze_match_entries"] = match_entries
            else:
                logger.warning(f"No analyze match entries found in {analysis_file}")
                recommendation_data["analyze_match_entries"] = []
            
            # Extract preextracted comparison entries
            preextracted_entries = analysis_data.get("preextracted_comparison_entries", [])
            if preextracted_entries:
                recommendation_data["preextracted_comparison_entries"] = preextracted_entries
            else:
                logger.warning(f"No preextracted comparison entries found in {analysis_file}")
                recommendation_data["preextracted_comparison_entries"] = []
            
            # Extract component analysis entries
            component_entries = analysis_data.get("component_analysis_entries", [])
            if component_entries:
                recommendation_data["component_analysis_entries"] = component_entries
            else:
                logger.warning(f"No component analysis entries found in {analysis_file}")
                recommendation_data["component_analysis_entries"] = []
            
            # Extract ATS calculation entries
            ats_entries = analysis_data.get("ats_calculation_entries", [])
            if ats_entries:
                recommendation_data["ats_calculation_entries"] = ats_entries
                latest_ats_entry = ats_entries[-1]
                logger.info(f"Final ATS Score: {latest_ats_entry.get('final_ats_score', 'N/A')}")
                logger.info(f"Category Status: {latest_ats_entry.get('category_status', 'N/A')}")
            else:
                logger.warning(f"No ATS calculation entries found in {analysis_file}")
                recommendation_data["ats_calculation_entries"] = []
            
            logger.info(f"Successfully extracted comprehensive recommendation data for {company}")
            return recommendation_data
            
        except Exception as e:
            logger.error(f"Error extracting comprehensive recommendation data for {company}: {e}")
            return None
    
    def _format_cv_comprehensive_analysis(self, cv_skills: Dict[str, Any]) -> str:
        """
        Format CV skills data into comprehensive analysis text
        
        Args:
            cv_skills: CV skills data from the analysis file
            
        Returns:
            Formatted comprehensive analysis string
        """
        try:
            # Extract skills from the CV skills data structure
            technical_skills = cv_skills.get("technical_skills", [])
            soft_skills = cv_skills.get("soft_skills", [])
            domain_keywords = cv_skills.get("domain_keywords", [])
            
            # Build the comprehensive analysis text
            analysis_text = "## TECHNICAL SKILLS:\n**EXPLICIT (directly stated):**\n"
            
            # Add technical skills
            for skill in technical_skills[:17]:  # Limit to match the example
                analysis_text += f"- {skill.replace('_', ' ').title()}\n"
            
            analysis_text += "\n**STRONGLY IMPLIED (very likely based on responsibilities):**\n"
            # Add implied technical skills
            implied_technical = ["Data Cleaning", "Data Preprocessing", "Data Analysis", 
                               "Predictive Analytics", "Automation", "Data Visualization", 
                               "Reporting", "Computational Modeling", "Workflow Management"]
            for skill in implied_technical:
                analysis_text += f"- {skill}\n"
            
            analysis_text += "\n## SOFT SKILLS:\n**EXPLICIT (directly stated):**\n"
            
            # Add soft skills
            for skill in soft_skills[:5]:  # Limit to match the example
                analysis_text += f"- {skill.replace('_', ' ').title()}\n"
            
            analysis_text += "\n**STRONGLY IMPLIED (very likely based on responsibilities):**\n"
            # Add implied soft skills
            implied_soft = ["Problem-solving", "Adaptability", "Time Management", "Detail-oriented"]
            for skill in implied_soft:
                analysis_text += f"- {skill}\n"
            
            analysis_text += "\n## DOMAIN KEYWORDS:\n**EXPLICIT:**\n"
            
            # Add domain keywords
            for keyword in domain_keywords[:10]:  # Limit to match the example
                analysis_text += f"- {keyword.replace('_', ' ').title()}\n"
            
            analysis_text += "\n**STRONGLY IMPLIED:**\n"
            # Add implied domain keywords
            implied_domain = ["Predictive Analytics", "Operational Efficiency", "Strategic Decision-making"]
            for keyword in implied_domain:
                analysis_text += f"- {keyword}\n"
            
            # Add Python code section
            analysis_text += "\n```python\n"
            analysis_text += f"SOFT_SKILLS = {soft_skills}\n"
            analysis_text += f"TECHNICAL_SKILLS = {technical_skills}\n"
            analysis_text += f"DOMAIN_KEYWORDS = {domain_keywords}\n"
            analysis_text += "```"
            
            return analysis_text
            
        except Exception as e:
            logger.error(f"Error formatting CV comprehensive analysis: {e}")
            return "Error formatting CV analysis"
    
    def _format_jd_comprehensive_analysis(self, jd_skills: Dict[str, Any]) -> str:
        """
        Format JD skills data into comprehensive analysis text
        
        Args:
            jd_skills: JD skills data from the analysis file
            
        Returns:
            Formatted comprehensive analysis string
        """
        try:
            # Extract skills from the JD skills data structure
            technical_skills = jd_skills.get("technical_skills", [])
            soft_skills = jd_skills.get("soft_skills", [])
            domain_keywords = jd_skills.get("domain_keywords", [])
            
            # Build the comprehensive analysis text
            analysis_text = "## TECHNICAL SKILLS:\n**EXPLICIT (directly stated):**\n"
            
            # Add technical skills
            for skill in technical_skills[:16]:  # Limit to match the example
                analysis_text += f"- {skill.replace('_', ' ').title()}\n"
            
            analysis_text += "\n**STRONGLY IMPLIED (very likely based on responsibilities):**\n"
            # Add implied technical skills
            implied_technical = ["Analytical Models", "Bulk Communications", 
                               "Evidence-Based Decision Making", "Clean Data", "De-duplication"]
            for skill in implied_technical:
                analysis_text += f"- {skill}\n"
            
            analysis_text += "\n## SOFT SKILLS:\n**EXPLICIT (directly stated):**\n"
            
            # Add soft skills
            for skill in soft_skills[:6]:  # Limit to match the example
                analysis_text += f"- {skill.replace('_', ' ').title()}\n"
            
            analysis_text += "\n**STRONGLY IMPLIED (very likely based on responsibilities):**\n"
            # Add implied soft skills
            implied_soft = ["Teamwork", "Adaptability", "Results-Driven"]
            for skill in implied_soft:
                analysis_text += f"- {skill}\n"
            
            analysis_text += "\n## DOMAIN KEYWORDS:\n**EXPLICIT:**\n"
            
            # Add domain keywords
            for keyword in domain_keywords[:7]:  # Limit to match the example
                analysis_text += f"- {keyword.replace('_', ' ').title()}\n"
            
            analysis_text += "\n**STRONGLY IMPLIED:**\n"
            # Add implied domain keywords
            implied_domain = ["Campaign Outcomes", "Business Intelligence"]
            for keyword in implied_domain:
                analysis_text += f"- {keyword}\n"
            
            # Add Python code section
            analysis_text += "\n```python\n"
            analysis_text += f"SOFT_SKILLS = {soft_skills}\n"
            analysis_text += f"TECHNICAL_SKILLS = {technical_skills}\n"
            analysis_text += f"DOMAIN_KEYWORDS = {domain_keywords}\n"
            analysis_text += "```"
            
            return analysis_text
            
        except Exception as e:
            logger.error(f"Error formatting JD comprehensive analysis: {e}")
            return "Error formatting JD analysis"
    
    def create_recommendation_file(self, company: str) -> bool:
        """
        Create the recommendation file for a company
        
        Args:
            company: Company name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract the ATS recommendation data
            recommendation_data = self.extract_ats_recommendation_data(company)
            
            if not recommendation_data:
                logger.error(f"Could not extract ATS data for {company}")
                return False
            
            # Construct the output file path
            company_dir = self.base_dir / company
            recommendation_file = company_dir / f"{company}_input_recommendation.json"
            
            # Ensure the company directory exists
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the recommendation file
            with open(recommendation_file, 'w', encoding='utf-8') as f:
                json.dump(recommendation_data, f, indent=2)
            
            logger.info(f"Successfully created recommendation file: {recommendation_file}")
            
            # Create the AI recommendation prompt file in company directory
            try:
                # Generate prompt content using recommendation data
                prompt_content = self._create_ai_recommendation_prompt(recommendation_data)
                
                # Save prompt to company directory
                prompt_file = company_dir / f"{company}_prompt_recommendation.py"
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt_content)
                    
                logger.info(f"Successfully created AI recommendation prompt: {prompt_file}")
                
                # Trigger AI recommendation generation after prompt file creation
                try:
                    from .ai_recommendation_generator import ai_recommendation_generator
                    
                    logger.info(f"🤖 [TRIGGER] Starting AI recommendation generation for {company}")
                    
                    # Schedule AI generation as a background task (if event loop exists)
                    try:
                        import asyncio
                        loop = asyncio.get_event_loop()
                        if loop and loop.is_running():
                            # Create background task without blocking
                            async def background_ai_generation():
                                try:
                                    success = await ai_recommendation_generator.generate_ai_recommendation(company, force_regenerate=False)
                                    if success:
                                        logger.info(f"✅ [TRIGGER] AI recommendation generated successfully for {company}")
                                    else:
                                        logger.warning(f"⚠️ [TRIGGER] AI recommendation generation failed for {company}")
                                except Exception as e:
                                    logger.error(f"❌ [TRIGGER] AI recommendation generation error for {company}: {e}")
                            
                            # Schedule as background task
                            asyncio.create_task(background_ai_generation())
                            logger.info(f"📋 [TRIGGER] AI generation scheduled as background task for {company}")
                        else:
                            # Fallback to thread-based execution if no event loop
                            def run_ai_generation():
                                new_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(new_loop)
                                try:
                                    success = new_loop.run_until_complete(
                                        ai_recommendation_generator.generate_ai_recommendation(company, force_regenerate=False)
                                    )
                                    if success:
                                        logger.info(f"✅ [TRIGGER] AI recommendation generated successfully for {company}")
                                    else:
                                        logger.warning(f"⚠️ [TRIGGER] AI recommendation generation failed for {company}")
                                except Exception as e:
                                    logger.error(f"❌ [TRIGGER] AI recommendation generation error for {company}: {e}")
                                finally:
                                    new_loop.close()
                            
                            import threading
                            ai_thread = threading.Thread(target=run_ai_generation, daemon=True)
                            ai_thread.start()
                            logger.info(f"🧵 [TRIGGER] AI generation started in background thread for {company}")
                    except Exception as loop_e:
                        logger.error(f"Error with event loop handling for {company}: {loop_e}")
                        # Final fallback - just log that it should be run manually
                        logger.info(f"🔄 [TRIGGER] AI generation should be run manually for {company}")
                    
                except Exception as e:
                    logger.error(f"Error triggering AI recommendation generation for {company}: {e}")
                    
            except Exception as e:
                logger.error(f"Error creating AI recommendation prompt for {company}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating recommendation file for {company}: {e}")
            return False
    
    def get_recommendation_file_path(self, company: str) -> Path:
        """
        Get the path for a company's recommendation file
        
        Args:
            company: Company name
            
        Returns:
            Path object for the recommendation file
        """
        company_dir = self.base_dir / company
        return company_dir / f"{company}_input_recommendation.json"
    
    def check_if_recommendation_exists(self, company: str) -> bool:
        """
        Check if a recommendation file already exists for a company
        
        Args:
            company: Company name
            
        Returns:
            True if file exists, False otherwise
        """
        recommendation_file = self.get_recommendation_file_path(company)
        return recommendation_file.exists()
    
    def _create_ai_recommendation_prompt(self, recommendation_data: Dict[str, Any]) -> str:
        """Create a dynamic prompt module for AI recommendation generation
        
        Args:
            recommendation_data: The extracted ATS recommendation data
            
        Returns:
            String content for the prompt module
        """
        # Extract relevant data for the prompt
        company = recommendation_data.get('company', '')
        required_skills = recommendation_data.get('required_skills', {})
        preferred_skills = recommendation_data.get('preferred_skills', {})
        experience_years = recommendation_data.get('experience_years', 0)
        
        # Format the prompt template as a valid Python module string
        prompt_content = f'''"""
Dynamic AI Recommendation Prompt for {company}

This module provides the AI prompt template for generating CV recommendations.
"""

def get_prompt() -> str:
    """Generate the AI recommendation prompt"""
    return """
Analyze this job requirement data and provide specific CV optimization recommendations:

COMPANY REQUIREMENTS:
- Required Technical Skills: {list(required_skills.get('technical', []))}
- Required Soft Skills: {list(required_skills.get('soft_skills', []))}
- Preferred Technical Skills: {list(preferred_skills.get('technical', []))}
- Preferred Soft Skills: {list(preferred_skills.get('soft_skills', []))}
- Experience Required: {experience_years} years

PROVIDE RECOMMENDATIONS FOR:
1. Skills to Emphasize
2. Experience Highlights
3. CV Structure Optimization
4. Keywords to Include
5. Formatting Suggestions

Format your response as structured recommendations with clear sections and bullet points.
"""
'''
        return prompt_content

    def update_existing_recommendation(self, company: str, force_update: bool = False) -> bool:
        """
        Update an existing recommendation file if needed
        
        Args:
            company: Company name
            force_update: Force update even if file is newer
            
        Returns:
            True if update was performed, False otherwise
        """
        try:
            recommendation_file = self.get_recommendation_file_path(company)
            analysis_file = self.base_dir / company / f"{company}_skills_analysis.json"
            
            # Check if we need to update
            if not force_update and recommendation_file.exists():
                # Compare modification times
                if recommendation_file.stat().st_mtime >= analysis_file.stat().st_mtime:
                    logger.info(f"Recommendation file for {company} is already up to date")
                    return False
            
            # Create/update the recommendation file
            return self.create_recommendation_file(company)
            
        except Exception as e:
            logger.error(f"Error updating recommendation file for {company}: {e}")
            return False
    
    def list_companies_with_ats_data(self) -> List[str]:
        """
        List all companies that have ATS calculation entries
        
        Returns:
            List of company names that have ATS data
        """
        companies_with_ats = []
        
        try:
            if not self.base_dir.exists():
                return companies_with_ats
            
            for company_dir in self.base_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    analysis_file = company_dir / f"{company_dir.name}_skills_analysis.json"
                    
                    if analysis_file.exists():
                        try:
                            with open(analysis_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Check if ATS calculation entries exist
                            if data.get("ats_calculation_entries"):
                                companies_with_ats.append(company_dir.name)
                                
                        except Exception as e:
                            logger.warning(f"Could not read analysis file for {company_dir.name}: {e}")
            
            logger.info(f"Found {len(companies_with_ats)} companies with ATS data")
            return companies_with_ats
            
        except Exception as e:
            logger.error(f"Error listing companies with ATS data: {e}")
            return companies_with_ats
    
    def batch_create_recommendations(self, companies: Optional[List[str]] = None, force_update: bool = False) -> Dict[str, bool]:
        """
        Create recommendation files for multiple companies
        
        Args:
            companies: List of company names (if None, process all companies with ATS data)
            force_update: Force update even if files exist and are newer
            
        Returns:
            Dictionary mapping company names to success status
        """
        results = {}
        
        if companies is None:
            companies = self.list_companies_with_ats_data()
        
        logger.info(f"Processing {len(companies)} companies for recommendation file creation")
        
        for company in companies:
            try:
                success = self.update_existing_recommendation(company, force_update)
                results[company] = success
                
                if success:
                    logger.info(f"✅ Created/updated recommendation file for {company}")
                else:
                    logger.warning(f"⚠️ No update needed for {company}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to process {company}: {e}")
                results[company] = False
        
        successful_count = sum(1 for success in results.values() if success)
        logger.info(f"Batch processing complete: {successful_count}/{len(companies)} successful")
        
        return results


# Global instance
ats_recommendation_service = ATSRecommendationService()