"""Import endpoints for test cases."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import json
from typing import Optional
import asyncio

from app.schemas.responses import AsyncImportResponse, AsyncImportStatusResponse
from app.services.azure_devops_token import AzureDevOpsTokenService
from app.services.test_case_service import TestCaseService
from app.services.background_tasks import task_manager
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(tags=["imports"])
logger = get_logger(__name__)


@router.post("/import/async", response_model=AsyncImportResponse)
async def import_versioned_test_cases_async(
    file: UploadFile = File(...),
    project_name: str = Form(...),
    token: str = Form(...),
    version: str = Form(...)
):
    """
    Import test cases from JSON file with version management (Async).
    
    This endpoint starts a background task and returns immediately with a task ID.
    Use the status endpoint to check progress and get results.
    
    **Version Management Logic:**
    - **Major** (مثل 3.0.1 → 4.0.0): همیشه **تست پلن جدید** ساخته می‌شود
    - **Minor** (مثل 3.0.1 → 3.1.0): همیشه **تست پلن جدید** ساخته می‌شود  
    - **Patch** (مثل 3.0.1 → 3.0.2): از **همان test plan موجود** استفاده می‌شود و **محتوای جدید** به آن اضافه می‌شود
    - **Same** (مثل 3.0.1 با خودش): محتوای تست پلن موجود **به‌روزرسانی** می‌شود
    
    **Authentication:**
    - NTLM: Use format `username:password` (e.g., `RPK\\ASadeghianAzar:iLAus1101`)
    - Basic Auth: Use format `:PAT` (e.g., `:your_personal_access_token_here`)
    """
    logger.info(f"Starting async import for project: {project_name}, version: {version}")
    
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and parse JSON file
        content = await file.read()
        try:
            json_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
        
        # Initialize services
        azure_service = AzureDevOpsTokenService(
            org_url=settings.azure_devops_org_url,
            project_name=project_name,
            token=token,
            api_version=settings.azure_devops_api_version
        )
        
        # Check connection
        if not azure_service.check_connection():
            raise HTTPException(
                status_code=401,
                detail="Failed to connect to Azure DevOps. Please check your credentials."
            )
        
        # Create background task
        task_id = task_manager.create_task(
            "import_versioned",
            project_name=project_name,
            version=version,
            token=token
        )
        
        # Immediately update status to 'starting' with initial progress
        task_manager.update_task_status(task_id, 'starting', 0, log="Task created and initializing...")
        
        # Start background task
        import_service = TestCaseService(azure_service)
        asyncio.create_task(
            task_manager.run_import_task(task_id, import_service, json_data, project_name, version)
        )
        
        # Give a moment for task to actually start
        await asyncio.sleep(0.1)  # Small delay to ensure task begins
        
        return AsyncImportResponse(
            task_id=task_id,
            status="started",
            message="Import task started successfully. Use the status endpoint to check progress."
        )
        
    except ValueError as e:
        logger.error(f"Version parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid version format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in async import: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/import/status/{task_id}", response_model=AsyncImportStatusResponse)
async def get_import_status(task_id: str):
    """
    Get the status of an async import task.
    
    Returns the current status, progress, and results if completed.
    Always returns immediately with current status.
    """
    logger.info(f"Checking status for task: {task_id}")
    
    status = task_manager.get_task_status(task_id)
    if not status:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    logger.info(f"Task status: {status.status}, progress: {status.progress}%")
    
    # Always return status immediately, regardless of completion
    return status


@router.get("/import/debug/tasks")
async def debug_tasks():
    """Debug endpoint to see all tasks"""
    tasks = task_manager.tasks
    return {
        "total_tasks": len(tasks),
        "tasks": [
            {
                "id": task_id,
                "status": task_info.get('status'),
                "progress": task_info.get('progress'),
                "created_at": str(task_info.get('created_at'))
            }
            for task_id, task_info in tasks.items()
        ]
    }


@router.get("/import/debug/version/{project_name}/{version}")
async def debug_version_management(project_name: str, version: str):
    """
    Debug endpoint to test version management logic.
    """
    try:
        from app.core.version_utils import parse_version, compare_versions
        from app.services.azure_devops_token import AzureDevOpsTokenService
        from app.services.test_case_service import TestCaseService
        
        # Initialize services
        azure_service = AzureDevOpsTokenService(
            org_url=settings.azure_devops_org_url,
            project_name=project_name,
            token="test",  # Not used for this debug
            api_version=settings.azure_devops_api_version
        )
        
        import_service = TestCaseService(azure_service)
        
        # Find latest version (async to prevent blocking, excluding current to prevent "same" detection)
        latest_version = await asyncio.to_thread(import_service._find_latest_version_excluding, project_name, version)
        
        # Compare versions
        if latest_version:
            version_type = compare_versions(latest_version, version)
        else:
            version_type = compare_versions("0.0.0", version)
        
        # Parse version
        major, minor, patch = parse_version(version)
        
        # Find similar plans (async to prevent blocking)
        similar_plan = await asyncio.to_thread(import_service._find_similar_test_plan, project_name, major, minor)
        
        return {
            "project_name": project_name,
            "current_version": version,
            "latest_version": latest_version,
            "version_type": version_type,
            "parsed_version": {"major": major, "minor": minor, "patch": patch},
            "similar_plan": similar_plan["name"] if similar_plan else None,
            "action_required": {
                "create_new_plan": version_type in ['major', 'minor'],
                "update_existing": version_type in ['patch', 'same'],
                "description": {
                    "major": "همیشه تست پلن جدید ساخته می‌شود",
                    "minor": "همیشه تست پلن جدید ساخته می‌شود", 
                    "patch": "از همان test plan موجود استفاده می‌شود و محتوای جدید به آن اضافه می‌شود",
                    "same": "محتوای تست پلن موجود به‌روزرسانی می‌شود"
                }.get(version_type, "unknown")
            }
        }
            
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))