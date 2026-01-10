"""
File: backend/app/core/security.py

JWT token creation and verification.
Password hashing utilities.

WHY? Centralized security logic:
- Create tokens for login
- Verify tokens for protected endpoints
- Hash passwords securely
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import hashlib
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings

# ============================================================================
# PASSWORD HASHING
# ============================================================================

# Create password hasher with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using SHA256 + bcrypt.
    
    First hashes with SHA256 (always 64 bytes), then bcrypt.
    This ensures bcrypt never receives input longer than 72 bytes.
    
    USAGE:
    hashed = hash_password("SecurePass123")
    # Returns: $2b$12$...long hash string...
    """
    # Pre-hash with SHA256 to normalize length (always 64 bytes)
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Now bcrypt the SHA256 hash (always 64 bytes, well under 72-byte limit)
    return pwd_context.hash(sha256_hash)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plaintext password against bcrypt hash.
    
    Uses same SHA256 + bcrypt approach as hash_password.
    
    USAGE:
    if verify_password("SecurePass123", user.password_hash):
        print("Password correct!")
    """
    # Apply same SHA256 pre-hash for consistency
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(sha256_hash, hashed_password)


# ============================================================================
# JWT TOKEN FUNCTIONS
# ============================================================================

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    USAGE:
    token = create_access_token(user_id)
    # Returns: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    
    WHY?
    - subject: Usually user_id
    - expires_delta: How long token lasts (default 15 min)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Create JWT refresh token.
    
    USAGE:
    refresh_token = create_refresh_token(user_id)
    
    WHY?
    - Access tokens expire quickly (15 min)
    - Refresh tokens last longer (7 days)
    - User uses refresh token to get new access token
    """
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """
    Verify JWT token and return user_id.
    
    USAGE:
    user_id = verify_token(token, token_type="access")
    if user_id:
        print(f"Token valid, user: {user_id}")
    else:
        print("Token invalid or expired")
    
    PARAMS:
    - token: The JWT token to verify
    - token_type: "access" or "refresh"
    
    RETURNS:
    - user_id if token is valid
    - None if token is invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        
        # Check token type matches
        if payload.get("type") != token_type:
            return None
        
        subject: str = payload.get("sub")
        
        if subject is None:
            return None
        
        return subject
    
    except jwt.ExpiredSignatureError:
        # Token expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid (wrong signature, malformed, etc)
        return None


# ============================================================================
# OPTIONAL: Token response helper
# ============================================================================

def create_token_pair(user_id: str) -> dict:
    """
    Create both access and refresh tokens.
    
    USAGE:
    tokens = create_token_pair(user.id)
    # Returns:
    # {
    #     "access_token": "eyJ...",
    #     "refresh_token": "eyJ...",
    #     "token_type": "bearer",
    #     "expires_in": 900  # 15 minutes in seconds
    # }
    """
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900  # 15 minutes
    }

