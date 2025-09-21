"""
Modular ATS Orchestrator

Orchestrates the modular ATS component analysis system.
This is the main entry point for the new modular approach.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from app.services.ats.component_assembler import ComponentAssembler

logger = logging.getLogger(__name__)


class ModularATSOrchestrator:
    """Main orchestrator for modular ATS component analysis."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir: Path = base_dir or Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        self.assembler = ComponentAssembler(base_dir)

    async def run_component_analysis(self, company: str) -> Dict[str, Any]:
        """
        Run complete modular component analysis for a company.
        
        This is the main entry point that:
        1. Runs all 5 component analyses in parallel
        2. Assembles the results
        3. Saves to {company}_skills_analysis.json
        4. Returns structured results
        
        Args:
            company: Company name for analysis
            
        Returns:
            Dict containing complete analysis results
        """
        logger.info("===== [MODULAR ATS] Starting component analysis for: %s =====", company)
        
        try:
            # Use the assembler to run all components and assemble results
            result = await self.assembler.assemble_analysis(company)
            
            logger.info("===== [MODULAR ATS] Component analysis completed for: %s =====", company)
            return result
            
        except Exception as e:
            logger.error("[MODULAR ATS] Component analysis failed for %s: %s", company, str(e))
            raise

    def get_analysis_summary(self, company: str) -> Dict[str, Any]:
        """
        Get a summary of the latest component analysis for a company.
        
        Args:
            company: Company name
            
        Returns:
            Dict containing analysis summary
        """
        # Use timestamped analysis file with fallback
        from app.utils.timestamp_utils import TimestampUtils
        company_dir = self.base_dir / company
        file_path = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
        if not file_path:
            file_path = company_dir / f"{company}_skills_analysis.json"
        
        if not file_path.exists():
            return {"error": "No analysis found", "company": company}
        
        try:
            import json
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Get the latest component analysis entry
            entries = data.get("component_analysis_entries", [])
            if not entries:
                return {"error": "No component analysis entries found", "company": company}
            
            latest_entry = entries[-1]
            
            return {
                "company": company,
                "timestamp": latest_entry.get("timestamp"),
                "scores": latest_entry.get("extracted_scores", {}),
                "status": "success"
            }
            
        except Exception as e:
            logger.error("[MODULAR ATS] Failed to get summary for %s: %s", company, str(e))
            return {"error": str(e), "company": company}


# Global instance
modular_ats_orchestrator = ModularATSOrchestrator()
