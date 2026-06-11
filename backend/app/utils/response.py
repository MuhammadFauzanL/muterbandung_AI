"""
Standard API response helpers.
Every endpoint should return one of these formats for consistency.
"""

from __future__ import annotations

from typing import Any, List, Optional


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> dict:
    """Build a standard success response."""
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
    }


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    errors: Optional[List] = None,
) -> dict:
    """Build a standard error response."""
    return {
        "statusCode": status_code,
        "message": message,
        "errors": errors or [],
    }


def paginated_response(
    data: list,
    page: int,
    limit: int,
    total: int,
    message: str = "Success",
    status_code: int = 200,
) -> dict:
    """Build a standard paginated response."""
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages,
        },
    }
