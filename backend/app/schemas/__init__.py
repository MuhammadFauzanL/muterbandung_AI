"""
Schemas package.
Import all Pydantic schemas here for convenient access.
"""

from app.schemas.auth_schema import (  # noqa: F401
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)

# Phase 3+: Import additional schemas as they are created, e.g.:
# from app.schemas.destination_schema import DestinationCreate, DestinationResponse

