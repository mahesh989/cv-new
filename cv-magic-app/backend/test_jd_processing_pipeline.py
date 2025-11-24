#!/usr/bin/env python3
"""
Integration-style test for the JD processing pipeline.

This script now uses a real LLM provider (OpenAI/Anthropic/DeepSeek) by default.
Provide the corresponding API key via environment variables before running:

    export OPENAI_API_KEY="sk-..."
    python test_jd_processing_pipeline.py

Optional env overrides:
    JD_TEST_LLM_PROVIDER  -> openai (default), anthropic, or deepseek
    JD_TEST_LLM_MODEL     -> overrides the provider's default model
    JD_PIPELINE_ALLOW_MOCK -> set to "1" to fall back to rule-based mocks
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure the backend package is resolvable when running as a standalone script
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ai.providers import OpenAIProvider, AnthropicProvider, DeepSeekProvider


class EnvLLMService:
    """Thin wrapper around provider implementations so the pipeline can call `generate_response`."""

    _PROVIDER_CLASSES = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "deepseek": DeepSeekProvider,
    }

    def __init__(self, provider_name: str, model_name: str, api_key: str):
        provider_name = provider_name.lower()
        if provider_name not in self._PROVIDER_CLASSES:
            raise ValueError(f"Unsupported provider '{provider_name}'")

        provider_cls = self._PROVIDER_CLASSES[provider_name]
        self.provider_name = provider_name
        self.model_name = model_name
        self._client = provider_cls(api_key, model_name)

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ):
        return await self._client.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )


def build_ai_service_from_env() -> EnvLLMService:
    """Create an AI service using whichever provider has a configured API key."""

    provider = os.getenv("JD_TEST_LLM_PROVIDER", "openai").lower()
    provider_env_var = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
    }.get(provider)

    if not provider_env_var:
        raise ValueError(
            f"Unsupported provider '{provider}'. "
            "Set JD_TEST_LLM_PROVIDER to openai, anthropic, or deepseek."
        )

    api_key = os.getenv(provider_env_var)
    if not api_key:
        raise RuntimeError(
            f"Missing API key. Set the {provider_env_var} environment variable."
        )

    default_models = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022",
        "deepseek": "deepseek-chat",
    }

    model_name = os.getenv("JD_TEST_LLM_MODEL", default_models[provider])
    print(
        f"🧠 Using {provider} ({model_name}) via {provider_env_var}. "
        "Set JD_PIPELINE_ALLOW_MOCK=1 to force mock mode."
    )
    return EnvLLMService(provider_name=provider, model_name=model_name, api_key=api_key)


def _extract_json_content(content: str) -> str:
    """Strip optional markdown fences and return raw JSON string."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        # Drop opening fence
        if lines:
            lines = lines[1:]
        # Drop closing fence if present
        while lines and lines[-1].strip() == "":
            lines.pop()
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    return content


def _sections_to_text(sections: Dict[str, Any]) -> str:
    """Convert structured sections into a single display string."""
    parts: List[str] = []
    for section_name, items in sections.items():
        if not items:
            continue
        section_lines = [section_name]
        if isinstance(items, list):
            section_lines.extend(items)
        else:
            section_lines.append(str(items))
        section_block = "\n".join(line for line in section_lines if line)
        if section_block:
            parts.append(section_block)
    return "\n\n".join(parts).strip()


class JDOptimizer:
    """
    Universal JD optimizer that handles filtering + reorganization in one pass.
    """

    def __init__(self, ai_service: Optional[Any] = None):
        use_mock_fallback = os.getenv("JD_PIPELINE_ALLOW_MOCK", "0") == "1"
        if ai_service:
            self.ai_service = ai_service
            self.using_real_ai = True
        else:
            try:
                self.ai_service = build_ai_service_from_env()
                self.using_real_ai = True
            except Exception as exc:
                if use_mock_fallback:
                    print(
                        f"⚠️ Unable to initialize API LLM ({exc}). "
                        "Falling back to mock processing."
                    )
                    self.ai_service = None
                    self.using_real_ai = False
                else:
                    raise

    async def universal_jd_processing(self, jd_text: str, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Single AI call that handles filtering + reorganization for any JD format.
        """

        universal_prompt = f"""
        **ROLE**: You are an expert Job Description Processor with 10+ years experience in HR tech and recruitment.

        **TASK**: Process this job description through TWO phases:

        ---

        ### **PHASE 1: CONTENT PRESERVATION FILTERING**

        **REMOVE ONLY THESE ELEMENTS**:
        - Salary figures, compensation details, bonus structures
        - Specific employee benefits (health insurance, gym memberships, free meals, etc.)
        - Application instructions ("click apply", "send email", "submit resume")
        - Contact information (email addresses, phone numbers, physical addresses)
        - Equal employment opportunity statements (unless they specify role requirements)
        - Employee testimonials or satisfaction survey results
        - Company stock performance or growth metrics
        - Office amenities and physical workspace descriptions
        - Generic "about our culture" statements that don't relate to job performance
        - Repetitive company background information

        **PRESERVE EVERYTHING ELSE**:
        - All job responsibilities and daily tasks
        - All required/preferred skills (technical, soft, domain-specific)
        - All experience requirements (years, specific background, industries)
        - All educational qualifications and certifications
        - Reporting structure and team information
        - Work arrangement (remote, hybrid, office location)
        - Tools, technologies, and software requirements
        - Performance expectations and success metrics
        - Industry/domain knowledge requirements
        - Project examples or portfolio requirements
        - Travel requirements or physical demands
        - Security clearances or background check requirements
        - Language proficiency requirements

        ---

        ### **PHASE 2: INTELLIGENT REORGANIZATION**

        **REORGANIZE INTO THESE SECTIONS** (create only sections that have content):
        1. **ROLE OVERVIEW & CONTEXT**
        2. **KEY RESPONSIBILITIES**
        3. **TECHNICAL REQUIREMENTS**
        4. **EXPERIENCE REQUIREMENTS**
        5. **QUALIFICATIONS & EDUCATION**
        6. **SOFT SKILLS & COMPETENCIES**
        7. **DOMAIN KNOWLEDGE**
        8. **WORK ARRANGEMENT**

        ---

        **CRITICAL RULES**:
        1. **PRESERVE EXACT PHRASING** - Never paraphrase or summarize requirements
        2. **REMOVE ONLY VERBATIM DUPLICATES** - Keep similar concepts if phrased differently
        3. **MAINTAIN ORIGINAL INTENT** - Don't lose nuance in requirements
        4. **CREATE NEW SECTIONS** if content doesn't fit standard categories
        5. **WHEN IN DOUBT, KEEP IT** - Better to have extra content than lose requirements
        6. **RESPECT JD STRUCTURE** - If JD has unique sections, preserve their intent
        7. **MAINTAIN TECHNICAL PRECISION** - Especially for engineering/medical/legal roles

        ---

        **INPUT JOB DESCRIPTION**:
        {jd_text}

        ---

        **OUTPUT FORMAT**:
        Return ONLY a JSON object (no markdown fences) in this structure:
        {{
            "sections": {{
                "ROLE OVERVIEW & CONTEXT": ["paragraph 1", "paragraph 2"],
                "KEY RESPONSIBILITIES": ["- bullet 1", "- bullet 2"],
                ...
            }},
            "additional_sections": {{
                "CUSTOM SECTION NAME": ["items if any"]
            }}
        }}

        - Use arrays of strings for each section so content stays exactly as in the JD.
        - Omit empty sections entirely.
        """

        if self.ai_service:
            response = await self.ai_service.generate_response(
                universal_prompt,
                system_prompt=(
                    "You are a universal JD processor that handles any format, industry, or structure. "
                    "Your goal is to preserve all meaningful job requirements while removing only true noise. "
                    "Adapt to the input format rather than forcing a specific output structure."
                ),
                temperature=0.1,
                max_tokens=4000,
            )
            parsed = self._parse_processed_response(response.content)
            return parsed
        return await self._mock_universal_processing(jd_text)

    def _parse_processed_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM response into structured sections."""
        raw = _extract_json_content(content)
        try:
            payload = json.loads(raw)
            if "sections" not in payload or not isinstance(payload["sections"], dict):
                raise ValueError("Missing sections key")
            return payload
        except Exception:
            # Fallback to wrapping raw text
            return {
                "sections": {
                    "RAW_OUTPUT": [content.strip()]
                }
            }

    async def _mock_universal_processing(self, jd_text: str) -> Dict[str, Any]:
        """
        Conservative mock fallback when no API provider is available.
        """

        lines = jd_text.split("\n")
        filtered_lines = []

        obvious_noise = [
            "please click",
            "[email protected]",
            "http://",
            "www.",
            "apply now",
            "submit your",
            "send your",
            "equal opportunity",
            "diversity and inclusion",
            "what you'll get",
            "benefits include",
            "salary:",
            "compensation:",
            "bonus",
            "stock options",
        ]

        filtered_block: List[str] = []
        for line in lines:
            line_lower = line.lower()
            if not any(noise in line_lower for noise in obvious_noise):
                filtered_block.append(line)
            elif len(line.strip()) > 50:
                filtered_block.append(line)

        filtered_text = "\n".join(filtered_block).strip()
        return {
            "sections": {
                "ROLE OVERVIEW & CONTEXT": [filtered_text] if filtered_text else []
            }
        }


class JDProcessingPipeline:
    """
    Main pipeline for processing job descriptions
    """

    def __init__(self, base_dir: str, ai_service: Optional[Any] = None):
        self.base_dir = Path(base_dir)
        self.optimizer = JDOptimizer(ai_service)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def process_job_description(
        self, jd_text: str, company_name: str, job_title: str, job_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main processing pipeline - universal single-pass processing
        """

        company_slug = company_name.lower().replace(" ", "_").replace("/", "_")
        company_dir = self.base_dir / company_slug
        company_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        job_info = {
            "company_name": company_name,
            "job_title": job_title,
            "job_url": job_url,
            "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        original_file = company_dir / f"jd_original_{timestamp}.json"
        with open(original_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    **job_info,
                    "length_chars": len(jd_text),
                    "text": jd_text,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"✅ Phase 0: Original JD saved ({len(jd_text)} chars)")

        processed_data = await self.optimizer.universal_jd_processing(jd_text, job_info)
        sections = processed_data.get("sections", {})
        processed_text = _sections_to_text(sections)
        processed_file = company_dir / f"jd_processed_{timestamp}.json"
        processing_mode = "universal_ai" if self.optimizer.using_real_ai else "mock_fallback"
        processed_payload = {
            **job_info,
            "length_chars": len(processed_text),
            "processing_mode": processing_mode,
            "sections": sections,
        }
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(processed_payload, f, ensure_ascii=False, indent=2)

        print(
            f"✅ Universal Processing: Final JD saved ({len(processed_text)} chars, "
            f"{len(jd_text) - len(processed_text)} chars removed)"
        )

        return {
            "original_file": str(original_file),
            "processed_file": str(processed_file),
            "stats": {
                "original_chars": len(jd_text),
                "processed_chars": len(processed_text),
                "reduction_percent": round((1 - len(processed_text) / len(jd_text)) * 100, 1),
                "processing_mode": processing_mode,
            },
        }


UNHCR_JD_TEXT = """
Software Engineer (React/Node/AWS)
52 Victoria St, McMahons Point NSW 2060, Australia
Full-time
Company Description
Drive is Nine’s brand appealing to the automotive enthusiast. Working with our industry leaders you will help us achieve our vision, to shape the future of automotive in Australia by providing authoritative reviews, detailed comparisons, and innovative commerce solutions.

2025 is an exciting year to be part of the Drive Marketplace team. Drive Marketplace is on a sharp growth trajectory with a vision to become Australia’s No.2 Automotive Marketplace in Australia.  

The expanding Drive Marketplace team has an ambitious, forward-thinking and highly collaborative culture, with a shared passion for the automotive industry. As the on-the-ground human faces of the Drive brand within the National Drive Dealer Network, genuine partnerships and a healthy dose of hard work and fun sit at the core of the team’s success to date.
Job Description
Drive is looking for a Full Stack Developer to join our team in Sydney. Reporting to the Senior Engineering Manager and working closely with a Technical Lead, this is a hands-on, mid-level role. You'll be a key individual contributor, helping to plan, design, and execute technical solutions and improvements to our product and platform. You will also help set standards and lead on matters of architecture, development, documentation, quality, and application performance.

Day to day you will:

Deliver key tasks each sprint as a hands-on developer.
Architect solutions that are automated, reliable, performant, and cost-efficient.
Mentor junior and offshore developers, providing guidance on architecture, code quality, and performance.
Ensure coding conventions, review processes, and test coverage processes are followed.
Participate in and provide input on feasibility, effort, and risk in product or business settings.
Craft and run Proof of Concepts (POCs) to de-risk complex items.
Suggest, scope, and implement improvements to the performance, cost, quality, or security of the Drive stack
 
Qualifications
What you'll bring:

Experience: 6+ years of hands-on development experience in a Full Stack environment with Typescript, Node, and React.
Education: A Bachelor's degree or better in Computer Science or a related discipline.
Cloud & DevOps: Experience developing/maintaining applications with at least one cloud vendor like AWS or GCP. You'll also have a practical understanding of key DevOps principles like
Automation, CI/CD, and Observability.
Methodology: An understanding of Agile development processes and practices such as backlog planning, grooming, and retrospectives.
Communication: Excellent written and verbal communication skills, with experience coaching and mentoring other developers.
Architecture: Experience building high-traffic systems that are secure, available, scalable, and cost-efficient, with a practical understanding of a framework like AWS's Well-Architected Framework.
Databases: Hands-on experience implementing solutions on top of SQL and NoSQL databases.
Nice to Have

Experience measuring and improving front-end performance using tools like Lighthouse and Web Vitals.
Experience measuring and improving API performance using tools like Cloudwatch.
Experience with frameworks such as
Serverless or SST for developing APIs and standalone applications.
Comfort using an ORM system like
Sequelize or Prisma.
What We Offer:

Flexible Work Arrangement: Enjoy a hybrid working model requiring 3 days in the office.
High-Calibre Team: Join a high-performing team known for its great culture and collaborative spirit.
Career Growth: Be an integral part of a fast-growing, dynamic business with ample opportunities for development.
Additional Information
Our Commitment to Diversity and Inclusion:

We're committed to a safe, respectful and inclusive Nine. From day one, you'll be encouraged to bring your whole self to work and will be supported to perform at your best.

We encourage applications from Aboriginal and Torres Strait Islander people, people with disabilities, and of all ages, genders, nationalities, backgrounds and cultures as we recognise the importance and value of diverse perspectives. Should you require any adjustments to the recruitment process, please advise us when you apply.

Work rights: Please note to apply for this role you must already have the right to lawfully work and live in Australia.
"""


async def main():
    """Test the JD processing pipeline with hardcoded JD text"""

    print("🚀 Starting JD Processing Pipeline Test...")

    pipeline = JDProcessingPipeline("./test_output")

    result = await pipeline.process_job_description(
        jd_text=UNHCR_JD_TEXT,
        company_name="Australia for UNHCR",
        job_title="Data Analyst",
        job_url="https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst",
    )

    print("\n📊 Processing Results:")
    print(f"Original file: {result['original_file']}")
    print(f"Processed file: {result['processed_file']}")
    print(f"Stats: {json.dumps(result['stats'], indent=2)}")

    with open(result["processed_file"], "r", encoding="utf-8") as f:
        processed_payload = json.load(f)
        processed_sections = processed_payload.get("sections", {})
        processed_content = _sections_to_text(processed_sections)

        print("\n📝 Sample of processed content (first 500 chars):")
        print((processed_content[:500] + "...") if processed_content else "[empty]")
        if processed_sections:
            first_section = next(iter(processed_sections.items()))
            print(f"\nFirst section: {first_section[0]} -> {first_section[1][:2]}")


if __name__ == "__main__":
    asyncio.run(main())

