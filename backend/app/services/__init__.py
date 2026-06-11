"""
Services package.
Business-logic layer that sits between API routes and database/models.
"""

from app.services.auth_service import (  # noqa: F401
    register_user,
    authenticate_user,
    get_user_by_id,
)

# Phase 3+: Import additional services as they are created, e.g.:
# from app.services.destination_service import DestinationService

