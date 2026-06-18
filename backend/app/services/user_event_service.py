"""
Service layer for user interaction event tracking and behavioral profiling.

Behavioral profile is built from the last 90 days of events using
exponential time decay (half-life ~30 days). More recent interactions
have stronger influence on recommendations.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.destination import Destination
from app.models.user_destination_event import UserDestinationEvent


# ── Constants ────────────────────────────────────────────

EVENT_RETENTION_DAYS = 90

# Base weight per event type (before time decay)
EVENT_WEIGHTS: dict[str, float] = {
    "favorite_add": 5.0,
    "planner_add": 4.0,
    "view_detail": 2.0,
    "search": 1.0,
    "filter_apply": 1.0,
    "favorite_remove": -2.0,  # negative signal
}

# Exponential decay: half-life of 30 days
# decay_factor = exp(-lambda * days_ago)
# At half_life: exp(-lambda * 30) = 0.5 → lambda = ln(2)/30
DECAY_LAMBDA = math.log(2) / 30.0


# ── Event tracking ───────────────────────────────────────


def track_event(
    db: Session,
    user_id: UUID,
    event_type: str,
    destination_external_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> UserDestinationEvent:
    """Record a single interaction event.

    destination_external_id is resolved to internal UUID if provided.
    Events with unknown destination IDs are stored with destination_id=None.
    """
    dest_internal_id: Optional[UUID] = None
    if destination_external_id:
        dest = (
            db.query(Destination.id)
            .filter(Destination.external_id == destination_external_id)
            .first()
        )
        if dest:
            dest_internal_id = dest[0]

    event = UserDestinationEvent(
        user_id=user_id,
        destination_id=dest_internal_id,
        event_type=event_type,
        event_metadata=metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# ── Behavioral profile builder ───────────────────────────


def _time_decay(created_at: datetime) -> float:
    """Calculate exponential decay multiplier based on event age."""
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    days_ago = max(0.0, (now - created_at).total_seconds() / 86400.0)
    return math.exp(-DECAY_LAMBDA * days_ago)


def build_behavior_profile(
    db: Session,
    user_id: UUID,
) -> dict[str, float]:
    """Aggregate recent events into an intent/label interest profile.

    Returns a dict mapping intent/label names to normalized scores (0-100).

    Algorithm:
    1. Fetch ALL events from last 90 days (including search with dest=None)
    2. For destination-linked events: get labels/intent from destination
    3. For search events (dest=None): match query keywords to known labels
    4. Multiply event base weight × time decay → add to intent/label scores
    5. Normalize top score to 100
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=EVENT_RETENTION_DAYS)

    # Fetch destination-linked events
    dest_events = (
        db.query(UserDestinationEvent)
        .filter(
            and_(
                UserDestinationEvent.user_id == user_id,
                UserDestinationEvent.destination_id.isnot(None),
                UserDestinationEvent.created_at >= cutoff,
            )
        )
        .options(
            joinedload(UserDestinationEvent.destination).joinedload(
                Destination.labels
            )
        )
        .all()
    )

    # Fetch search/filter events (destination_id is NULL)
    search_events = (
        db.query(UserDestinationEvent)
        .filter(
            and_(
                UserDestinationEvent.user_id == user_id,
                UserDestinationEvent.destination_id.is_(None),
                UserDestinationEvent.event_type.in_(["search", "filter_apply"]),
                UserDestinationEvent.created_at >= cutoff,
            )
        )
        .all()
    )

    if not dest_events and not search_events:
        return {}

    scores: dict[str, float] = defaultdict(float)

    # ── Process destination-linked events ──
    for event in dest_events:
        base_weight = EVENT_WEIGHTS.get(event.event_type, 1.0)
        decay = _time_decay(event.created_at)
        weighted = base_weight * decay

        dest = event.destination
        if dest is None:
            continue

        intents_labels: list[str] = []
        if dest.labels:
            if dest.labels.primary_intent:
                intents_labels.append(dest.labels.primary_intent)
            if dest.labels.core_labels:
                if isinstance(dest.labels.core_labels, list):
                    intents_labels.extend(dest.labels.core_labels)
                elif isinstance(dest.labels.core_labels, str):
                    intents_labels.extend(dest.labels.core_labels.split(";"))

        if dest.category:
            intents_labels.append(dest.category)

        for label in intents_labels:
            label = label.strip()
            if label:
                scores[label] += weighted

    # ── Process search/filter events via keyword matching ──
    if search_events:
        known_labels = _get_known_labels_cached(db)
        for event in search_events:
            base_weight = EVENT_WEIGHTS.get(event.event_type, 1.0)
            decay = _time_decay(event.created_at)
            weighted = base_weight * decay

            query_text = ""
            if event.event_metadata and isinstance(event.event_metadata, dict):
                query_text = str(event.event_metadata.get("query", ""))
                # Also check filter metadata keys
                if not query_text:
                    for key in ("intent", "category"):
                        val = event.event_metadata.get(key)
                        if val:
                            query_text = str(val)
                            break

            if not query_text:
                continue

            query_lower = query_text.lower()
            for label in known_labels:
                if label.lower() in query_lower or query_lower in label.lower():
                    scores[label] += weighted

    if not scores:
        return {}

    # Normalize to 0-100
    max_score = max(scores.values())
    if max_score <= 0:
        return {}

    return {
        label: round(min(100.0, (score / max_score) * 100.0), 2)
        for label, score in scores.items()
        if score > 0
    }


# ── Cached known label set (refreshes per-request is fine) ────
_known_labels_cache: Optional[tuple[float, set[str]]] = None


def _get_known_labels_cached(db: Session) -> set[str]:
    """Return all known intent/label/category values from the database.

    Cached for 5 minutes to avoid repeated DB queries within a request batch.
    """
    import time

    global _known_labels_cache
    now = time.time()
    if _known_labels_cache and (now - _known_labels_cache[0]) < 300:
        return _known_labels_cache[1]

    from app.models.destination_label import DestinationLabel

    labels: set[str] = set()

    # Collect all unique categories
    cat_rows = db.query(Destination.category).distinct().all()
    for (cat,) in cat_rows:
        if cat:
            labels.add(cat.strip())

    # Collect all unique primary intents
    intent_rows = db.query(DestinationLabel.primary_intent).distinct().all()
    for (intent,) in intent_rows:
        if intent:
            labels.add(intent.strip())

    # Collect all unique core labels
    core_rows = db.query(DestinationLabel.core_labels).distinct().all()
    for (core,) in core_rows:
        if core:
            if isinstance(core, list):
                for item in core:
                    if item:
                        labels.add(str(item).strip())
            elif isinstance(core, str):
                for item in core.split(";"):
                    if item.strip():
                        labels.add(item.strip())

    _known_labels_cache = (now, labels)
    return labels

