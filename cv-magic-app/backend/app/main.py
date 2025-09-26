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
from app.routes.cv_structured import router as cv_structured_router
from app.routes.job_description import router as job_router
from app.routes.skills_analysis import router as skills_analysis_router
from app.routes.jd_analysis import router as jd_analysis_router
from app.routes.cv_jd_matching import cv_jd_matching_router
from app.routes.ai_recommendations import router as ai_recommendations_router
from app.tailored_cv.routes.cv_tailoring_routes import router as cv_tailoring_router
from app.routes.enhanced_skills_analysis import router as enhanced_skills_router  # New enhanced skills routes
from app.routes.saved_jobs import router as saved_jobs_router  # Saved jobs routes
from app.routes.api_keys import router as api_keys_router  # API key management routes

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
    public_endpoints = ["/api/auth/login", "/api/auth/register", "/api/auth/refresh-session", "/api/quick-login", "/health", "/api/info", "/api/ai/health", "/api/tailored-cv/save-edited"]
    
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
app.include_router(cv_structured_router)  # New structured CV routes
app.include_router(job_router)  # Job description routes
app.include_router(job_analysis_router)  # Job analysis routes
app.include_router(skills_analysis_router)  # Skills analysis routes
app.include_router(enhanced_skills_router)  # Enhanced skills analysis routes
app.include_router(jd_analysis_router)  # Job description analysis routes
app.include_router(cv_jd_matching_router)  # CV-JD matching routes
app.include_router(ai_recommendations_router, prefix="/api")  # AI recommendations routes
app.include_router(cv_tailoring_router, prefix="/api")  # CV tailoring routes
app.include_router(saved_jobs_router)  # Saved jobs routes
app.include_router(api_keys_router)  # API key management routes


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


# Skills analysis endpoints and functions moved to app/routes/skills_analysis.py
# This includes: skill extraction, preliminary analysis, caching, and file management


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
