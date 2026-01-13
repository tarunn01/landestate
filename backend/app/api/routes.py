"""
File: backend/app/api/routes.py

Main router that includes all API version resources.
"""

from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1 import properties
from app.api.v1 import users

# Create main router
main_router = APIRouter(prefix="/api/v1")

# Include routers
main_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
main_router.include_router(properties.router, prefix="/properties", tags=["properties"])
main_router.include_router(users.router, prefix="/users", tags=["users"])

# Health check endpoint
@main_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "v1"}


