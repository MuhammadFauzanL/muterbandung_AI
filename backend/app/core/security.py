"""
Security utilities – password hashing, JWT token management, and auth dependency.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.database import get_db

# ── Password Hashing ────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ───────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Payload includes:
        sub: user_id (str)
        email: user email
        exp: expiration timestamp
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Raises UnauthorizedException if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise UnauthorizedException(message="Invalid or expired token")


# ── FastAPI Dependency ───────────────────────────────────

# HTTPBearer shows a simple "Bearer Token" text field in Swagger UI
# instead of OAuth2's username/password form.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency that extracts and validates the current user
    from the Authorization Bearer token.

    Usage:
        @router.get("/protected")
        def protected(current_user = Depends(get_current_user)):
            ...
    """
    # Avoid circular import – import here
    from app.models.user import User

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id: Optional[str] = payload.get("sub")

    if user_id is None:
        raise UnauthorizedException(message="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise UnauthorizedException(message="Invalid or expired token")

    if not user.is_active:
        raise UnauthorizedException(message="User account is deactivated")

    return user

