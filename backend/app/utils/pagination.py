"""
Pagination utilities for database queries.
"""

from sqlalchemy.orm import Query


def paginate(query: Query, page: int = 1, limit: int = 10) -> tuple:
    """
    Apply pagination to a SQLAlchemy query.

    Returns:
        tuple: (items, total_count)
    """
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100  # prevent excessive page sizes

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    return items, total
