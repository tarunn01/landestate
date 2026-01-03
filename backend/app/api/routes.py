"""
File: backend/app/api/routes.py

Main router that includes all API version routers.

THIS FILE:
- Imports all routers (auth, properties, users, etc)
- Includes them with their prefixes
- Version prefix allows future /api/v2 routes

FLOW:
User request: POST /api/auth/login
↓
Main router checks prefix /api
↓
Auth router checks /auth
↓
Endpoint /login is called
"""

from fastapi import APIRouter

# TODO: Import all routers once created
# from app.api.v1 import auth, properties, users, locations, reviews

# Create main router
router = APIRouter(prefix="/api/v1")

# TODO: Include all routers
# router.include_router(auth.router)
# router.include_router(properties.router)
# router.include_router(users.router)
# router.include_router(locations.router)
# router.include_router(reviews.router)

# For now, keep dummy endpoint for testing
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "v1"}
