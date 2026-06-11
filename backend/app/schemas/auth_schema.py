"""
Pydantic schemas for authentication endpoints.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Request Schemas ──────────────────────────────────────


class UserRegisterRequest(BaseModel):
    """Payload for POST /auth/register."""

    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")


class UserLoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


# ── Response Schemas ─────────────────────────────────────


class UserResponse(BaseModel):
    """Public user representation — never includes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token payload returned after login."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
