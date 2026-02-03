"""
File: backend/app/api/v1/locations.py

LOCATION ENDPOINTS - Pure FastAPI with Class-Based Resources

RESOURCES:
- LocationsResource: GET (list), POST (create)
- LocationResource: GET (detail), PUT (update), DELETE (delete)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.locations import Location as LocationModel

from app.schemas.locations import (
    LocationCreateRequest,
    LocationDetailedResponse,
    LocationResponse,
    LocationUpdateRequest,
    LocationUpdateResponse,
)

router = APIRouter(tags=["Locations"])


# ============================================================================
# RESOURCE CLASS: LocationsResource (List and Create)
# ============================================================================


class LocationsResource:
    """Resource for managing the collection of locations."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def list_locations(self, skip: int = 0, limit: int = 10) -> dict:
        """List all locations with pagination."""
        locations = self.db.query(LocationModel).offset(skip).limit(limit).all()
        total = self.db.query(LocationModel).count()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [LocationDetailedResponse.from_orm(p) for p in locations],
        }

    async def create_location(
        self, location_in: LocationCreateRequest, current_user: dict
    ) -> LocationResponse:
        """Create a new location."""
        new_location = LocationModel(
            name=location_in.location_name,
            country=location_in.country,
            latitude=location_in.latitude,
            longitude=location_in.longitude,
            description=location_in.description,
            created_by=current_user["user_id"],
        )
        self.db.add(new_location)
        self.db.commit()
        self.db.refresh(new_location)
        return LocationResponse.from_orm(new_location)


# ============================================================================
# RESOURCE CLASS: LocationResource (Get, Update, Delete)
# ============================================================================


class LocationResource:
    """Resource for managing a single location."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _get_location(self, location_id: str) -> LocationModel:
        """Helper to get location by ID or raise 404."""
        location = (
            self.db.query(LocationModel).filter(LocationModel.location_id == location_id).first()
        )
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
        return location

    async def get_detail(self, location_id: str) -> LocationDetailedResponse:
        """Get location details."""
        location = self._get_location(location_id)
        return LocationDetailedResponse.from_orm(location)

    async def update_location(
        self, location_id: str, location_in: LocationUpdateRequest, current_user: dict
    ) -> LocationUpdateResponse:
        """Update location - admin or creator can update."""
        location = self._get_location(location_id)

        # Authorization: admin or creator
        is_admin = current_user["role"] == "admin"
        is_creator = location.created_by == current_user["user_id"]

        if not (is_admin or is_creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update location. Only admin or creator allowed.",
            )

        # Update fields
        for field, value in location_in.dict(exclude_unset=True).items():
            setattr(location, field, value)

        self.db.commit()
        self.db.refresh(location)
        return LocationUpdateResponse.from_orm(location)

    async def delete_location(self, location_id: str, current_user: dict) -> dict:
        """Delete location - admin or creator can delete."""
        location = self._get_location(location_id)

        # Authorization: admin or creator
        is_admin = current_user["role"] == "admin"
        is_creator = location.created_by == current_user["user_id"]

        if not (is_admin or is_creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete location. Only admin or creator allowed.",
            )

        self.db.delete(location)
        self.db.commit()
        return {"message": "Location deleted successfully", "id": location_id}


# ============================================================================
# ROUTE HANDLERS
# ============================================================================


@router.get("/locations", response_model=dict)
async def list_locations_handler(
    skip: int = 0, limit: int = 10, resource: LocationsResource = Depends()
):
    """List all locations with pagination."""
    return await resource.list_locations(skip=skip, limit=limit)


@router.post("/locations", response_model=LocationResponse)
async def create_location_handler(
    location_in: LocationCreateRequest,
    current_user: dict = Depends(get_current_user),
    resource: LocationsResource = Depends(),
) -> LocationResponse:
    """Create a new location."""
    return await resource.create_location(location_in=location_in, current_user=current_user)


@router.get("/locations/{location_id}", response_model=LocationDetailedResponse)
async def get_location_detail_handler(
    location_id: str, resource: LocationResource = Depends()
) -> LocationDetailedResponse:
    """Get location details."""
    return await resource.get_detail(location_id=location_id)


@router.put("/locations/{location_id}", response_model=LocationUpdateResponse)
async def update_location_handler(
    location_id: str,
    location_in: LocationUpdateRequest,
    current_user: dict = Depends(get_current_user),
    resource: LocationResource = Depends(),
) -> LocationUpdateResponse:
    """Update location."""
    return await resource.update_location(
        location_id=location_id, location_in=location_in, current_user=current_user
    )


@router.delete("/locations/{location_id}")
async def delete_location_handler(
    location_id: str,
    current_user: dict = Depends(get_current_user),
    resource: LocationResource = Depends(),
) -> dict:
    """Delete location."""
    return await resource.delete_location(location_id=location_id, current_user=current_user)
