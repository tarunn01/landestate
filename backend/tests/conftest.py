"""
File: tests/conftest.py

Pytest configuration and shared fixtures for all tests.

WHY CONFTEST?
- Centralized fixtures (reusable test utilities)
- Shared setup/teardown logic
- Test database configuration
- Mock dependencies
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import hash_password


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


# Create in-memory SQLite database for testing (super fast, isolated)
@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh in-memory database for each test.

    SCOPE="function" means: A new DB for EVERY test (isolation)
    This prevents tests from interfering with each other.

    EXAMPLE:
    def test_something(test_db):
        user = test_db.query(User).first()
        assert user is not None
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Inject test DB into FastAPI dependency
    app.dependency_overrides[get_db] = override_get_db

    yield SessionLocal()

    # Cleanup after test
    app.dependency_overrides.clear()


# ============================================================================
# CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def client(test_db):
    """
    FastAPI TestClient for making HTTP requests in tests.

    EXAMPLE:
    def test_login(client):
        response = client.post("/auth/login", json={"email": "...", "password": "..."})
        assert response.status_code == 200
    """
    return TestClient(app)


# ============================================================================
# USER FIXTURES
# ============================================================================


@pytest.fixture
def test_user_data():
    """
    Standard test user data (no database, just dict).

    USAGE:
    def test_registration(client, test_user_data):
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 201
    """
    return {
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "role": "USER",
    }


@pytest.fixture
def test_user_in_db(test_db, test_user_data):
    """
    Create a real user in test database.

    USAGE:
    def test_login(client, test_user_in_db):
        # User already exists in DB
        response = client.post("/auth/login", json={
            "email": test_user_in_db.email,
            "password": "SecurePass123!"
        })
        assert response.status_code == 200
    """
    user = User(
        id="test-user-1",
        email=test_user_data["email"],
        password_hash=hash_password(test_user_data["password"]),
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
        phone=test_user_data["phone"],
        role=test_user_data["role"],
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def valid_token(test_user_in_db, test_user_data):
    """
    Generate a valid JWT token for authenticated requests.

    USAGE:
    def test_get_profile(client, valid_token):
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
    """
    from app.core.security import create_access_token

    return create_access_token(test_user_in_db.id)


# ============================================================================
# INVALID DATA FIXTURES (for error testing)
# ============================================================================


@pytest.fixture
def invalid_emails():
    """Test various invalid email formats."""
    return [
        "notanemail",
        "missing@domain",
        "@nodomain.com",
        "spaces in@email.com",
        "",
    ]


@pytest.fixture
def weak_passwords():
    """Test various weak passwords."""
    return [
        "short",  # Too short
        "12345678",  # Only numbers
        "abcdefgh",  # Only lowercase
        "ABCDEFGH",  # Only uppercase
        "",  # Empty
    ]


# ============================================================================
# MARKS FOR CATEGORIZING TESTS
# ============================================================================


def pytest_configure(config):
    """
    Register custom pytest marks.

    USAGE IN TESTS:
    @pytest.mark.unit
    def test_password_hashing():
        ...

    RUN ONLY UNIT TESTS:
    pytest -m unit
    """
    config.addinivalue_line("markers", "unit: Unit tests (no DB)")
    config.addinivalue_line("markers", "integration: Integration tests (with DB)")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
