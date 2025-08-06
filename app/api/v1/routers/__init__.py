"""API v1 routers."""

from fastapi import APIRouter
from app.api.v1.routers import health, test_plans, imports, logs

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router)
api_router.include_router(test_plans.router)
api_router.include_router(imports.router)
api_router.include_router(logs.router)