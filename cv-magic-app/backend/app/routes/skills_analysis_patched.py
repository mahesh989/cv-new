# The modified function with the fix:
async def perform_preliminary_skills_analysis(cv_content: str, jd_text: str, cv_filename: str, current_model: str, config_name: Optional[str] = None, user_id: Optional[int] = None):
    """Execute preliminary skills analysis with the specified configuration"""
    try:
        # Extract company name from JD text before analysis
        company = await _extract_company_name_from_jd(jd_text)
        logger.info(f"🏢 Using company name for skills analysis: {company}")

        # Ensure result saver has company info
        result_saver.current_company = company

        # Rest of the original function...

        # Save analyze match result if available (modified section)
        if analyze_match_output:
            try:
                # Use already extracted company name
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

        # Return original failure response if no analyze match output
        return {
            "success": False,
            "error": "Failed to generate analyze match output"
        }

    except Exception as e:
        logger.error(f"❌ Preliminary analysis failed: {str(e)}")
        raise e