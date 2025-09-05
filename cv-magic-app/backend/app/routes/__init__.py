# Routes package
"""
Enhanced route modules for the CV analysis application
"""

try:
    from .cv_enhanced import router as cv_enhanced_router
    from .jd_enhanced import router as jd_enhanced_router  
    from .analysis_enhanced import router as analysis_enhanced_router
    
    __all__ = [
        "cv_enhanced_router",
        "jd_enhanced_router", 
        "analysis_enhanced_router"
    ]
except ImportError as e:
    print(f"Enhanced routes not available: {e}")
    __all__ = []
