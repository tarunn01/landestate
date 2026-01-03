"""
File: backend/app/schemas/property.py

Property-related request and response schemas.

WHY? Define what data is expected for properties and what we return.
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
from .common import LocationResponse, TimestampMixin, GeometryCoordinates


# ============================================================================
# BROKER SCHEMAS (Used in property responses)
# ============================================================================

class BrokerBase(BaseModel):
    """
    Broker data shared in responses.
    
    WHY? When user sees a property, they need broker contact info.
    """
    id: str = Field(..., description="Broker unique ID")
    name: str = Field(..., description="Broker name")
    phone: str = Field(..., description="Broker phone")
    email: str = Field(..., description="Broker email")
    company: Optional[str] = Field(None, description="Company name")


class BrokerResponse(BrokerBase, TimestampMixin):
    """
    Complete broker data returned from API.
    """
    profile_picture: Optional[str] = Field(None, description="Profile image URL")
    bio: Optional[str] = Field(None, description="Broker bio")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    total_reviews: int = Field(0, description="Total reviews count")

    class Config:
        from_attributes = True


# ============================================================================
# IMAGE SCHEMAS
# ============================================================================

class PropertyImageResponse(BaseModel):
    """
    Property image data.
    
    WHY? Properties need multiple images shown in gallery.
    
    EXAMPLE:
    {
        "id": "img-1",
        "url": "https://s3.example.com/property-1.jpg",
        "is_primary": true,
        "uploaded_at": "2024-01-02T10:00:00Z"
    }
    """
    id: str = Field(..., description="Image unique ID")
    url: str = Field(..., description="Image URL (S3 link)")
    is_primary: bool = Field(False, description="Is this the main image?")
    uploaded_at: datetime = Field(..., description="When image was uploaded")

    class Config:
        from_attributes = True


# ============================================================================
# REQUEST SCHEMAS (What frontend SENDS)
# ============================================================================

class PropertyCreateRequest(BaseModel):
    """
    Request body for POST /properties
    
    EXAMPLE REQUEST:
    {
        "title": "2 Acre Residential Plot",
        "description": "Beautiful land with road access",
        "property_type": "RESIDENTIAL",
        "price": 500000,
        "currency": "USD",
        "area_sqft": 87120,
        "location_id": "loc-123",
        "amenities": ["Water Access", "Road Access"],
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[40.7128, -74.0060], ...]]
        },
        "contact_phone": "+1234567890"
    }
    
    WHO CREATES? Only BROKER and OWNER roles
    """
    title: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Property title"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Property description"
    )
    property_type: Literal[
        "RESIDENTIAL",
        "COMMERCIAL",
        "AGRICULTURAL",
        "INDUSTRIAL",
        "MIXED"
    ] = Field(..., description="Type of property")
    price: float = Field(..., gt=0, description="Property price")
    currency: str = Field("USD", max_length=3, description="Currency code")
    area_sqft: float = Field(..., gt=0, description="Area in square feet")
    location_id: str = Field(..., description="Location ID")
    amenities: List[str] = Field(
        default_factory=list,
        description="List of amenities (Water, Road, Electricity, etc)"
    )
    geometry: Optional[GeometryCoordinates] = Field(
        None,
        description="Plot boundary as GeoJSON polygon"
    )
    contact_phone: str = Field(..., description="Contact phone number")


class PropertyUpdateRequest(BaseModel):
    """
    Request body for PUT /properties/{property_id}
    
    All fields are OPTIONAL - only update what you send.
    """
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    price: Optional[float] = Field(None, gt=0)
    amenities: Optional[List[str]] = Field(None)
    contact_phone: Optional[str] = Field(None)


# ============================================================================
# RESPONSE SCHEMAS (What backend SENDS back)
# ============================================================================

class PropertyListItemResponse(TimestampMixin):
    """
    Property in LIST response (simplified version).
    
    WHY? Lists show 20+ properties at once.
    Don't need ALL details (images, reviews, etc).
    Keep it lightweight for fast loading.
    
    USED IN: GET /properties response
    
    EXAMPLE:
    {
        "id": "prop-789",
        "title": "2 Acre Residential Plot",
        "price": 500000,
        "currency": "USD",
        "area_sqft": 87120,
        "location": {...},
        "broker": {...},
        "image_url": "https://s3.example.com/prop-789.jpg",
        "status": "AVAILABLE",
        "views_count": 1250,
        "favorites_count": 45,
        "created_at": "2024-01-01T10:00:00Z"
    }
    """
    id: str = Field(..., description="Property unique ID")
    title: str = Field(..., description="Property title")
    price: float = Field(..., description="Property price")
    currency: str = Field(..., description="Currency code")
    area_sqft: float = Field(..., description="Area in square feet")
    property_type: str = Field(..., description="Type of property")
    location: LocationResponse = Field(..., description="Location details")
    broker: BrokerBase = Field(..., description="Broker info")
    image_url: Optional[str] = Field(None, description="Primary image URL")
    status: str = Field(..., description="AVAILABLE, SOLD, PENDING")
    views_count: int = Field(0, description="Number of views")
    favorites_count: int = Field(0, description="Number of favorites")

    class Config:
        from_attributes = True


class PropertyDetailResponse(TimestampMixin):
    """
    Complete property data for detail view.
    
    USED IN: GET /properties/{property_id} response
    
    INCLUDES:
    - All basic info
    - Full broker details
    - All images
    - All reviews
    - Geometry (plot boundary)
    - Amenities
    
    This is the FULL response with everything.
    """
    id: str = Field(..., description="Property unique ID")
    title: str = Field(..., description="Property title")
    description: str = Field(..., description="Full description")
    property_type: str = Field(..., description="Property type")
    price: float = Field(..., description="Property price")
    currency: str = Field(..., description="Currency code")
    area_sqft: float = Field(..., description="Area in square feet")
    total_area_sqm: float = Field(..., description="Area in square meters")
    
    # Location with full details
    location: LocationResponse = Field(..., description="Location details")
    
    # Broker with full details
    broker: BrokerResponse = Field(..., description="Broker details")
    
    # Amenities list
    amenities: List[str] = Field(
        default_factory=list,
        description="List of amenities"
    )
    
    # Images
    images: List[PropertyImageResponse] = Field(
        default_factory=list,
        description="Property images"
    )
    
    # Geometry (plot boundary on map)
    geometry: Optional[GeometryCoordinates] = Field(
        None,
        description="Plot boundary as GeoJSON"
    )
    
    # Status and counts
    status: str = Field(..., description="AVAILABLE, SOLD, PENDING")
    views_count: int = Field(0, description="View count")
    favorites_count: int = Field(0, description="Favorite count")
    contact_phone: str = Field(..., description="Contact phone")

    class Config:
        from_attributes = True


class PropertyCreateResponse(BaseModel):
    """
    Response from creating a property.
    
    USED IN: POST /properties response (201 Created)
    
    EXAMPLE:
    {
        "id": "prop-789",
        "title": "2 Acre Residential Plot",
        "price": 500000,
        "status": "AVAILABLE",
        "created_at": "2024-01-03T10:30:00Z"
    }
    
    WHY simple? Frontend just needs the ID to redirect to detail page.
    """
    id: str = Field(..., description="Property ID (use for detail view)")
    title: str = Field(..., description="Property title")
    price: float = Field(..., description="Property price")
    status: str = Field(..., description="Initial status")
    created_at: datetime = Field(..., description="Created timestamp")


# ============================================================================
# SEARCH RESPONSE SCHEMAS
# ============================================================================

class PropertyNearbyResponse(BaseModel):
    """
    Property in search by location response.
    
    USED IN: GET /properties/search/nearby
    
    INCLUDES: distance_km
    
    WHY? When user searches nearby, they need to see distance from their location.
    """
    id: str = Field(..., description="Property ID")
    title: str = Field(..., description="Property title")
    price: float = Field(..., description="Price")
    currency: str = Field(..., description="Currency")
    area_sqft: float = Field(..., description="Area")
    property_type: str = Field(..., description="Type")
    
    location: LocationResponse = Field(..., description="Location")
    broker: BrokerBase = Field(..., description="Broker info")
    image_url: Optional[str] = Field(None, description="Image URL")
    
    # KEY DIFFERENCE: distance from search location
    distance_km: float = Field(
        ...,
        description="Distance from search location in kilometers"
    )

    class Config:
        from_attributes = True


class PropertySearchResponseWrapper(BaseModel):
    """
    Wrapper for search by location response.
    
    USED IN: GET /properties/search/nearby response
    
    EXAMPLE RESPONSE:
    {
        "user_location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "search_radius_km": 5,
        "total": 15,
        "items": [...]
    }
    
    WHY? Confirm what location was searched and radius used.
    """
    user_location: BaseModel = Field(..., description="Search center location")
    search_radius_km: float = Field(..., description="Search radius in km")
    total: int = Field(..., description="Total results")
    items: List[PropertyNearbyResponse] = Field(
        ...,
        description="Properties sorted by distance"
    )

