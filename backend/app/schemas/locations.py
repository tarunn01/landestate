from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator, ConfigDict
from .common import LocationResponse


# base response
class BaseLocation(BaseModel):
    """base location model"""

    name: str = Field(...)
    location_id: str = Field(..., description="provide location id")
    latitude: float = Field(..., description="provide precise latitude")
    longitude: float = Field(..., description="provide precise longitude")
    country: str = Field(..., description="location's country")
    state: str = Field(..., description="location's state")
    description: Optional[str] = Field(..., description="short description of location.")


class LocationCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the location")
    latitude: float = Field(..., description="provide precise latitude")
    longitude: float = Field(..., description="provide precise longitude")
    country: str = Field(..., description="location's country")
    state: str = Field(..., description="location's state")
    description: Optional[str] = Field(..., description="short description of location.")


class LocationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    latitude: Optional[float] = Field(None, description="provide precise latitude")
    longitude: Optional[float] = Field(None, description="provide precise longitude")
    country: Optional[str] = Field(None, min_length=5, max_length=150)
    state: Optional[str] = Field(None, min_length=3, max_length=150)


class LocationUpdateResponse(BaseModel):
    location_id: Optional[str] = Field(None, description="location ID")
    updated_at: Optional[datetime] = Field(None, description="Last updated timestamp")
    name: Optional[str] = Field(None)
    latitude: Optional[float] = Field(None, description="location precise latitude")
    longitude: Optional[float] = Field(None, description="location precise longitude")
    created_at: Optional[datetime] = Field(None, description="giving location created timestamp.")

    country: Optional[str] = Field(None, description="location country")
    state: Optional[str] = Field(None, description="location's state")
    description: Optional[str] = Field(None, description="short description of location")
    model_config = ConfigDict(from_attributes=True)
    # type: Optional[location_type] = Field(None, description="type of location")


# class

# country         → Country name (user provided)
# state           → State/Province (user provided)
# description     → Location description (user provided, optional)
# created_at      → Auto-set when location created (system)
# updated_at      → Auto-updated when location modified (system)
