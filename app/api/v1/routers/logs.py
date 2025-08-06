"""Log viewing endpoints."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from typing import Optional
import os
from app.core.logging import get_logger, get_latest_log_file

router = APIRouter(tags=["logs"])
logger = get_logger(__name__)


@router.get("/logs", response_class=PlainTextResponse)
async def get_logs(
    lines: Optional[int] = Query(100, description="Number of lines to return from the end of the file"),
    level: Optional[str] = Query(None, description="Filter by log level (ERROR, WARNING, INFO, DEBUG)")
):
    """
    Get the latest log entries.
    
    **Parameters:**
    - `lines`: Number of lines to return from the end of the file (default: 100)
    - `level`: Filter by log level (ERROR, WARNING, INFO, DEBUG)
    
    **Returns:**
    - Plain text log content
    """
    try:
        log_file = get_latest_log_file()
        if not log_file or not os.path.exists(log_file):
            raise HTTPException(status_code=404, detail="No log file found")
        
        # Read the log file
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # Filter by level if specified
        if level:
            level = level.upper()
            filtered_lines = [line for line in all_lines if f" - {level} - " in line]
            all_lines = filtered_lines
        
        # Get the last N lines
        if lines > 0:
            all_lines = all_lines[-lines:]
        
        return ''.join(all_lines)
        
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")


@router.get("/logs/download")
async def download_logs():
    """
    Download the latest log file.
    
    **Returns:**
    - Log file as attachment
    """
    try:
        log_file = get_latest_log_file()
        if not log_file or not os.path.exists(log_file):
            raise HTTPException(status_code=404, detail="No log file found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=log_file,
            filename=os.path.basename(log_file),
            media_type='text/plain'
        )
        
    except Exception as e:
        logger.error(f"Error downloading logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading logs: {str(e)}")