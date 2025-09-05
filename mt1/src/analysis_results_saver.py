"""
Analysis Results Saver - Saves comprehensive CV/JD analysis results to text files
"""
import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
import logging
try:
    from .ai_config import get_model_params
except ImportError:
    # Handle relative import for testing
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from ai_config import get_model_params

logger = logging.getLogger(__name__)

class AnalysisResultsSaver:
    def __init__(self, results_dir: str = "analysis_results", debug: bool = False):
        """Initialize with results directory and debug flag"""
        self.results_dir = results_dir
        self.debug = debug
        os.makedirs(results_dir, exist_ok=True)
    
    def extract_company_name(self, jd_text: str) -> str:
        """Extract company name from JD text using LLM for intelligent extraction"""
        try:
            # Use LLM to extract company information
            import asyncio
            try:
                # Check if we're in an event loop already
                loop = asyncio.get_running_loop()
                # If we are, we need to create a task or use a different approach
                # For now, let's use a synchronous fallback
                company_info = None
                print(f"⚠️ [LLM_EXTRACTION] Running in event loop - using fallback extraction")
            except RuntimeError:
                # Not in an event loop, safe to use asyncio.run
                company_info = asyncio.run(self.extract_company_info_with_llm(jd_text))
            
            if company_info and company_info.get('company_name'):
                company_name = company_info['company_name']
                # Clean up company name for filename
                company_name = re.sub(r'[^\w\s&.-]', '', company_name)
                company_name = re.sub(r'\s+', '_', company_name)
                company_name = company_name.strip('_')
                
                if len(company_name) >= 3:
                    print(f"🏢 [LLM_EXTRACTION] Company Info:")
                    print(f"   Company: {company_info.get('company_name', 'N/A')}")
                    print(f"   Position: {company_info.get('job_position', 'N/A')}")
                    print(f"   Location: {company_info.get('location', 'N/A')}")
                    print(f"   Phone: {company_info.get('phone_number', 'N/A')}")
                    print(f"   Filename: {company_name}_output_log.txt")
                    
                    return company_name
        
        except Exception as e:
            print(f"⚠️ [LLM_EXTRACTION] Error: {e}, falling back to timestamp")
        
        # Fallback to timestamp-based name
        return f"Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def extract_company_info_with_llm(self, jd_text: str) -> dict:
        """Use LLM to extract comprehensive company information from job description"""
        try:
            # Import hybrid AI service
            try:
                from .hybrid_ai_service import hybrid_ai
            except ImportError:
                # Handle relative import for testing
                import sys
                import os
                sys.path.append(os.path.dirname(__file__))
                from hybrid_ai_service import hybrid_ai
            
            # Enhanced prompt for comprehensive company information extraction
            extraction_prompt = f"""
You are an expert at extracting comprehensive information from job descriptions and job postings.

Extract the following information from this job description. Return ONLY a JSON object with these exact keys:

{{
    "company_name": "exact company name",
    "job_title": "job title/position", 
    "location": "job location/city",
    "experience_required": "experience requirements (e.g., 2-3 years, 5+ years)",
    "seniority_level": "entry-level/mid-level/senior/lead/principal",
    "industry": "industry/sector (e.g., technology, healthcare, finance)",
    "phone_number": "phone number if mentioned, otherwise null",
    "email": "email address if mentioned, otherwise null",
    "website": "company website if mentioned, otherwise null",
    "work_type": "remote/hybrid/onsite if mentioned, otherwise null"
}}

**IMPORTANT EXTRACTION RULES:**

1. **Company Name**: Look for these patterns and prioritize them:
   - Company names mentioned after "at", "with", "for", "by" (e.g., "Data Analyst at Microsoft")
   - Company names in headers, titles, or beginning of job posts
   - Well-known company names (avoid generic terms like "Company", "Organization", "Client")
   - Look in contact information, email domains, or website URLs
   - If multiple companies mentioned, choose the hiring company (not client companies)
   - Use the most formal/complete version if company name appears multiple times

2. **Job Title**: Extract the actual job title/role
   - Look for patterns like "Senior Data Analyst", "Software Engineer", "Marketing Manager"
   - Include seniority level if mentioned (Junior, Senior, Lead, Principal, etc.)
   - Avoid generic terms like "position", "role", "opportunity"

3. **Location**: Extract city, state/territory, country
   - Look for patterns like "Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD"
   - Include remote work information if mentioned
   - If multiple locations, choose the primary work location
   - Keep it SHORT and clean: "City, Country" format
   - Do NOT include suburbs, CBD, inner suburbs, metro areas, regional descriptions

4. **Experience Required**: Extract experience requirements
   - Look for patterns like "2-3 years", "5+ years", "minimum 3 years"
   - Include phrases like "entry-level", "mid-level", "senior", "lead"
   - Extract both numeric requirements and seniority indicators

5. **Seniority Level**: Determine the seniority level
   - entry-level: 0-2 years, graduate, junior, entry
   - mid-level: 2-5 years, intermediate, mid
   - senior: 5+ years, senior, lead, principal
   - lead: team lead, technical lead, lead
   - principal: principal, architect, director

6. **Industry**: Extract industry or sector information
   - Look for industry mentions: technology, healthcare, finance, education, etc.
   - Consider company context and job requirements
   - Use specific industry names rather than generic terms

7. **Contact Information**: Extract phone numbers, email addresses, websites
   - Look for phone numbers in various formats
   - Extract email addresses (especially company domains)
   - Extract company websites or application URLs

8. **Work Type**: Extract work arrangement information
   - Remote work options
   - Hybrid work arrangements
   - Onsite requirements

**EXTRACTION GUIDELINES:**
- Be thorough but accurate - don't guess or make up information
- Prefer specific company names over generic terms
- Look throughout the entire job description, not just the beginning
- Consider the context - is this the hiring company or a client mentioned in the role?
- Return null for missing information rather than guessing
- Return ONLY the JSON object, no other text

Job Description:
{jd_text[:3000]}  
"""

            # Get response from LLM (await since it's async)
            response = await hybrid_ai.generate_response(
                extraction_prompt, 
                temperature=0.1, 
                max_tokens=300
            )
            
            # Parse JSON response
            import json
            # Extract JSON from response (in case there's extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                company_info = json.loads(json_str)
                return company_info
            else:
                print(f"⚠️ [LLM_EXTRACTION] Could not parse JSON from response: {response}")
                return self._get_fallback_data()
                
        except Exception as e:
            print(f"❌ [LLM_EXTRACTION] Error extracting company info: {e}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> dict:
        """Return fallback data when extraction fails"""
        return {
            "company_name": "Unknown",
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
    
    def save_analysis_results(self, 
                            cv_text: str,
                            jd_text: str,
                            skill_comparison: Dict,
                            ats_results: Dict,
                            company_name: Optional[str] = None) -> str:
        """
        Save analysis results to company slug_output_log.txt
        
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
                try:
                    company_name = self.extract_company_name(jd_text)
                except Exception as e:
                    logger.warning(f"Failed to extract company name: {e}")
                    company_name = f"Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create company slug
            company_slug = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '_')
            
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
            
            # Debug: Print file content if debug is enabled
            if self.debug:
                self._debug_print_file_content(filepath, report_content)
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save output log: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def save_ui_outputs_to_json(self, 
                               analyze_match_output: Dict = None,
                               skill_comparison_output: Dict = None,
                               ats_test_output: Dict = None,
                               company_name: Optional[str] = None) -> str:
        """
        Save exact UI outputs from each step in JSON format to the same file
        
        Args:
            analyze_match_output: Output from CV-Magic tab analyze match
            skill_comparison_output: Output from ATS tab skill comparison
            ats_test_output: Output from ATS tab test (detailed score breakdown + enhanced requirement bonus)
            company_name: Optional company name override
            
        Returns:
            str: Path to saved file
        """
        try:
            # Extract company name if not provided
            if not company_name:
                # Try to get company name from any available output
                jd_text = ""
                if analyze_match_output:
                    jd_text = analyze_match_output.get('jd_text', '')
                elif skill_comparison_output:
                    jd_text = skill_comparison_output.get('jd_text', '')
                elif ats_test_output:
                    jd_text = ats_test_output.get('jd_text', '')
                
                company_name = self.extract_company_name(jd_text) if jd_text else "Company"
            
            # Create company slug
            company_slug = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '_')
            
            # Create company subdirectory
            company_dir = os.path.join(self.results_dir, company_slug)
            os.makedirs(company_dir, exist_ok=True)
            
            # Create filename: company_slug_output_log.txt (same as analysis results)
            filename = f"{company_slug}_output_log.txt"
            filepath = os.path.join(company_dir, filename)
            
            # Load existing data if file exists
            existing_data = {}
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract JSON from the end of the file
                        json_start = content.rfind('{')
                        if json_start != -1:
                            json_content = content[json_start:]
                            existing_data = json.loads(json_content)
                except Exception as e:
                    logger.warning(f"Could not load existing data: {e}")
                    existing_data = {}
            
            # Initialize data structure if empty
            if not existing_data:
                existing_data = {
                    "analysis_metadata": {
                        "company_name": company_name,
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "analysis_type": "exact_ui_outputs"
                    },
                    "cv_magic_analyze_match": None,
                    "ats_skill_comparison": None,
                    "ats_test_results": None
                }
            
            # Update with new data
            if analyze_match_output:
                existing_data["cv_magic_analyze_match"] = analyze_match_output
                existing_data["analysis_metadata"]["last_updated"] = datetime.now().isoformat()
            
            if skill_comparison_output:
                existing_data["ats_skill_comparison"] = skill_comparison_output
                existing_data["analysis_metadata"]["last_updated"] = datetime.now().isoformat()
            
            if ats_test_output:
                existing_data["ats_test_results"] = ats_test_output
                existing_data["analysis_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save as formatted text file with JSON content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("EXACT UI OUTPUTS ANALYSIS REPORT\n")
                f.write(f"Company: {company_name}\n")
                f.write(f"Created: {existing_data['analysis_metadata']['created_at']}\n")
                f.write(f"Last Updated: {existing_data['analysis_metadata']['last_updated']}\n")
                f.write("=" * 80 + "\n\n")
                
                # 1. CV-Magic Analyze Match Output
                if existing_data.get("cv_magic_analyze_match"):
                    f.write("📊 1. CV-MAGIC ANALYZE MATCH OUTPUT\n")
                    f.write("-" * 50 + "\n")
                    f.write("Raw Analysis:\n")
                    f.write(existing_data["cv_magic_analyze_match"].get('raw_analysis', 'No analysis available') + "\n\n")
                    f.write("Formatted Result:\n")
                    f.write(json.dumps(existing_data["cv_magic_analyze_match"].get('formatted_result', {}), indent=2) + "\n\n")
                
                # 2. ATS Skill Comparison Output
                if existing_data.get("ats_skill_comparison"):
                    f.write("📊 2. ATS SKILL COMPARISON OUTPUT\n")
                    f.write("-" * 50 + "\n")
                    f.write("Detailed Analysis:\n")
                    f.write(json.dumps(existing_data["ats_skill_comparison"], indent=2) + "\n\n")
                
                # 3. ATS Test Results (Detailed Score Breakdown + Enhanced Requirement Bonus)
                if existing_data.get("ats_test_results"):
                    f.write("📊 3. ATS TEST RESULTS\n")
                    f.write("-" * 50 + "\n")
                    f.write("Detailed Score Breakdown:\n")
                    f.write(json.dumps(existing_data["ats_test_results"].get('detailed_score_breakdown', {}), indent=2) + "\n\n")
                    f.write("Enhanced Requirement Bonus:\n")
                    f.write(json.dumps(existing_data["ats_test_results"].get('enhanced_requirement_bonus', {}), indent=2) + "\n\n")
                
                # 4. Complete JSON Output
                f.write("📊 4. COMPLETE JSON OUTPUT\n")
                f.write("-" * 50 + "\n")
                f.write(json.dumps(existing_data, indent=2) + "\n")
            
            logger.info(f"✅ UI outputs saved to: {filepath}")
            
            # Debug: Print file content if debug is enabled
            if self.debug:
                self._debug_print_file_content(filepath, "UI outputs saved successfully")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save UI outputs: {e}")
            raise

    def auto_save_analyze_match(self, analyze_match_output: Dict, company_name: Optional[str] = None) -> str:
        """
        Automatically save analyze match output when displayed in Flutter UI
        """
        return self.save_ui_outputs_to_json(
            analyze_match_output=analyze_match_output,
            company_name=company_name
        )

    def auto_save_skill_comparison(self, skill_comparison_output: Dict, company_name: Optional[str] = None) -> str:
        """
        Automatically save skill comparison output when displayed in Flutter UI
        """
        return self.save_ui_outputs_to_json(
            skill_comparison_output=skill_comparison_output,
            company_name=company_name
        )

    def auto_save_ats_test(self, ats_test_output: Dict, company_name: Optional[str] = None) -> str:
        """
        Automatically save ATS test output when displayed in Flutter UI
        """
        return self.save_ui_outputs_to_json(
            ats_test_output=ats_test_output,
            company_name=company_name
        )
    
    def generate_llm_recommendations(self, analysis_filepath: str, api_key: str) -> Dict[str, Any]:
        """
        Generate LLM-based recommendations from saved analysis file
        
        Args:
            analysis_filepath: Path to the saved analysis file
            api_key: Anthropic API key for LLM access
            
        Returns:
            Dict containing LLM recommendations
        """
        try:
            # Read the analysis file
            with open(analysis_filepath, 'r', encoding='utf-8') as f:
                analysis_content = f.read()
            
            # Initialize LLM client
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Create comprehensive prompt for LLM recommendations
            prompt = self._create_recommendation_prompt(analysis_content)
            
            # Get LLM recommendations
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse LLM response
            recommendations = self._parse_llm_recommendations(response.content[0].text)
            
            if self.debug:
                self._debug_print_recommendations(recommendations, analysis_filepath)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate LLM recommendations: {e}")
            return {
                "error": f"Failed to generate recommendations: {str(e)}",
                "recommendations": [],
                "priority_actions": [],
                "skill_gaps": [],
                "strengths": []
            }
    
    def _create_recommendation_prompt(self, analysis_content: str) -> str:
        """Create comprehensive prompt for CV tailoring recommendations based on analysis"""
        # Import the centralized prompt module
        try:
            from .ai_recommendations import get_ai_recommendations_prompt
            return get_ai_recommendations_prompt(analysis_content)
        except ImportError:
            # Fallback if the prompts module is not available
            return f"""# CV Tailoring Recommendation Generator Prompt

## SYSTEM PROMPT

You are an expert CV tailoring consultant. Analyze the provided comprehensive analysis data and generate actionable CV tailoring recommendations. Base your analysis SOLELY on the information provided in the analysis data.

## COMPREHENSIVE ANALYSIS DATA:
{analysis_content}

## ANALYSIS FRAMEWORK

### 1. EXTRACT KEY DATA POINTS
From the provided analysis data, identify and extract:
- Overall match percentage and hiring probability
- Market reality insights and flexibility indicators  
- Matched vs missing skills breakdown
- Strategic positioning opportunities
- Industry-specific requirements
- ATS score breakdown and critical gaps
- Essential vs preferred skills analysis

### 2. GENERATE STRATEGIC POSITIONING
Based on the analysis findings, provide:
- **Primary positioning strategy** (how to frame the candidate's background)
- **Key reframing opportunities** (academic → business, technical → commercial)
- **Mission alignment approach** (if relevant to the role/sector)
- **Competitive advantages** to emphasize

### 3. PROVIDE SPECIFIC RECOMMENDATIONS

#### Technical Skills Enhancement
- Prioritize skills that are matched and emphasize them prominently
- Address missing technical skills through:
  - Reframing existing experience
  - Identifying transferable capabilities
  - Strategic omissions (don't invent skills)

#### Soft Skills Repositioning
- Leverage matched soft skills with specific examples
- Bridge missing soft skills through related experience
- Strengthen communication and leadership narratives

#### Achievement Reframing
- Transform existing achievements to align with job requirements
- Quantify impact using business-relevant metrics
- Connect technical accomplishments to business outcomes

### 4. KEYWORD INTEGRATION STRATEGY
Based on the matched and missing domain keywords from the analysis:
- **Emphasize matched keywords** prominently throughout the CV
- **Strategically incorporate** relevant terms where authentic experience exists
- **Avoid forcing missing keywords** - don't fabricate experience around unmatched terms
- **Use semantic alternatives** for missing keywords where applicable

### 5. ATS OPTIMIZATION STRATEGY
Based on the ATS score breakdown:
- Address lowest-scoring components first
- Focus on essential skills gaps that impact scoring
- Optimize for requirement bonus opportunities
- Strategic positioning for maximum ATS score improvement

## OUTPUT FORMAT

Structure the recommendations as:

```markdown
# CV Tailoring Strategy for [Role Type] Position

## 🎯 STRATEGIC POSITIONING
[Core positioning strategy based on analysis]

## 📊 MATCH ANALYSIS SUMMARY
[Key statistics and insights from the provided analysis]

## 🔧 TECHNICAL SKILLS STRATEGY
[Specific recommendations for technical skills presentation]

## 🎪 SOFT SKILLS ENHANCEMENT
[Soft skills repositioning and strengthening]

## 📈 ACHIEVEMENT TRANSFORMATION
[How to reframe existing achievements]

## 🏢 SECTOR-SPECIFIC ADAPTATIONS
[Industry/sector-specific recommendations]

## 🔑 KEYWORD INTEGRATION STRATEGY
[How to authentically incorporate matched keywords and avoid forcing missing ones]

## 📋 ATS SCORE OPTIMIZATION
[Specific actions to improve ATS scoring based on the analysis]

## ⚠️ STRATEGIC WARNINGS
### Don't Oversell Missing Skills
- Identify specific missing skills from the analysis and warn against fabricating experience
- List concrete examples of skills/experience NOT to claim based on the gaps identified

### Don't Undersell Your Strengths  
- Identify the candidate's strongest assets from the matched skills analysis
- Emphasize leveraging distinctive strengths that differentiate from typical candidates

## 🎯 SUCCESS PROBABILITY
[Overall assessment and final positioning statement]
```

## IMPORTANT CONSTRAINTS

1. **Work ONLY with provided analysis data** - Do not add external assumptions
2. **Extract specific percentages and insights** from the analysis
3. **Use actual skills and keywords** mentioned in the analysis
4. **Reference specific ATS scores and breakdowns** provided
5. **Base recommendations on actual gaps** identified in the analysis
6. **Use sector-specific insights** if mentioned in the analysis data

Generate tailored, actionable recommendations that will maximize the candidate's chances of securing an interview based solely on this comprehensive analysis data.
"""
    
    def _parse_llm_recommendations(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured recommendations"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                return recommendations
            else:
                # Fallback parsing
                return self._fallback_parse_recommendations(llm_response)
        except Exception as e:
            logger.error(f"Failed to parse LLM recommendations: {e}")
            return self._fallback_parse_recommendations(llm_response)
    
    def _fallback_parse_recommendations(self, llm_response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        return {
            "ats_score_summary": {
                "current_score": "Unknown",
                "score_category": "Unknown",
                "overall_performance": "Unknown"
            },
            "score_breakdown": {
                "technical_skills": {
                    "score": "Unknown",
                    "status": "Unknown",
                    "impact": "Unknown"
                },
                "soft_skills": {
                    "score": "Unknown",
                    "status": "Unknown",
                    "impact": "Unknown"
                },
                "domain_keywords": {
                    "score": "Unknown",
                    "status": "Unknown",
                    "impact": "Unknown"
                }
            },
            "critical_requirements": {
                "essential_met": "Unknown",
                "preferred_met": "Unknown",
                "missing_critical": [],
                "key_strengths": []
            },
            "raw_response": llm_response[:500] + "..." if len(llm_response) > 500 else llm_response
        }
    
    def _debug_print_recommendations(self, recommendations: Dict, analysis_filepath: str):
        """Debug function to print LLM recommendations"""
        print("\n" + "="*80)
        print(f"🧠 DEBUG: LLM Recommendations Generated")
        print(f"📁 Analysis File: {analysis_filepath}")
        print("="*80)
        print(json.dumps(recommendations, indent=2))
        print("="*80 + "\n")
    
    def _debug_print_file_content(self, filepath: str, content: str):
        """Debug function to print file content"""
        print("\n" + "="*80)
        print(f"🔍 DEBUG: Analysis Results File Content")
        print(f"📁 File: {filepath}")
        print("="*80)
        print(content)
        print("="*80)
        print(f"📊 File Statistics:")
        print(f"   • Total lines: {len(content.splitlines())}")
        print(f"   • Total characters: {len(content)}")
        print(f"   • File size: {os.path.getsize(filepath)} bytes")
        print("="*80 + "\n")
    
    def _generate_comprehensive_report(self, 
                                    cv_text: str,
                                    jd_text: str,
                                    skill_comparison: Dict,
                                    ats_results: Dict,
                                    company_name: str) -> str:
        """Generate comprehensive analysis report"""
        
        report = []
        report.append("=" * 80)
        report.append(f"COMPREHENSIVE CV/JD ANALYSIS REPORT")
        report.append(f"Company: {company_name}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # 1. SKILL COMPARISON ANALYSIS
        report.append("📊 1. SKILL COMPARISON ANALYSIS")
        report.append("-" * 50)
        report.extend(self._format_skill_comparison(skill_comparison))
        report.append("")
        
        # 2. ATS SCORE COMPONENTS
        report.append("🎯 2. ENHANCED ATS SCORE COMPONENTS")
        report.append("-" * 50)
        report.extend(self._format_ats_components(ats_results))
        report.append("")
        
        # 3. REQUIREMENT BONUS ANALYSIS
        report.append("🎁 3. REQUIREMENT BONUS ANALYSIS")
        report.append("-" * 50)
        report.extend(self._format_requirement_bonus(ats_results))
        report.append("")
        
        # 4. LLM ANALYSIS
        report.append("🧠 4. LLM-BASED ANALYSIS")
        report.append("-" * 50)
        report.extend(self._format_llm_analysis(ats_results))
        report.append("")
        
        # 5. OPTIMIZATION RECOMMENDATIONS
        report.append("💡 5. OPTIMIZATION RECOMMENDATIONS")
        report.append("-" * 50)
        report.extend(self._format_recommendations(ats_results))
        report.append("")
        
        # 6. SUMMARY
        report.append("📋 6. EXECUTIVE SUMMARY")
        report.append("-" * 50)
        report.extend(self._format_summary(ats_results, skill_comparison))
        report.append("")
        
        return "\n".join(report)
    
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
    
    def _format_skill_comparison(self, skill_comparison: Dict) -> list:
        """Format skill comparison results"""
        lines = []
        
        if not skill_comparison:
            lines.append("No skill comparison data available")
            return lines
        
        try:
            # Overall match summary
            match_summary = skill_comparison.get('match_summary', {})
            total_matches = match_summary.get('total_matches', 0)
            total_requirements = match_summary.get('total_jd_requirements', 0)
            match_percentage = match_summary.get('match_percentage', 0)
            
            lines.append(f"Overall Match: {match_percentage}% ({total_matches}/{total_requirements} requirements)")
            lines.append("")
            
            # Category breakdown
            categories = ['technical_skills', 'soft_skills', 'domain_keywords']
            category_names = ['Technical Skills', 'Soft Skills', 'Domain Keywords']
            
            for i, category in enumerate(categories):
                lines.append(f"📌 {category_names[i]}:")
                
                # Matched skills
                matched = skill_comparison.get('matched', {}).get(category, [])
                if matched:
                    lines.append("  ✅ Matched Skills:")
                    for match in matched[:10]:  # Limit to first 10
                        if isinstance(match, dict):
                            jd_skill = match.get('jd_requirement', 'Unknown')
                            cv_skill = match.get('cv_equivalent', 'Unknown')
                            lines.append(f"    • {jd_skill} ← {cv_skill}")
                        else:
                            lines.append(f"    • {match}")
                    if len(matched) > 10:
                        lines.append(f"    ... and {len(matched) - 10} more")
                
                # Missing skills
                missing = skill_comparison.get('missing', {}).get(category, [])
                if missing:
                    lines.append("  ❌ Missing Skills:")
                    for skill in missing[:10]:  # Limit to first 10
                        lines.append(f"    • {skill}")
                    if len(missing) > 10:
                        lines.append(f"    ... and {len(missing) - 10} more")
                
                lines.append("")
        except Exception as e:
            lines.append(f"Error formatting skill comparison: {str(e)}")
            lines.append("Raw data: " + str(skill_comparison)[:200] + "...")
        
        return lines
    
    def _format_ats_components(self, ats_results: Dict) -> list:
        """Format ATS score components"""
        lines = []
        
        if not ats_results:
            lines.append("No ATS results data available")
            return lines
        
        try:
            # Overall score
            overall_score = ats_results.get('overall_ats_score', 0)
            score_category = ats_results.get('score_category', 'Unknown')
            lines.append(f"Overall ATS Score: {overall_score}/100 ({score_category})")
            lines.append("")
            
            # Detailed breakdown
            detailed_breakdown = ats_results.get('detailed_breakdown', {})
            
            if not detailed_breakdown:
                lines.append("No detailed breakdown available")
                return lines
            
            components = [
                ('technical_skills_match', 'Technical Skills Match'),
                ('soft_skills_match', 'Soft Skills Match'),
                ('domain_keywords_match', 'Domain Keywords Match'),
                ('skills_relevance', 'Skills Relevance'),
                ('experience_alignment', 'Experience Alignment'),
                ('industry_fit', 'Industry Fit'),
                ('role_seniority', 'Role Seniority'),
                ('technical_depth', 'Technical Depth')
            ]
            
            lines.append("Component Breakdown:")
            for component_key, component_name in components:
                component_data = detailed_breakdown.get(component_key, {})
                if component_data:
                    score = component_data.get('score', 0)
                    weight = component_data.get('weight', 0)
                    contribution = component_data.get('contribution', 0)
                    
                    lines.append(f"  • {component_name}: {score}/100 (Weight: {weight}% → Contribution: {contribution:.1f})")
                else:
                    lines.append(f"  • {component_name}: No data available")
        except Exception as e:
            lines.append(f"Error formatting ATS components: {str(e)}")
            lines.append("Raw data: " + str(ats_results)[:200] + "...")
        
        return lines
    
    def _format_requirement_bonus(self, ats_results: Dict) -> list:
        """Format requirement bonus analysis"""
        lines = []
        
        detailed_breakdown = ats_results.get('detailed_breakdown', {})
        requirement_bonus = detailed_breakdown.get('requirement_bonus', {})
        
        if not requirement_bonus:
            lines.append("No requirement bonus data available")
            return lines
        
        # Get critical and preferred requirements from the actual data structure
        critical_requirements = requirement_bonus.get('critical_requirements', [])
        preferred_requirements = requirement_bonus.get('preferred_requirements', [])
        
        # Calculate matches and missing
        critical_matches = [req for req in critical_requirements if req.get('matched', False)]
        critical_missing = [req for req in critical_requirements if not req.get('matched', False)]
        preferred_matches = [req for req in preferred_requirements if req.get('matched', False)]
        preferred_missing = [req for req in preferred_requirements if not req.get('matched', False)]
        
        # Get bonus points from the actual structure
        critical_points = requirement_bonus.get('critical_points', 0)
        preferred_points = requirement_bonus.get('preferred_points', 0)
        total_bonus_points = requirement_bonus.get('total_bonus_points', 0)
        
        lines.append("🎯 Critical Requirements:")
        lines.append(f"  Found: {len(critical_matches)} skills")
        lines.append(f"  Missing: {len(critical_missing)} skills")
        lines.append(f"  Bonus Points: {critical_points}")
        
        if critical_matches:
            lines.append("  ✅ Matched Critical Skills:")
            for match in critical_matches[:5]:
                requirement = match.get('requirement', 'Unknown')
                jd_proof = match.get('jd_proof_text', 'No proof text')
                lines.append(f"    • {requirement}")
                lines.append(f"      Proof: {jd_proof[:100]}...")
        
        if critical_missing:
            lines.append("  ❌ Missing Critical Skills:")
            for missing in critical_missing[:5]:
                requirement = missing.get('requirement', 'Unknown')
                lines.append(f"    • {requirement}")
        
        lines.append("")
        
        # Preferred requirements
        lines.append("⭐ Preferred Requirements:")
        lines.append(f"  Found: {len(preferred_matches)} skills")
        lines.append(f"  Missing: {len(preferred_missing)} skills")
        lines.append(f"  Bonus Points: {preferred_points}")
        
        if preferred_matches:
            lines.append("  ✅ Matched Preferred Skills:")
            for match in preferred_matches[:5]:
                requirement = match.get('requirement', 'Unknown')
                lines.append(f"    • {requirement}")
        
        lines.append("")
        lines.append(f"Total Requirement Bonus: {total_bonus_points} points")
        
        return lines
    
    def _format_llm_analysis(self, ats_results: Dict) -> list:
        """Format LLM-based analysis"""
        lines = []
        
        detailed_analysis = ats_results.get('detailed_analysis', {})
        
        # Skills relevance analysis
        skills_relevance = detailed_analysis.get('skills_relevance', {})
        if skills_relevance:
            lines.append("🛠️ Skills Relevance Analysis:")
            overall_score = skills_relevance.get('overall_skills_score', 0)
            lines.append(f"  Overall Relevance Score: {overall_score}/100")
            
            skills_analysis = skills_relevance.get('skills_analysis', [])
            if skills_analysis:
                lines.append("  Top Skills Analysis:")
                for skill_data in skills_analysis[:3]:
                    skill = skill_data.get('skill', 'Unknown')
                    relevance = skill_data.get('relevance_score', 0)
                    level = skill_data.get('skill_level', 'Unknown')
                    lines.append(f"    • {skill}: {relevance}/100 ({level})")
        
        lines.append("")
        
        # Experience alignment
        experience_alignment = detailed_analysis.get('experience_alignment', {})
        if experience_alignment:
            experience_analysis = experience_alignment.get('experience_analysis', {})
            lines.append("👤 Experience Alignment:")
            alignment_score = experience_analysis.get('alignment_score', 0)
            cv_years = experience_analysis.get('cv_experience_years', 0)
            cv_level = experience_analysis.get('cv_role_level', 'Unknown')
            jd_years = experience_analysis.get('jd_required_years', 'Unknown')
            jd_level = experience_analysis.get('jd_role_level', 'Unknown')
            
            lines.append(f"  Alignment Score: {alignment_score}/100")
            lines.append(f"  CV Experience: {cv_years} years ({cv_level})")
            lines.append(f"  JD Requirements: {jd_years} years ({jd_level})")
        
        lines.append("")
        
        # Missing skills impact
        missing_skills = detailed_analysis.get('missing_skills_impact', {})
        if missing_skills:
            lines.append("⚠️ Missing Skills Impact:")
            impact_score = missing_skills.get('overall_impact_score', 0)
            critical_gaps = missing_skills.get('critical_gaps', [])
            lines.append(f"  Impact Score: {impact_score}/100")
            if critical_gaps:
                lines.append("  Critical Gaps:")
                for gap in critical_gaps[:5]:
                    lines.append(f"    • {gap}")
        
        return lines
    
    def _format_recommendations(self, ats_results: Dict) -> list:
        """Format optimization recommendations"""
        lines = []
        
        recommendations = ats_results.get('recommendations', [])
        
        if recommendations:
            lines.append("💡 Optimization Recommendations:")
            for i, rec in enumerate(recommendations[:10], 1):
                lines.append(f"  {i}. {rec}")
        else:
            lines.append("No specific recommendations available.")
        
        return lines
    
    def _format_summary(self, ats_results: Dict, skill_comparison: Dict) -> list:
        """Format executive summary"""
        lines = []
        
        # Overall metrics
        ats_score = ats_results.get('overall_ats_score', 0)
        score_category = ats_results.get('score_category', 'Unknown')
        
        match_summary = skill_comparison.get('match_summary', {})
        match_percentage = match_summary.get('match_percentage', 0)
        
        lines.append("📊 Executive Summary:")
        lines.append(f"  • ATS Score: {ats_score}/100 ({score_category})")
        lines.append(f"  • Skill Match: {match_percentage}%")
        
        # Key strengths and weaknesses
        detailed_breakdown = ats_results.get('detailed_breakdown', {})
        
        # Find highest scoring component
        best_component = None
        best_score = 0
        for key, data in detailed_breakdown.items():
            if isinstance(data, dict) and 'score' in data:
                score = data.get('score', 0)
                if score > best_score:
                    best_score = score
                    best_component = key
        
        # Find lowest scoring component
        worst_component = None
        worst_score = 100
        for key, data in detailed_breakdown.items():
            if isinstance(data, dict) and 'score' in data:
                score = data.get('score', 100)
                if score < worst_score:
                    worst_score = score
                    worst_component = key
        
        if best_component:
            component_name = best_component.replace('_', ' ').title()
            lines.append(f"  • Strongest Area: {component_name} ({best_score}/100)")
        
        if worst_component:
            component_name = worst_component.replace('_', ' ').title()
            lines.append(f"  • Needs Improvement: {component_name} ({worst_score}/100)")
        
        # Overall assessment
        if ats_score >= 80:
            lines.append("  • Assessment: Strong candidate fit")
        elif ats_score >= 60:
            lines.append("  • Assessment: Good candidate fit with room for improvement")
        else:
            lines.append("  • Assessment: Significant gaps identified")
        
        return lines 

    def append_ui_output_to_file(self, output_text: str, step_name: str, company_name: str) -> str:
        """
        Simply append UI output text to a single file
        
        Args:
            output_text: The exact text displayed in Flutter UI
            step_name: Name of the step (e.g., "Analyze Match", "Skill Comparison", "ATS Test")
            company_name: Company name for the file
            
        Returns:
            str: Path to saved file
        """
        try:
            # Create company subdirectory
            company_dir = os.path.join(self.results_dir, company_name)
            os.makedirs(company_dir, exist_ok=True)
            
            # Create filename with company name
            filename = f"UI_Outputs.txt"
            filepath = os.path.join(company_dir, filename)
            
            # Append to file
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"📊 {step_name.upper()} OUTPUT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
                f.write(output_text)
                f.write("\n\n")
            
            logger.info(f"✅ {step_name} output appended to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to append {step_name} output: {e}")
            raise

    def append_analyze_match(self, raw_analysis: str, company_name: str) -> str:
        """
        Append analyze match output to file
        """
        return self.append_ui_output_to_file(raw_analysis, "ANALYZE MATCH", company_name)

    def append_skill_comparison(self, skill_comparison_text: str, company_name: str) -> str:
        """
        Append skill comparison output to file
        """
        return self.append_ui_output_to_file(skill_comparison_text, "SKILL COMPARISON", company_name)

    def append_ats_test(self, ats_test_text: str, company_name: str) -> str:
        """
        Append ATS test output to file
        """
        return self.append_ui_output_to_file(ats_test_text, "ATS TEST RESULTS", company_name) 

    def append_detailed_skill_analysis(self, detailed_analysis: dict, company_name: str) -> str:
        """
        Append detailed skill analysis with full breakdown to file
        
        Args:
            detailed_analysis: The detailed analysis dict with technical_skills, soft_skills, domain_keywords
            company_name: Company name for the file
            
        Returns:
            str: Path to saved file
        """
        try:
            # Create company subdirectory
            company_dir = os.path.join(self.results_dir, company_name)
            os.makedirs(company_dir, exist_ok=True)
            
            filename = f"UI_Outputs.txt"
            filepath = os.path.join(company_dir, filename)
            
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"📊 DETAILED SKILL ANALYSIS OUTPUT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
                
                # Technical Skills
                if 'technical_skills' in detailed_analysis:
                    f.write("🔧 TECHNICAL SKILLS\n")
                    f.write("=" * 50 + "\n")
                    
                    # Matched skills
                    if detailed_analysis['technical_skills'].get('matched'):
                        f.write(f"✅ MATCHED JD REQUIREMENTS ({len(detailed_analysis['technical_skills']['matched'])} items):\n")
                        for item in detailed_analysis['technical_skills']['matched']:
                            f.write(f"• JD Required: '{item.get('jd_skill', 'N/A')}'\n")
                            f.write(f"  → Found in CV: '{item.get('cv_equivalent', 'N/A')}'\n")
                            f.write(f"  💡 {item.get('reasoning', 'No explanation provided')}\n\n")
                    
                    # Missing skills
                    if detailed_analysis['technical_skills'].get('missing'):
                        f.write(f"❌ MISSING FROM CV ({len(detailed_analysis['technical_skills']['missing'])} items):\n")
                        f.write("(JD requirements NOT covered by your CV)\n")
                        for item in detailed_analysis['technical_skills']['missing']:
                            f.write(f"• JD Requires: '{item.get('jd_skill', 'N/A')}'\n")
                            f.write(f"  💡 {item.get('reasoning', 'No explanation provided')}\n\n")
                
                # Soft Skills
                if 'soft_skills' in detailed_analysis:
                    f.write("🤝 SOFT SKILLS\n")
                    f.write("=" * 50 + "\n")
                    
                    # Matched skills
                    if detailed_analysis['soft_skills'].get('matched'):
                        f.write(f"✅ MATCHED JD REQUIREMENTS ({len(detailed_analysis['soft_skills']['matched'])} items):\n")
                        for item in detailed_analysis['soft_skills']['matched']:
                            f.write(f"• JD Required: '{item.get('jd_skill', 'N/A')}'\n")
                            f.write(f"  → Found in CV: '{item.get('cv_equivalent', 'N/A')}'\n")
                            f.write(f"  💡 {item.get('reasoning', 'No explanation provided')}\n\n")
                    
                    # Missing skills
                    if detailed_analysis['soft_skills'].get('missing'):
                        f.write(f"❌ MISSING FROM CV ({len(detailed_analysis['soft_skills']['missing'])} items):\n")
                        f.write("(JD requirements NOT covered by your CV)\n")
                        for item in detailed_analysis['soft_skills']['missing']:
                            f.write(f"• JD Requires: '{item.get('jd_skill', 'N/A')}'\n")
                            f.write(f"  💡 {item.get('reasoning', 'No explanation provided')}\n\n")
                
                # Domain Keywords
                if 'domain_keywords' in detailed_analysis:
                    f.write("🏷️ DOMAIN KEYWORDS\n")
                    f.write("=" * 50 + "\n")
                    
                    # Matched skills
                    if detailed_analysis['domain_keywords'].get('matched'):
                        f.write(f"✅ MATCHED JD REQUIREMENTS ({len(detailed_analysis['domain_keywords']['matched'])} items):\n")
                        for item in detailed_analysis['domain_keywords']['matched']:
                            f.write(f"• JD Required: '{item.get('jd_skill', 'N/A')}'\n")
                            f.write(f"  → Found in CV: '{item.get('cv_equivalent', 'N/A')}'\n")
                            f.write(f"  💡 {item.get('reasoning', 'No explanation provided')}\n\n")
                    
                    # Missing skills
                    if detailed_analysis['domain_keywords'].get('missing'):
                        f.write(f"❌ MISSING FROM CV ({len(detailed_analysis['domain_keywords']['missing'])} items):\n")
                        f.write("(JD requirements NOT covered by your CV)\n")
                        for item in detailed_analysis['domain_keywords']['missing']:
                            f.write(f"• JD Requires: '{item.get('jd_skill', 'N/A')}'\n")
                            f.write(f"  💡 {item.get('reasoning', 'No explanation provided')}\n\n")
                
                f.write("\n")
            
            logger.info(f"✅ Detailed skill analysis appended to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to append detailed skill analysis: {e}")
            raise 

    def save_all_ui_outputs_to_json(self, 
                                    analyze_match_output: str = None,
                                    skill_comparison_output: dict = None,
                                    ats_score_output: dict = None,
                                    company_name: str = "Company") -> str:
        """
        Save all UI outputs to a single JSON file with proper structure
        
        Args:
            analyze_match_output: Raw text from CV-Magic analyze match
            skill_comparison_output: Detailed skill comparison dict
            ats_score_output: ATS score breakdown dict
            company_name: Company name for filename
            
        Returns:
            str: Path to saved file
        """
        try:
            # Create company subdirectory
            company_dir = os.path.join(self.results_dir, company_name)
            os.makedirs(company_dir, exist_ok=True)
            
            filename = f"Complete_Analysis.json"
            filepath = os.path.join(company_dir, filename)
            
            # Load existing data if file exists
            existing_data = {}
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = {}
            
            # Initialize structure if new
            if not existing_data:
                existing_data = {
                    "analysis_metadata": {
                        "company_name": company_name,
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "analysis_type": "complete_ui_outputs"
                    },
                    "cv_magic_analyze_match": {},
                    "skill_comparison": {
                        "technical_skills": {"matched": [], "missing": []},
                        "soft_skills": {"matched": [], "missing": []},
                        "domain_keywords": {"matched": [], "missing": []}
                    },
                    "ats_score_analysis": {
                        "detailed_score_breakdown": {},
                        "enhanced_requirement_bonus": {},
                        "overall_ats_score": 0
                    }
                }
            
            # Update metadata
            existing_data["analysis_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Update analyze match if provided
            if analyze_match_output:
                existing_data["cv_magic_analyze_match"] = {
                    "raw_output": analyze_match_output,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Update skill comparison if provided
            if skill_comparison_output:
                if "technical_skills" in skill_comparison_output:
                    existing_data["skill_comparison"]["technical_skills"] = skill_comparison_output["technical_skills"]
                if "soft_skills" in skill_comparison_output:
                    existing_data["skill_comparison"]["soft_skills"] = skill_comparison_output["soft_skills"]
                if "domain_keywords" in skill_comparison_output:
                    existing_data["skill_comparison"]["domain_keywords"] = skill_comparison_output["domain_keywords"]
            
            # Update ATS score if provided
            if ats_score_output:
                if "detailed_score_breakdown" in ats_score_output:
                    existing_data["ats_score_analysis"]["detailed_score_breakdown"] = ats_score_output["detailed_score_breakdown"]
                if "enhanced_requirement_bonus" in ats_score_output:
                    existing_data["ats_score_analysis"]["enhanced_requirement_bonus"] = ats_score_output["enhanced_requirement_bonus"]
                if "overall_ats_score" in ats_score_output:
                    existing_data["ats_score_analysis"]["overall_ats_score"] = ats_score_output["overall_ats_score"]
            
            # Write updated data back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ All UI outputs saved to JSON: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save UI outputs to JSON: {e}")
            raise

    def auto_save_analyze_match_json(self, analyze_match_output: str, company_name: str) -> str:
        """
        Auto-save analyze match output to JSON file
        """
        return self.save_all_ui_outputs_to_json(analyze_match_output=analyze_match_output, company_name=company_name)

    def auto_save_skill_comparison_json(self, skill_comparison_output: dict, company_name: str) -> str:
        """
        Auto-save skill comparison output to JSON file
        """
        return self.save_all_ui_outputs_to_json(skill_comparison_output=skill_comparison_output, company_name=company_name)

    def auto_save_ats_score_json(self, ats_score_output: dict, company_name: str) -> str:
        """
        Auto-save ATS score output to JSON file
        """
        return self.save_all_ui_outputs_to_json(ats_score_output=ats_score_output, company_name=company_name)

    def save_session_analysis(self, cv_filename: str, jd_text: str, 
                            analyze_match_output: str = None,
                            skill_comparison_output: dict = None,
                            ats_score_output: dict = None) -> str:
        """
        Save analysis results using session file manager for unique file naming
        
        Args:
            cv_filename: Name of the CV file
            jd_text: Job description text
            analyze_match_output: Raw analyze match output
            skill_comparison_output: Skill comparison results dict
            ats_score_output: ATS score breakdown dict
            
        Returns:
            str: Path to saved file
        """
        try:
            from .session_file_manager import session_file_manager
            
            # Get or create session file
            filename, filepath, is_new_file = session_file_manager.get_or_create_session_file(
                cv_filename, jd_text
            )
            
            if is_new_file:
                # Initialize new session file
                session_file_manager.initialize_session_file(filepath, cv_filename, jd_text)
            
            # Update session file with analysis data
            if analyze_match_output:
                session_file_manager.update_session_file(
                    filepath, "preliminary_analysis", 
                    {"raw_output": analyze_match_output}
                )
            
            if skill_comparison_output:
                session_file_manager.update_session_file(
                    filepath, "skill_comparison", skill_comparison_output
                )
            
            if ats_score_output:
                session_file_manager.update_session_file(
                    filepath, "enhanced_ats_score", ats_score_output
                )
            
            logger.info(f"✅ Session analysis saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save session analysis: {e}")
            raise

    def save_exact_ui_text(self, step_name: str, ui_output_text: str, company_name: str, timestamp: str = None) -> str:
        """
        Save exact UI output text as displayed in Flutter app
        This captures every letter, word, emoji, and formatting exactly as shown in UI
        
        Args:
            step_name: Name of the step (e.g., "Analyze Match", "Skill Comparison", "ATS Test")
            ui_output_text: The exact text displayed in Flutter UI
            company_name: Company name for filename
            timestamp: Optional timestamp
            
        Returns:
            str: Path to saved file
        """
        try:
            if not timestamp:
                timestamp = datetime.now().isoformat()
            
            # Create company subdirectory
            safe_company_name = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '_')
            company_dir = os.path.join(self.results_dir, safe_company_name)
            os.makedirs(company_dir, exist_ok=True)
            
            filename = f"Exact_UI_Outputs.json"
            filepath = os.path.join(company_dir, filename)
            
            # Load existing data if file exists
            existing_data = {}
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = {}
            
            # Initialize structure if new
            if not existing_data:
                existing_data = {
                    "metadata": {
                        "company_name": company_name,
                        "created_at": timestamp,
                        "last_updated": timestamp,
                        "file_type": "exact_ui_outputs",
                        "description": "Exact text output as displayed in Flutter UI"
                    },
                    "ui_outputs": []
                }
            
            # Update metadata
            existing_data["metadata"]["last_updated"] = timestamp
            
            # Add new output
            new_output = {
                "step_name": step_name,
                "timestamp": timestamp,
                "ui_text": ui_output_text,
                "character_count": len(ui_output_text),
                "word_count": len(ui_output_text.split())
            }
            
            # Check if this step already exists and update or append
            existing_step_index = -1
            for i, output in enumerate(existing_data["ui_outputs"]):
                if output.get("step_name") == step_name:
                    existing_step_index = i
                    break
            
            if existing_step_index != -1:
                # Update existing step
                existing_data["ui_outputs"][existing_step_index] = new_output
                logger.info(f"✅ Updated existing {step_name} output")
            else:
                # Add new step
                existing_data["ui_outputs"].append(new_output)
                logger.info(f"✅ Added new {step_name} output")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exact UI text saved to: {filepath}")
            
            # Debug: Print file content if debug is enabled
            if self.debug:
                self._debug_print_ui_text_save(filepath, step_name, len(ui_output_text))
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save exact UI text: {e}")
            raise
    
    def _debug_print_ui_text_save(self, filepath: str, step_name: str, text_length: int):
        """Debug function to print UI text save info"""
        print("\n" + "="*80)
        print(f"💾 DEBUG: Exact UI Text Saved")
        print(f"📁 File: {filepath}")
        print(f"📊 Step: {step_name}")
        print(f"📏 Text Length: {text_length} characters")
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print(f"✅ Exact UI output captured and saved successfully")
        print("="*80 + "\n")

    def save_job_info_as_json(self, jd_text: str, job_link: str = None) -> str:
        """
        Extract job information using LLM and save as JSON file
        
        Args:
            jd_text: Job description text
            job_link: Optional job link
            
        Returns:
            str: Path to saved JSON file
        """
        try:
            # Extract company information using LLM
            import asyncio
            try:
                # Check if we're in an event loop already
                loop = asyncio.get_running_loop()
                # If we are, we need to use a different approach - for now use fallback
                print(f"⚠️ [LLM_EXTRACTION] Running in event loop - using fallback data")
                company_info = self._get_fallback_data()
            except RuntimeError:
                # Not in an event loop, safe to use asyncio.run
                company_info = asyncio.run(self.extract_company_info_with_llm(jd_text))
            
            if not company_info:
                raise Exception("Failed to extract company information")
            
            # Create company-specific directory
            company_name = company_info.get('company_name', 'Unknown_Company')
            safe_company_name = re.sub(r'[^\w\s&.-]', '', company_name)
            safe_company_name = re.sub(r'\s+', '_', safe_company_name)
            safe_company_name = safe_company_name.strip('_')
            
            company_dir = os.path.join(self.results_dir, safe_company_name)
            os.makedirs(company_dir, exist_ok=True)
            
            # Create filename
            filename = f"job_info_{safe_company_name}.json"
            filepath = os.path.join(company_dir, filename)
            
            # Prepare job info data - use direct structure like original backend
            job_info = company_info.copy()  # Use the extracted data directly
            
            # Add job_link if provided
            if job_link:
                job_info['job_link'] = job_link
            
            # Save to JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(job_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Job info saved to: {filepath}")
            
            if self.debug:
                print(f"🏢 [JOB_INFO] Company: {company_name}")
                print(f"📁 [JOB_INFO] File: {filepath}")
                print(f"📊 [JOB_INFO] Position: {company_info.get('job_title', 'N/A')}")
                print(f"📍 [JOB_INFO] Location: {company_info.get('location', 'N/A')}")
                print(f"📅 [JOB_INFO] Experience: {company_info.get('experience_required', 'N/A')}")
                print(f"🎯 [JOB_INFO] Level: {company_info.get('seniority_level', 'N/A')}")
                print(f"🏭 [JOB_INFO] Industry: {company_info.get('industry', 'N/A')}")
                print(f"📧 [JOB_INFO] Email: {company_info.get('email', 'N/A')}")
                print(f"🌐 [JOB_INFO] Website: {company_info.get('website', 'N/A')}")
                print(f"🏠 [JOB_INFO] Work Type: {company_info.get('work_type', 'N/A')}")
            
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
            safe_company_name = re.sub(r'[^\w\s&.-]', '', company_name)
            safe_company_name = re.sub(r'\s+', '_', safe_company_name)
            safe_company_name = safe_company_name.strip('_')
            
            # Create company-specific directory
            company_dir = os.path.join(self.results_dir, safe_company_name)
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
            
            if self.debug:
                print(f"📄 [ORIGINAL_CV] Company: {company_name}")
                print(f"📁 [ORIGINAL_CV] File: {filepath}")
                print(f"📏 [ORIGINAL_CV] Length: {len(cv_text)} characters")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save original CV text: {e}")
            raise 
