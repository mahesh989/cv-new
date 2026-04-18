"""
Post-skill-extraction background pipeline.

After skills are extracted from a CV, this pipeline runs JD analysis,
CV-JD matching, component/ATS scoring, input recommendation creation,
AI recommendation generation, and tailored CV generation — all as a
fire-and-forget background task.
"""
import asyncio
import logging
import traceback
from typing import Optional

from app.utils.user_path_utils import get_user_base_path
from app.utils.timestamp_utils import TimestampUtils
from app.services.cv_jd_matching import match_and_save_cv_jd

logger = logging.getLogger(__name__)


def schedule_post_skill_pipeline(company_name: Optional[str], token_data=None) -> None:
    """Fire-and-forget: schedule the full post-skill pipeline for *company_name*."""
    if not company_name:
        logger.warning("[PIPELINE] No company detected; skipping post-skill pipeline.")
        return
    logger.info(f"[PIPELINE] Scheduling pipeline for '{company_name}'...")
    try:
        asyncio.create_task(run_pipeline(company_name, token_data))
    except Exception as e:
        logger.warning(f"[PIPELINE] Failed to schedule background pipeline: {e}")


async def run_pipeline(cname: str, token_data=None) -> None:
    """Execute the full 6-step post-analysis pipeline for *cname*."""
    results = {
        "jd_analysis": False,
        "cv_jd_matching": False,
        "component_analysis": False,
        "input_recommendation": False,
        "ai_recommendation": False,
        "tailored_cv": False,
    }

    user_email = getattr(token_data, "email", None) if token_data else None
    if not user_email:
        raise ValueError("User authentication required for pipeline operations")

    base_dir = get_user_base_path(user_email)

    # ── Step 1: JD Analysis ──────────────────────────────────────────────────
    jd_result = None
    try:
        logger.info(f"[PIPELINE] Step 1 – JD analysis for '{cname}'")
        from app.services.jd_analysis.jd_analyzer import JDAnalyzer
        analyzer = JDAnalyzer(user_email=user_email)
        jd_result_obj = await analyzer.analyze_and_save_company_jd(
            cname, force_refresh=True, base_path=str(base_dir)
        )
        jd_result = (
            jd_result_obj.model_dump()
            if hasattr(jd_result_obj, "model_dump")
            else jd_result_obj.__dict__
        )
        logger.info(f"[PIPELINE] Step 1 done – JD saved for '{cname}'")

        try:
            from app.services.jd_usage_tracker import JDUsageTracker
            tracker = JDUsageTracker(user_email)
            tracker.record_jd_usage(
                jd_result.get("jd_url", "") or "",
                jd_result.get("jd_text", "") or "",
                cname,
                jd_result.get("job_title", "") or "",
            )
        except Exception as e:
            logger.warning(f"[PIPELINE] JD usage tracking failed: {e}")

        results["jd_analysis"] = True
    except Exception as e:
        logger.error(f"[PIPELINE] Step 1 failed for '{cname}': {e}")

    # ── Step 2: CV-JD Matching ───────────────────────────────────────────────
    try:
        logger.info(f"[PIPELINE] Step 2 – CV-JD matching for '{cname}'")
        cv_txt_path = _resolve_cv_txt_path(cname, user_email)
        await match_and_save_cv_jd(
            cname,
            cv_file_path=cv_txt_path,
            force_refresh=True,
            jd_analysis_data=jd_result,
            user_email=user_email,
        )
        logger.info(f"[PIPELINE] Step 2 done – CV-JD match saved for '{cname}'")
        results["cv_jd_matching"] = True
    except Exception as e:
        logger.error(f"[PIPELINE] Step 2 failed for '{cname}': {e}")
        logger.debug(traceback.format_exc())

    # ── Step 3: Component / ATS Analysis ────────────────────────────────────
    try:
        logger.info(f"[PIPELINE] Step 3 – Component analysis for '{cname}'")
        from app.services.ats.modular_ats_orchestrator import get_modular_ats_orchestrator
        from app.unified_latest_file_selector import get_selector_for_user

        orchestrator = get_modular_ats_orchestrator(user_email=user_email)
        selector = get_selector_for_user(user_email)
        cv_text = selector.get_cv_content_across_all(cname)

        company_dir = base_dir / "applied_companies" / cname
        jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json") \
                  or company_dir / "jd_original.json"
        skills_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{cname}_skills_analysis", "json") \
                      or company_dir / f"{cname}_skills_analysis.json"

        if cv_text and jd_file.exists() and skills_file.exists():
            await orchestrator.run_component_analysis(cname, cv_text=cv_text)
            logger.info(f"[PIPELINE] Step 3 done – Component analysis completed for '{cname}'")
            results["component_analysis"] = True
        else:
            missing = (
                (["CV"] if not cv_text else [])
                + (["JD"] if not jd_file.exists() else [])
                + (["Skills"] if not skills_file.exists() else [])
            )
            logger.warning(f"[PIPELINE] Step 3 skipped – missing: {missing}")
    except Exception as e:
        logger.error(f"[PIPELINE] Step 3 failed for '{cname}': {e}")
        logger.debug(traceback.format_exc())

    # ── Step 4: Input Recommendation File ───────────────────────────────────
    try:
        logger.info(f"[PIPELINE] Step 4 – Input recommendation for '{cname}'")
        from app.services.ats_recommendation_service import ATSRecommendationService
        svc = ATSRecommendationService(user_email=user_email)
        results["input_recommendation"] = svc.create_recommendation_file(cname)
        if results["input_recommendation"]:
            logger.info(f"[PIPELINE] Step 4 done – Recommendation file created for '{cname}'")
        else:
            logger.warning(f"[PIPELINE] Step 4 – Failed to create recommendation file for '{cname}'")
    except Exception as e:
        logger.error(f"[PIPELINE] Step 4 failed for '{cname}': {e}")

    # ── Step 5: AI Recommendation Generation ────────────────────────────────
    if results["input_recommendation"]:
        try:
            logger.info(f"[PIPELINE] Step 5 – AI recommendation for '{cname}'")
            from app.services.ai_recommendation_generator import AIRecommendationGenerator
            gen = AIRecommendationGenerator(user_email=user_email)
            results["ai_recommendation"] = await gen.generate_ai_recommendation(cname, force_regenerate=False)
            if results["ai_recommendation"]:
                logger.info(f"[PIPELINE] Step 5 done – AI recommendation generated for '{cname}'")
            else:
                logger.warning(f"[PIPELINE] Step 5 – AI recommendation failed for '{cname}'")
        except Exception as e:
            logger.error(f"[PIPELINE] Step 5 failed for '{cname}': {e}")
    else:
        logger.info(f"[PIPELINE] Step 5 skipped – input recommendation failed for '{cname}'")

    # ── Step 6: Tailored CV ──────────────────────────────────────────────────
    if results["ai_recommendation"]:
        try:
            logger.info(f"[PIPELINE] Step 6 – Checking tailored CV for '{cname}'")
            company_dir = base_dir / "applied_companies" / cname
            ai_rec_file = None
            for pattern in [f"{cname}_ai_recommendation_*.json", f"{cname}_ai_recommendation.json"]:
                files = list(company_dir.glob(pattern))
                if files:
                    ai_rec_file = max(files, key=lambda f: f.stat().st_mtime)
                    break

            if ai_rec_file and ai_rec_file.exists():
                tailored_files = list((base_dir / "cvs" / "tailored").glob(f"{cname}_tailored_cv_*.txt"))
                results["tailored_cv"] = bool(tailored_files)
                if results["tailored_cv"]:
                    logger.info(f"[PIPELINE] Step 6 done – Tailored CV found for '{cname}'")
                else:
                    logger.warning(f"[PIPELINE] Step 6 – No tailored CV file found for '{cname}'")
            else:
                logger.warning(f"[PIPELINE] Step 6 – AI recommendation file missing for '{cname}'")
        except Exception as e:
            logger.error(f"[PIPELINE] Step 6 failed for '{cname}': {e}")
    else:
        logger.info(f"[PIPELINE] Step 6 skipped – AI recommendation failed for '{cname}'")

    # ── Summary ──────────────────────────────────────────────────────────────
    ok = [k for k, v in results.items() if v]
    fail = [k for k, v in results.items() if not v]
    logger.info(f"[PIPELINE] Summary for '{cname}': OK={ok}, FAILED={fail}")


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _resolve_cv_txt_path(company_name: str, user_email: str) -> Optional[str]:
    """Return the best available CV .txt path for *company_name*."""
    try:
        base = get_user_base_path(user_email)
        company_dir = base / "applied_companies" / company_name
        if company_dir.exists():
            candidates = list(company_dir.glob(f"{company_name}_tailored_cv_*.txt"))
            if candidates:
                return str(max(candidates, key=lambda p: p.stat().st_mtime))
        from app.unified_latest_file_selector import get_selector_for_user
        selector = get_selector_for_user(user_email)
        ctx = selector.get_latest_cv_across_all(company_name)
        return str(ctx.txt_path) if ctx and ctx.txt_path else None
    except Exception as e:
        logger.warning(f"[PIPELINE] Could not resolve CV txt path: {e}")
        return None
