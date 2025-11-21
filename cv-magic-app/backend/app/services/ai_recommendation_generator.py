"""
AI Recommendation Generator Service

This service executes AI recommendation prompts using the centralized AI system
and saves the generated recommendations as structured JSON files.

UPDATED: Handles JSON output from AI and converts to markdown for frontend display
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from app.ai.ai_service import ai_service
from app.ai.base_provider import AIResponse
from app.utils.timestamp_utils import TimestampUtils

# Import CV tailoring service with conditional import to avoid circular dependencies
try:
    from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
    CV_TAILORING_AVAILABLE = True
except ImportError:
    CV_TAILORING_AVAILABLE = False
    CVTailoringService = None

logger = logging.getLogger(__name__)


class AIRecommendationGenerator:
    """Service for generating AI-based CV optimization recommendations"""
    
    def __init__(self, user_email: str):
        from app.utils.user_path_utils import get_user_base_path
        self.user_email = user_email
        self.base_dir = get_user_base_path(user_email)
        self.prompt_dir = Path("/app/prompt")
    
    async def generate_ai_recommendation(self, company: str, force_regenerate: bool = False) -> bool:
        """
        Generate AI recommendation for a company using the centralized AI system
        
        Args:
            company: Company name
            force_regenerate: Force regeneration even if file exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🤖 [AI GENERATOR] Starting AI recommendation generation for: {company}")
            
            # Check recency between latest input recommendation and latest AI recommendation
            output_file = self._get_output_file_path(company)
            if not force_regenerate:
                try:
                    company_dir = self.base_dir / "applied_companies" / company
                    latest_input = TimestampUtils.find_latest_timestamped_file(
                        company_dir, f"{company}_input_recommendation", "json"
                    ) or (company_dir / f"{company}_input_recommendation.json")

                    latest_ai = TimestampUtils.find_latest_timestamped_file(
                        company_dir, f"{company}_ai_recommendation", "json"
                    ) or (company_dir / f"{company}_ai_recommendation.json")

                    latest_input_mtime = latest_input.stat().st_mtime if latest_input and latest_input.exists() else 0
                    latest_ai_mtime = latest_ai.stat().st_mtime if latest_ai and latest_ai.exists() else 0

                    if latest_ai.exists() and latest_ai_mtime >= latest_input_mtime:
                        logger.info(
                            f"🟢 [AI GENERATOR] Latest AI recommendation ({latest_ai.name}) is up-to-date vs input ({latest_input.name if latest_input else 'N/A'}); skipping regeneration"
                        )
                        return True
                    else:
                        logger.info(
                            f"🟡 [AI GENERATOR] Input recommendation is newer (ai_mtime={latest_ai_mtime}, input_mtime={latest_input_mtime}); regenerating AI recommendation"
                        )
                except Exception as time_err:
                    logger.warning(f"⚠️ [AI GENERATOR] Timestamp check failed, proceeding with generation: {time_err}")
            
            # Check if CV has been updated since input recommendation was generated
            if not self._check_cv_freshness(company):
                logger.warning(f"⚠️ [AI GENERATOR] CV has been updated since input recommendation was generated")
                logger.warning(f"⚠️ [AI GENERATOR] Input recommendation may be outdated - consider regenerating input recommendation first")
            
            # Load the AI prompt
            prompt_content = self._load_ai_prompt(company)
            if not prompt_content:
                logger.error(f"Could not load AI prompt for {company}")
                return False
            
            # Generate AI response using centralized AI system
            logger.info(f"🧠 [AI GENERATOR] Executing AI prompt for {company}")
            ai_response = await self._execute_ai_prompt(prompt_content)
            
            if not ai_response:
                logger.error(f"Failed to get AI response for {company}")
                return False
            
            # Parse and structure the AI response
            structured_response = self._structure_ai_response(ai_response, company)
            
            # Save the structured response as JSON
            success = self._save_ai_recommendation(company, structured_response)
            
            if success:
                logger.info(f"✅ [AI GENERATOR] AI recommendation generated and saved for {company}")
                logger.info(f"📄 File: {output_file}")
                logger.info(f"💰 Cost: ${ai_response.cost:.4f}")
                logger.info(f"🔤 Tokens: {ai_response.tokens_used}")
                
                # Automatically trigger CV tailoring after successful AI recommendation generation
                try:
                    cv_success = await self._trigger_cv_tailoring(company)
                    if cv_success:
                        logger.info(f"🎯 [AI GENERATOR] CV tailoring completed automatically for {company}")
                    else:
                        logger.warning(f"⚠️ [AI GENERATOR] CV tailoring failed for {company}")
                except Exception as cv_error:
                    logger.error(f"❌ [AI GENERATOR] CV tailoring error for {company}: {cv_error}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error generating AI recommendation for {company}: {e}")
            return False
    
    def _get_output_file_path(self, company: str) -> Path:
        """Get the latest output file path for AI recommendation"""
        company_dir = self.base_dir / "applied_companies" / company
        latest_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "json")
        if latest_file:
            return latest_file
        return company_dir / f"{company}_ai_recommendation.json"
    
    def _get_input_recommendation_file_path(self, company: str) -> Path:
        """Get the input recommendation file path for a company"""
        company_dir = self.base_dir / "applied_companies" / company
        input_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_input_recommendation", "json")
        if not input_file:
            input_file = company_dir / f"{company}_input_recommendation.json"
        return input_file
    
    def _check_cv_freshness(self, company: str) -> bool:
        """Check if the CV has been updated since the input recommendation was generated"""
        try:
            from app.unified_latest_file_selector import get_selector_for_user
            
            user_selector = get_selector_for_user(self.user_email)
            cv_context = user_selector.get_latest_cv_across_all(company)
            if not cv_context.exists:
                logger.warning(f"⚠️ [AI GENERATOR] No CV found for {company}")
                return True
            
            input_file = self._get_input_recommendation_file_path(company)
            if not input_file.exists():
                logger.warning(f"⚠️ [AI GENERATOR] No input recommendation file found for {company}")
                return True
            
            cv_mtime = cv_context.timestamp.timestamp() if cv_context.timestamp else 0
            input_mtime = input_file.stat().st_mtime
            
            if cv_mtime > input_mtime:
                logger.warning(f"⚠️ [AI GENERATOR] CV is newer than input recommendation")
                return False
            
            logger.info(f"✅ [AI GENERATOR] CV is fresh - no updates since input recommendation")
            return True
            
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error checking CV freshness: {e}")
            return True
    
    def _load_ai_prompt(self, company: str) -> Optional[str]:
        """Generate AI prompt using the centralized template with company analysis data"""
        try:
            input_file = self._get_input_recommendation_file_path(company)
            if not input_file.exists():
                logger.error(f"Input recommendation file not found: {input_file}")
                return None
            
            with open(input_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            import sys
            import importlib.util
            
            template_path = self.prompt_dir / "ai_recommendation_prompt_template.py"
            if not template_path.exists():
                logger.error(f"AI recommendation template not found: {template_path}")
                return None
            
            spec = importlib.util.spec_from_file_location("ai_recommendation_prompt_template", template_path)
            template_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_module)
            
            prompt_content = template_module.generate_ai_recommendation_prompt(company, analysis_data)
            
            logger.info(f"📋 [AI GENERATOR] Generated AI prompt for {company} using centralized template ({len(prompt_content)} characters)")
            return prompt_content
                
        except Exception as e:
            logger.error(f"Error generating AI prompt for {company}: {e}")
            return None
    
    async def _execute_ai_prompt(self, prompt_content: str) -> Optional[AIResponse]:
        """Execute the AI prompt using the centralized AI system"""
        try:
            from app.models.auth import UserData
            from datetime import datetime, timezone
            current_user = UserData(
                id="pipeline_user",
                email=self.user_email,
                name=self.user_email.split("@")[0] if self.user_email else "user",
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            response = await ai_service.generate_response(
                prompt=prompt_content,
                user=current_user,
                system_prompt="You are an expert CV strategist and career consultant. Provide detailed, actionable recommendations in the exact JSON format requested. Return ONLY valid JSON, no markdown formatting.",
                temperature=0.0,
                max_tokens=4000
            )
            
            logger.info(f"🧠 [AI GENERATOR] AI response generated - Provider: {response.provider}, Model: {response.model}")
            logger.info(f"💰 [AI GENERATOR] Cost: ${response.cost:.4f}, Tokens: {response.tokens_used}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing AI prompt: {e}")
            return None
    
    def _structure_ai_response(self, ai_response: AIResponse, company: str) -> Dict[str, Any]:
        """
        Structure the AI response - parse JSON and convert to markdown for frontend display
        
        Args:
            ai_response: Raw AI response
            company: Company name
            
        Returns:
            Structured JSON data with both markdown (for display) and JSON (for CV generation)
        """
        logger.info(f"🔍 [AI_RESPONSE] Parsing AI response for {company}")
        
        # Clean the response before parsing
        cleaned_content = self._clean_json_response(ai_response.content)
        
        try:
            # Try to parse response as JSON
            json_data = json.loads(cleaned_content)
            logger.info(f"✅ [AI_RESPONSE] Successfully parsed JSON")
            
            # Check keyword categorization
            keyword_integration = json_data.get('keyword_integration', {})
            tier1 = keyword_integration.get('tier1_integrate_immediately', {})
            tier2 = keyword_integration.get('tier2_add_with_evidence', {})
            tier3 = keyword_integration.get('tier3_never_add', {})
            
            tier1_count = len(tier1.get('technical', [])) + len(tier1.get('soft', [])) + len(tier1.get('domain', []))
            tier2_count = len(tier2.get('technical', [])) + len(tier2.get('soft', [])) + len(tier2.get('domain', []))
            tier3_count = len(tier3.get('technical', [])) + len(tier3.get('soft', [])) + len(tier3.get('domain', []))
            
            logger.info(f"📊 [AI_RESPONSE] Keyword Categorization:")
            logger.info(f"   - Tier 1: {tier1_count} keywords (Technical: {len(tier1.get('technical', []))}, Soft: {len(tier1.get('soft', []))}, Domain: {len(tier1.get('domain', []))})")
            logger.info(f"   - Tier 2: {tier2_count} keywords (Technical: {len(tier2.get('technical', []))}, Soft: {len(tier2.get('soft', []))}, Domain: {len(tier2.get('domain', []))})")
            logger.info(f"   - Tier 3: {tier3_count} keywords (Technical: {len(tier3.get('technical', []))}, Soft: {len(tier3.get('soft', []))}, Domain: {len(tier3.get('domain', []))})")
            logger.info(f"   - Total categorized: {tier1_count + tier2_count + tier3_count}")
            
            # Convert JSON to markdown for frontend display
            markdown_content = self._convert_json_to_markdown(json_data, company)
            
            # Extract actionable guidance for CV generation
            try:
                actionable_guidance = self._extract_actionable_guidance(json_data)
                logger.info(f"✅ [AI_RESPONSE] Extracted actionable guidance:")
                tier1_act = actionable_guidance.get('tier1_add_immediately', {})
                tier2_act = actionable_guidance.get('tier2_add_with_evidence', {})
                logger.info(f"   - Tier 1: {len(tier1_act.get('technical', []))} technical, {len(tier1_act.get('soft', []))} soft")
                logger.info(f"   - Tier 2: {len(tier2_act.get('technical', []))} technical, {len(tier2_act.get('soft', []))} soft")
                logger.info(f"   - Tier 3 avoid: {len(actionable_guidance.get('tier3_never_add', []))} keywords")
            except Exception as e:
                logger.warning(f"⚠️ [AI_RESPONSE] Failed to extract actionable guidance: {e}")
                actionable_guidance = {}  # Empty dict if extraction fails
            
            return {
                "company": company,
                "generated_at": datetime.now().isoformat(),
                "recommendation_content": markdown_content,  # Markdown for frontend display
                "structured_recommendations": json_data,     # JSON for programmatic CV generation
                "actionable_guidance": actionable_guidance,   # Flattened actionable guidance for CV generation
                "ai_model_info": {
                    "provider": ai_response.provider,
                    "model": ai_response.model,
                    "cost": ai_response.cost,
                    "tokens_used": ai_response.tokens_used
                },
                "metadata": {
                    "content_length": len(markdown_content),
                    "format_version": "2.0",  # Updated format with structured data
                    "has_structured_data": True,
                    "has_actionable_guidance": bool(actionable_guidance)  # Indicates actionable_guidance is available
                }
            }
            
        except json.JSONDecodeError as e:
            # Fallback: If AI returns markdown instead of JSON
            logger.warning(f"⚠️ [AI GENERATOR] AI response is not valid JSON, treating as markdown: {e}")
            logger.warning(f"⚠️ [AI GENERATOR] Response preview: {ai_response.content[:200]}...")
            return {
                "company": company,
                "generated_at": datetime.now().isoformat(),
                "recommendation_content": ai_response.content,  # Raw markdown
                "ai_model_info": {
                    "provider": ai_response.provider,
                    "model": ai_response.model,
                    "cost": ai_response.cost,
                    "tokens_used": ai_response.tokens_used
                },
                "metadata": {
                    "content_length": len(ai_response.content),
                    "format_version": "1.0",  # Legacy markdown format
                    "has_structured_data": False
                }
            }
    
    def _clean_json_response(self, content: str) -> str:
        """
        Clean AI response to extract valid JSON
        
        Removes markdown code blocks, extra text, and fixes common JSON issues
        
        Args:
            content: Raw AI response content
            
        Returns:
            Cleaned JSON string ready for parsing
        """
        import re
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Remove markdown code blocks (```json or ```)
        content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        # Find the first { and last } to extract JSON object
        # This handles cases where AI adds explanatory text before/after JSON
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            # Extract JSON portion
            content = content[start_idx:end_idx + 1]
        elif start_idx == -1 or end_idx == -1:
            # No JSON found, return as-is (will fail parsing and fall back to markdown)
            logger.warning(f"⚠️ [AI GENERATOR] No JSON object found in response")
            return content
        
        # Fix common JSON issues
        # Remove trailing commas before closing braces/brackets
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        return content.strip()
    
    def _extract_actionable_guidance(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and flatten actionable guidance from structured recommendations
        
        Args:
            json_data: Structured recommendations JSON
            
        Returns:
            Flattened actionable guidance for easy CV generation
        """
        keyword_integration = json_data.get('keyword_integration', {})
        experience_reframing = json_data.get('experience_reframing', {})
        warnings = json_data.get('strategic_warnings', {})
        roadmap = json_data.get('implementation_roadmap', {})
        tone_style = json_data.get('tone_and_style', {})
        
        # Extract Tier 1 keywords (add immediately)
        tier1 = keyword_integration.get('tier1_integrate_immediately', {})
        tier1_flattened = {
            'technical': [
                {
                    'keyword': item.get('keyword'),
                    'integration': item.get('integration'),
                    'validation': item.get('validation')
                }
                for item in tier1.get('technical', [])
            ],
            'soft': [
                {
                    'keyword': item.get('keyword'),
                    'integration': item.get('integration'),
                    'validation': item.get('validation')
                }
                for item in tier1.get('soft', [])
            ],
            'domain': [
                {
                    'keyword': item.get('keyword'),
                    'integration': item.get('integration'),
                    'validation': item.get('validation')
                }
                for item in tier1.get('domain', [])
            ]
        }
        
        # Extract Tier 2 keywords (add with evidence)
        tier2 = keyword_integration.get('tier2_add_with_evidence', {})
        tier2_flattened = {
            'technical': [
                {
                    'keyword': item.get('keyword'),
                    'integration': item.get('integration'),
                    'validation': item.get('validation'),
                    'evidence_required': True
                }
                for item in tier2.get('technical', [])
            ],
            'soft': [
                {
                    'keyword': item.get('keyword'),
                    'integration': item.get('integration'),
                    'validation': item.get('validation'),
                    'evidence_required': True
                }
                for item in tier2.get('soft', [])
            ],
            'domain': [
                {
                    'keyword': item.get('keyword'),
                    'integration': item.get('integration'),
                    'validation': item.get('validation'),
                    'evidence_required': True
                }
                for item in tier2.get('domain', [])
            ]
        }
        
        # Extract Tier 3 keywords (never add)
        tier3 = keyword_integration.get('tier3_never_add', {})
        tier3_flat = []
        for item in tier3.get('technical', []):
            tier3_flat.append(item.get('keyword'))
        for item in tier3.get('domain', []):
            tier3_flat.append(item.get('keyword'))
        for item in tier3.get('soft', []):
            tier3_flat.append(item.get('keyword'))
        
        # Extract strategic positioning
        industry_transition = experience_reframing.get('industry_transition', {})
        
        # Extract experience optimization
        technical_showcase = experience_reframing.get('technical_showcase', {})
        
        # Extract warnings
        dont_undersell = warnings.get('dont_undersell', {})
        
        return {
            # Keyword tiers
            "tier1_add_immediately": tier1_flattened,
            "tier2_add_with_evidence": tier2_flattened,
            "tier3_never_add": tier3_flat,
            
            # Strategic positioning
            "strategic_positioning": {
                "emphasis_areas": industry_transition.get('emphasis_areas', []),
                "de_emphasize": industry_transition.get('de_emphasize', []),
                "bridging_statements": industry_transition.get('bridging_statements', []),
                "strategy": experience_reframing.get('seniority_positioning', {}).get('strategy', '')
            },
            
            # Experience optimization
            "experience_optimization": {
                "strengths_to_highlight": technical_showcase.get('strengths_to_highlight', []),
                "gaps_to_address": technical_showcase.get('gaps_to_address', [])
            },
            
            # Achievements to emphasize
            "achievements": {
                "transferable_experience": dont_undersell.get('transferable_experience', []),
                "core_competencies": dont_undersell.get('core_competencies', [])
            },
            
            # Implementation roadmap
            "implementation_plan": {
                "phase1_quick_wins": roadmap.get('phase1_quick_wins', []),
                "phase2_evidence_based": roadmap.get('phase2_evidence_based', []),
                "phase3_positioning": roadmap.get('phase3_positioning', [])
            },
            
            # Messaging guidance
            "messaging": {
                "key_messages": tone_style.get('key_messages', []),
                "avoid_messages": tone_style.get('avoid_messages', [])
            }
        }
    
    def _convert_json_to_markdown(self, json_data: Dict[str, Any], company: str) -> str:
        """
        Convert structured JSON recommendations to formatted markdown for frontend display
        
        Args:
            json_data: Structured JSON recommendation data
            company: Company name
            
        Returns:
            Formatted markdown string
        """
        lines = []
        
        # Title
        lines.append(f"# CV Tailoring Strategy Report for {company}\n")
        
        # Priority Gaps
        priority_gaps = json_data.get("priority_gaps", {})
        if priority_gaps:
            lines.append("## Priority Gap Analysis\n")
            
            # Keyword coverage gaps
            keyword_gaps = priority_gaps.get("keyword_coverage_gaps", {})
            if keyword_gaps:
                lines.append("**Keyword Coverage Gaps:**")
                lines.append(f"- Technical Gap: {keyword_gaps.get('technical_gap_percentage', 0):.1f}%")
                lines.append(f"- Soft Skills Gap: {keyword_gaps.get('soft_gap_percentage', 0):.1f}%")
                lines.append(f"- Domain Gap: {keyword_gaps.get('domain_gap_percentage', 0):.1f}%")
                lines.append(f"- Overall Keyword Gap: {keyword_gaps.get('overall_keyword_gap', 0):.1f}%\n")
            
            # Component gaps
            component_gaps = priority_gaps.get("component_gaps", {})
            if component_gaps:
                lines.append("**Component Alignment Gaps:**")
                lines.append(f"- Technical Depth Gap: {component_gaps.get('technical_depth_gap', 0):.1f}%")
                lines.append(f"- Experience Alignment Gap: {component_gaps.get('experience_alignment_gap', 0):.1f}%")
                lines.append(f"- Industry Fit Gap: {component_gaps.get('industry_fit_gap', 0):.1f}%")
                lines.append(f"- Seniority Alignment Gap: {component_gaps.get('seniority_alignment_gap', 0):.1f}%\n")
            
            # Immediate action items
            immediate = priority_gaps.get("immediate_action_items", {})
            if immediate:
                category1 = immediate.get("category1_missing_counts", {})
                if category1:
                    lines.append("**Immediate Action Required (Missing Keywords):**")
                    lines.append(f"- Technical: {category1.get('technical', 0)}")
                    lines.append(f"- Soft Skills: {category1.get('soft', 0)}")
                    lines.append(f"- Domain: {category1.get('domain', 0)}")
                    lines.append(f"- **Total Missing: {category1.get('total', 0)}**\n")
        
        # Keyword Integration
        keyword_integration = json_data.get("keyword_integration", {})
        if keyword_integration:
            lines.append("## Keyword Integration Strategy\n")
            
            # Tier 1
            tier1 = keyword_integration.get("tier1_integrate_immediately", {})
            if tier1:
                lines.append("### TIER 1 - INTEGRATE IMMEDIATELY (Low Risk)")
                
                tech = tier1.get("technical", [])
                if tech:
                    lines.append("**Technical Keywords to Add:**")
                    for item in tech:
                        lines.append(f"- **{item.get('keyword', 'N/A')}**")
                        lines.append(f"  - **Basis:** {item.get('basis', 'N/A')}")
                        lines.append(f"  - **Integration:** {item.get('integration', 'N/A')}")
                        lines.append(f"  - **Validation:** {item.get('validation', 'N/A')}")
                        lines.append(f"  - **Risk:** {item.get('risk', 'low')}")
                
                soft = tier1.get("soft", [])
                if soft:
                    lines.append("\n**Soft Skills to Add:**")
                    for item in soft:
                        lines.append(f"- **{item.get('keyword', 'N/A')}**")
                        lines.append(f"  - **Basis:** {item.get('basis', 'N/A')}")
                        lines.append(f"  - **Integration:** {item.get('integration', 'N/A')}")
                        lines.append(f"  - **Validation:** {item.get('validation', 'N/A')}")
                        lines.append(f"  - **Risk:** {item.get('risk', 'low')}")
                lines.append("")
            
            # Tier 2
            tier2 = keyword_integration.get("tier2_add_with_evidence", {})
            if tier2:
                lines.append("### TIER 2 - ADD WITH EVIDENCE (Medium Risk)")
                
                tech = tier2.get("technical", [])
                if tech:
                    lines.append("**Technical Keywords (If Evidence Exists):**")
                    for item in tech:
                        lines.append(f"- **{item.get('keyword', 'N/A')}**")
                        lines.append(f"  - **Basis:** {item.get('basis', 'N/A')}")
                        lines.append(f"  - **Integration:** {item.get('integration', 'N/A')}")
                        lines.append(f"  - **Validation:** {item.get('validation', 'N/A')}")
                        lines.append(f"  - **Risk:** {item.get('risk', 'medium')}")
                
                soft = tier2.get("soft", [])
                if soft:
                    lines.append("\n**Soft Skills (If Evidence Exists):**")
                    for item in soft:
                        lines.append(f"- **{item.get('keyword', 'N/A')}**")
                        lines.append(f"  - **Basis:** {item.get('basis', 'N/A')}")
                        lines.append(f"  - **Integration:** {item.get('integration', 'N/A')}")
                        lines.append(f"  - **Validation:** {item.get('validation', 'N/A')}")
                        lines.append(f"  - **Risk:** {item.get('risk', 'medium')}")
                lines.append("")
            
            # Tier 3
            tier3 = keyword_integration.get("tier3_never_add", {})
            if tier3:
                lines.append("### TIER 3 - DO NOT ADD (High Risk)")
                lines.append("**Keywords to Avoid:**")
                
                tech = tier3.get("technical", [])
                for item in tech:
                    lines.append(f"- **{item.get('keyword', 'N/A')}**")
                    lines.append(f"  - **Why Not:** {item.get('why_not', 'N/A')}")
                    lines.append(f"  - **Risk:** {item.get('risk', 'high')}")
                    if item.get('alternative'):
                        lines.append(f"  - **Alternative:** {item.get('alternative')}")
                
                domain = tier3.get("domain", [])
                for item in domain:
                    lines.append(f"- **{item.get('keyword', 'N/A')}**")
                    lines.append(f"  - **Why Not:** {item.get('why_not', 'N/A')}")
                    lines.append(f"  - **Risk:** {item.get('risk', 'high')}")
                    if item.get('alternative'):
                        lines.append(f"  - **Alternative:** {item.get('alternative')}")
                lines.append("")
        
        # Experience Reframing
        exp_reframing = json_data.get("experience_reframing", {})
        if exp_reframing:
            lines.append("## Experience Reframing Strategy\n")
            
            industry = exp_reframing.get("industry_transition", {})
            if industry:
                lines.append("### Industry Transition Focus")
                lines.append(f"**Objective:** {industry.get('objective', 'N/A')}\n")
                
                emphasis = industry.get("emphasis_areas", [])
                if emphasis:
                    lines.append("**Emphasis Areas:**")
                    for area in emphasis:
                        lines.append(f"- {area}")
                    lines.append("")
                
                de_emphasize = industry.get("de_emphasize", [])
                if de_emphasize:
                    lines.append("**De-Emphasize:**")
                    for area in de_emphasize:
                        lines.append(f"- {area}")
                    lines.append("")
                
                bridging = industry.get("bridging_statements", [])
                if bridging:
                    lines.append("**Bridging Statements to Use:**")
                    for statement in bridging:
                        lines.append(f"- {statement}")
                    lines.append("")
            
            seniority = exp_reframing.get("seniority_positioning", {})
            if seniority:
                lines.append("### Seniority Positioning")
                lines.append(f"**Current:** {seniority.get('current_level', 'Unknown')}")
                lines.append(f"**Target:** {seniority.get('target_level', 'Unknown')}")
                lines.append(f"**Strategy:** {seniority.get('strategy', 'N/A')}\n")
            
            technical = exp_reframing.get("technical_showcase", {})
            if technical:
                lines.append("### Technical Depth Showcase")
                
                strengths = technical.get("strengths_to_highlight", [])
                if strengths:
                    lines.append("**Strengths to Highlight:**")
                    for strength in strengths:
                        lines.append(f"- {strength}")
                    lines.append("")
                
                gaps = technical.get("gaps_to_address", [])
                if gaps:
                    lines.append("**Gaps to Address:**")
                    for gap in gaps:
                        lines.append(f"- {gap}")
                    lines.append("")
        
        # Strategic Warnings
        warnings = json_data.get("strategic_warnings", {})
        if warnings:
            lines.append("## Strategic Warnings\n")
            
            dont_oversell = warnings.get("dont_oversell", {})
            if dont_oversell:
                lines.append("### Don't Oversell (Avoid These Claims)")
                lines.append(f"- **Tier 3 Keywords:** {dont_oversell.get('tier3_keywords', 'Never add without direct evidence')}")
                
                domain_specific = dont_oversell.get("domain_specific", [])
                if domain_specific:
                    lines.append(f"- **Domain-Specific Terms:** {', '.join(domain_specific)} - Cannot claim without industry experience")
                
                unverifiable = dont_oversell.get("unverifiable_skills", [])
                if unverifiable:
                    lines.append(f"- **Unverifiable Skills:** {', '.join(unverifiable)} - No supporting evidence")
                lines.append("")
            
            dont_undersell = warnings.get("dont_undersell", {})
            if dont_undersell:
                lines.append("### Don't Undersell (Emphasize These Strengths)")
                
                matched = dont_undersell.get("matched_skills", [])
                if matched:
                    lines.append(f"- **Matched Skills:** {', '.join(matched)}")
                
                transferable = dont_undersell.get("transferable_experience", [])
                if transferable:
                    lines.append(f"- **Transferable Experience:** {'; '.join(transferable)}")
                
                core = dont_undersell.get("core_competencies", [])
                if core:
                    lines.append(f"- **Core Competencies:** {'; '.join(core)}")
                lines.append("")
        
        # Implementation Roadmap
        roadmap = json_data.get("implementation_roadmap", {})
        if roadmap:
            lines.append("## Implementation Roadmap\n")
            
            phase1 = roadmap.get("phase1_quick_wins", [])
            if phase1:
                lines.append("### Phase 1: High-Impact Quick Wins")
                for item in phase1:
                    lines.append(f"{item}")
                lines.append("")
            
            phase2 = roadmap.get("phase2_evidence_based", [])
            if phase2:
                lines.append("### Phase 2: Evidence-Based Additions")
                for item in phase2:
                    lines.append(f"{item}")
                lines.append("")
            
            phase3 = roadmap.get("phase3_positioning", [])
            if phase3:
                lines.append("### Phase 3: Strategic Positioning")
                for item in phase3:
                    lines.append(f"{item}")
                lines.append("")
        
        # Tone and Style
        tone_style = json_data.get("tone_and_style", {})
        if tone_style:
            lines.append("## Section Completeness Notes")
            lines.append(f"- **Overall Tone:** {tone_style.get('overall_tone', 'Professional and results-oriented')}")
            
            key_messages = tone_style.get("key_messages", [])
            if key_messages:
                lines.append(f"- **Key Messages:** {', '.join(key_messages)}")
            
            avoid = tone_style.get("avoid_messages", [])
            if avoid:
                lines.append(f"- **Avoid:** {', '.join(avoid)}")
        
        return "\n".join(lines)
    
    def _save_ai_recommendation(self, company: str, recommendation_data: Dict[str, Any]) -> bool:
        """Save the AI recommendation data as JSON file"""
        try:
            company_dir = self.base_dir / "applied_companies" / company
            company_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = TimestampUtils.get_timestamp()
            output_file = company_dir / f"{company}_ai_recommendation_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(recommendation_data, f, indent=2, ensure_ascii=False)
            
            file_size = output_file.stat().st_size / 1024
            logger.info(f"💾 [AI GENERATOR] Saved AI recommendation: {output_file} ({file_size:.1f}KB)")
            
            # Log if structured data is available
            if recommendation_data.get("structured_recommendations"):
                logger.info(f"📊 [AI GENERATOR] Structured JSON data available for programmatic CV generation")
            
            # Register in DB (best-effort)
            try:
                from app.database import SessionLocal
                from app.services.file_registry_service import FileRegistryService
                db = SessionLocal()
                try:
                    registry = FileRegistryService.from_email(db, self.user_email)
                    company_id = registry.upsert_company(company, display_name=company.replace('_', ' '))
                    file_id = registry.register_file(company_id, "ai_recommendation", output_file, timestamp=timestamp)
                    registry.record_analysis_run(company_id, kind="ai_reco", output_file_id=file_id)
                    db.commit()
                finally:
                    db.close()
            except Exception as reg_err:
                logger.warning(f"⚠️ [DB] Failed to register AI recommendation: {reg_err}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving AI recommendation for {company}: {e}")
            return False
    
    def get_ai_recommendation_path(self, company: str) -> Path:
        """Get the path to AI recommendation file"""
        return self._get_output_file_path(company)
    
    def check_ai_recommendation_exists(self, company: str) -> bool:
        """Check if AI recommendation file exists"""
        company_dir = self.base_dir / "applied_companies" / company
        latest_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "json")
        return latest_file is not None and latest_file.exists()
    
    def list_companies_with_ai_recommendations(self) -> List[str]:
        """List all companies that have AI recommendation files"""
        companies = []
        
        try:
            applied_companies_dir = self.base_dir / "applied_companies"
            if not applied_companies_dir.exists():
                return companies
            
            for company_dir in applied_companies_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    latest_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_ai_recommendation", "json")
                    if latest_file and latest_file.exists():
                        companies.append(company_dir.name)
            
            logger.info(f"Found {len(companies)} companies with AI recommendations")
            return companies
            
        except Exception as e:
            logger.error(f"Error listing companies with AI recommendations: {e}")
            return companies
    
    async def batch_generate_recommendations(
        self, 
        companies: Optional[List[str]] = None, 
        force_regenerate: bool = False,
        max_concurrent: int = 3
    ) -> Dict[str, bool]:
        """Generate AI recommendations for multiple companies in batch"""
        if companies is None:
            companies = self._find_companies_with_prompts()
        
        logger.info(f"🔄 [AI GENERATOR] Starting batch AI recommendation generation for {len(companies)} companies")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(company: str) -> tuple[str, bool]:
            async with semaphore:
                success = await self.generate_ai_recommendation(company, force_regenerate)
                return company, success
        
        tasks = [generate_with_semaphore(company) for company in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch generation task failed: {result}")
                continue
            
            company, success = result
            final_results[company] = success
        
        successful_count = sum(1 for success in final_results.values() if success)
        logger.info(f"✅ [AI GENERATOR] Batch generation complete: {successful_count}/{len(companies)} successful")
        
        return final_results
    
    def _find_companies_with_prompts(self) -> List[str]:
        """Find all companies that have prompt files"""
        companies = []
        
        try:
            if not self.prompt_dir.exists():
                return companies
            
            for prompt_file in self.prompt_dir.glob("*_prompt_recommendation.py"):
                company_name = prompt_file.stem.replace("_prompt_recommendation", "")
                companies.append(company_name)
            
            return companies
            
        except Exception as e:
            logger.error(f"Error finding companies with prompts: {e}")
            return companies
    
    def get_ai_recommendation_info(self, company: str) -> Optional[Dict[str, Any]]:
        """Get information about an AI recommendation file"""
        try:
            ai_file = self._get_output_file_path(company)
            
            if not ai_file.exists():
                return None
            
            stat_info = ai_file.stat()
            
            with open(ai_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "company": company,
                "file_path": str(ai_file),
                "file_size": stat_info.st_size,
                "last_modified": stat_info.st_mtime,
                "content_length": len(data.get("recommendation_content", "")),
                "has_content": bool(data.get("recommendation_content", "").strip()),
                "has_structured_data": data.get("metadata", {}).get("has_structured_data", False),
                "generated_at": data.get("generated_at"),
                "ai_model": data.get("ai_model_info", {}).get("model")
            }
            
        except Exception as e:
            logger.error(f"Error getting AI recommendation info for {company}: {e}")
            return None

    def convert_txt_to_json(self, company: str) -> bool:
        """Convert existing TXT recommendation file to JSON format"""
        try:
            company_dir = self.base_dir / "applied_companies" / company
            
            txt_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "txt")
            if not txt_file:
                txt_file = company_dir / f"{company}_ai_recommendation.txt"
            
            json_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "json")
            if not json_file:
                json_file = company_dir / f"{company}_ai_recommendation.json"
            
            if not txt_file.exists():
                logger.error(f"TXT file not found: {txt_file}")
                return False
            
            with open(txt_file, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            
            json_data = {
                "company": company,
                "generated_at": datetime.fromtimestamp(txt_file.stat().st_mtime).isoformat(),
                "recommendation_content": txt_content,
                "ai_model_info": {
                    "provider": "unknown",
                    "model": "unknown",
                    "cost": 0.0,
                    "tokens_used": 0
                },
                "metadata": {
                    "content_length": len(txt_content),
                    "format_version": "1.0",
                    "converted_from_txt": True,
                    "has_structured_data": False
                }
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            file_size = json_file.stat().st_size / 1024
            logger.info(f"✅ [AI GENERATOR] Converted TXT to JSON: {json_file} ({file_size:.1f}KB)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error converting TXT to JSON for {company}: {e}")
            return False
    
    def batch_convert_txt_to_json(self) -> Dict[str, bool]:
        """Convert all existing TXT recommendation files to JSON format"""
        results = {}
        
        try:
            applied_companies_dir = self.base_dir / "applied_companies"
            if not applied_companies_dir.exists():
                return results
            
            for company_dir in applied_companies_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    txt_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_ai_recommendation", "txt")
                    if not txt_file:
                        txt_file = company_dir / f"{company_dir.name}_ai_recommendation.txt"
                    
                    json_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_ai_recommendation", "json")
                    if not json_file:
                        json_file = company_dir / f"{company_dir.name}_ai_recommendation.json"
                    
                    if txt_file.exists():
                        should_convert = not json_file.exists()
                        if json_file.exists():
                            should_convert = txt_file.stat().st_mtime > json_file.stat().st_mtime
                        
                        if should_convert:
                            success = self.convert_txt_to_json(company_dir.name)
                            results[company_dir.name] = success
                        else:
                            logger.info(f"Skipping {company_dir.name} - JSON file is up to date")
            
            successful_count = sum(1 for success in results.values() if success)
            logger.info(f"✅ [AI GENERATOR] Batch TXT to JSON conversion complete: {successful_count}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch TXT to JSON conversion: {e}")
            return results
    
    async def _trigger_cv_tailoring(self, company: str) -> bool:
        """Automatically trigger CV tailoring after AI recommendations are generated"""
        if not CV_TAILORING_AVAILABLE:
            logger.warning(f"⚠️ [AI GENERATOR] CV tailoring service not available for {company}")
            return False
        
        try:
            logger.info(f"🚀 [AI GENERATOR] Starting automatic CV tailoring for {company}")
            
            cv_tailoring_service = CVTailoringService(user_email=self.user_email)
            
            # load_real_cv_and_recommendation returns (OriginalCV, RecommendationAnalysis, is_tailored_cv)
            original_cv, recommendation, is_tailored_cv = cv_tailoring_service.load_real_cv_and_recommendation(company)
            
            from app.tailored_cv.models.cv_models import CVTailoringRequest
            
            request = CVTailoringRequest(
                original_cv=original_cv,
                recommendations=recommendation,
                custom_instructions="Auto-generated after AI recommendations",
                company_folder=None
            )
            
            response = await cv_tailoring_service.tailor_cv(request)
            
            if response.success:
                file_path = cv_tailoring_service.save_tailored_cv_to_analysis_folder(response.tailored_cv, company)
                logger.info(f"✅ [AI GENERATOR] Tailored CV saved automatically to {file_path}")
                logger.info(f"📊 [AI GENERATOR] Estimated ATS score: {response.tailored_cv.estimated_ats_score}")
                
                return True
            else:
                logger.error(f"❌ [AI GENERATOR] CV tailoring failed for {company}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [AI GENERATOR] Error during automatic CV tailoring for {company}: {e}")
            return False