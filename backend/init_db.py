"""
Initialize database - creates all tables based on SQLAlchemy models.

Run this once before starting the server:
    python init_db.py

This will DROP all existing tables and recreate them fresh!
"""

from app.core.database import Base, engine
from app.models.user import User
from app.models.properties import Property


def init_db():
    print("Creating new database tables...")
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
