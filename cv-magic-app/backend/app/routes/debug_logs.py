"""
Debug Logs Streaming Endpoint
Streams backend logs to frontend for real-time debugging
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import logging
import json
import time
from pathlib import Path
from datetime import datetime

from app.core.dependencies import get_current_user
from app.models.auth import UserData
import asyncio

router = APIRouter(prefix="/api/debug", tags=["Debug Logs"])

logger = logging.getLogger(__name__)


def get_log_file_path() -> Optional[Path]:
    """Get path to backend log file"""
    try:
        backend_root = Path(__file__).resolve().parents[2]  # cv-magic-app/backend
        log_file = backend_root / "log.txt"
        if log_file.exists():
            return log_file
        
        # Also check Docker logs location
        docker_log = Path("/app/logs/backend_logs.txt")
        if docker_log.exists():
            return docker_log
        
        return None
    except Exception as e:
        logger.error(f"Error getting log file path: {e}")
        return None


@router.get("/logs/recent")
async def get_recent_logs(
    lines: int = 100,
    filter_keyword: Optional[str] = None,
    current_user: UserData = Depends(get_current_user)
):
    """
    Get recent backend logs
    
    Args:
        lines: Number of recent lines to return (default: 100, max: 1000)
        filter_keyword: Optional keyword to filter logs (e.g., "JD_PROCESSING")
    
    Returns:
        JSON with recent log lines
    """
    try:
        lines = min(lines, 1000)  # Cap at 1000 lines
        
        log_file = get_log_file_path()
        if not log_file:
            return {
                "success": False,
                "error": "Log file not found",
                "logs": []
            }
        
        # Read recent lines from log file
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            return {
                "success": False,
                "error": f"Error reading log file: {str(e)}",
                "logs": []
            }
        
        # Filter by keyword if provided
        if filter_keyword:
            recent_lines = [line for line in recent_lines if filter_keyword in line]
        
        # Format logs with timestamps
        formatted_logs = []
        for line in recent_lines:
            line = line.strip()
            if line:
                formatted_logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "message": line
                })
        
        return {
            "success": True,
            "total_lines": len(formatted_logs),
            "filter_keyword": filter_keyword,
            "logs": formatted_logs[-100:]  # Return last 100 filtered lines
        }
        
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        return {
            "success": False,
            "error": str(e),
            "logs": []
        }


@router.get("/logs/stream")
async def stream_logs(
    filter_keyword: Optional[str] = None,
    current_user: UserData = Depends(get_current_user)
):
    """
    Stream backend logs in real-time using Server-Sent Events (SSE)
    
    Args:
        filter_keyword: Optional keyword to filter logs (e.g., "JD_PROCESSING")
    
    Returns:
        StreamingResponse with SSE format
    """
    log_file = get_log_file_path()
    
    async def generate_log_stream():
        """Generator function for SSE streaming"""
        if not log_file:
            yield f"data: {json.dumps({'error': 'Log file not found'})}\n\n"
            return
        
        try:
            # Read file from end
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        line = line.strip()
                        if line:
                            # Filter by keyword if provided
                            if filter_keyword and filter_keyword not in line:
                                continue
                            
                            log_data = {
                                "timestamp": datetime.now().isoformat(),
                                "message": line
                            }
                            yield f"data: {json.dumps(log_data)}\n\n"
                    else:
                        # No new data, wait a bit
                        await asyncio.sleep(0.5)
                        
        except Exception as e:
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_log_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/logs/jd-processing")
async def get_jd_processing_logs(
    lines: int = 200,
    current_user: UserData = Depends(get_current_user)
):
    """
    Get JD processing specific logs (convenience endpoint)
    
    Returns:
        JSON with JD processing logs
    """
    return await get_recent_logs(lines=lines, filter_keyword="JD_PROCESSING", current_user=current_user)

