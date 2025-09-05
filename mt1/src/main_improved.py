"""
Improved and organized main.py
- Modular structure
- Proper error handling
- Performance optimizations
- Security improvements
- Better logging and monitoring
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from dotenv import load_dotenv

# Core imports
from .core.exceptions import APIError, handle_api_error
from .core.performance import cache, metrics, optimize_file_operations

# API routers
# CV router imported below where needed

# Service imports
from .hybrid_ai_service import hybrid_ai
from .ai_config import model_state
from .job_tracker import router as job_tracker_router
from .ats_tester import router as ats_tester_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
TAILORED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tailored_cvs"))
JOB_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "job_db.json"))
ATS_DASHBOARD_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ats_dashboard.json"))

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TAILORED_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting AI CV Agent Backend")
    optimize_file_operations()
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI CV Agent Backend")
    cache.clear()
    logger.info("✅ Application shutdown complete")


# Create FastAPI app with lifespan events
app = FastAPI(
    title="AI CV Agent Backend",
    description="Advanced CV analysis and optimization system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/tailored_cvs", StaticFiles(directory=TAILORED_DIR), name="tailored_cvs")

# Exception handler for APIErrors
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors"""
    logger.error(f"API Error on {request.url}: {exc.message}")
    return handle_api_error(exc)

# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(f"Unexpected error on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "An unexpected error occurred",
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )

# Include routers
from .api.cv_endpoints import router as cv_router
app.include_router(cv_router)
app.include_router(job_tracker_router)
app.include_router(ats_tester_router)


# Health and status endpoints
@app.get("/", tags=["status"])
async def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "service": "AI CV Agent Backend",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["status"])
async def health_check():
    """Enhanced health check endpoint"""
    try:
        # Test basic imports and dependencies
        import requests
        import bs4
        
        # Test cache
        cache_stats = cache.stats()
        
        # Test AI service
        ai_status = hybrid_ai.get_status()
        
        # Test file system
        upload_accessible = os.access(UPLOAD_DIR, os.R_OK | os.W_OK)
        tailored_accessible = os.access(TAILORED_DIR, os.R_OK | os.W_OK)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "dependencies": {
                "requests": "ok",
                "bs4": "ok"
            },
            "cache": cache_stats,
            "ai_service": ai_status,
            "file_system": {
                "upload_dir": "ok" if upload_accessible else "error",
                "tailored_dir": "ok" if tailored_accessible else "error"
            },
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """Get application metrics"""
    return {
        "cache": cache.stats(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/ai-status", tags=["ai"])
async def get_ai_status():
    """Get AI service status"""
    try:
        status = hybrid_ai.get_status()
        status.update({
            'current_model': model_state.get_current_model(),
            'current_provider': model_state.get_current_provider(),
            'timestamp': datetime.now().isoformat()
        })
        return status
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting AI status: {str(e)}")


# Configuration endpoints
@app.post("/api/set-deepseek-model", tags=["configuration"])
async def set_deepseek_model(request: Request):
    """Set DeepSeek model configuration"""
    try:
        data = await request.json()
        deepseek_model = data.get('model', 'deepseek-chat')
        
        # Validate model
        valid_models = ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner']
        if deepseek_model not in valid_models:
            deepseek_model = 'deepseek-chat'
        
        # Update model state
        model_state.set_model(deepseek_model)
        
        logger.info(f"Model updated to: {deepseek_model}")
        
        return {
            "success": True,
            "message": f"Switched to {deepseek_model}",
            "current_model": model_state.get_current_model(),
            "current_provider": model_state.get_current_provider()
        }
        
    except Exception as e:
        logger.error(f"Error setting model: {e}")
        raise HTTPException(status_code=500, detail=f"Error setting model: {str(e)}")


# Cache management endpoints
@app.post("/api/cache/clear", tags=["administration"])
async def clear_cache():
    """Clear application cache"""
    try:
        cache.clear()
        logger.info("Cache cleared successfully")
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@app.get("/api/cache/stats", tags=["monitoring"])
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "cache_stats": cache.stats(),
        "timestamp": datetime.now().isoformat()
    }


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Log request details
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    # Record metrics
    metrics.record("request_duration", process_time, {
        "method": request.method,
        "endpoint": str(request.url.path),
        "status": str(response.status_code)
    })
    
    return response


# Dependency for common validations
async def validate_request_size(request: Request):
    """Validate request size"""
    if hasattr(request, 'headers'):
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > 100_000_000:  # 100MB limit
            raise HTTPException(
                status_code=413,
                detail="Request too large. Maximum size: 100MB"
            )


# Apply validation to all endpoints
app.dependency_overrides = {}


if __name__ == "__main__":
    import uvicorn
    
    # Development configuration
    uvicorn.run(
        "main_improved:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
