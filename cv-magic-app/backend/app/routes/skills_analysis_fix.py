"""
Fix for company name missing error in analyze match saving process.

This fix ensures that company name is always provided when saving analyze match results.
"""

# ... Rest of the original file content ...

# Replace the section in the perform_preliminary_skills_analysis function with this:
async def perform_preliminary_skills_analysis(cv_content: str, jd_text: str, cv_filename: str, current_model: str, config_name: Optional[str] = None, user_id: Optional[int] = None):
    """Execute preliminary skills analysis with the specified configuration"""
    try:
        # ... Rest of the function ...

        # When saving analyze match results, ensure company name is provided
        if analyze_match_output:
            # Get company name from saved file path or extract from JD
            company = ""
            try:
                saved_path = result.get("saved_file_path")
                if saved_path:
                    company = Path(saved_path).parent.name
                    logger.info(f"🏢 [ANALYZE_MATCH] Using company from saved path: {company}")
            except Exception:
                pass

            if not company:
                company = await _extract_company_name_from_jd(jd_text)
                logger.info(f"🏢 [ANALYZE_MATCH] Extracted company from JD: {company}")

            try:
                # Save analyze match results with company name
                saved_path = await result_saver.append_analyze_match(analyze_match_output, company)
                logger.info(f"✅ [ANALYZE_MATCH] Results saved to: {saved_path}")
                
                response_data = {
                    "success": True, 
                    "analyze_match": analyze_match_output,
                    "company": company,
                    "saved_path": saved_path
                }
            except Exception as save_err:
                logger.error(f"❌ [ANALYZE_MATCH] Failed to save results: {save_err}")
                response_data = {
                    "success": True,
                    "analyze_match": analyze_match_output,
                    "error": f"Failed to save results: {str(save_err)}"
                }
            return JSONResponse(content=response_data)

        # ... Rest of the error handling ...