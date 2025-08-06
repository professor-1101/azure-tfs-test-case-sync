"""Test plan management endpoints."""

from fastapi import APIRouter, HTTPException
from app.services.azure_devops_token import AzureDevOpsTokenService
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(tags=["test-plans"])
logger = get_logger(__name__)


@router.get("/test-plans/{project_name}")
async def list_test_plans(project_name: str, token: str):
    """
    List available test plans for a project.
    
    This endpoint lists all test plans available in the specified Azure DevOps project.
    Useful for debugging and verifying which test plans exist before importing.
    
    **Parameters:**
    - `project_name`: Name of the Azure DevOps project
    - `token`: Authentication token (NTLM or Basic Auth format)
    
    **Returns:**
    - List of test plans with their IDs and names
    """
    try:
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
        
        # Get test plans
        url = f"{azure_service.org_url}/{azure_service.project_name}/_apis/test/plans?api-version={azure_service.api_version}"
        plans_response = azure_service._request("GET", url)
        available_plans = [{"id": p.get("id"), "name": p.get("name", "Unknown")} for p in plans_response.get("value", [])]
        
        return {
            "status": "success",
            "project_name": project_name,
            "test_plans": available_plans,
            "count": len(available_plans)
        }
        
    except Exception as e:
        logger.error(f"Error listing test plans: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing test plans: {str(e)}"
        )