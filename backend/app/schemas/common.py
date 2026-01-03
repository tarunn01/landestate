"""
File: backend/app/schemas/common.py

This file contains SHARED Pydantic schemas used across multiple endpoints.
These define the REQUEST and RESPONSE formats.

WHY? To enforce consistent data validation and auto-generate API docs.
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, EmailStr, validator

T = TypeVar('T')

# ============================================================================
# PAGINATION SCHEMAS - Used in list endpoints (GET /properties?page=1)
# ============================================================================

class PaginationParams(BaseModel):
    """
    Common pagination parameters for list endpoints.
    Use this in your endpoint like:
    
    @router.get("/properties")
    async def get_properties(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
    ):
        pass
    """
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    
    USAGE EXAMPLE:
    ✅ Response type: PaginatedResponse[PropertyResponse]
    
    This will return:
    {
        "total": 250,
        "page": 1,
        "page_size": 20,
        "total_pages": 13,
        "items": [...]
    }
    """
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    items: List[T] = Field(..., description="List of items")


# ============================================================================
# ERROR SCHEMAS - Used in all error responses
# ============================================================================

class ErrorDetail(BaseModel):
    """
    Single field error detail.
    
    USAGE:
    {
        "field": "email",
        "message": "Invalid email format"
    }
    """
    field: str = Field(..., description="Field name that has error")
    message: str = Field(..., description="Error message for the field")


class ErrorResponse(BaseModel):
    """
    Standard error response for all endpoints.
    
    USAGE EXAMPLE:
    Returns 400 Bad Request:
    {
        "detail": "Validation failed",
        "error_code": "VALIDATION_ERROR",
        "errors": [{"field": "email", "message": "Invalid format"}]
    }
    """
    detail: str = Field(..., description="Main error message")
    error_code: str = Field(..., description="Error code for client handling")
    errors: Optional[List[ErrorDetail]] = Field(
        None, 
        description="Detailed field errors"
    )


# ============================================================================
# LOCATION SCHEMAS - Used in property endpoints (contains coordinates)
# ============================================================================

class CoordinateBase(BaseModel):
    """
    GPS coordinates for a location.
    
    WHY? We need latitude/longitude for:
    - Displaying on maps
    - Distance calculations
    - Geospatial queries
    """
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)


class LocationBase(CoordinateBase):
    """
    Location data shared between request/response.
    
    INCLUDES:
    - Coordinates (GPS)
    - Address details
    - City/State/Country
    """
    name: str = Field(..., min_length=1, max_length=255, description="Location name")
    address: Optional[str] = Field(None, max_length=500, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    zip_code: Optional[str] = Field(None, max_length=20, description="Postal code")


class LocationResponse(LocationBase):
    """
    Location data returned from API.
    
    ADDS:
    - Database ID
    - Property count in this location
    """
    id: str = Field(..., description="Location unique ID (UUID)")
    property_count: int = Field(0, description="Number of properties in location")

    class Config:
        from_attributes = True  # Works with SQLAlchemy models


# ============================================================================
# GEOMETRY SCHEMAS - For storing plot shapes (GeoJSON format)
# ============================================================================

class GeometryCoordinates(BaseModel):
    """
    GeoJSON coordinates.
    
    WHY? Properties might be polygons (plot boundaries), points, etc.
    
    EXAMPLE POLYGON (rectangular plot):
    {
        "type": "Polygon",
        "coordinates": [
            [
                [40.7128, -74.0060],
                [40.7130, -74.0060],
                [40.7130, -74.0058],
                [40.7128, -74.0058],
                [40.7128, -74.0060]  # Must close the polygon
            ]
        ]
    }
    """
    type: str = Field(..., description="Geometry type: Point, Polygon, etc")
    coordinates: List = Field(..., description="GeoJSON coordinates array")


# ============================================================================
# TIMESTAMP MIXIN - Used in models with created_at/updated_at
# ============================================================================

class TimestampMixin(BaseModel):
    """
    Mixin for timestamp fields.
    
    USAGE:
    class PropertyResponse(TimestampMixin):
        id: str
        title: str
    
    This gives you automatically:
    - created_at: datetime
    - updated_at: datetime
    """
    created_at: datetime = Field(..., description="When this was created")
    updated_at: Optional[datetime] = Field(None, description="When this was last updated")

    class Config:
        from_attributes = True


# ============================================================================
# SUCCESS RESPONSE WRAPPER (Optional, for consistency)
# ============================================================================

class SuccessResponse(BaseModel, Generic[T]):
    """
    Generic success response wrapper.
    
    OPTIONAL: Use if you want consistent success responses.
    
    USAGE:
    return SuccessResponse(
        message="Property created successfully",
        data=property_obj,
        status="success"
    )
    
    RESPONSE:
    {
        "message": "Property created successfully",
        "data": {...},
        "status": "success"
    }
    """
    message: str = Field(..., description="Success message")
    data: Optional[T] = Field(None, description="Response data")
    status: str = Field("success", description="Status flag")


