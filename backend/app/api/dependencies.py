"""
File: backend/app/api/dependencies.py

Shared dependencies for all endpoints.

WHY? Dependencies are reusable functions injected into endpoints:
- Current user verification (from JWT token)
- Database session
- Query parameters
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

# ============================================================================
# JWT SECURITY SCHEME
# ============================================================================

# This makes FastAPI show "Authorize" button in Swagger UI
security = HTTPBearer(description="JWT token in Authorization header")


# ============================================================================
# DEPENDENCY: Get Current User from JWT Token
# ============================================================================


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Extract and validate JWT token from Authorization header.

    USAGE in protected endpoints:
    @router.get("/me")
    async def get_me(current_user = Depends(get_current_user)):
        return current_user

    This ensures only authenticated users can access the endpoint.

    REQUEST HEADER:
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    ERROR if token is:
    - Missing
    - Invalid
    - Expired
    - Wrong type
    """

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]  # Remove "Bearer " prefix

    # Verify token and get user_id
    user_id = verify_token(token, token_type="access")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch the actual User object from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Return the User ORM object (will be converted to UserResponse by schema)
    return user


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
        ...
    ):
        if current_user:
            # User is logged in
            return properties_for_user(current_user)
        else:
            # User not logged in - show public properties
            return public_properties()
    """

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    user_id = verify_token(token, token_type="access")

    if user_id is None:
        return None

    return {"user_id": user_id}


# ============================================================================
# DEPENDENCY: Verify Refresh Token
# ============================================================================


async def verify_refresh_token(
    request: Request,
) -> str:
    """
    Verify refresh token and return user_id.

    USAGE in /auth/refresh endpoint:
    @router.post("/refresh")
    async def refresh(
        user_id = Depends(verify_refresh_token),
    ):
        # Create new access token
        access_token = create_access_token(user_id)
        return {...}

    REQUEST HEADER:
    Authorization: Bearer {refresh_token}
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


# ============================================================================
# DEPENDENCY: Check User Role
# ============================================================================


async def require_broker_role(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ensure user has BROKER role.

    USAGE:
    @router.post("/properties")
    async def create_property(
        request: PropertyCreateRequest,
        current_user = Depends(require_broker_role),  # Only brokers can create
    ):
        ...
    """

    # TODO: Check user role in database
    # user = db.query(User).filter(User.id == current_user["id"]).first()
    # if user.role != "BROKER":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Only brokers can create properties"
    #     )

    return current_user


async def require_owner_or_admin(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ensure user is owner or admin.

    USAGE:
    @router.delete("/{id}")
    async def delete_property(
        id: str,
        current_user = Depends(require_owner_or_admin),  # Only owner/admin can delete
    ):
        ...
    """

    # TODO: Check user role in database
    # user = db.query(User).filter(User.id == current_user["id"]).first()
    # if user.role not in ["OWNER", "ADMIN"]:
    #     raise HTTPException(status_code=403, detail="Forbidden")

    return current_user
