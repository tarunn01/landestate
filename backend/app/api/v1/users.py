"""
File: backend/app/api/v1/users_endpoints.py

USER ENDPOINTS - Pure FastAPI with Class-Based Resources

RESOURCES:
- UserResource: GET (profile), PUT (update)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import UserResponse, UserUpdateRequest
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(tags=["Users"])


# ============================================================================
# RESOURCE CLASS: UserResource (Get and Update)
# ============================================================================


class UserResource:
    """Resource for managing individual user profiles."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _get_user(self, user_id: str) -> User:
        """Helper to get user by ID or raise 404."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_profile(self, user_id: str) -> UserResponse:
        """Get user profile."""
        user = self._get_user(user_id)
        return UserResponse.model_validate(user)

    async def update_profile(
        self,
        user_id: str,
        user_in: UserUpdateRequest,
        current_user: User,
    ) -> UserResponse:
        """Update user profile."""
        user = self._get_user(user_id)

        # Only user can update their own profile
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this profile",
            )

        # Update fields
        for field, value in user_in.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)


# ============================================================================
# ENDPOINTS
# ============================================================================

# NOTE: /me must come BEFORE /{user_id} because FastAPI matches routes in order
# If /{user_id} comes first, it will match /me as user_id="me" and return 404


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """GET /me - Get current authenticated user's profile"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    resource: UserResource = Depends(),
):
    """GET /users/{user_id} - Get user profile"""
    return await resource.get_profile(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_in: UserUpdateRequest,
    current_user=Depends(get_current_user),
    resource: UserResource = Depends(),
):
    """PUT /users/{user_id} - Update user profile"""
    return await resource.update_profile(user_id, user_in, current_user)
