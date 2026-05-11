"""
File: backend/app/api/v1/properties.py

PROPERTY ENDPOINTS - Pure FastAPI with Class-Based Resources

RESOURCES:
- PropertiesResource: GET (list), POST (create)
- PropertyResource: GET (detail), PUT (update), DELETE (delete)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.schemas.property import (
    PropertyCreateRequest,
    PropertyCreateResponse,
    PropertyDetailResponse,
    PropertyUpdateRequest,
    PropertyUpdateResponse,
    PropertyImageResponse,
)
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.properties import Property as PropertyModel
from app.models.properties import PropertyImage
from app.models.user import User
from app.services.s3 import S3Service

router = APIRouter(tags=["Properties"])


# ============================================================================
# RESOURCE CLASS: PropertiesResource (List and Create)
# ============================================================================


class PropertiesResource:
    """Resource for managing the collection of properties."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def list_properties(self, skip: int = 0, limit: int = 10) -> dict:
        """List all properties with pagination."""
        properties = self.db.query(PropertyModel).offset(skip).limit(limit).all()
        total = self.db.query(PropertyModel).count()
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [PropertyDetailResponse.model_validate(p) for p in properties],
        }

    async def create_property(
        self,
        property_in: PropertyCreateRequest,
        current_user: User,
    ) -> PropertyCreateResponse:
        """Create a new property."""
        new_property = PropertyModel(
            title=property_in.title,
            location_id=property_in.location_id,
            description=property_in.description,
            price=property_in.price,
            city=property_in.city,
            address=property_in.address,
            bedrooms=property_in.bedrooms,
            bathrooms=property_in.bathrooms,
            plot_size=property_in.plot_size,
            built_area=property_in.built_area,
            contact_phone=property_in.contact_phone,
            broker_id=current_user.id,
        )
        self.db.add(new_property)
        self.db.commit()
        self.db.refresh(new_property)
        return PropertyCreateResponse.model_validate(new_property)


# ============================================================================
# RESOURCE CLASS: PropertyResource (Get,Update, Delete)
# ============================================================================


class PropertyResource:
    """Resource for managing a single property."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _get_property(self, property_id: str) -> PropertyModel:
        """Helper to get property by ID or raise 404."""
        prop = self.db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
        if not prop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
        return prop

    async def get_detail(self, property_id: str) -> PropertyDetailResponse:
        """Get property details."""
        prop = self._get_property(property_id)
        return PropertyDetailResponse.model_validate(prop)

    async def update_property(
        self,
        property_id: str,
        property_in: PropertyUpdateRequest,
        current_user: User,
    ) -> PropertyUpdateResponse:
        """Update property."""
        prop = self._get_property(property_id)

        # Check authorization
        if prop.broker_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this property",
            )

        # Update fields
        for field, value in property_in.model_dump(exclude_unset=True).items():
            setattr(prop, field, value)

        self.db.commit()
        self.db.refresh(prop)
        return PropertyUpdateResponse.model_validate(prop)

    async def delete_property(
        self,
        property_id: str,
        current_user: User,
    ) -> dict:
        """Delete property."""
        prop = self._get_property(property_id)

        # Check authorization
        if prop.broker_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this property",
            )

        self.db.delete(prop)
        self.db.commit()
        return {"message": "Property deleted", "id": property_id}


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("", response_model=dict)
async def list_properties(
    skip: int = 0,
    limit: int = 10,
    resource: PropertiesResource = Depends(),
):
    """GET /properties - List all properties"""
    return await resource.list_properties(skip=skip, limit=limit)


@router.post("", response_model=PropertyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_in: PropertyCreateRequest,
    current_user=Depends(get_current_user),
    resource: PropertiesResource = Depends(),
):
    """POST /properties - Create new property"""
    return await resource.create_property(property_in, current_user)


@router.get("/{property_id}", response_model=PropertyDetailResponse)
async def get_property(
    property_id: str,
    resource: PropertyResource = Depends(),
):
    """GET /properties/{property_id} - Get property detail"""
    return await resource.get_detail(property_id)


@router.put("/{property_id}", response_model=PropertyUpdateResponse)
async def update_property(
    property_id: str,
    property_in: PropertyUpdateRequest,
    current_user=Depends(get_current_user),
    resource: PropertyResource = Depends(),
):
    """PUT /properties/{property_id} - Update property"""
    return await resource.update_property(property_id, property_in, current_user)


@router.delete("/{property_id}", response_model=dict)
async def delete_property(
    property_id: str,
    current_user=Depends(get_current_user),
    resource: PropertyResource = Depends(),
):
    """DELETE /properties/{property_id} - Delete property"""
    return await resource.delete_property(property_id, current_user)


@router.post("/{property_id}/images", status_code=201)
async def upload_image(
    property_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    fetched_property = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if not fetched_property:
        raise HTTPException(status_code=404, detail="no property found with the details")

    if fetched_property.broker_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not authorised to upload images."
        )
    s3 = S3Service()
    key, url = s3.upload_image(file.file, property_id, file.filename)
    property_image = PropertyImage(url=url, property_id=property_id, s3_key=key)
    db.add(property_image)
    db.commit()
    db.refresh(property_image)

    return PropertyImageResponse.model_validate(property_image)
