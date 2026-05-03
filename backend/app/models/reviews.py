from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

# from geoalchemy2 import Geometry
from datetime import datetime, timezone
import uuid
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rating = Column(Integer, nullable=False)
    feedback = Column(String, nullable=True)
    property_id = Column(String(150), ForeignKey("properties.id"), nullable=False)
    reviewer_id = Column(String(150), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
