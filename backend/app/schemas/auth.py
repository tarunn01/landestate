"""
File: backend/app/schemas/auth.py

Authentication request and response schemas.

WHY? These define:
- What data we accept for login/register
- What we send back to the frontend
- Auto-validates email format, password requirements
- Prevents invalid data from being processed
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, validator, field_validator
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
    email: EmailStr = Field(..., description="User email (must be valid)")
    password: str = Field(
        ..., 
        min_length=8,
        max_length=100,
        description="Password (min 8 chars)"
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's first name"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's last name"
    )
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    role: Literal["USER", "BROKER", "OWNER"] = Field(
        "USER",
        description="User role"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password has uppercase, lowercase, and number.
        
        WHY? Enforce strong passwords for security.
        """
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v


class UserLoginRequest(BaseModel):
    """
    Request body for POST /auth/login
    
    EXAMPLE REQUEST:
    {
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    """
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


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
        from_attributes = True  # Convert SQLAlchemy model to this schema


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


class LoginResponse(BaseModel):
    """
    Complete login response (tokens + user data).
    
    STRUCTURE:
    POST /auth/login returns this
    """
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


