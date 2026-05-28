"""
File: backend/app/schemas/common.py

This file contains SHARED Pydantic schemas used across multiple endpoints.
These define the REQUEST and RESPONSE formats.

WHY? To enforce consistent data validation and auto-generate API docs.
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict

T = TypeVar("T")

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
    Single field error detail for validation errors.

    ERROR CODES:
    - INVALID_EMAIL: Email format is invalid
    - WEAK_PASSWORD: Password doesn't meet strength requirements
    - INVALID_PHONE: Phone number format is invalid
    - REQUIRED_FIELD: Required field is missing
    - VALUE_TOO_SHORT: Value is too short
    - VALUE_TOO_LONG: Value is too long
    - DUPLICATE_VALUE: Value already exists (e.g., email)

    USAGE:
    {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_EMAIL"
    }
    """

    field: str = Field(..., description="Field name that has error")
    message: str = Field(..., description="Error message for the field")
    code: str = Field(..., description="Error code (INVALID_EMAIL, WEAK_PASSWORD, etc.)")


class ValidationErrorResponse(BaseModel):
    """
    Standard validation error response (422 Unprocessable Entity).

    Used when request body has validation errors.

    EXAMPLE:
    {
        "detail": "Validation failed",
        "error_code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "password",
                "message": "Password must contain uppercase letter",
                "code": "WEAK_PASSWORD"
            },
            {
                "field": "phone",
                "message": "Phone number must be 10-15 digits",
                "code": "INVALID_PHONE"
            }
        ]
    }
    """

    detail: str = Field(..., description="Main error message")
    error_code: str = Field(default="VALIDATION_ERROR", description="Error type")
    errors: List[ErrorDetail] = Field(..., description="List of validation errors")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": [
                    {
                        "field": "password",
                        "message": "Password must contain at least 1 uppercase letter",
                        "code": "WEAK_PASSWORD",
                    }
                ],
            }
        }


class AuthErrorResponse(BaseModel):
    """
    Authentication error response (401/403 status).

    Used for login failures, token issues, permission errors.

    ERROR CODES:
    - INVALID_CREDENTIALS: Email/password combination is wrong
    - USER_NOT_FOUND: User with email doesn't exist
    - INVALID_TOKEN: JWT token is invalid or expired
    - PERMISSION_DENIED: User doesn't have required permissions

    EXAMPLE:
    {
        "detail": "Invalid email or password",
        "error_code": "INVALID_CREDENTIALS",
        "errors": null
    }
    """

    detail: str = Field(..., description="Error description")
    error_code: str = Field(..., description="Error code for client handling")
    errors: Optional[List[ErrorDetail]] = Field(
        None, description="Additional error details (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid email or password",
                "error_code": "INVALID_CREDENTIALS",
                "errors": None,
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response for all endpoints.

    Used for general server errors, bad requests, etc.

    USAGE EXAMPLE:
    Returns 400 Bad Request:
    {
        "detail": "Validation failed",
        "error_code": "VALIDATION_ERROR",
        "errors": [{"field": "email", "message": "Invalid format", "code": "INVALID_EMAIL"}]
    }
    """

    detail: str = Field(..., description="Main error message")
    error_code: str = Field(..., description="Error code for client handling")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Detailed field errors")


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
    # city: str = Field(..., min_length=1, max_length=100, description="City name")
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

    name: str = Field(...)
    location_id: str = Field(..., description="Location unique ID (UUID)")
    latitude: float = Field(..., description="location precise latitude")
    longitude: float = Field(..., description="location precise longitude")
    created_at: datetime = Field(..., description="giving location created timestamp.")
    updated_at: datetime = Field(..., description="giving updated location timestamp.")

    country: str = Field(..., description="location country")
    state: str = Field(..., description="location's state")
    description: Optional[str] = Field(None, description="short description of location")
    location_type: Optional[str] = Field(None, description="type of location")

    property_count: int = Field(0, description="Number of properties in location")

    model_config = ConfigDict(from_attributes=True)


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
