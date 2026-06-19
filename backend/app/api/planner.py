"""
Planner endpoints.

- POST /planner/insight — generate contextual AI insight for selected destinations
"""

from __future__ import annotations

from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.planner_insight_service import generate_planner_insight
from app.utils.response import success_response

router = APIRouter(prefix="/planner")


class InsightRequest(BaseModel):
    destination_ids: list[str] = []


@router.post("/insight")
def planner_insight(
    body: InsightRequest,
    db: Session = Depends(get_db),
):
    """Generate a contextual AI insight based on selected planner destinations."""
    data = generate_planner_insight(
        db,
        destination_ids=body.destination_ids,
    )
    return success_response(
        data=data,
        message="Planner insight generated successfully",
    )
