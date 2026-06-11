"""
Authentication service – business logic for register, login, and user lookup.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ForbiddenException, UnauthorizedException
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth_schema import UserRegisterRequest

logger = logging.getLogger(__name__)


def register_user(db: Session, payload: UserRegisterRequest) -> User:
    """
    Register a new user.

    Raises:
        AppException 409 if email is already taken.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise AppException(status_code=409, message="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("New user registered: %s", user.email)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user by email and password.

    Raises:
        UnauthorizedException if credentials are invalid.
        ForbiddenException if user account is deactivated.
    """
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise UnauthorizedException(message="Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise UnauthorizedException(message="Invalid email or password")

    if not user.is_active:
        raise ForbiddenException(message="User account is deactivated")

    return user


def get_user_by_id(db: Session, user_id: UUID) -> User:
    """
    Look up a user by their UUID.

    Returns None if not found.
    """
    return db.query(User).filter(User.id == user_id).first()
