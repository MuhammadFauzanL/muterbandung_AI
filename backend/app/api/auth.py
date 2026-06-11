"""
Authentication endpoints.

- POST /auth/register  — create a new user account
- POST /auth/login     — authenticate and receive a JWT token
- GET  /auth/me        — retrieve the current user from a valid token
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user
from app.database import get_db
from app.schemas.auth_schema import (
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import authenticate_user, register_user
from app.utils.response import success_response

router = APIRouter()


@router.post("/register", status_code=201)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **name**: full name (required)
    - **email**: valid email, must be unique
    - **password**: minimum 8 characters
    """
    user = register_user(db, payload)
    user_data = UserResponse.model_validate(user)

    return success_response(
        data=user_data.model_dump(mode="json"),
        message="Register success",
        status_code=201,
    )


@router.post("/login")
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email and password.

    Returns a JWT access token and user profile on success.
    """
    user = authenticate_user(db, payload.email, payload.password)

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    user_data = UserResponse.model_validate(user)
    token_data = TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_data,
    )

    return success_response(
        data=token_data.model_dump(mode="json"),
        message="Login success",
    )


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's profile.

    Requires a valid `Authorization: Bearer <token>` header.
    """
    user_data = UserResponse.model_validate(current_user)

    return success_response(
        data=user_data.model_dump(mode="json"),
        message="Current user retrieved successfully",
    )
