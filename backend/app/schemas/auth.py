"""
File: backend/app/schemas/auth.py

Authentication request and response schemas.

WHY? These define:
- What data we accept for login/register
- What we send back to the frontend
- Auto-validates email format, password requirements
- Prevents invalid data from being processed
"""

import re
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, validator
from .common import TimestampMixin


# ============================================================================
# REQUEST SCHEMAS (What frontend SENDS to backend)
# ============================================================================


class UserRegisterRequest(BaseModel):
    """
    Request body for POST /auth/register

    EXAMPLE REQUEST:
    {
        "email": "john@example.com",
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "role": "USER"
    }
    """

    # FIELD: email
    # RULES: Must be valid email format (validated by EmailStr)
    # EXAMPLES: john@example.com, jane_doe@company.co.uk, user+tag@domain.org
    # ERROR CODE: INVALID_EMAIL
    email: EmailStr = Field(..., description="User email (must be valid email format)")
    
    # FIELD: password
    # RULES:
    #   - Minimum 8 characters, Maximum 100 characters
    #   - Must contain at least 1 uppercase letter (A-Z)
    #   - Must contain at least 1 lowercase letter (a-z)
    #   - Must contain at least 1 digit (0-9)
    #   - Must contain at least 1 special character (!@#$%^&*...)
    # EXAMPLES: SecurePass123!, MyP@ssw0rd, Test!2024Pass
    # ERROR CODE: WEAK_PASSWORD
    password: str = Field(..., min_length=8, max_length=100, description="Strong password (8-100 chars: uppercase, lowercase, digit, special)")
    
    # FIELD: first_name
    # RULES:
    #   - Minimum 1 character, Maximum 50 characters
    #   - Required (cannot be null or empty)
    # EXAMPLES: John, Mary-Jane, José, 李
    # ERROR CODES: VALUE_TOO_SHORT, VALUE_TOO_LONG
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name (1-50 characters)")
    
    # FIELD: last_name
    # RULES:
    #   - Minimum 1 character, Maximum 50 characters
    #   - Required (cannot be null or empty)
    # EXAMPLES: Doe, Smith-Johnson, García, 王
    # ERROR CODES: VALUE_TOO_SHORT, VALUE_TOO_LONG
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name (1-50 characters)")
    
    # FIELD: phone
    # RULES:
    #   - Optional (can be null or empty string)
    #   - When provided, must contain 10-15 digits
    #   - Accepts formats: +1234567890, 123-456-7890, (123) 456-7890, +1 (234) 567-8901
    #   - Formatting chars (+, -, (, ), spaces) are stripped before validation
    # EXAMPLES: +1234567890, 123-456-7890, (123) 456-7890, +1-234-567-8901
    # ERROR CODE: INVALID_PHONE
    phone: Optional[str] = Field(None, description="Phone number (optional: 10-15 digits, e.g., +1234567890 or 123-456-7890)")
    
    # FIELD: role
    # RULES:
    #   - Must be one of: USER, BROKER, OWNER
    #   - Defaults to "USER" if not provided
    #   - Case-sensitive (only uppercase values allowed)
    # EXAMPLES: USER, BROKER, OWNER
    # ERROR CODE: INVALID_CHOICE
    role: Literal["USER", "BROKER", "OWNER"] = Field("USER", description="User role (USER, BROKER, or OWNER)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "role": "USER",
            }
        }

    @validator("phone", pre=True, always=True)
    @classmethod
    def validate_phone(cls, p: Optional[str]) -> Optional[str]:
        """Validate phone number format (optional field)"""
        # Allow None or empty string (optional field)
        if p is None or p == "":
            return None

        # Remove common formatting characters
        cleaned = re.sub(r"[\s\-().+]", "", p)

        # Check length after cleaning
        if not (10 <= len(cleaned) <= 15):
            raise ValueError("Phone number must have 10-15 digits (optional field)")

        # Check if all characters are digits
        if not cleaned.isdigit():
            raise ValueError(
                "Phone number must contain only digits and formatting characters (+, -, (, ), spaces)"
            )

        return p

    @validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password has uppercase, lowercase, and number.

        WHY? Enforce strong passwords for security.
        """
        special_chars_pattern = re.compile(r"[!@#$%^&*()_+{}[\]:;<>,.?/\\|]")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        if not special_chars_pattern.search(v):
            raise ValueError("Password must contain 1 or more special symbol.")
        return v


class UserLoginRequest(BaseModel):
    """
    Request body for POST /auth/login

    Authenticates user with email and password.
    Returns access_token and refresh_token if credentials are valid.
    
    EXAMPLE REQUEST:
    {
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    """

    # FIELD: email
    # RULES: Must be valid email format (validated by EmailStr)
    # EXAMPLES: john@example.com, user@company.org
    # ERROR CODE: INVALID_EMAIL
    email: EmailStr = Field(..., description="User email (must be valid email format)")
    
    # FIELD: password
    # RULES: User's account password (no additional length restrictions on login)
    # EXAMPLES: SecurePass123!
    # NOTE: Password strength requirements are enforced at registration time
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {"example": {"email": "john@example.com", "password": "SecurePass123!"}}


class UserUpdateRequest(BaseModel):
    """
    Request body for PUT /users/{user_id}

    All fields are OPTIONAL - only update what you send.

    EXAMPLE REQUEST:
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "profile_picture": "https://example.com/image.jpg"
    }
    """

    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    profile_picture: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "profile_picture": "https://example.com/image.jpg",
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Request body for POST /auth/refresh

    EXAMPLE REQUEST:
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }

    WHY? Get a new access token without entering password again.
    Access tokens expire quickly (15 min), refresh tokens last longer (7 days).
    """

    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {
            "example": {"refresh_token": "p298u3419r8ywehdsiuh1p3982whedsijhb39p8wqdisuvbli"}
        }


# ============================================================================
# RESPONSE SCHEMAS (What backend SENDS back to frontend)
# ============================================================================


class UserResponse(TimestampMixin):
    """
    User data returned from API.

    USED IN:
    - /auth/register response
    - /auth/me response
    - /users/{user_id} response

    EXAMPLE RESPONSE:
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "role": "USER",
        "profile_picture": null,
        "is_active": true,
        "created_at": "2024-01-03T10:30:00Z",
        "updated_at": "2024-01-03T10:30:00Z"
    }
    """

    id: str = Field(..., description="User unique ID (UUID)")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role")
    profile_picture: Optional[str] = Field(None, description="Profile image URL")
    is_active: bool = Field(True, description="Is user active")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "role": "USER",
                "profile_picture": "null",
                "is_active": "true",
                "created_at": "2024-01-03T10:30:00Z",
                "updated_at": "2024-01-03T10:30:00Z",
            }
        }

    class Config(TimestampMixin.Config):
        from_attributes = True  # Allow conversion from SQLAlchemy ORM models


class TokenResponse(BaseModel):
    """
    Token data returned after login/register.

    USED IN:
    - /auth/login response
    - /auth/register response

    EXAMPLE RESPONSE:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "john@example.com",
            ...
        }
    }

    WHY?
    - access_token: Use this in Authorization header: "Bearer {token}"
    - refresh_token: Use to get new access token when it expires
    - token_type: Always "bearer" for JWT
    - expires_in: Seconds until token expires (3600 = 1 hour)
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(3600, description="Token expiration in seconds")
    user: UserResponse = Field(..., description="User data")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": "3600",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "john@example.com",
                },
            }
        }


class LoginResponse(BaseModel):
    """
    Complete login response (tokens + user data).

    STRUCTURE:
    POST /auth/login returns this
    """

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "pdiaspfuhxvijnapiduhsapudfqiweudfhpahdspinqfieuwhpinoais3982u",
                "refresh_token": "jhdsoiu132089qweuoifsduhf349qew8hfdwuih209wehdfy9ewdicnfewd3892wudfr8dujchvf",
                "token_type": "bearer",
                "expires_in": "3600",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1234567890",
                    "role": "USER",
                    "profile_picture": "null",
                    "is_active": "true",
                    "created_at": "2024-01-03T10:30:00Z",
                    "updated_at": "2024-01-03T10:30:00Z",
                },
            }
        }

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(3600, description="Seconds until expiration")
    user: UserResponse = Field(..., description="Logged in user")


class LogoutResponse(BaseModel):
    """
    Logout response.

    EXAMPLE RESPONSE:
    {
        "message": "Successfully logged out",
        "status": "success"
    }
    """

    message: str = Field(..., description="Logout message")
    status: str = Field("success", description="Status")

    class Config:
        json_schema_extra = {"example": {"message": "Successfully logged out", "status": "success"}}


# ============================================================================
# JWT PAYLOAD SCHEMA (Internal - for token verification)
# ============================================================================


class TokenPayload(BaseModel):
    """
    Payload inside JWT token.

    WHY? When we decode JWT, we get this structure.
    Use this to verify token contains required fields.

    INTERNAL USE ONLY (not sent to clients)

    EXAMPLE PAYLOAD (when you decode the JWT):
    {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "exp": 1704283800,
        "iat": 1704280200,
        "type": "access"
    }
    """

    sub: str = Field(..., description="Subject (user_id)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    type: str = Field(..., description="Token type: 'access' or 'refresh'")

    class Config:
        json_schema_extra = {
            "example": {
                "sub": "550e8400-e29b-41d4-a716-446655440000",
                "exp": 1704283800,
                "iat": 1704280200,
                "type": "access",
            }
        }
