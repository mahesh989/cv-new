# JD Processing URL Test

## Overview

This test script (`test_jd_url.py`) tests the JD processing pipeline with a real URL from EthicalJobs.com.au.

## Test URL

**URL**: https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst

**Company**: Australia for UNHCR  
**Position**: Data Analyst

## How to Run

### Prerequisites

1. **Set API Key** (one of the following):
   ```bash
   export OPENAI_API_KEY="sk-..."
   # OR
   export ANTHROPIC_API_KEY="sk-ant-..."
   # OR
   export DEEPSEEK_API_KEY="sk-..."
   ```

2. **Optional**: Set provider and model
   ```bash
   export JD_TEST_LLM_PROVIDER="openai"  # or "anthropic" or "deepseek"
   export JD_TEST_LLM_MODEL="gpt-4o-mini"  # optional, uses default if not set
   ```

### Run the Test

```bash
cd /Users/mahesh/Documents/Github/cv-new
python test_jd_url.py
```

## What the Test Does

1. **Scrapes JD from URL** - Extracts job description text from the EthicalJobs URL
2. **Extracts Metadata** - Attempts to extract company name and job title
3. **Sets up AI Service** - Configures AI provider from environment variables
4. **Processes JD** - Runs the universal JD processing pipeline
5. **Saves Processed JD** - Creates `jd_processed_{timestamp}.json` file
6. **Verifies Output** - Checks that processed file exists and is properly formatted
7. **Displays Results** - Shows processing statistics and sample sections

## Expected Output

```
================================================================================
🧪 Testing JD Processing for URL
   https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst
================================================================================

📥 Step 1: Scraping job description from URL...
✅ Scraped JD successfully: 6014 characters

🔍 Step 2: Extracting job metadata...
✅ Extracted metadata:
   Company: Australia_for_UNHCR
   Job Title: Data Analyst

👤 Step 3: Setting up AI service...
✅ AI service configured: openai (gpt-4o-mini)

🔄 Step 4: Processing JD...
✅ JD processed successfully!
   Processing mode: universal_ai
   Sections: 8
   Length reduction: 6014 → 2788 chars (53% reduction)

📁 Step 5: Verifying processed JD file...
✅ Found processed JD file: jd_processed_20251125_102716.json
   File size: 12345 bytes
   Has sections: True
   Processing mode: universal_ai

📋 Step 6: Sample processed sections:
   • ROLE OVERVIEW & CONTEXT: Australia for UNHCR is seeking...
   • KEY RESPONSIBILITIES: Delivering analytics on...
   • TECHNICAL REQUIREMENTS: Minimum 2 years' experience...

✅ TEST COMPLETED SUCCESSFULLY!
```

## Output Files

The test creates files in:
```
/app/user/test@example.com/cv-analysis/applied_companies/Australia_for_UNHCR/
├── jd_processed_{timestamp}.json  # Processed JD with structured sections
```

## Troubleshooting

### No API Key Error
```
⚠️ Warning: Missing API key. Set the OPENAI_API_KEY environment variable.
```
**Solution**: Set one of the API key environment variables (see Prerequisites)

### Scraping Failed
```
❌ Failed to scrape JD from URL
```
**Solution**: Check internet connection and URL accessibility

### Processing Failed
```
❌ JD processing returned None
```
**Solution**: 
- Check API key is valid
- Check API key has sufficient credits
- Review error logs for details

## Test Results Summary

✅ **JD Scraping**: Successfully extracts 6014 characters from URL  
✅ **Metadata Extraction**: Extracts company and job title (with fallback)  
✅ **JD Processing**: Processes JD into structured sections  
✅ **File Creation**: Creates properly formatted JSON file  
✅ **Verification**: Validates file structure and content  

---

**Note**: This test uses a test user (`test@example.com`) and doesn't require database authentication. It directly uses environment variables for API keys, making it ideal for local testing.

