"""
Skills Analysis Routes

Extracted from main.py to provide better organization and maintainability
"""
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.auth import verify_token
from app.core.model_dependency import get_current_model
from app.services.skill_extraction import skill_extraction_service
from app.services.cv_content_service import cv_content_service
from app.services.skills_analysis_config import skills_analysis_config_service
from app.services.skill_extraction.prompt_templates import get_prompt as get_skill_prompt
from app.services.skill_extraction.response_parser import SkillExtractionParser
from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
from app.ai.ai_service import ai_service
from app.services.jd_analysis import analyze_and_save_company_jd
from app.services.cv_jd_matching import match_and_save_cv_jd
from pathlib import Path
import asyncio
import json
import re

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Skills Analysis"])


def _extract_match_rates_from_content(content: str) -> dict:
    """Extract match rates from preextracted comparison content"""
    rates = {
        "technical_skills": 0,
        "soft_skills": 0,
        "domain_keywords": 0,
        "overall": 0
    }
    
    try:
        # Extract overall match rate (new format)
        overall_match = re.search(r"Match Rate:\s*(\d+(?:\.\d+)?)%", content)
        if overall_match:
            rates["overall"] = int(float(overall_match.group(1)))
        
        # Extract from table format
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "Category" in line and "Match Rate" in line:
                # Found header, check next lines for data
                for j in range(i+1, min(i+10, len(lines))):
                    data_line = lines[j].strip()
                    if data_line:
                        # Try to parse table row
                        parts = [p.strip() for p in data_line.split()]
                        if len(parts) >= 6:  # Category, CV Total, JD Total, Matched, Missing, Match Rate
                            try:
                                category = parts[0].lower()
                                match_rate = float(parts[-1]) if parts[-1].replace('.', '').isdigit() else 0
                                
                                if "technical" in category:
                                    rates["technical_skills"] = int(match_rate)
                                elif "soft" in category:
                                    rates["soft_skills"] = int(match_rate)
                                elif "domain" in category:
                                    rates["domain_keywords"] = int(match_rate)
                            except:
                                pass
        
        # Legacy format support
        if rates["technical_skills"] == 0:
            tech_match = re.search(r"Technical Skills Match Rate:\s*(\d+)%", content)
            if tech_match:
                rates["technical_skills"] = int(tech_match.group(1))
        
        if rates["soft_skills"] == 0:
            soft_match = re.search(r"Soft Skills Match Rate:\s*(\d+)%", content)
            if soft_match:
                rates["soft_skills"] = int(soft_match.group(1))
        
        if rates["domain_keywords"] == 0:
            domain_match = re.search(r"Domain Keywords Match Rate:\s*(\d+)%", content)
            if domain_match:
                rates["domain_keywords"] = int(domain_match.group(1))
        
        # If overall not found, calculate it
        if rates["overall"] == 0 and any([rates["technical_skills"], rates["soft_skills"], rates["domain_keywords"]]):
            rates["overall"] = int((rates["technical_skills"] + rates["soft_skills"] + rates["domain_keywords"]) / 3)
    
    except Exception as e:
        logger.warning(f"Failed to extract match rates: {e}")
    
    return rates


def _detect_most_recent_company() -> Optional[str]:
    """Detect the most recent company folder in cv-analysis with a job_info_*.json or jd_original.txt.

    Returns the company folder name or None if not found.
    """
    try:
        base_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        if not base_path.exists():
            return None

        candidates = []
        for d in base_path.iterdir():
            if d.is_dir() and d.name != "Unknown_Company":
                if list(d.glob("job_info_*.json")) or (d / "jd_original.json").exists():
                    candidates.append(d)

        if not candidates:
            return None

        most_recent = max(candidates, key=lambda p: p.stat().st_mtime)
        return most_recent.name
    except Exception:
        return None


def _schedule_post_skill_pipeline(company_name: Optional[str]):
    """Fire-and-forget JD analysis and CV–JD match pipeline for the given company."""
    if not company_name:
        logger.warning("⚠️ [PIPELINE] No company detected; skipping JD analysis & CV–JD matching.")
        return

    logger.info(f"🚀 [PIPELINE] Scheduling JD analysis and CV–JD matching for '{company_name}'...")

    async def _run_pipeline(cname: str):
        """Run the complete analysis pipeline with error recovery"""
        pipeline_results = {
            "jd_analysis": False,
            "cv_jd_matching": False,
            "component_analysis": False
        }
        
        # Step 1: JD Analysis
        try:
            logger.info(f"🔧 [PIPELINE] Starting JD analysis for {cname}")
            await analyze_and_save_company_jd(cname, force_refresh=False)
            logger.info(f"✅ [PIPELINE] JD analysis saved for {cname}")
            pipeline_results["jd_analysis"] = True
        except Exception as e:
            logger.error(f"❌ [PIPELINE] JD analysis failed for {cname}: {e}")
            # Continue with next steps even if this fails

        # Step 2: CV-JD Matching
        try:
            logger.info(f"🔧 [PIPELINE] Starting CV–JD matching for {cname}")
            await match_and_save_cv_jd(cname, cv_file_path=None, force_refresh=False)
            logger.info(f"✅ [PIPELINE] CV–JD match results saved for {cname}")
            pipeline_results["cv_jd_matching"] = True
        except Exception as e:
            logger.error(f"❌ [PIPELINE] CV-JD matching failed for {cname}: {e}")
            # Log detailed error for debugging
            import traceback
            logger.error(f"[PIPELINE] CV-JD matching traceback: {traceback.format_exc()}")
            # Continue with component analysis even if matching fails

        # Step 3: Component Analysis (includes ATS calculation)
        try:
            logger.info(f"🔍 [PIPELINE] Starting component analysis for {cname}")
            from app.services.ats.modular_ats_orchestrator import modular_ats_orchestrator
            
            # Check if we have the minimum required files
            base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
            cv_file = base_dir / "cvs" / "original" / "original_cv.json"
            jd_file = base_dir / cname / "jd_original.json"
            skills_file = base_dir / cname / f"{cname}_skills_analysis.json"
            
            # We can run component analysis if we have CV, JD, and skills analysis
            if cv_file.exists() and jd_file.exists() and skills_file.exists():
                logger.info(f"📄 [PIPELINE] Required files found, proceeding with component analysis")
                component_result = await modular_ats_orchestrator.run_component_analysis(cname)
                logger.info(f"✅ [PIPELINE] Component analysis completed for {cname}")
                pipeline_results["component_analysis"] = True
                
                # Log extracted scores if available
                if isinstance(component_result, dict) and 'extracted_scores' in component_result:
                    scores = component_result['extracted_scores']
                    logger.info(f"📊 [PIPELINE] Component scores extracted: {len(scores)} scores")
                    # Log key scores
                    for key in ['skills_relevance', 'experience_alignment', 'industry_fit', 'role_seniority', 'technical_depth']:
                        if key in scores:
                            logger.info(f"📊 [PIPELINE] {key}: {scores[key]:.1f}")
                
                # Check if ATS was calculated
                if isinstance(component_result, dict) and 'ats_results' in component_result:
                    final_score = component_result['ats_results'].get('final_ats_score')
                    logger.info(f"🎯 [PIPELINE] ATS Score calculated: {final_score}")
            else:
                missing = []
                if not cv_file.exists(): missing.append("CV")
                if not jd_file.exists(): missing.append("JD")
                if not skills_file.exists(): missing.append("Skills")
                logger.warning(f"⚠️ [PIPELINE] Missing files for component analysis: {missing}")
                logger.info(f"🔄 [PIPELINE] Skipping component analysis for {cname} due to missing files")
                
        except Exception as component_error:
            logger.error(f"❌ [PIPELINE] Component analysis failed for {cname}: {component_error}")
            import traceback
            logger.error(f"[PIPELINE] Component analysis traceback: {traceback.format_exc()}")
        
        # Log pipeline summary
        successful_steps = [step for step, success in pipeline_results.items() if success]
        failed_steps = [step for step, success in pipeline_results.items() if not success]
        
        logger.info(f"📋 [PIPELINE] Pipeline summary for {cname}:")
        logger.info(f"   ✅ Successful: {successful_steps}")
        if failed_steps:
            logger.info(f"   ❌ Failed: {failed_steps}")
        else:
            logger.info(f"   🎉 All steps completed successfully!")

    try:
        asyncio.create_task(_run_pipeline(company_name))
    except Exception as e:
        logger.warning(f"⚠️ [PIPELINE] Failed to schedule background pipeline: {e}")

@router.post("/skill-extraction/analyze")
async def analyze_skills(request: Request):
    """Extract skills from CV and JD using AI with caching"""
    try:
        data = await request.json()
        
        # Extract parameters
        cv_filename = data.get("cv_filename")
        jd_url = data.get("jd_url")
        user_id = data.get("user_id", 1)
        force_refresh = data.get("force_refresh", False)
        config_name = data.get("config_name")  # Optional custom config
        
        # Validate required parameters
        if not cv_filename:
            return JSONResponse(
                status_code=400, 
                content={"error": "cv_filename is required"}
            )
        
        if not jd_url:
            return JSONResponse(
                status_code=400,
                content={"error": "jd_url is required"}
            )
        
        logger.info(f"🎯 Skill extraction request: CV={cv_filename}, JD_URL={jd_url}, USER={user_id}, CONFIG={config_name}")
        
        # Perform skill analysis using the service (no fallback)
        result = await skill_extraction_service.analyze_skills(
            cv_filename=cv_filename,
            jd_url=jd_url,
            user_id=user_id,
            force_refresh=force_refresh
        )

        # Fire-and-forget: run JD analysis and CV–JD matching pipeline in background
        company_name = _detect_most_recent_company()
        _schedule_post_skill_pipeline(company_name)
        
        return JSONResponse(content={
            "success": True,
            "message": "Skill extraction completed successfully",
            "config_used": config_name or "default",
            **result
        })
        
    except Exception as e:
        logger.error(f"❌ Skill extraction endpoint error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Skill extraction failed: {str(e)}"}
        )


@router.post("/preliminary-analysis")
async def preliminary_analysis(
    request: Request,
    current_model: str = Depends(get_current_model)
):
    """Preliminary skills analysis from CV filename and JD text"""
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        data = await request.json()
        
        # Extract parameters
        cv_filename = data.get("cv_filename")
        jd_text = data.get("jd_text")
        config_name = data.get("config_name")  # Optional custom config
        user_id = getattr(token_data, 'user_id', 1)
        
        # Validate required parameters
        if not cv_filename:
            return JSONResponse(
                status_code=400, 
                content={"error": "cv_filename is required"}
            )
        
        if not jd_text:
            return JSONResponse(
                status_code=400,
                content={"error": "jd_text is required"}
            )
        
        logger.info(f"🎯 Preliminary analysis request: CV={cv_filename}, JD_length={len(jd_text)}, CONFIG={config_name}")
        
        # Get CV content dynamically (no fallback)
        cv_content_result = cv_content_service.get_cv_content(cv_filename, user_id, use_fallback=False)
        if not cv_content_result["success"]:
            return JSONResponse(
                status_code=404,
                content={
                    "error": cv_content_result.get('error', 'CV content not found'),
                    "suggestions": cv_content_result.get('suggestions', []),
                    "filename": cv_filename
                }
            )
        
        cv_content = cv_content_result["content"]
        logger.info(f"Using CV content from {cv_content_result['source']} for {cv_filename} (length: {len(cv_content)})")
        
        # Perform skills analysis with configuration
        result = await perform_preliminary_skills_analysis(
            cv_content=cv_content,
            jd_text=jd_text,
            cv_filename=cv_filename,
            current_model=current_model,
            config_name=config_name,
            user_id=user_id
        )
        # Persist inputs for downstream pipeline and trigger JD analysis + CV–JD matching
        try:
            # Derive company from the actual saved path when available
            saved_path = result.get("saved_file_path")
            company_name = None
            if saved_path:
                try:
                    company_name = Path(saved_path).parent.name
                except Exception:
                    company_name = None

            # Fallback to detector if we couldn't extract from saved path
            if not company_name:
                company_name = _detect_most_recent_company()
                logger.info(f"🏢 [PIPELINE] (preliminary-analysis) fallback detected company: {company_name}")

            # If we have a company, ensure required files exist for the pipeline
            if company_name:
                base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
                company_dir = base_dir / company_name
                try:
                    company_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    # best-effort; continue
                    pass

                # Save JD content to jd_original.json for JD analyzer
                try:
                    import json
                    jd_file = company_dir / "jd_original.json"
                    with open(jd_file, 'w', encoding='utf-8') as f:
                        json.dump({"text": jd_text or "", "saved_at": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
                    logger.info(f"💾 [PIPELINE] (preliminary-analysis) JD JSON saved to: {jd_file}")
                except Exception as e:
                    logger.warning(f"⚠️ [PIPELINE] (preliminary-analysis) failed to save JD file: {e}")

                # Ensure original_cv.json exists for the matcher (but don't overwrite if it already exists with structured data)
                try:
                    import json
                    cv_file = base_dir / "cvs" / "original" / "original_cv.json"
                    
                    # Check if file exists and has structured data
                    should_save = True
                    if cv_file.exists():
                        try:
                            with open(cv_file, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                            # If file has structured CV data (not just text), don't overwrite it
                            if isinstance(existing_data, dict) and any(key in existing_data for key in ['personal_information', 'career_profile', 'skills', 'education', 'experience']):
                                logger.info(f"💾 [PIPELINE] (preliminary-analysis) Structured CV already exists, preserving it: {cv_file}")
                                should_save = False
                        except:
                            # If we can't read the file, we'll save the simple version
                            pass
                    
                    if should_save:
                        with open(cv_file, 'w', encoding='utf-8') as f:
                            json.dump({"text": cv_content or "", "saved_at": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
                        logger.info(f"💾 [PIPELINE] (preliminary-analysis) CV JSON saved to: {cv_file}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ [PIPELINE] (preliminary-analysis) failed to save CV file: {e}")

            logger.info(f"🚀 [PIPELINE] (preliminary-analysis) scheduling for company: {company_name}")
            _schedule_post_skill_pipeline(company_name)
        except Exception as e:
            logger.warning(f"⚠️ [PIPELINE] (preliminary-analysis) failed to schedule: {e}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else "Unknown error occurred"
        error_type = type(e).__name__
        traceback_info = traceback.format_exc()
        
        logger.error(f"❌ Preliminary analysis error ({error_type}): {error_msg}")
        logger.error(f"Traceback: {traceback_info}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Preliminary analysis failed ({error_type}): {error_msg}",
                "type": error_type
            }
        )


@router.get("/preliminary-analysis/cache")
async def get_cached_preliminary_analysis(request: Request):
    """Get cached preliminary analysis results"""
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        # For now, return no cached results (always perform fresh analysis)
        # This can be enhanced to implement actual caching
        return JSONResponse(content={"cached": False})
        
    except Exception as e:
        logger.error(f"❌ Cache retrieval error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve cache: {str(e)}"}
        )


@router.get("/preliminary-analysis/status")
async def get_preliminary_analysis_status(request: Request):
    """Get preliminary analysis status"""
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        # Return status information
        return JSONResponse(content={
            "status": "ready",
            "message": "Preliminary analysis service is available",
            "timestamp": datetime.now().isoformat(),
            "available_configs": list(skills_analysis_config_service.list_configs().keys())
        })
        
    except Exception as e:
        logger.error(f"❌ Status check error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to check status: {str(e)}"}
        )


@router.get("/skill-extraction/files")
async def list_analysis_files(company_name: Optional[str] = None):
    """List saved skill extraction analysis files"""
    try:
        files_info = skill_extraction_service.result_saver.list_saved_analyses(company_name)
        
        return JSONResponse(content={
            "success": True,
            "message": "Analysis files listed successfully",
            **files_info
        })
        
    except Exception as e:
        logger.error(f"❌ List analysis files error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list analysis files: {str(e)}"}
        )


@router.post("/trigger-component-analysis/{company}")
async def trigger_component_analysis(company: str):
    """Manually trigger component analysis for a specific company (for testing/debugging)"""
    try:
        logger.info(f"🔧 [MANUAL] Triggering component analysis for company: {company}")
        
        from app.services.ats.modular_ats_orchestrator import modular_ats_orchestrator
        
        # Check if required files exist
        base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        required_files = {
            "cv_file": base_dir / "cvs" / "original" / "original_cv.json",
            "jd_file": base_dir / company / "jd_original.json", 
            "match_file": base_dir / company / "cv_jd_match_results.json"
        }
        
        missing_files = {k: str(v) for k, v in required_files.items() if not v.exists()}
        if missing_files:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Missing required files for component analysis",
                    "missing_files": missing_files,
                    "company": company
                }
            )
        
        # Run component analysis
        result = await modular_ats_orchestrator.run_component_analysis(company)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Component analysis completed for {company}",
            "company": company,
            "extracted_scores": result.get("extracted_scores", {}),
            "timestamp": result.get("timestamp"),
            "total_scores": len(result.get("extracted_scores", {}))
        })
        
    except Exception as e:
        logger.error(f"❌ [MANUAL] Component analysis failed for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Component analysis failed: {str(e)}",
                "company": company
            }
        )


@router.post("/trigger-complete-pipeline/{company}")
async def trigger_complete_pipeline(company: str):
    """Manually trigger the complete analysis pipeline for a company (JD analysis → CV-JD matching → Component analysis → ATS calculation)"""
    try:
        logger.info(f"🚀 [MANUAL] Triggering complete pipeline for company: {company}")
        
        results = {
            "company": company,
            "steps": []
        }
        
        # Step 1: JD Analysis
        try:
            logger.info(f"🔧 [MANUAL] Step 1: JD Analysis for {company}")
            await analyze_and_save_company_jd(company, force_refresh=True)
            results["steps"].append({"step": "jd_analysis", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] JD Analysis failed: {e}")
            results["steps"].append({"step": "jd_analysis", "status": "failed", "error": str(e)})
            
        # Step 2: CV-JD Matching
        try:
            logger.info(f"🔧 [MANUAL] Step 2: CV-JD Matching for {company}")
            await match_and_save_cv_jd(company, cv_file_path=None, force_refresh=True)
            results["steps"].append({"step": "cv_jd_matching", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] CV-JD Matching failed: {e}")
            results["steps"].append({"step": "cv_jd_matching", "status": "failed", "error": str(e)})
            
        # Step 3: Component Analysis (includes ATS calculation)
        try:
            logger.info(f"🔧 [MANUAL] Step 3: Component Analysis for {company}")
            from app.services.ats.modular_ats_orchestrator import modular_ats_orchestrator
            component_result = await modular_ats_orchestrator.run_component_analysis(company)
            
            if isinstance(component_result, dict) and 'extracted_scores' in component_result:
                results["steps"].append({
                    "step": "component_analysis", 
                    "status": "success",
                    "scores_count": len(component_result.get('extracted_scores', {}))
                })
                
                # Check if ATS was calculated
                if 'ats_results' in component_result:
                    results["steps"].append({
                        "step": "ats_calculation",
                        "status": "success",
                        "final_score": component_result['ats_results'].get('final_ats_score')
                    })
            else:
                results["steps"].append({"step": "component_analysis", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] Component Analysis failed: {e}")
            results["steps"].append({"step": "component_analysis", "status": "failed", "error": str(e)})
        
        # Check final status
        all_success = all(step.get("status") == "success" for step in results["steps"])
        results["overall_status"] = "success" if all_success else "partial_failure"
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"❌ [MANUAL] Complete pipeline failed for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Pipeline failed: {str(e)}",
                "company": company
            }
        )


@router.post("/create-recommendation-file/{company}")
async def create_recommendation_file(company: str, force_update: bool = False):
    """Manually create or update a recommendation file for a company"""
    try:
        from app.services.ats_recommendation_service import ats_recommendation_service
        
        logger.info(f"🔧 [MANUAL] Creating recommendation file for company: {company}")
        
        # Check if company has ATS data first
        companies_with_ats = ats_recommendation_service.list_companies_with_ats_data()
        if company not in companies_with_ats:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No ATS calculation data found for this company",
                    "company": company,
                    "companies_with_ats": companies_with_ats
                }
            )
        
        # Create/update the recommendation file
        success = ats_recommendation_service.update_existing_recommendation(company, force_update)
        
        if success:
            recommendation_file = ats_recommendation_service.get_recommendation_file_path(company)
            return JSONResponse(content={
                "success": True,
                "message": f"Recommendation file created/updated for {company}",
                "company": company,
                "file_path": str(recommendation_file),
                "force_update": force_update
            })
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Failed to create recommendation file or no update needed",
                    "company": company,
                    "force_update": force_update
                }
            )
    
    except Exception as e:
        logger.error(f"❌ [MANUAL] Failed to create recommendation file for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to create recommendation file: {str(e)}",
                "company": company
            }
        )


@router.post("/batch-create-recommendations")
async def batch_create_recommendations(companies: Optional[List[str]] = None, force_update: bool = False):
    """Batch create recommendation files for multiple companies"""
    try:
        from app.services.ats_recommendation_service import ats_recommendation_service
        
        logger.info(f"🔧 [BATCH] Creating recommendation files - Force update: {force_update}")
        
        # Process companies
        results = ats_recommendation_service.batch_create_recommendations(companies, force_update)
        
        successful_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Batch recommendation creation completed",
            "results": results,
            "summary": {
                "successful": successful_count,
                "total": total_count,
                "failed": total_count - successful_count
            },
            "force_update": force_update
        })
    
    except Exception as e:
        logger.error(f"❌ [BATCH] Batch recommendation creation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Batch creation failed: {str(e)}"
            }
        )


@router.get("/recommendation-files")
async def list_recommendation_files():
    """List all companies with recommendation files"""
    try:
        from app.services.ats_recommendation_service import ats_recommendation_service
        
        base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        companies_with_recommendations = []
        
        if base_dir.exists():
            for company_dir in base_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    recommendation_file = ats_recommendation_service.get_recommendation_file_path(company_dir.name)
                    
                    if recommendation_file.exists():
                        # Get file info
                        stat_info = recommendation_file.stat()
                        
                        # Read the recommendation data
                        try:
                            with open(recommendation_file, 'r', encoding='utf-8') as f:
                                recommendation_data = json.load(f)
                            
                            ats_entries = recommendation_data.get("ats_calculation_entries", [])
                            latest_entry = ats_entries[-1] if ats_entries else {}
                            
                            companies_with_recommendations.append({
                                "company": company_dir.name,
                                "file_path": str(recommendation_file),
                                "file_size": stat_info.st_size,
                                "last_modified": stat_info.st_mtime,
                                "ats_score": latest_entry.get("final_ats_score"),
                                "category_status": latest_entry.get("category_status"),
                                "recommendation": latest_entry.get("recommendation")
                            })
                            
                        except Exception as e:
                            logger.warning(f"Could not read recommendation file for {company_dir.name}: {e}")
                            companies_with_recommendations.append({
                                "company": company_dir.name,
                                "file_path": str(recommendation_file),
                                "file_size": stat_info.st_size,
                                "last_modified": stat_info.st_mtime,
                                "error": "Could not read file contents"
                            })
        
        return JSONResponse(content={
            "success": True,
            "companies_with_recommendations": companies_with_recommendations,
            "total_count": len(companies_with_recommendations)
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to list recommendation files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to list recommendation files: {str(e)}"
            }
        )


@router.post("/create-ai-prompt/{company}")
async def create_ai_recommendation_prompt(company: str):
    """Create AI recommendation prompt file for a company"""
    try:
        from app.services.ats_recommendation_service import ats_recommendation_service
        
        logger.info(f"🤖 [AI PROMPT] Creating AI recommendation prompt for: {company}")
        
        # Check if recommendation file exists
        recommendation_file = ats_recommendation_service.get_recommendation_file_path(company)
        if not recommendation_file.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Recommendation file not found for this company",
                    "company": company,
                    "recommendation_file": str(recommendation_file),
                    "suggestion": "Create recommendation file first using /create-recommendation-file endpoint"
                }
            )
        
        # Create AI prompt file
        try:
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent.parent.parent
            sys.path.append(str(backend_path))
            
            from prompt.ai_recommendation_prompt_template import create_company_prompt_file
            prompt_file_path = create_company_prompt_file(company, str(recommendation_file))
            
            return JSONResponse(content={
                "success": True,
                "message": f"AI recommendation prompt created for {company}",
                "company": company,
                "prompt_file_path": prompt_file_path,
                "recommendation_file_path": str(recommendation_file)
            })
            
        except Exception as e:
            logger.error(f"❌ [AI PROMPT] Failed to create prompt for {company}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"Failed to create AI prompt: {str(e)}",
                    "company": company
                }
            )
    
    except Exception as e:
        logger.error(f"❌ [AI PROMPT] Error in create_ai_recommendation_prompt for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"API error: {str(e)}",
                "company": company
            }
        )


@router.get("/ai-prompt-files")
async def list_ai_prompt_files():
    """List all AI recommendation prompt files"""
    try:
        from pathlib import Path
        
        prompt_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/prompt")
        prompt_files = []
        
        if prompt_dir.exists():
            for prompt_file in prompt_dir.glob("*_prompt_recommendation.py"):
                # Extract company name from filename
                company_name = prompt_file.stem.replace("_prompt_recommendation", "")
                
                # Get file info
                stat_info = prompt_file.stat()
                
                # Try to extract ATS score from file content
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for ATS Score comment line
                    ats_score = "N/A"
                    for line in content.split('\n'):
                        if line.strip().startswith("# ATS Score:"):
                            ats_score = line.split(":")[1].strip()
                            break
                    
                    prompt_files.append({
                        "company": company_name,
                        "file_path": str(prompt_file),
                        "file_size": stat_info.st_size,
                        "last_modified": stat_info.st_mtime,
                        "ats_score": ats_score
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not read prompt file for {company_name}: {e}")
                    prompt_files.append({
                        "company": company_name,
                        "file_path": str(prompt_file),
                        "file_size": stat_info.st_size,
                        "last_modified": stat_info.st_mtime,
                        "error": "Could not read file contents"
                    })
        
        return JSONResponse(content={
            "success": True,
            "prompt_files": prompt_files,
            "total_count": len(prompt_files)
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to list AI prompt files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to list AI prompt files: {str(e)}"
            }
        )


@router.post("/generate-ai-recommendation/{company}")
async def generate_ai_recommendation(company: str, force_regenerate: bool = False):
    """Generate AI recommendation for a specific company"""
    try:
        from app.services.ai_recommendation_generator import ai_recommendation_generator
        
        logger.info(f"🤖 [API] Generating AI recommendation for: {company}")
        
        # Check if prompt file exists
        prompt_file = Path(f"/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/prompt/{company}_prompt_recommendation.py")
        if not prompt_file.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Prompt file not found for this company",
                    "company": company,
                    "prompt_file": str(prompt_file),
                    "suggestion": "Create recommendation and prompt files first"
                }
            )
        
        # Generate AI recommendation
        success = await ai_recommendation_generator.generate_ai_recommendation(company, force_regenerate)
        
        if success:
            ai_file = ai_recommendation_generator.get_ai_recommendation_path(company)
            ai_info = ai_recommendation_generator.get_ai_recommendation_info(company)
            
            return JSONResponse(content={
                "success": True,
                "message": f"AI recommendation generated for {company}",
                "company": company,
                "ai_file_path": str(ai_file),
                "file_info": ai_info,
                "force_regenerate": force_regenerate
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Failed to generate AI recommendation",
                    "company": company
                }
            )
    
    except Exception as e:
        logger.error(f"❌ [API] Error generating AI recommendation for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"API error: {str(e)}",
                "company": company
            }
        )


@router.post("/batch-generate-ai-recommendations")
async def batch_generate_ai_recommendations(
    companies: Optional[List[str]] = None, 
    force_regenerate: bool = False,
    max_concurrent: int = 2
):
    """Generate AI recommendations for multiple companies in batch"""
    try:
        from app.services.ai_recommendation_generator import ai_recommendation_generator
        
        logger.info(f"🚀 [BATCH API] Starting batch AI recommendation generation")
        logger.info(f"   Companies: {companies or 'All with prompts'}")
        logger.info(f"   Force regenerate: {force_regenerate}")
        logger.info(f"   Max concurrent: {max_concurrent}")
        
        # Generate recommendations
        results = await ai_recommendation_generator.batch_generate_recommendations(
            companies=companies,
            force_regenerate=force_regenerate,
            max_concurrent=max_concurrent
        )
        
        successful_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Batch AI recommendation generation completed",
            "results": results,
            "summary": {
                "successful": successful_count,
                "total": total_count,
                "failed": total_count - successful_count,
                "success_rate": f"{(successful_count/total_count*100):.1f}%" if total_count > 0 else "0%"
            },
            "settings": {
                "force_regenerate": force_regenerate,
                "max_concurrent": max_concurrent
            }
        })
    
    except Exception as e:
        logger.error(f"❌ [BATCH API] Batch AI recommendation generation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Batch generation failed: {str(e)}"
            }
        )


@router.get("/ai-recommendation-files")
async def list_ai_recommendation_files():
    """List all AI recommendation files"""
    try:
        from app.services.ai_recommendation_generator import ai_recommendation_generator
        
        companies_with_ai = ai_recommendation_generator.list_companies_with_ai_recommendations()
        ai_files_info = []
        
        for company in companies_with_ai:
            ai_info = ai_recommendation_generator.get_ai_recommendation_info(company)
            if ai_info:
                ai_files_info.append(ai_info)
        
        return JSONResponse(content={
            "success": True,
            "ai_recommendation_files": ai_files_info,
            "total_count": len(ai_files_info)
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to list AI recommendation files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to list AI recommendation files: {str(e)}"
            }
        )


@router.get("/ai-recommendation/{company}")
async def get_ai_recommendation(company: str):
    """Get AI recommendation content for a specific company"""
    try:
        from app.services.ai_recommendation_generator import ai_recommendation_generator
        
        ai_file = ai_recommendation_generator.get_ai_recommendation_path(company)
        
        if not ai_file.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "error": "AI recommendation not found for this company",
                    "company": company,
                    "ai_file_path": str(ai_file)
                }
            )
        
        # Read AI recommendation content
        with open(ai_file, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)
        
        return JSONResponse(content={
            "success": True,
            "company": company,
            "ai_recommendation": ai_data
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to get AI recommendation for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to get AI recommendation: {str(e)}",
                "company": company
            }
        )


@router.get("/skills-analysis/configs")
async def list_analysis_configs():
    """List available analysis configurations"""
    try:
        configs = skills_analysis_config_service.list_configs()
        
        return JSONResponse(content={
            "success": True,
            "configurations": configs,
            "total_count": len(configs)
        })
        
    except Exception as e:
        logger.error(f"❌ List configs error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list configurations: {str(e)}"}
        )


@router.get("/analysis-results")
async def list_companies_with_results():
    """List all companies that have analysis results"""
    try:
        base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        
        if not base_dir.exists():
            return JSONResponse(content={
                "success": True,
                "companies": []
            })
        
        companies = []
        for company_dir in base_dir.iterdir():
            if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                analysis_file = company_dir / f"{company_dir.name}_skills_analysis.json"
                if analysis_file.exists():
                    # Get basic info about the analysis
                    try:
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Check what analyses are available
                        analyses_available = {
                            "skills": bool(data.get("cv_skills") or data.get("jd_skills")),
                            "preextracted_comparison": bool(data.get("preextracted_comparison_entries")),
                            "component_analysis": bool(data.get("component_analysis_entries")),
                            "ats_calculation": bool(data.get("ats_calculation_entries"))
                        }
                        
                        # Get latest ATS score if available
                        ats_score = None
                        ats_entries = data.get("ats_calculation_entries", [])
                        if ats_entries:
                            ats_score = ats_entries[-1].get("final_ats_score")
                        
                        companies.append({
                            "name": company_dir.name,
                            "analyses_available": analyses_available,
                            "ats_score": ats_score,
                            "last_modified": analysis_file.stat().st_mtime
                        })
                    except Exception as e:
                        logger.warning(f"Failed to read analysis for {company_dir.name}: {e}")
        
        # Sort by last modified time (most recent first)
        companies.sort(key=lambda x: x["last_modified"], reverse=True)
        
        return JSONResponse(content={
            "success": True,
            "companies": companies,
            "total": len(companies)
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Failed to list companies with results: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list companies: {str(e)}"}
        )


@router.get("/analysis-results/{company}")
async def get_analysis_results(company: str):
    """Get complete analysis results for a company (skills, components, ATS) for frontend display"""
    try:
        logger.info(f"📊 [API] Fetching analysis results for company: {company}")
        
        # Build file path
        base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
        analysis_file = base_dir / company / f"{company}_skills_analysis.json"
        
        if not analysis_file.exists():
            return JSONResponse(
                status_code=404,
                content={"error": f"No analysis found for company: {company}"}
            )
        
        # Read analysis data
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract latest entries from each analysis type
        result = {
            "company": company,
            "skills_analysis": {
                "cv_skills": data.get("cv_skills", {}),
                "jd_skills": data.get("jd_skills", {})
            },
            "preextracted_comparison": None,
            "component_analysis": None,
            "ats_score": None
        }
        
        # Get latest preextracted comparison
        preextracted_entries = data.get("preextracted_comparison_entries", [])
        if preextracted_entries:
            latest = preextracted_entries[-1]
            # Parse the content to extract match rates
            content = latest.get("content", "")
            result["preextracted_comparison"] = {
                "timestamp": latest.get("timestamp"),
                "model_used": latest.get("model_used"),
                "raw_content": content,
                # Extract match rates from content using regex
                "match_rates": _extract_match_rates_from_content(content)
            }
        
        # Get latest component analysis
        component_entries = data.get("component_analysis_entries", [])
        if component_entries:
            latest = component_entries[-1]
            result["component_analysis"] = {
                "timestamp": latest.get("timestamp"),
                "extracted_scores": latest.get("extracted_scores", {}),
                "component_details": latest.get("component_analyses", {})
            }
        
        # Get latest ATS calculation
        ats_entries = data.get("ats_calculation_entries", [])
        if ats_entries:
            latest = ats_entries[-1]
            result["ats_score"] = latest
        
        # Get AI recommendation content if available
        ai_recommendation_file = base_dir / company / f"{company}_ai_recommendation.json"
        if ai_recommendation_file.exists():
            try:
                with open(ai_recommendation_file, 'r', encoding='utf-8') as f:
                    ai_data = json.load(f)
                result["ai_recommendation"] = {
                    "content": ai_data.get("recommendation_content"),
                    "generated_at": ai_data.get("generated_at"),
                    "model_info": ai_data.get("ai_model_info", {})
                }
            except Exception as e:
                logger.warning(f"Failed to load AI recommendation for {company}: {e}")
                result["ai_recommendation"] = None
        else:
            result["ai_recommendation"] = None
        
        return JSONResponse(content={
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Failed to get analysis results for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve analysis results: {str(e)}"}
        )


@router.post("/skills-analysis/configs")
async def create_analysis_config(request: Request):
    """Create a custom analysis configuration"""
    try:
        data = await request.json()
        
        config_name = data.get("name")
        if not config_name:
            return JSONResponse(
                status_code=400,
                content={"error": "Configuration name is required"}
            )
        
        # Create custom configuration
        config = skills_analysis_config_service.create_custom_config(
            config_name, 
            **{k: v for k, v in data.items() if k != "name"}
        )
        
        return JSONResponse(content={
            "success": True,
            "message": f"Configuration '{config_name}' created successfully",
            "config": skills_analysis_config_service._config_to_dict(config)
        })
        
    except Exception as e:
        logger.error(f"❌ Create config error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create configuration: {str(e)}"}
        )


async def perform_preliminary_skills_analysis(
    cv_content: str, 
    jd_text: str, 
    cv_filename: str, 
    current_model: str,
    config_name: Optional[str] = None,
    user_id: int = 1
) -> dict:
    """Perform preliminary skills analysis between CV and JD using AI prompts with detailed output"""
    try:
        # Get configuration
        config = skills_analysis_config_service.get_config(config_name)
        ai_params = skills_analysis_config_service.get_ai_parameters(config_name)
        logging_params = skills_analysis_config_service.get_logging_parameters(config_name)
        
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Starting AI-powered skills analysis for {cv_filename}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] CV content length: {len(cv_content)} chars")
            logger.info(f"🔍 [SKILLS_ANALYSIS] JD content length: {len(jd_text)} chars")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Using config: {config_name or 'default'}")
        
        # Get AI service instance
        from app.ai.ai_service import ai_service
        
        # Log current AI service status
        current_status = ai_service.get_current_status()
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI provider: {current_status.get('current_provider')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI model: {current_status.get('current_model')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Provider available: {current_status.get('provider_available')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Model from header: {current_model}")
        
        # Extract CV skills using enhanced structured prompt
        if logging_params["enable_detailed_logging"]:
            logger.info("🔍 [SKILLS_ANALYSIS] Extracting CV skills with detailed structured analysis...")
        
        cv_structured_prompt = get_skill_prompt('combined_structured', text=cv_content, document_type="CV")
        
        # Use configuration parameters
        cv_structured_response = await ai_service.generate_response(
            prompt=cv_structured_prompt,
            temperature=ai_params["temperature"],
            max_tokens=ai_params["max_tokens"]
        )
        cv_raw_response = cv_structured_response.content
        
        # Parse the structured response
        cv_parser = SkillExtractionParser()
        cv_parsed = cv_parser.parse_response(cv_raw_response, "CV")
        cv_technical_skills = cv_parsed.get('technical_skills', [])
        cv_soft_skills = cv_parsed.get('soft_skills', [])
        cv_domain_keywords = cv_parsed.get('domain_keywords', [])
        
        # Extract JD skills using enhanced structured prompt
        if logging_params["enable_detailed_logging"]:
            logger.info("🔍 [SKILLS_ANALYSIS] Extracting JD skills with detailed structured analysis...")
        
        jd_structured_prompt = get_skill_prompt('combined_structured', text=jd_text, document_type="Job Description")
        
        # Use configuration parameters
        jd_structured_response = await ai_service.generate_response(
            prompt=jd_structured_prompt,
            temperature=ai_params["temperature"],
            max_tokens=ai_params["max_tokens"]
        )
        jd_raw_response = jd_structured_response.content
        
        # Parse the structured response
        jd_parser = SkillExtractionParser()
        jd_parsed = jd_parser.parse_response(jd_raw_response, "JD")
        jd_technical_skills = jd_parsed.get('technical_skills', [])
        jd_soft_skills = jd_parsed.get('soft_skills', [])
        jd_domain_keywords = jd_parsed.get('domain_keywords', [])
        
        # Generate comprehensive analysis
        if logging_params["enable_detailed_logging"]:
            logger.info("🔍 [SKILLS_ANALYSIS] Using structured analysis as comprehensive analysis...")
        
        # Use the detailed structured responses as the comprehensive analysis
        cv_analysis = cv_raw_response
        jd_analysis = jd_raw_response
        
        # Debug logging
        if logging_params["enable_detailed_logging"]:
            logger.info(f"✅ [SKILLS_ANALYSIS] CV Technical Skills ({len(cv_technical_skills)}): {cv_technical_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] CV Soft Skills ({len(cv_soft_skills)}): {cv_soft_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] CV Domain Keywords ({len(cv_domain_keywords)}): {cv_domain_keywords}")
            logger.info(f"✅ [SKILLS_ANALYSIS] JD Technical Skills ({len(jd_technical_skills)}): {jd_technical_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] JD Soft Skills ({len(jd_soft_skills)}): {jd_soft_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] JD Domain Keywords ({len(jd_domain_keywords)}): {jd_domain_keywords}")
        
        result = {
            "cv_skills": {
                "technical_skills": cv_technical_skills,
                "soft_skills": cv_soft_skills,
                "domain_keywords": cv_domain_keywords
            },
            "jd_skills": {
                "technical_skills": jd_technical_skills,
                "soft_skills": jd_soft_skills,
                "domain_keywords": jd_domain_keywords
            },
            "cv_comprehensive_analysis": cv_analysis,
            "jd_comprehensive_analysis": jd_analysis,
            "expandable_analysis": {
                "cv_analysis": {
                    "title": "CV Analysis",
                    "content": cv_analysis,
                    "skills_summary": {
                        "technical": f"{len(cv_technical_skills)} technical skills",
                        "soft": f"{len(cv_soft_skills)} soft skills", 
                        "domain": f"{len(cv_domain_keywords)} domain keywords"
                    }
                },
                "jd_analysis": {
                    "title": "Job Description Analysis", 
                    "content": jd_analysis,
                    "skills_summary": {
                        "technical": f"{len(jd_technical_skills)} technical skills",
                        "soft": f"{len(jd_soft_skills)} soft skills",
                        "domain": f"{len(jd_domain_keywords)} domain keywords"
                    }
                }
            },
            "extracted_keywords": list(set(cv_technical_skills + jd_technical_skills + cv_soft_skills + jd_soft_skills + cv_domain_keywords + jd_domain_keywords)),
            "analysis_timestamp": datetime.now().isoformat(),
            "config_used": config_name or "default"
        }
        
        if logging_params["enable_detailed_logging"]:
            logger.info(f"✅ [SKILLS_ANALYSIS] Analysis completed successfully")
        
        # Save results to file if enabled
        file_params = skills_analysis_config_service.get_file_parameters(config_name)
        if file_params["save_analysis_results"]:
            try:
                result_saver = SkillExtractionResultSaver()
                
                # Get the most recent company folder (created during JD analysis)
                company_name = None
                if file_params["auto_detect_company"]:
                    try:
                        from pathlib import Path
                        cv_analysis_dir = Path("cv-analysis")
                        if cv_analysis_dir.exists():
                            # Find the most recently created company folder (excluding Unknown_Company)
                            company_folders = []
                            for company_folder in cv_analysis_dir.iterdir():
                                if (company_folder.is_dir() and 
                                    company_folder.name != "Unknown_Company" and
                                    list(company_folder.glob("job_info_*.json"))):
                                    company_folders.append(company_folder)
                            
                            if company_folders:
                                # Sort by creation time (most recent first)
                                most_recent_folder = max(company_folders, key=lambda p: p.stat().st_mtime)
                                company_name = most_recent_folder.name
                                if logging_params["enable_detailed_logging"]:
                                    logger.info(f"🏢 [COMPANY_DETECTION] Using most recent company folder: {company_name}")
                            else:
                                if logging_params["enable_detailed_logging"]:
                                    logger.warning(f"⚠️ [COMPANY_DETECTION] No valid company folders found")
                    except Exception as e:
                        if logging_params["enable_detailed_logging"]:
                            logger.warning(f"⚠️ [COMPANY_DETECTION] Failed to detect company folder: {e}")
                
                # Prepare data for saving (including the detailed raw responses)
                cv_skills_data = {
                    "technical_skills": cv_technical_skills,
                    "soft_skills": cv_soft_skills,
                    "domain_keywords": cv_domain_keywords,
                    "comprehensive_analysis": cv_analysis,
                    "raw_response": cv_raw_response if logging_params["log_raw_responses"] else ""
                }
                
                jd_skills_data = {
                    "technical_skills": jd_technical_skills,
                    "soft_skills": jd_soft_skills,
                    "domain_keywords": jd_domain_keywords,
                    "comprehensive_analysis": jd_analysis,
                    "raw_response": jd_raw_response if logging_params["log_raw_responses"] else ""
                }
                
                # Save to file with company name
                saved_file_path = result_saver.save_analysis_results(
                    cv_skills=cv_skills_data,
                    jd_skills=jd_skills_data,
                    jd_url="preliminary_analysis",
                    cv_filename=cv_filename,
                    user_id=user_id,
                    cv_comprehensive_analysis=cv_analysis,
                    jd_comprehensive_analysis=jd_analysis,
                    cv_data={"text": cv_content, "filename": cv_filename},
                    jd_data=None,
                    company_name=company_name
                )
                
                if logging_params["enable_detailed_logging"]:
                    logger.info(f"📁 [FILE_SAVE] Results saved to: {saved_file_path}")
                result["saved_file_path"] = saved_file_path
                
            except Exception as e:
                if logging_params["enable_detailed_logging"]:
                    logger.warning(f"⚠️ [FILE_SAVE] Failed to save results to file: {str(e)}")
                result["saved_file_path"] = None
        
        # NEW: Perform analyze match after skills analysis completes
        try:
            if logging_params["enable_detailed_logging"]:
                logger.info("🔍 [ANALYZE_MATCH] Starting analyze match assessment...")
            
            # Get analyze match prompt
            analyze_match_prompt = get_skill_prompt('analyze_match', cv_text=cv_content, job_text=jd_text)
            
            # Generate AI response for analyze match
            analyze_match_response = await ai_service.generate_response(
                prompt=analyze_match_prompt,
                temperature=0.3,
                max_tokens=4000
            )
            analyze_match_content = analyze_match_response.content
            
            if logging_params["enable_detailed_logging"]:
                logger.info(f"✅ [ANALYZE_MATCH] Analysis completed (length: {len(analyze_match_content)} chars)")
            
            # Save analyze match to the same file
            try:
                analyze_match_file_path = result_saver.append_analyze_match(analyze_match_content, company_name)
                if logging_params["enable_detailed_logging"]:
                    logger.info(f"📁 [ANALYZE_MATCH] Results appended to: {analyze_match_file_path}")
                result["analyze_match_file_path"] = analyze_match_file_path
            except Exception as e:
                if logging_params["enable_detailed_logging"]:
                    logger.warning(f"⚠️ [ANALYZE_MATCH] Failed to save analyze match: {str(e)}")
                result["analyze_match_file_path"] = None
            
            # Add analyze match to response
            result["analyze_match"] = {
                "raw_analysis": analyze_match_content,
                "company_name": company_name
            }
            
        except Exception as e:
            logger.error(f"❌ [ANALYZE_MATCH] Error in analyze match: {str(e)}")
            # Don't fail the entire request if analyze match fails
            result["analyze_match"] = {
                "error": f"Analyze match failed: {str(e)}",
                "raw_analysis": None
            }
        
        # NEW STEP: Pre-Extracted Skills Comparison (auto-trigger after Analyze Match)
        try:
            if logging_params["enable_detailed_logging"]:
                logger.info("🔍 [PREEXTRACTED_COMPARISON] Starting pre-extracted skills semantic comparison...")

            # Validate skill inputs before comparison
            if not cv_technical_skills and not cv_soft_skills and not cv_domain_keywords:
                raise ValueError("No CV skills extracted - cannot perform comparison")
            if not jd_technical_skills and not jd_soft_skills and not jd_domain_keywords:
                raise ValueError("No JD skills extracted - cannot perform comparison")

            # Build input skill lists from the parsed results above
            pre_cv_skills = {
                "technical_skills": cv_technical_skills,
                "soft_skills": cv_soft_skills,
                "domain_keywords": cv_domain_keywords
            }
            pre_jd_skills = {
                "technical_skills": jd_technical_skills,
                "soft_skills": jd_soft_skills,
                "domain_keywords": jd_domain_keywords
            }

            # Use centralized AI service with the exact provided prompt
            from app.services.skill_extraction.preextracted_comparator import execute_skills_semantic_comparison
            preextracted_output = await execute_skills_semantic_comparison(
                ai_service,
                cv_skills=pre_cv_skills,
                jd_skills=pre_jd_skills,
                temperature=ai_params["temperature"],
                max_tokens=min(ai_params["max_tokens"], 3000)
            )

            if logging_params["enable_detailed_logging"]:
                logger.info(f"✅ [PREEXTRACTED_COMPARISON] Completed (length: {len(preextracted_output)} chars)")

            # Append to the same analysis file (same as analyze match)
            try:
                pre_file_path = result_saver.append_preextracted_comparison(
                  preextracted_output,
                  company_name or "Unknown_Company",
                  result.get("saved_file_path")
                )
                if logging_params["enable_detailed_logging"]:
                    logger.info(f"📁 [PREEXTRACTED_COMPARISON] Results appended to: {pre_file_path}")
                result["preextracted_comparison_file_path"] = pre_file_path
            except Exception as e:
                logger.error(f"❌ [PREEXTRACTED_COMPARISON] Failed to append results: {str(e)}")
                result["preextracted_comparison_file_path"] = None

            # Include raw formatted analysis in response payload
            result["preextracted_skills_comparison"] = {
                "raw_output": preextracted_output,
                "company_name": company_name
            }

            # Note: Component analysis moved to run after skill comparison completes
            # (see _schedule_post_skill_pipeline function)
            result["component_analysis"] = {"status": "scheduled_after_skill_comparison"}

        except Exception as e:
            logger.error(f"❌ [PREEXTRACTED_COMPARISON] Error: {str(e)}")
            result["preextracted_skills_comparison"] = {
                "error": f"Pre-extracted comparison failed: {str(e)}",
                "raw_output": None
            }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ [SKILLS_ANALYSIS] Error in preliminary skills analysis: {str(e)}")
        raise e
