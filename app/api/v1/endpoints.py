"""
API v1 endpoints.

This module now serves as a simple re-export of the modularized routers.
All endpoints have been organized into separate modules for better maintainability.
"""

from app.api.v1.routers import api_router as router

__all__ = ["router"]