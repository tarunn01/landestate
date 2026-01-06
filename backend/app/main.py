from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes

app = FastAPI(
    title="LandEstate API",
    version="0.1.0",
    description="Geospatial property marketplace REST API using FastAPI + fastapi-restful"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Using APIResourceRouter from fastapi-restful for resource-based routing
app.include_router(routes.main_router)

@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "message": "Welcome to LandEstate API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi_schema": "/openapi.json"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
