"""
Pydantic schemas for user preference onboarding and personalization.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _CamelModel(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
    )


class PlacePreference(str, Enum):
    """Canonical place preference values persisted by the API."""

    nature = "nature"
    culinary = "culinary"
    shopping = "shopping"
    history = "history"
    culture = "culture"
    wildlife = "wildlife"
    religion = "religion"
    education = "education"
    family = "family"


class ActivityPreference(str, Enum):
    """Canonical activity preference values persisted by the API."""

    healing = "healing"
    photo_spot = "photo_spot"
    adventure = "adventure"


class VisitorTargetPreference(str, Enum):
    """Canonical visitor target preference values persisted by the API."""

    family = "family"
    child_friendly = "child_friendly"


class AtmospherePreference(str, Enum):
    """Canonical atmosphere preference values persisted by the API."""

    indoor = "indoor"
    outdoor = "outdoor"
    night = "night"


class UserPreferenceUpsertRequest(_CamelModel):
    """Request body for creating/updating the current user's preferences."""

    favoritePlaceTypes: list[PlacePreference] = Field(
        default_factory=list,
        max_length=3,
    )
    favoriteActivities: list[ActivityPreference] = Field(
        default_factory=list,
        max_length=2,
    )
    visitorTarget: Optional[VisitorTargetPreference] = None
    preferredAtmospheres: list[AtmospherePreference] = Field(default_factory=list)
    freeOnly: bool = False

    @property
    def favorite_place_types(self) -> list[str]:
        return self.favoritePlaceTypes

    @property
    def favorite_activities(self) -> list[str]:
        return self.favoriteActivities

    @property
    def visitor_target(self) -> Optional[str]:
        return self.visitorTarget

    @property
    def preferred_atmospheres(self) -> list[str]:
        return self.preferredAtmospheres

    @property
    def free_only(self) -> bool:
        return self.freeOnly


class UserPreferenceResponse(UserPreferenceUpsertRequest):
    """Persisted preference response."""

    id: UUID
    userId: UUID
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_entity(cls, preference) -> "UserPreferenceResponse":
        """Build an API response DTO from the SQLAlchemy preference entity."""
        return cls(
            id=preference.id,
            userId=preference.user_id,
            favoritePlaceTypes=preference.favorite_place_types or [],
            favoriteActivities=preference.favorite_activities or [],
            visitorTarget=preference.visitor_target,
            preferredAtmospheres=preference.preferred_atmospheres or [],
            freeOnly=preference.free_only,
            createdAt=preference.created_at,
            updatedAt=preference.updated_at,
        )
