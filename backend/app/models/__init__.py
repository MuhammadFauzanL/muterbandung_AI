"""
Models package.
Import all models here so Alembic can detect them via Base.metadata.
"""

from app.models.user import User  # noqa: F401
from app.models.user_preference import UserPreference  # noqa: F401
from app.models.user_favorite import UserFavorite  # noqa: F401
from app.models.user_destination_event import UserDestinationEvent  # noqa: F401

# Destination domain models (Phase 2)
from app.models.destination import Destination  # noqa: F401
from app.models.destination_media import DestinationMedia  # noqa: F401
from app.models.destination_label import DestinationLabel  # noqa: F401
from app.models.destination_facility import DestinationFacility  # noqa: F401

