from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

# from geoalchemy2 import Geometry
from datetime import datetime
import uuid
from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    location_type = Column(String(100), nullable=True)
    created_by = Column(String(100), ForeignKey("user.id"), nullable=True)

    # Relationships
    properties = relationship("Property", back_populates="locations")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name})>"
