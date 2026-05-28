from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship

# from geoalchemy2 import Geometry
from datetime import datetime, timezone
import uuid
from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    city = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    plot_size = Column(Float, nullable=True)  # in square meters
    built_area = Column(Float, nullable=True)  # in square meters
    contact_phone = Column(String, nullable=False)
    status = Column(String, default="AVAILABLE", nullable=False)  # AVAILABLE, SOLD, PENDING
    # geometry = Column(Geometry('POLYGON'), nullable=True)  # Optional geometry

    # Foreign key to broker (User)
    broker_id = Column(String, ForeignKey("users.id"), nullable=False)
    location_id = Column(String, ForeignKey("locations.location_id"), nullable=False)

    # relationships
    broker = relationship("User", back_populates="properties")
    location = relationship("Location", back_populates="properties")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    images = relationship("PropertyImage", back_populates="property", cascade="all,delete-orphan")

    updated_at = Column(
        DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )


class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, nullable=False)
    property_id = Column(String, ForeignKey("properties.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_primary = Column(Boolean, default=False)
    s3_key = Column(String, nullable=False)

    property = relationship("Property", back_populates="images")
