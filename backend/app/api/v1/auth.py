"""
File: backend/app/api/v1/auth.py

AUTHENTICATION ENDPOINTS EXAMPLE

This file shows WHERE and HOW to create API endpoints.
Follow this pattern for other endpoint files.

WHAT TO DO:
1. Create this file exactly as shown
2. Create similar files for: properties.py, users.py, locations.py, reviews.py
3. Import all routers in: app/api/routes.py
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

# Import schemas (request/response structures)
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    LoginResponse,
    UserResponse,
    LogoutResponse,
    RefreshTokenRequest,
)

# Import core utilities (database, config)
from app.core.database import get_db
from app.core.config import settings

# TODO: Create these modules in next tasks
# from app.services.auth_service import AuthService
# from app.crud.user import UserRepository

# ============================================================================
# ROUTER SETUP
# ============================================================================

# Create router for auth endpoints
router = APIRouter(
    prefix="/auth",           # All routes will start with /api/auth
    tags=["Authentication"],  # For API docs organization
)


# ============================================================================
# DEPENDENCY: Current User (for protected endpoints)
# ============================================================================

async def get_current_user(
    token: str = Depends(...)  # TODO: Add JWT dependency
):
    """
    Extract and validate JWT token from request headers.
    
    USAGE in protected endpoints:
    @router.get("/me")
    async def get_current_user(current_user = Depends(get_current_user)):
        return current_user
    
    This ensures only authenticated users can access the endpoint.
    """
    pass


# ============================================================================
# ENDPOINT 1: POST /api/auth/register
# ============================================================================

@router.post(
    "/register",
    response_model=LoginResponse,  # What we return (schemas.auth)
    status_code=status.HTTP_201_CREATED,  # 201 = Created
    summary="Register new user",
    description="Create new user account with email and password",
)
async def register(
    request: UserRegisterRequest,  # Request validation (auto from schema)
    db: Session = Depends(get_db),  # Database connection (auto injected)
):
    """
    Register a new user account.
    
    REQUEST BODY:
    {
        "email": "john@example.com",
        "password": "SecurePass123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "role": "USER"
    }
    
    RESPONSE (201 Created):
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
    
    ERRORS:
    - 400: Email already exists
    - 400: Validation error
    
    ✅ HOW TO IMPLEMENT:
    1. Check if email already exists
    2. Hash the password with bcrypt
    3. Create new User in database
    4. Generate JWT tokens
    5. Return tokens + user data
    """
    
    # TODO: Implement here
    # 1. Check if email exists
    # existing_user = await UserRepository.get_by_email(db, request.email)
    # if existing_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Email already registered",
    #     )
    
    # 2. Hash password
    # hashed_password = await hash_password(request.password)
    
    # 3. Create user in database
    # new_user = await UserRepository.create(
    #     db,
    #     email=request.email,
    #     password_hash=hashed_password,
    #     first_name=request.first_name,
    #     last_name=request.last_name,
    #     phone=request.phone,
    #     role=request.role,
    # )
    
    # 4. Generate tokens
    # access_token = create_access_token(new_user.id)
    # refresh_token = create_refresh_token(new_user.id)
    
    # 5. Return response
    # return LoginResponse(
    #     access_token=access_token,
    #     refresh_token=refresh_token,
    #     token_type="bearer",
    #     expires_in=3600,
    #     user=UserResponse.from_orm(new_user),
    # )
    
    pass


# ============================================================================
# ENDPOINT 2: POST /api/auth/login
# ============================================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,  # 200 = OK
    summary="User login",
    description="Login with email and password to get tokens",
)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user with email/password.
    
    REQUEST BODY:
    {
        "email": "john@example.com",
        "password": "SecurePass123"
    }
    
    RESPONSE (200 OK):
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {...}
    }
    
    ERROR (401 Unauthorized):
    {
        "detail": "Invalid email or password",
        "error_code": "INVALID_CREDENTIALS"
    }
    
    ✅ HOW TO IMPLEMENT:
    1. Find user by email
    2. Verify password hash
    3. Generate JWT tokens
    4. Return tokens + user data
    """
    
    # TODO: Implement here
    # 1. Get user by email
    # user = await UserRepository.get_by_email(db, request.email)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid email or password",
    #     )
    
    # 2. Verify password
    # if not verify_password(request.password, user.password_hash):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid email or password",
    #     )
    
    # 3. Generate tokens
    # access_token = create_access_token(user.id)
    # refresh_token = create_refresh_token(user.id)
    
    # 4. Return response
    # return LoginResponse(
    #     access_token=access_token,
    #     refresh_token=refresh_token,
    #     token_type="bearer",
    #     expires_in=3600,
    #     user=UserResponse.from_orm(user),
    # )
    
    pass


# ============================================================================
# ENDPOINT 3: POST /api/auth/refresh
# ============================================================================

@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Get new access token when current one expires.
    
    REQUEST BODY:
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    
    RESPONSE (200 OK):
    {
        "access_token": "NEW_TOKEN_HERE",
        "refresh_token": "same_or_new_refresh_token",
        ...
    }
    
    WHY? Access tokens expire quickly (15 min) for security.
    Refresh tokens last longer (7 days).
    User doesn't need to login again if refresh token is valid.
    
    ✅ HOW TO IMPLEMENT:
    1. Verify refresh token is valid
    2. Extract user_id from token
    3. Generate new access token
    4. Return new tokens
    """
    
    # TODO: Implement here
    pass


# ============================================================================
# ENDPOINT 4: GET /api/auth/me
# ============================================================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get logged-in user's profile",
)
async def get_me(
    current_user = Depends(get_current_user),  # Auto validates JWT
):
    """
    Get current authenticated user's profile.
    
    HEADERS REQUIRED:
    Authorization: Bearer {access_token}
    
    RESPONSE (200 OK):
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "USER",
        ...
    }
    
    ERROR (401 Unauthorized):
    {
        "detail": "Not authenticated",
        "error_code": "NOT_AUTHENTICATED"
    }
    
    ✅ HOW TO IMPLEMENT:
    1. get_current_user dependency handles JWT validation
    2. Just return the current_user
    """
    
    return current_user


# ============================================================================
# ENDPOINT 5: POST /api/auth/logout
# ============================================================================

@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout user",
    description="Invalidate user's tokens",
)
async def logout(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout authenticated user.
    
    HEADERS REQUIRED:
    Authorization: Bearer {access_token}
    
    RESPONSE (200 OK):
    {
        "message": "Successfully logged out",
        "status": "success"
    }
    
    ✅ HOW TO IMPLEMENT:
    1. Get current user from JWT
    2. Invalidate refresh tokens (optional: add to blacklist)
    3. Return success message
    
    NOTE: With JWT, we don't have server-side sessions to destroy.
    Option 1: Add token to blacklist (requires Redis)
    Option 2: Client just deletes token from localStorage
    """
    
    return LogoutResponse(
        message="Successfully logged out",
        status="success",
    )


# ============================================================================
# NEXT STEPS: Create similar routers for:
# ============================================================================
# 
# ✅ app/api/v1/properties.py
#    - GET /properties          (list with pagination)
#    - GET /properties/{id}     (detail)
#    - POST /properties         (create)
#    - PUT /properties/{id}     (update)
#    - DELETE /properties/{id}  (delete)
#    - GET /properties/search/nearby (geospatial search)
#
# ✅ app/api/v1/users.py
#    - GET /users/{id}          (profile)
#    - PUT /users/{id}          (update)
#    - POST /users/{id}/favorites
#    - DELETE /users/{id}/favorites/{prop_id}
#
# ✅ app/api/v1/locations.py
#    - GET /locations
#    - GET /locations/{id}
#    - GET /locations/{id}/properties
#
# ✅ app/api/v1/reviews.py
#    - GET /properties/{id}/reviews
#    - POST /properties/{id}/reviews
#    - PUT /reviews/{id}
#    - DELETE /reviews/{id}
#

