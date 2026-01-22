from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
# from geoalchemy2 import Geometry
from datetime import datetime
import uuid
from app.core.database import Base