"""
File: backend/app/api/v1/auth.py

AUTHENTICATION ENDPOINTS - Pure FastAPI with Class-Based Resources

Pattern:
- Resource class groups dependencies
- Endpoint functions inject resource and call methods
- Clean, readable, no external libraries
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    LoginResponse,
    UserResponse,
    LogoutResponse,
    RefreshTokenRequest,
)
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_token_pair,
    verify_token,
)
from app.models.user import User
from app.api.dependencies import get_current_user


router = APIRouter(tags=["Authentication"])


# ============================================================================
# RESOURCE CLASS: Auth (Register, Login, Logout)
# ============================================================================


class Auth:
    """Authentication resource - handles user login, registration, and logout."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def register(self, request: UserRegisterRequest) -> LoginResponse:
        """Register a new user account."""
        existing_user = self.db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = hash_password(request.password)
        new_user = User(
            email=request.email,
            password_hash=hashed_password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role=request.role,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        tokens = create_token_pair(str(new_user.id))
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=3600,
            user=UserResponse.from_orm(new_user),
        )

    async def login(self, request: UserLoginRequest) -> LoginResponse:
        """Authenticate user with email/password."""
        user = self.db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        tokens = create_token_pair(str(user.id))
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=3600,
            user=UserResponse.from_orm(user),
        )

    async def logout(self) -> LogoutResponse:
        """Logout user."""
        return LogoutResponse(
            message="Successfully logged out",
            status="success",
        )


# ============================================================================
# RESOURCE CLASS: AuthMe (Current user profile)
# ============================================================================


class AuthMe:
    """Current user profile resource."""

    def __init__(self, current_user=Depends(get_current_user)):
        self.current_user = current_user

    async def get_me(self) -> UserResponse:
        """Get current user profile."""
        return self.current_user

    async def update_me(self, request) -> UserResponse:
        """Update current user profile."""
        # TODO: Implement profile update
        pass


# ============================================================================
# RESOURCE CLASS: AuthRefresh (Refresh token)
# ============================================================================


class AuthRefresh:
    """Token refresh resource."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def refresh(self, request: RefreshTokenRequest) -> LoginResponse:
        """Get new access token using refresh token."""
        user_id = verify_token(request.refresh_token, token_type="refresh")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        tokens = create_token_pair(str(user.id))
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=3600,
            user=UserResponse.from_orm(user),
        )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    auth: Auth = Depends(),
):
    """POST /auth - Register new user"""
    return await auth.register(request)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: UserLoginRequest,
    auth: Auth = Depends(),
):
    """POST /auth/login - User login"""
    return await auth.login(request)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user=Depends(get_current_user),
    auth: Auth = Depends(),
):
    """POST /auth/logout - Logout user"""
    return await auth.logout()


@router.get("/me", response_model=UserResponse)
async def get_me(
    auth_me: AuthMe = Depends(),
):
    """GET /auth/me - Get current user"""
    return await auth_me.get_me()


@router.patch("/me", response_model=UserResponse)
async def update_me(
    request,
    auth_me: AuthMe = Depends(),
):
    """PATCH /auth/me - Update current user profile"""
    return await auth_me.update_me(request)


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_refresh: AuthRefresh = Depends(),
):
    """POST /auth/refresh - Get new access token"""
    return await auth_refresh.refresh(request)
