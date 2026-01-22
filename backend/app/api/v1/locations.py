"""RESOURCES:
- locationsResource: GET (list), POST (create)
- locationResource: GET (detail), PUT (update), DELETE (delete)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.locations import Location as locationModel

from app.schemas.locations import LocationCreateRequest, LocationDetailedResponse, LocationResponse


class locationresource:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def list_locations(self, skip: int = 0, limit: int = 10) -> dict:
        "list all the locations with pagination"
        locations = self.db.query(locationModel).offset(skip).limit(limit).all()
        total = self.db.query(locationModel).count()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [LocationDetailedResponse.from_orm(p) for p in locations],
        }

    async def create_location(self, location_in: LocationCreateRequest) -> LocationResponse:
        """creating new location"""
        new_location = locationModel(
            name=location_in.location_name,
            country=location_in.country,
            location_id=location_in.location_id,
            longitude=location_in.longitude,
            latitude=location_in.latitude,
            description=location_in.description,
        )
        self.db.add(new_location)
        self.db.commit()
        self.db.refresh(new_location)

        return LocationResponse.from_orm(new_location)

    async def update_location(
        self,
    ):
        new_location = locationModel(name)
