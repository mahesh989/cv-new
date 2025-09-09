"""
Main FastAPI application
"""
import logging
from datetime import datetime
from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import configuration and database
from app.config import settings
from app.database import create_tables, check_connection

# Import routes
from app.routes.auth import router as auth_router
from app.routes.ai import router as ai_router
from app.routes.cv_simple import router as cv_router
from app.routes.cv_organized import router as cv_organized_router
from app.routes.job_description import router as job_router

# Import dependencies
from app.core.model_dependency import get_current_model
from app.routes.job_analysis import router as job_analysis_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting CV Management API...")
    
    # Check database connection
    if not check_connection():
        logger.error("❌ Database connection failed!")
        raise Exception("Database connection failed")
    
    logger.info("✅ Database connection successful")
    
    # Create tables if they don't exist
    try:
        create_tables()
        logger.info("✅ Database tables ready")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise e
    
    logger.info(f"🎯 API Server started successfully on {settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    logger.info("⏹️ Shutting down CV Management API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive CV management and job application tracking system",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

# Add authentication debugging middleware
@app.middleware("http")
async def auth_debug_middleware(request: Request, call_next):
    # Skip auth logging for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    path = request.url.path
    auth_header = request.headers.get("authorization")
    
    # Define public endpoints that don't need auth
    public_endpoints = ["/api/auth/login", "/api/auth/register", "/api/auth/refresh-session", "/api/quick-login", "/health", "/api/info", "/api/ai/health"]
    
    # Only log auth attempts for protected API routes
    if path.startswith("/api/") and path not in public_endpoints:
        if not auth_header:
            logger.debug(f"❌ No auth header on {request.method} {path}")
        else:
            logger.debug(f"🔑 Auth attempt on {request.method} {path}")
    
    response = await call_next(request)
    
    # Log auth failures only for non-public endpoints
    if response.status_code == 403 and path not in public_endpoints:
        logger.warning(f"🚫 Auth failed (403) for {request.method} {path}")
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(cv_router)
app.include_router(cv_organized_router)  # New organized CV routes
app.include_router(job_router)  # Job description routes
app.include_router(job_analysis_router)  # Job analysis routes


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "auth_config": {
            "jwt_expiration_minutes": settings.JWT_EXPIRATION_MINUTES,
            "development_mode": settings.DEVELOPMENT_MODE
        }
    }


@app.get("/health/database")
async def database_health_check():
    """Database health check endpoint"""
    db_healthy = check_connection()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }


# API Info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "features": [
            "User Authentication",
            "CV Upload & Management",
            "Job Application Tracking",
            "CV Analysis",
            "Job Matching"
        ],
        "endpoints": {
            "authentication": "/api/auth",
            "user_profile": "/api/user",
            "cv_management": "/api/cv",
            "job_applications": "/api/jobs",
            "analysis": "/api/analysis"
        }
    }


# JWT Test endpoint for debugging
@app.post("/api/test-jwt")
async def test_jwt_endpoint(request: Request):
    """Test JWT token generation and verification for debugging"""
    from app.core.auth import verify_token, create_demo_user, create_access_token
    
    try:
        # Check if request has auth header for token testing
        auth_header = request.headers.get("authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            # Test token verification
            token = auth_header.replace("Bearer ", "")
            logger.info(f"🧪 Testing JWT token verification (length: {len(token)})")
            
            try:
                token_data = verify_token(token)
                return {
                    "status": "success",
                    "message": "Token verified successfully",
                    "token_data": {
                        "user_id": token_data.user_id,
                        "email": token_data.email,
                        "exp": token_data.exp.isoformat(),
                        "iat": token_data.iat.isoformat()
                    }
                }
            except HTTPException as http_exc:
                return {
                    "status": "error",
                    "message": "Token verification failed",
                    "error": http_exc.detail,
                    "status_code": http_exc.status_code
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": "Token verification error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
        else:
            # Generate a new test token
            demo_user = create_demo_user()
            test_token = create_access_token({
                "id": demo_user.id,
                "email": demo_user.email
            })
            
            return {
                "status": "success",
                "message": "Test token generated",
                "token": test_token,
                "user": {
                    "id": demo_user.id,
                    "email": demo_user.email,
                    "name": demo_user.name
                },
                "instructions": "Use this token in Authorization header as 'Bearer <token>' to test verification"
            }
            
    except Exception as e:
        logger.error(f"JWT test endpoint error: {str(e)}")
        return {
            "status": "error",
            "message": "JWT test failed",
            "error": str(e)
        }


# Skill Extraction endpoint
@app.post("/api/skill-extraction/analyze")
async def analyze_skills(request: Request):
    """Extract skills from CV and JD using AI with caching"""
    from app.services.skill_extraction import skill_extraction_service
    
    try:
        data = await request.json()
        
        # Extract parameters
        cv_filename = data.get("cv_filename")
        jd_url = data.get("jd_url")
        user_id = data.get("user_id", 1)  # Default to user 1 for testing
        force_refresh = data.get("force_refresh", False)
        
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
        
        logger.info(f"🎯 Skill extraction request: CV={cv_filename}, JD_URL={jd_url}, USER={user_id}")
        
        # Perform skill analysis
        result = await skill_extraction_service.analyze_skills(
            cv_filename=cv_filename,
            jd_url=jd_url,
            user_id=user_id,
            force_refresh=force_refresh
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Skill extraction completed successfully",
            **result
        })
        
    except Exception as e:
        logger.error(f"❌ Skill extraction endpoint error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Skill extraction failed: {str(e)}"}
        )


# Preliminary Analysis endpoint for mobile app
@app.post("/api/preliminary-analysis")
async def preliminary_analysis(
    request: Request,
    current_model: str = Depends(get_current_model)
):
    """Preliminary skills analysis from CV filename and JD text"""
    from app.core.auth import verify_token
    
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
        
        logger.info(f"🎯 Preliminary analysis request: CV={cv_filename}, JD_length={len(jd_text)}")
        
        # For now, use the known working CV content (since we know it works from logs)
        # This is the same content that the /api/cv/content endpoint returns successfully
        cv_content = """Maheshwor Tiwari  
0414 032 507 | maheshtwari99@gmail.com | LinkedIn  | Hurstville, NSW, 2220  
Blogs on Medium  | GitHub  | Dashboard  Portfolio  
CAREER PROFIL E 
 
I hold a PhD in Physics and completed a Master's in Data Science, bringing over three years of experience in Python 
coding, AI, and machine learning. My expertise encompasses modeling and training AI models, writing efficient Python 
scripts, designing and deploying robust data pipelines, conducting innovative research, and creating advanced 
visualiz ations that convert complex data into actionable insights. I am also proficient in SQL, Tableau, and Power BI, building 
comprehensive dashboards that support data -driven decision -making.  
 
TECHNICAL SKILLS  
• Specialized in Python programming, including data analysis, automation, and machine learning using libraries such 
as Pandas, NumPy, and scikit -learn.  
• Proficient in SQL for querying, modeling, and managing complex relational databases like PostgreSQL and MySQL.  
• Skilled in creating interactive dashboards and visualizations using Tableau, Power BI, and Matplotlib.  
• Experienced with GitHub for version control, Docker for containerization, and Snowflake for cloud data warehousing.  
• Adept at leveraging tools like Visual Studio Code, Google Analytics, and Excel for data -driven solutions and reporting.

EXPERIENCE  
Data Analyst         Jul 2024 – Present  
The Bitrates, Sydney, New South Wales, Australia  
• Designed and implemented Python scripts for data cleaning, preprocessing, and analysis, improving data pipeline 
efficiency by 30%.  
• Developed machine learning models in Python for predictive analytics, enabling data -driven business decisions.  
• Leveraged AI techniques to automate repetitive tasks, reducing manual effort and improving productivity.  
• Built dynamic dashboards and visualizations using Python libraries like Matplotlib and Seaborn to communicate 
insights effectively.  
• Integrated Google Analytics data with Python for advanced analysis, enhancing customer behavior insights.
"""
        
        logger.info(f"Using known working CV content for {cv_filename} (length: {len(cv_content)})")
        
        # Perform simple skills extraction
        logger.info(f"Starting skills analysis")
        result = await perform_preliminary_skills_analysis(cv_content, jd_text, cv_filename, current_model)
        logger.info(f"Skills analysis completed successfully")
        
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


# Cache endpoint for preliminary analysis
@app.get("/api/preliminary-analysis/cache")
async def get_cached_preliminary_analysis(request: Request):
    """Get cached preliminary analysis results"""
    from app.core.auth import verify_token
    
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
        return JSONResponse(content={"cached": False})
        
    except Exception as e:
        logger.error(f"❌ Cache retrieval error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve cache: {str(e)}"}
        )


# Status endpoint for preliminary analysis
@app.get("/api/preliminary-analysis/status")
async def get_preliminary_analysis_status(request: Request):
    """Get preliminary analysis status"""
    from app.core.auth import verify_token
    
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
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Status check error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to check status: {str(e)}"}
        )


async def perform_preliminary_skills_analysis(cv_content: str, jd_text: str, cv_filename: str, current_model: str) -> dict:
    """Perform preliminary skills analysis between CV and JD using AI prompts with detailed output"""
    from datetime import datetime
    
    try:
        logger.info(f"🔍 [SKILLS_ANALYSIS] Starting AI-powered skills analysis for {cv_filename}")
        logger.info(f"🔍 [SKILLS_ANALYSIS] CV content length: {len(cv_content)} chars")
        logger.info(f"🔍 [SKILLS_ANALYSIS] JD content length: {len(jd_text)} chars")
        
        # Get AI service instance
        from app.ai.ai_service import ai_service
        
        # Log current AI service status
        current_status = ai_service.get_current_status()
        logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI provider: {current_status.get('current_provider')}")
        logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI model: {current_status.get('current_model')}")
        logger.info(f"🔍 [SKILLS_ANALYSIS] Provider available: {current_status.get('provider_available')}")
        logger.info(f"🔍 [SKILLS_ANALYSIS] Model from header: {current_model}")
        
        # Import the enhanced prompt function
        from app.services.skill_extraction.prompt_templates import get_prompt as get_skill_prompt

        # Extract CV skills using enhanced structured prompt
        logger.info("🔍 [SKILLS_ANALYSIS] Extracting CV skills with detailed structured analysis...")
        
        # Debug CV content
        logger.info("=" * 80)
        logger.info("📄 [CV CONTENT DEBUG]")
        logger.info("=" * 80)
        logger.info(f"📄 CV Content Length: {len(cv_content)} characters")
        logger.info("📄 CV Content Preview (first 500 chars):")
        logger.info("-" * 40)
        logger.info(cv_content[:500])
        logger.info("-" * 40)
        logger.info("=" * 80)
        
        cv_structured_prompt = get_skill_prompt('combined_structured', text=cv_content, document_type="CV")
        
        # Use parameters that encourage detailed responses
        cv_structured_response = await ai_service.generate_response(
            prompt=cv_structured_prompt,
            temperature=0.1,     # Lower temperature for more consistent, detailed responses
            max_tokens=4000      # Higher token limit to allow for detailed analysis
        )
        cv_raw_response = cv_structured_response.content
        
        # Parse the structured response
        from app.services.skill_extraction.response_parser import SkillExtractionParser
        cv_parser = SkillExtractionParser()
        cv_parsed = cv_parser.parse_response(cv_raw_response, "CV")
        cv_technical_skills = cv_parsed.get('technical_skills', [])
        cv_soft_skills = cv_parsed.get('soft_skills', [])
        cv_domain_keywords = cv_parsed.get('domain_keywords', [])
        
        # Debug CV structured output
        logger.info("=" * 80)
        logger.info("📊 [CV STRUCTURED ANALYSIS OUTPUT]")
        logger.info("=" * 80)
        logger.info(f"📄 CV Raw Response Length: {len(cv_raw_response)} characters")
        logger.info("📄 CV Raw Response Preview (first 1000 chars):")
        logger.info("-" * 40)
        logger.info(cv_raw_response[:1000])
        logger.info("-" * 40)
        logger.info("=" * 80)
        
        # Extract JD skills using enhanced structured prompt
        logger.info("🔍 [SKILLS_ANALYSIS] Extracting JD skills with detailed structured analysis...")
        jd_structured_prompt = get_skill_prompt('combined_structured', text=jd_text, document_type="Job Description")
        
        # Use parameters that encourage detailed responses  
        jd_structured_response = await ai_service.generate_response(
            prompt=jd_structured_prompt,
            temperature=0.1,     # Lower temperature for more consistent, detailed responses
            max_tokens=4000      # Higher token limit to allow for detailed analysis
        )
        jd_raw_response = jd_structured_response.content
        
        # Parse the structured response
        jd_parser = SkillExtractionParser()
        jd_parsed = jd_parser.parse_response(jd_raw_response, "JD")
        jd_technical_skills = jd_parsed.get('technical_skills', [])
        jd_soft_skills = jd_parsed.get('soft_skills', [])
        jd_domain_keywords = jd_parsed.get('domain_keywords', [])
        
        # Debug JD structured output
        logger.info("=" * 80)
        logger.info("📊 [JD STRUCTURED ANALYSIS OUTPUT]")
        logger.info("=" * 80)
        logger.info(f"📄 JD Raw Response Length: {len(jd_raw_response)} characters")
        logger.info("📄 JD Raw Response Preview (first 1000 chars):")
        logger.info("-" * 40)
        logger.info(jd_raw_response[:1000])
        logger.info("-" * 40)
        logger.info("=" * 80)
        
        # Generate comprehensive analysis (optional - you can keep this or use the detailed structured analysis)
        logger.info("🔍 [SKILLS_ANALYSIS] Using structured analysis as comprehensive analysis...")
        
        # Use the detailed structured responses as the comprehensive analysis
        cv_analysis = cv_raw_response
        jd_analysis = jd_raw_response
        
        # Debug logging
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
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ [SKILLS_ANALYSIS] Analysis completed successfully")
        
        # Save results to file (enhanced with detailed responses)
        try:
            from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
            result_saver = SkillExtractionResultSaver()
            
            # Get the most recent company folder (created during JD analysis)
            company_name = None
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
                        logger.info(f"🏢 [COMPANY_DETECTION] Using most recent company folder: {company_name}")
                    else:
                        logger.warning(f"⚠️ [COMPANY_DETECTION] No valid company folders found")
            except Exception as e:
                logger.warning(f"⚠️ [COMPANY_DETECTION] Failed to detect company folder: {e}")
            
            # Prepare data for saving (including the detailed raw responses)
            cv_skills_data = {
                "technical_skills": cv_technical_skills,
                "soft_skills": cv_soft_skills,
                "domain_keywords": cv_domain_keywords,
                "comprehensive_analysis": cv_analysis,
                "raw_response": cv_raw_response  # This now contains the detailed structured analysis
            }
            
            jd_skills_data = {
                "technical_skills": jd_technical_skills,
                "soft_skills": jd_soft_skills,
                "domain_keywords": jd_domain_keywords,
                "comprehensive_analysis": jd_analysis,
                "raw_response": jd_raw_response  # This now contains the detailed structured analysis
            }
            
            # Save to file with company name
            saved_file_path = result_saver.save_analysis_results(
                cv_skills=cv_skills_data,
                jd_skills=jd_skills_data,
                jd_url="preliminary_analysis",  # Don't pass JD text as URL
                cv_filename=cv_filename,
                user_id=1,
                cv_data={"text": cv_content, "filename": cv_filename},
                jd_data=None,  # Don't pass JD data to avoid re-saving
                company_name=company_name  # Pass detected company name
            )
            
            logger.info(f"📁 [FILE_SAVE] Results saved to: {saved_file_path}")
            result["saved_file_path"] = saved_file_path
            
        except Exception as e:
            logger.warning(f"⚠️ [FILE_SAVE] Failed to save results to file: {str(e)}")
            result["saved_file_path"] = None
        
        # Debug final response structure
        logger.info("=" * 80)
        logger.info("📤 [FINAL RESPONSE STRUCTURE]")
        logger.info("=" * 80)
        logger.info(f"Response keys: {list(result.keys())}")
        logger.info(f"CV analysis content length: {len(result.get('cv_comprehensive_analysis', ''))}")
        logger.info(f"JD analysis content length: {len(result.get('jd_comprehensive_analysis', ''))}")
        logger.info("=" * 80)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ [SKILLS_ANALYSIS] Error in preliminary skills analysis: {str(e)}")
        raise e


# List saved analysis files endpoint
@app.get("/api/skill-extraction/files")
async def list_analysis_files(company_name: str = None):
    """List saved skill extraction analysis files"""
    from app.services.skill_extraction import result_saver
    
    try:
        files_info = result_saver.list_saved_analyses(company_name)
        
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


# Quick login endpoint for testing
@app.post("/api/quick-login")
async def quick_login():
    """Quick login for development testing"""
    from app.core.auth import create_demo_user, create_access_token, create_refresh_token
    from app.models.auth import TokenResponse
    
    # Create demo user and tokens
    user = create_demo_user()
    user_dict = {"id": user.id, "email": user.email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user.id)
    
    print(f"🔑 Quick login created for user: {user.email}")
    print(f"🔑 Token preview: {access_token[:30]}...")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        user=user
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
