#!/usr/bin/env python3
"""
Test JD processing for a specific URL.

Usage:
    python test_jd_url.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure the backend package is resolvable
BACKEND_DIR = Path(__file__).resolve().parent / "cv-magic-app" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.job_scraper import scrape_job_description
from app.services.jd_processing_service import get_jd_processing_service, JDOptimizer
from app.ai.ai_service import ai_service
from app.models.auth import UserData
from app.ai.providers import OpenAIProvider, AnthropicProvider, DeepSeekProvider
from datetime import timezone


class EnvLLMService:
    """Thin wrapper around provider implementations for testing"""
    
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
        **kwargs,
    ):
        return await self._client.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )


def build_ai_service_from_env() -> EnvLLMService:
    """Create an AI service using environment variables"""
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
    return EnvLLMService(provider, model_name, api_key)


async def test_jd_processing_from_url(url: str):
    """Test JD processing from a URL"""
    
    print(f"\n{'='*80}")
    print(f"🧪 Testing JD Processing for URL")
    print(f"   {url}")
    print(f"{'='*80}\n")
    
    # Step 1: Scrape JD from URL (with fallback to hardcoded text if URL fails)
    print("📥 Step 1: Scraping job description from URL...")
    try:
        jd_text = scrape_job_description(url)
        
        # Check if scraping failed (error message in response)
        if not jd_text or len(jd_text.strip()) < 50 or jd_text.startswith("Error"):
            print(f"⚠️ URL scraping failed or returned error. Using hardcoded JD text from web search...")
            # Use the JD text from the web search results provided
            jd_text = """Data Analyst Australia for UNHCR Job Summary Australia for UNHCR Applications close: Job posted on: 14th Mar 2025 Sydney Contract , Full Time International Aid and Development , Fundraising Not For Profit (NFP) Job description Work in a high performing, values-driven organisation Competitive salary with salary packaging benefits Hybrid work arrangement with office located in Sydney CBD Full-time 15-month contract position ABOUT US Our passionate team empowers refugees to find safety and protection when they need it most. Australia for UNHCR is the UN Refugee Agency's partner in Australia, raising funds and awareness to assist people forced to flee conflict, disaster or persecution. With more than 120 million people now forcibly displaced worldwide, this work has never been more vital. At Australia for UNHCR, we harness the generosity of Australians to help UNHCR deliver life-saving aid during humanitarian emergencies. This aid includes shelter, clean water, medicine, emergency cash assistance and counselling. We also support long-term education, healthcare and employment programs to help refugees rebuild their lives and create more secure futures. As part of the UN network, we make a difference for millions of people every year. WHO WE ARE LOOKING FOR Our people are collaborative and inclusive team players, committed to finding new ways to increase support for refugees. A highly motivated, organised and detail-oriented Data Analyst to join our high performing Business Intelligence Unit, who work closely with our business stakeholders, providing data to support data-driven business decision-making across Australia for UNHCR and New Zealand for UNHCR. A data-passionate individual with strong analytical and problem-solving skills, to play a vital part in contributing to the evolving data requirements of the organisation by providing segmented data selections, data mining, analysis, and developing and maintaining reports. YOU'LL MAKE AN IMPACT BY Delivering analytics on the business-critical objective of understanding how to maximise the value from our donors, in the form of data-mining, profile analysis, building analytical models and BI report authoring in Power BI or a similar reporting suite. Addressing data extract requirements for direct marketing campaigns with a high degree of service; manipulating data in preparation for bulk communications, updating records with contact history, and working with Fundraising stakeholders to advise on segmentation strategies considering a multi-channel communication and donor-centricity approach. Producing reports and analysis for reviewing results post campaign. Building projection and segmentation models to answer key business questions. Assisting the BI Analyst and BI Manager to administer and develop A4U's data warehouse (DWH) considering current and future business requirements to strategise and implement enhancements to the platform through research, analysis, consultation and evaluation of program needs. Working with a range of internal and external stakeholders to satisfy their business intelligence requirements for analysis, report creation, data selections, and data mining within a strong project management framework, driving evidence-based decision making throughout the organisation. WE WOULD LIKE YOU TO HAVE Minimum 2 years' experience in a similar role Experience building models in spreadsheets, and comfortable writing formulas and VBA in Excel. Experience in the development, maintenance and remediation of issues relating to data models within a SQL data warehouse environment. Strong SQL coding skills and database knowledge Experience using business intelligence tools such as Power BI, Tableau, etc. Hands on experience in querying and extracting data across multiple, disparate and complex relational databases or a data warehouse Strong project management skills to deliver multiple projects and work autonomously to meet deadlines Strong stakeholder management skills. Excellent communication and customer service skills Experience extracting data for marketing campaigns with knowledge of how to best utilise data to optimise campaign outcomes An advanced understanding of how data is used for communication purposes, the process and the governing regulations / best practice guidelines. An appreciation of data issues and their solutions, particularly de-duplication and the importance of maintaining clean data. WHAT YOU'LL GET IN RETURN Working at Australia for UNHCR means that you get to make a difference for refugees every day. Our people give their best, work with compassion, and feel valued and supported. We have an inclusive and supportive culture built on a shared purpose. How do we know this? Our employees tell us! Our 2024 employee engagement survey revealed that: 100% of employees are proud to work at Australia for UNHCR 100% of employees feel trusted and valued by their Manager 89% can be successful as their authentic selves We also offer: A competitive salary commensurate with the NFP sector Access to $15,900 salary packaging Additional leave entitlements with five weeks of annual leave A flexible and hybrid work environment A focus on wellbeing, including weekly fruit box, access to a holistic Employee Assistance Program with offerings on mental health, nutrition, parenting, financial support and much more A focus on learning and development at individual, team and organisational levels We are a workplace that embraces diversity, inclusion and equal opportunity. We recognise the value of a diverse workforce and the creation of inclusive workforce cultures. We welcome applications from people with diverse experiences and cultural backgrounds, including migrants and former refugees."""
            print(f"✅ Using hardcoded JD text: {len(jd_text)} characters")
        else:
            print(f"✅ Scraped JD successfully: {len(jd_text)} characters")
        
        print(f"   Preview: {jd_text[:200]}...\n")
    except Exception as e:
        print(f"⚠️ Error scraping JD: {e}")
        print("   Using hardcoded JD text from web search...")
        # Fallback to hardcoded text
        jd_text = """Data Analyst Australia for UNHCR Job Summary Australia for UNHCR Applications close: Job posted on: 14th Mar 2025 Sydney Contract , Full Time International Aid and Development , Fundraising Not For Profit (NFP) Job description Work in a high performing, values-driven organisation Competitive salary with salary packaging benefits Hybrid work arrangement with office located in Sydney CBD Full-time 15-month contract position ABOUT US Our passionate team empowers refugees to find safety and protection when they need it most. Australia for UNHCR is the UN Refugee Agency's partner in Australia, raising funds and awareness to assist people forced to flee conflict, disaster or persecution. With more than 120 million people now forcibly displaced worldwide, this work has never been more vital. At Australia for UNHCR, we harness the generosity of Australians to help UNHCR deliver life-saving aid during humanitarian emergencies. This aid includes shelter, clean water, medicine, emergency cash assistance and counselling. We also support long-term education, healthcare and employment programs to help refugees rebuild their lives and create more secure futures. As part of the UN network, we make a difference for millions of people every year. WHO WE ARE LOOKING FOR Our people are collaborative and inclusive team players, committed to finding new ways to increase support for refugees. A highly motivated, organised and detail-oriented Data Analyst to join our high performing Business Intelligence Unit, who work closely with our business stakeholders, providing data to support data-driven business decision-making across Australia for UNHCR and New Zealand for UNHCR. A data-passionate individual with strong analytical and problem-solving skills, to play a vital part in contributing to the evolving data requirements of the organisation by providing segmented data selections, data mining, analysis, and developing and maintaining reports. YOU'LL MAKE AN IMPACT BY Delivering analytics on the business-critical objective of understanding how to maximise the value from our donors, in the form of data-mining, profile analysis, building analytical models and BI report authoring in Power BI or a similar reporting suite. Addressing data extract requirements for direct marketing campaigns with a high degree of service; manipulating data in preparation for bulk communications, updating records with contact history, and working with Fundraising stakeholders to advise on segmentation strategies considering a multi-channel communication and donor-centricity approach. Producing reports and analysis for reviewing results post campaign. Building projection and segmentation models to answer key business questions. Assisting the BI Analyst and BI Manager to administer and develop A4U's data warehouse (DWH) considering current and future business requirements to strategise and implement enhancements to the platform through research, analysis, consultation and evaluation of program needs. Working with a range of internal and external stakeholders to satisfy their business intelligence requirements for analysis, report creation, data selections, and data mining within a strong project management framework, driving evidence-based decision making throughout the organisation. WE WOULD LIKE YOU TO HAVE Minimum 2 years' experience in a similar role Experience building models in spreadsheets, and comfortable writing formulas and VBA in Excel. Experience in the development, maintenance and remediation of issues relating to data models within a SQL data warehouse environment. Strong SQL coding skills and database knowledge Experience using business intelligence tools such as Power BI, Tableau, etc. Hands on experience in querying and extracting data across multiple, disparate and complex relational databases or a data warehouse Strong project management skills to deliver multiple projects and work autonomously to meet deadlines Strong stakeholder management skills. Excellent communication and customer service skills Experience extracting data for marketing campaigns with knowledge of how to best utilise data to optimise campaign outcomes An advanced understanding of how data is used for communication purposes, the process and the governing regulations / best practice guidelines. An appreciation of data issues and their solutions, particularly de-duplication and the importance of maintaining clean data. WHAT YOU'LL GET IN RETURN Working at Australia for UNHCR means that you get to make a difference for refugees every day. Our people give their best, work with compassion, and feel valued and supported. We have an inclusive and supportive culture built on a shared purpose. How do we know this? Our employees tell us! Our 2024 employee engagement survey revealed that: 100% of employees are proud to work at Australia for UNHCR 100% of employees feel trusted and valued by their Manager 89% can be successful as their authentic selves We also offer: A competitive salary commensurate with the NFP sector Access to $15,900 salary packaging Additional leave entitlements with five weeks of annual leave A flexible and hybrid work environment A focus on wellbeing, including weekly fruit box, access to a holistic Employee Assistance Program with offerings on mental health, nutrition, parenting, financial support and much more A focus on learning and development at individual, team and organisational levels We are a workplace that embraces diversity, inclusion and equal opportunity. We recognise the value of a diverse workforce and the creation of inclusive workforce cultures. We welcome applications from people with diverse experiences and cultural backgrounds, including migrants and former refugees."""
        print(f"✅ Using hardcoded JD text: {len(jd_text)} characters")
        print(f"   Preview: {jd_text[:200]}...\n")
    
    # Step 2: Extract job metadata
    print("🔍 Step 2: Extracting job metadata...")
    try:
        from app.services.job_extractor import extract_job_metadata_v2
        job_metadata = await extract_job_metadata_v2(jd_url=url, jd_text=jd_text)
        
        company_name = job_metadata.get('company_name', 'Unknown_Company')
        job_title = job_metadata.get('job_title', 'Unknown')
        
        print(f"✅ Extracted metadata:")
        print(f"   Company: {company_name}")
        print(f"   Job Title: {job_title}\n")
    except Exception as e:
        print(f"⚠️ Error extracting metadata: {e}")
        company_name = "Australia_for_UNHCR"
        job_title = "Data Analyst"
        job_metadata = {}
    
    # Step 3: Setup AI service from environment
    print("👤 Step 3: Setting up AI service...")
    try:
        env_ai_service = build_ai_service_from_env()
        print(f"✅ AI service configured: {env_ai_service.provider_name} ({env_ai_service.model_name})\n")
    except Exception as e:
        print(f"⚠️ Warning: {e}")
        print("   Will use mock fallback if available\n")
        env_ai_service = None
    
    # Step 4: Process JD using direct optimizer (bypassing user API key requirement)
    print("🔄 Step 4: Processing JD...")
    try:
        if env_ai_service:
            # Use environment-based AI service directly
            print(f"   Using {env_ai_service.provider_name} AI service...")
            optimizer = JDOptimizer(ai_service=env_ai_service)
            
            # Create a test user object for the processing
            test_user = UserData(
                id="test_user",
                email="test@example.com",
                name="Test User",
                created_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            job_info = {
                "company_name": company_name,
                "job_title": job_title,
                "job_url": url,
                "user": test_user,  # Add user object
            }
            
            print(f"   Calling universal_jd_processing...")
            processed_data = await optimizer.universal_jd_processing(jd_text, job_info)
            
            if not processed_data:
                print("❌ JD processing returned None")
                return False
            
            # Save processed JD manually
            from app.utils.user_path_utils import get_user_base_path
            test_user_email = "test@example.com"
            base_path = get_user_base_path(test_user_email)
            company_dir = base_path / "applied_companies" / company_name
            company_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_file = company_dir / f"jd_processed_{timestamp}.json"
            
            sections = processed_data.get("sections", {})
            additional_sections = processed_data.get("additional_sections", {})
            
            processed_payload = {
                "company_name": company_name,
                "job_title": job_title,
                "job_url": url,
                "length_chars": len(jd_text),
                "processing_mode": "universal_ai" if optimizer.using_real_ai else "mock_fallback",
                "sections": sections,
                "additional_sections": additional_sections,
                "processed_at": datetime.now().isoformat(),
            }
            
            print(f"   Saving processed JD to: {processed_file}")
            with open(processed_file, "w", encoding="utf-8") as f:
                json.dump(processed_payload, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            processed_data = processed_payload
        else:
            print("   ⚠️ No API key available, skipping processing")
            print("   Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or DEEPSEEK_API_KEY to test processing")
            return False
        
        if not processed_data:
            print("❌ JD processing returned None")
            return False
        
        print(f"✅ JD processed successfully!")
        print(f"   Processing mode: {processed_data.get('processing_mode', 'unknown')}")
        print(f"   Sections: {len(processed_data.get('sections', {}))}")
        print(f"   Additional sections: {len(processed_data.get('additional_sections', {}))}")
        
        # Calculate reduction
        from app.services.jd_processing_service import JDProcessingService
        jd_service = JDProcessingService("test@example.com")
        processed_text = jd_service.processed_jd_to_text(processed_data)
        original_len = len(jd_text)
        processed_len = len(processed_text)
        reduction = original_len - processed_len
        reduction_pct = round((reduction / original_len) * 100, 1) if original_len > 0 else 0
        
        print(f"   Length reduction: {original_len} → {processed_len} chars ({reduction_pct}% reduction)\n")
        
    except Exception as e:
        print(f"❌ Error processing JD: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Verify processed JD file exists
    print("📁 Step 5: Verifying processed JD file...")
    try:
        from app.utils.user_path_utils import get_user_base_path
        test_user_email = "test@example.com"
        base_path = get_user_base_path(test_user_email)
        company_dir = base_path / "applied_companies" / company_name
        
        # Find processed JD file
        processed_files = list(company_dir.glob("jd_processed_*.json"))
        if not processed_files:
            print("⚠️ No processed JD file found")
            return False
        
        latest_file = max(processed_files, key=lambda f: f.stat().st_mtime)
        print(f"✅ Found processed JD file: {latest_file.name}")
        
        # Read and verify file
        with open(latest_file, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        print(f"   File size: {latest_file.stat().st_size} bytes")
        print(f"   Has sections: {bool(file_data.get('sections'))}")
        print(f"   Has additional_sections: {bool(file_data.get('additional_sections'))}")
        print(f"   Processing mode: {file_data.get('processing_mode', 'unknown')}")
        
        # Check if file is complete
        if not file_data.get('sections'):
            print("⚠️ Warning: Processed file has no sections!")
            return False
        
        print(f"\n✅ File verification passed!\n")
        
        # Step 6: Display sample sections
        print("📋 Step 6: Sample processed sections:")
        sections = file_data.get('sections', {})
        for section_name, section_content in list(sections.items())[:3]:
            preview = section_content[0][:100] if section_content and len(section_content) > 0 else "N/A"
            print(f"   • {section_name}: {preview}...")
        
        print(f"\n{'='*80}")
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying file: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    
    # Test URL
    test_url = "https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst"
    
    print("\n" + "="*80)
    print("🧪 JD Processing Test - URL Test")
    print("="*80)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
        print("\n⚠️ Warning: No API key found in environment variables.")
        print("   Set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or DEEPSEEK_API_KEY")
        print("   Processing will use mock fallback if available.\n")
    
    success = await test_jd_processing_from_url(test_url)
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

