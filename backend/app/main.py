from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.api import routes


from app.core.database import get_db

app = FastAPI(
    title="LandEstate API",
    version="0.1.0",
    description="Geospatial property marketplace REST API using FastAPI + fastapi-restful",
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
        "openapi_schema": "/openapi.json",
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="check your db health status,Database connection failed",
        )
    return {"status": "healthy"}
