"""
File: backend/app/api/dependencies.py

Shared dependencies for all endpoints.

WHY? Dependencies are reusable functions injected into endpoints:
- Current user verification (from JWT token)
- Database session
- Role-based access control (RBAC)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db, get_redis
from app.core.security import verify_token
from app.models.user import User

# ============================================================================
# JWT SECURITY SCHEME
# ============================================================================

security = HTTPBearer(description="JWT token in Authorization header")


# ============================================================================
# DEPENDENCY: Get Current User from JWT Token
# ============================================================================


async def get_current_user(
    request: Request,
    rds=Depends(get_redis),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate JWT token from Authorization header.
    Returns the full User ORM object.
    USAGE in protected endpoints:
    @router.get("/me")
    async def get_me(current_user = Depends(get_current_user)):
        return current_user
    """

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]  # Remove "Bearer " prefix

    if rds.get(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token has been revoked"
        )
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


def rate_limit(request: Request, rds=Depends(get_redis)):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    count = rds.incr(key)
    if count == 1:
        rds.expire(key, 60)
    if count > 10:
        raise HTTPException(429, "Too many requests")


# ============================================================================
# RBAC: Role checker factory
# ============================================================================


def require_roles(*roles: str):
    """
    Factory function that returns a dependency checking for allowed roles.

    WHY factory pattern?
    - Avoids writing a separate function for every role combination
    - Single source of truth for role enforcement
    - Clean usage at endpoint level

    USAGE:
    # Only admins
    @router.delete("/{id}")
    async def delete_user(current_user = Depends(require_roles("ADMIN"))):
        ...

    # Brokers or admins
    @router.post("/properties")
    async def create_property(current_user = Depends(require_roles("BROKER", "ADMIN"))):
        ...

    # Any authenticated user with specific roles
    @router.get("/dashboard")
    async def dashboard(current_user = Depends(require_roles("USER", "BROKER", "OWNER", "ADMIN"))):
        ...
    """
    allowed_roles: List[str] = [r.upper() for r in roles]

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.upper() not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}. Your role: {current_user.role}",
            )
        return current_user

    return role_checker


# ============================================================================
# PREDEFINED ROLE DEPENDENCIES
# (Convenience wrappers around require_roles for common patterns)
# ============================================================================

# Any authenticated user
require_authenticated = get_current_user

# Only admins
require_admin = require_roles("ADMIN")

# Brokers and admins (property management)
require_broker = require_roles("BROKER", "ADMIN")

# Owners and admins (property ownership actions)
require_owner = require_roles("OWNER", "ADMIN")

# Brokers, owners, and admins
require_broker_or_owner = require_roles("BROKER", "OWNER", "ADMIN")


# ============================================================================
# DEPENDENCY: Optional Authentication
# ============================================================================


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Optional authentication - endpoint works with or without token.

    USAGE:
    @router.get("/properties")
    async def list_properties(
        current_user = Depends(get_current_user_optional),
    ):
        if current_user:
            return properties_for_logged_in_user(current_user)
        return public_properties()
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        return None

    return db.query(User).filter(User.id == user_id).first()


# ============================================================================
# DEPENDENCY: Verify Refresh Token
# ============================================================================


async def verify_refresh_token(request: Request) -> str:
    """
    Verify refresh token and return user_id.

    USAGE in /auth/refresh endpoint:
    @router.post("/refresh")
    async def refresh(user_id = Depends(verify_refresh_token)):
        access_token = create_access_token(user_id)
        return {...}

    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]
    user_id = verify_token(token, token_type="refresh")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
