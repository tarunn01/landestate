"""
Initialize database - creates all tables based on SQLAlchemy models.

Run this once before starting the server:
    python init_db.py
"""

from app.core.database import Base, engine
from app.models.user import User
from app.models.properties import Property

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
