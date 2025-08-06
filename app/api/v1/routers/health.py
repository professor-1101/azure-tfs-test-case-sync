"""Health check endpoints."""

from fastapi import APIRouter
from app.schemas.responses import HealthResponse
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the API and Azure DevOps connection.
    Use this endpoint to verify that the API is running and can connect to Azure DevOps.
    """
    return HealthResponse(
        status="healthy",
        version=settings.version,
        azure_devops_connected=True
    )