from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

# from geoalchemy2 import Geometry
from datetime import datetime
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
    # geometry = Column(Geometry('POLYGON'), nullable=True)  # Optional geometry

    # Foreign key to broker (User)
    broker_id = Column(String, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
