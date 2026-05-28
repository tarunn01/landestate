"""
File: tests/test_auth_basics.py

BASIC TESTING EXAMPLES FOR AUTHENTICATION

This file demonstrates:
1. Unit tests (testing functions in isolation)
2. Integration tests (testing endpoints with DB)
3. Error case testing
4. Fixtures usage
5. Assertions and expectations

RUN ONLY THESE TESTS:
    pytest tests/test_auth_basics.py -v

RUN WITH COVERAGE:
    pytest tests/test_auth_basics.py --cov=app --cov-report=html
"""

import pytest
from fastapi import status
from pydantic import ValidationError
from app.core.security import hash_password, verify_password, create_access_token, verify_token
from app.schemas.auth import UserRegisterRequest


# ============================================================================
# UNIT TESTS: Test functions without HTTP/DB
# ============================================================================


class TestPasswordHashing:
    """
    Test password hashing and verification.

    WHY UNIT TESTS?
    - Fast (no database)
    - Test business logic in isolation
    - Good for learning fundamentals
    """

    @pytest.mark.unit
    def test_hash_password_creates_different_hash(self):
        """
        Same password should produce different hashes each time (salting).
        """
        password = "MySecurePassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2
        print(f"Hash 1: {hash1}")
        print(f"Hash 2: {hash2}")

    @pytest.mark.unit
    def test_verify_password_correct(self):
        """Test that correct password verifies successfully."""
        password = "MySecurePassword123"
        hashed = hash_password(password)

        # Should return True for correct password
        assert verify_password(password, hashed) is True

    @pytest.mark.unit
    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification."""
        password = "MySecurePassword123"
        hashed = hash_password(password)
        wrong_password = "WrongPassword456"
        # Should return False for incorrect password
        assert verify_password(wrong_password, hashed) is False

    @pytest.mark.unit
    def test_validate_phone_valid_formats(self):
        """Test phone validation with valid phone formats"""
        valid_phones = [
            "+1234567890",  # International format
            "1234567890",  # Simple format
            "123-456-7890",  # Dashes
            "(123)456-7890",  # Parentheses and dash
            "+1(234)567-8901",  # Mixed format
        ]
        for phone in valid_phones:
            user = UserRegisterRequest(
                email="test@example.com",
                password="ValidPass123!",
                first_name="John",
                last_name="Doe",
                phone=phone,
            )
            assert user.phone == phone

    @pytest.mark.unit
    def test_validate_phone_optional(self):
        """Test that phone is optional"""
        # Phone can be None
        user = UserRegisterRequest(
            email="test@example.com",
            password="ValidPass123!",
            first_name="John",
            last_name="Doe",
            phone=None,
        )
        assert user.phone is None

    @pytest.mark.unit
    def test_validate_phone_invalid_too_short(self):
        """Test phone validation rejects too short numbers"""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(
                email="test@example.com",
                password="ValidPass123!",
                first_name="John",
                last_name="Doe",
                phone="12345",  # Too short
            )
        assert "Phone number must have 10-15 digits" in str(exc_info.value)

    @pytest.mark.unit
    def test_validate_phone_invalid_too_long(self):
        """Test phone validation rejects too long numbers"""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(
                email="test@example.com",
                password="ValidPass123!",
                first_name="John",
                last_name="Doe",
                phone="123456789012345678",  # Too long
            )
        assert "Phone number must have 10-15 digits" in str(exc_info.value)

    @pytest.mark.unit
    def test_validate_phone_invalid_characters(self):
        """Test phone validation rejects invalid characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(
                email="test@example.com",
                password="ValidPass123!",
                first_name="John",
                last_name="Doe",
                phone="123-ABC-7890",  # Contains letters
            )
        assert "only digits and formatting characters" in str(exc_info.value)

    @pytest.mark.unit
    def test_verify_password_empty_string(self):
        """Test that empty string fails verification."""
        hashed = hash_password("MyPassword")
        assert verify_password("", hashed) is False


class TestTokenGeneration:
    """Test JWT token creation and verification."""

    @pytest.mark.unit
    def test_create_access_token_returns_string(self):
        """Token should be a string."""
        user_id = "test-user-123"
        token = create_access_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0
        print(f"Generated token: {token[:20]}...")

    @pytest.mark.unit
    def test_verify_token_valid(self):
        """Valid token should verify successfully."""
        user_id = "test-user-123"
        token = create_access_token(user_id)

        # Should return the user_id
        decoded_user_id = verify_token(token)
        assert decoded_user_id == user_id

    @pytest.mark.unit
    def test_verify_token_invalid(self):
        """Invalid token should return None."""
        invalid_token = "invalid.token.here"

        # Should return None for invalid token
        result = verify_token(invalid_token)
        assert result is None

    @pytest.mark.unit
    def test_verify_token_empty_string(self):
        """Empty token should return None."""
        result = verify_token("")
        assert result is None


# ============================================================================
# INTEGRATION TESTS: Test endpoints with database
# ============================================================================


class TestAuthRegisterEndpoint:
    """
    Test POST /auth/register endpoint.

    Integration test = Real HTTP request + Real database
    Uses TestClient to make requests to FastAPI app
    """

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_success(self, client, test_user_data):
        """
        Test successful user registration.

        FLOW:
        1. Send POST with user data
        2. Check status code is 201 (Created)
        3. Check response contains user info
        4. Check password is NOT in response

        ASSERTION TYPES:
        - Status code: assert response.status_code == 201
        - Response data: assert response.json()["email"] == "..."
        - Check field exists: assert "access_token" in response.json()
        """
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert "password" not in data  # Never return password!
        assert "access_token" in data
        assert "token_type" in data

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_duplicate_email(self, client, test_user_in_db, test_user_data):
        """
        Test that duplicate email registration fails.

        WHY TEST THIS?
        - User tries to register with same email twice
        - Should return 400 Bad Request
        - This is a business rule error (not server error)
        """
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already" in response.json()["detail"].lower()

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        invalid_data = {
            "email": "notanemail",  # Invalid!
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)

        # Pydantic validation should fail (422)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_weak_password(self, client):
        """Test registration with password too short."""
        invalid_data = {
            "email": "test@example.com",
            "password": "short",  # Less than 8 chars
            "first_name": "John",
            "last_name": "Doe",
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)

        # Pydantic validation should fail (422)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_missing_required_field(self, client):
        """Test registration without required field."""
        invalid_data = {
            "email": "test@example.com",
            # Missing password!
            "first_name": "John",
            "last_name": "Doe",
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLoginEndpoint:
    """Test POST /auth/login endpoint."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_login_success(self, client, test_user_in_db, test_user_data):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["email"] == test_user_data["email"]
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.integration
    @pytest.mark.auth
    def test_login_wrong_password(self, client, test_user_in_db, test_user_data):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": "WrongPassword123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.integration
    @pytest.mark.auth
    def test_login_user_not_found(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "AnyPassword123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthProtectedEndpoint:
    """Test that protected endpoints require authentication."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_profile_without_token(self, client):
        """
        Test accessing protected endpoint without token.

        Protected endpoints should return 401 if no Authorization header.
        """
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_profile_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_profile_with_valid_token(self, client, valid_token, test_user_in_db):
        """Test accessing protected endpoint with valid token."""
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_in_db.email


# ============================================================================
# PARAMETRIZED TESTS (Test multiple cases in one test)
# ============================================================================


class TestPasswordValidation:
    """
    Parametrized tests - run same test with multiple inputs.

    WHY PARAMETRIZE?
    - Test multiple cases without code duplication
    - DRY principle (Don't Repeat Yourself)
    - Easy to add new test cases
    """

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "password",
        [
            "short",  # Too short
            "12345678",  # Only numbers
            "abcdefgh",  # Only lowercase
            "ABCDEFGH",  # Only uppercase
            "",  # Empty
        ],
    )
    def test_weak_passwords_fail(self, password):
        """Test that weak passwords are rejected by Pydantic validator."""
        from app.schemas.auth import UserRegisterRequest
        from pydantic import ValidationError

        # Should raise ValidationError
        with pytest.raises(ValidationError):
            UserRegisterRequest(
                email="test@example.com",
                password=password,
                first_name="John",
                last_name="Doe",
            )

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "email",
        [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "",
        ],
    )
    def test_invalid_emails_fail(self, email):
        """Test that invalid email formats are rejected by Pydantic validator."""
        from app.schemas.auth import UserRegisterRequest
        from pydantic import ValidationError

        # Should raise ValidationError
        with pytest.raises(ValidationError):
            UserRegisterRequest(
                email=email,
                password="SecurePass123!",
                first_name="John",
                last_name="Doe",
            )


# ============================================================================
# USING FIXTURES FOR SETUP
# ============================================================================


class TestWithFixtures:
    """Demonstrate fixture usage."""

    @pytest.mark.integration
    def test_user_created_with_fixture(self, test_user_in_db):
        """
        Fixture automatically creates a user in DB.

        BENEFITS:
        - No need to create user manually
        - Reusable across tests
        - Clean, readable test code
        """
        assert test_user_in_db.email == "testuser@example.com"
        assert test_user_in_db.first_name == "John"
        assert test_user_in_db.is_active is True

    @pytest.mark.integration
    def test_token_created_with_fixture(self, valid_token, test_user_in_db):
        """
        Fixture automatically generates valid token for test user.
        """
        assert isinstance(valid_token, str)
        assert len(valid_token) > 0


# ============================================================================
# REFRESH TOKEN TESTS
# ============================================================================


class TestRefreshTokens:
    """Test refresh token creation, verification, and token pairs."""

    @pytest.mark.unit
    def test_create_refresh_token_returns_string(self):
        from app.core.security import create_refresh_token

        token = create_refresh_token("user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.unit
    def test_verify_refresh_token_valid(self):
        from app.core.security import create_refresh_token, verify_token

        token = create_refresh_token("user-123")
        result = verify_token(token, token_type="refresh")
        assert result == "user-123"

    @pytest.mark.unit
    def test_refresh_token_fails_as_access_type(self):
        """A refresh token must not be accepted where an access token is expected."""
        from app.core.security import create_refresh_token, verify_token

        refresh = create_refresh_token("user-123")
        result = verify_token(refresh, token_type="access")
        assert result is None

    @pytest.mark.unit
    def test_access_token_fails_as_refresh_type(self):
        """An access token must not be accepted where a refresh token is expected."""
        from app.core.security import create_access_token, verify_token

        access = create_access_token("user-123")
        result = verify_token(access, token_type="refresh")
        assert result is None

    @pytest.mark.unit
    def test_create_token_pair_structure(self):
        from app.core.security import create_token_pair

        tokens = create_token_pair("user-123")
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] == 900
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)

    @pytest.mark.unit
    def test_create_access_token_with_custom_expiry(self):
        from datetime import timedelta
        from app.core.security import create_access_token, verify_token

        token = create_access_token("user-123", expires_delta=timedelta(hours=1))
        result = verify_token(token)
        assert result == "user-123"

    @pytest.mark.unit
    def test_verify_expired_token_returns_none(self):
        from datetime import timedelta
        from app.core.security import create_access_token, verify_token

        # Negative delta creates an already-expired token
        token = create_access_token("user-123", expires_delta=timedelta(seconds=-1))
        result = verify_token(token)
        assert result is None
