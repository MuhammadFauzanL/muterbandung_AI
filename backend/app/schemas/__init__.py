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
from app.schemas.user_preference_schema import (  # noqa: F401
    UserPreferenceResponse,
    UserPreferenceUpsertRequest,
)

# Phase 3+: Import additional schemas as they are created, e.g.:
# from app.schemas.destination_schema import DestinationCreate, DestinationResponse
