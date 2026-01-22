from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from .common import LocationResponse, TimestampMixin, GeometryCoordinates


# base response
class BaseLocation(BaseModel):
    """base location model"""

    location_name: str = Field(...)
    location_id: str = Field(..., description="provide location id")
    latitude: float = Field(..., description="provide precise latitude")
    longitude: float = Field(..., description="provide precise longitude")
    country: str = Field(..., description="location's country")
    state: str = Field(..., description="location's state")
    description: Optional[str] = Field(..., description="short description of location.")


class LocationResponse(BaseLocation, TimestampMixin):
    """complete location details should be given to client"""

    location_name: str = Field(...)
    location_id: str = Field(..., description="location unique id")
    latitude: float = Field(..., description="location precise latitude")
    longitude: float = Field(..., description="location precise longitude")
    created_at: datetime = Field(..., description="giving location created timestamp.")
    updated_at: datetime = Field(..., description="giving updated location timestamp.")

    country: str = Field(..., description="location country")
    state: str = Field(..., description="location's state")
    description: str = Field(..., description="short description of location")


class LocationDetailedResponse(BaseLocation, TimestampMixin):
    """complete location details should be given to client"""

    location_name: str = Field(...)
    location_id: str = Field(..., description="location unique id")
    latitude: float = Field(..., description="location precise latitude")
    longitude: float = Field(..., description="location precise longitude")
    created_at: datetime = Field(..., description="giving location created timestamp.")
    updated_at: datetime = Field(..., description="giving updated location timestamp.")

    location_type = Optional[str] = Field(..., description="type of location")
    country: str = Field(..., description="location country")
    state: str = Field(..., description="location's state")
    description: str = Field(..., description="short description of location")


class LocationCreateRequest(BaseLocation):
    location_name: str = Field(...)
    location_id: str = Field(..., description="provide location id")
    latitude: float = Field(..., description="provide precise latitude")
    longitude: float = Field(..., description="provide precise longitude")
    country: str = Field(..., description="location's country")
    state: str = Field(..., description="location's state")
    description: Optional[str] = Field(..., description="short description of location.")
    created_at: datetime = Field(..., description="giving location created timestamp.")
    updated_at: datetime = Field(..., description="giving updated location timestamp.")


# class

# country         → Country name (user provided)
# state           → State/Province (user provided)
# description     → Location description (user provided, optional)
# created_at      → Auto-set when location created (system)
# updated_at      → Auto-updated when location modified (system)
