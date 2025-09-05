"""
Main FastAPI application
"""
import logging
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import configuration and database
from app.config import settings
from app.database import create_tables, check_connection

# Import routes
from app.routes.auth import router as auth_router
from app.routes.ai import router as ai_router

# Import simple routes for CV and JD processing
try:
    from app.routes.cv_simple import router as cv_router
    from app.routes.jd_simple import router as jd_router
    from app.routes.flutter_compat import router as flutter_router
    simple_routes_available = True
except ImportError as e:
    logger.warning(f"Simple routes not available: {e}")
    simple_routes_available = False

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
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


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

# Include simple routers if available
if simple_routes_available:
    app.include_router(cv_router)
    app.include_router(jd_router)
    app.include_router(flutter_router)  # Flutter-compatible routes
    logger.info("✅ Simple CV, JD, and Flutter-compatible routes enabled")
else:
    logger.info("⚠️ Simple routes disabled due to import errors")


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
        "version": settings.APP_VERSION
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


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
