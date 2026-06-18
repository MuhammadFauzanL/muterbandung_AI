"""
Planner insight service — generates contextual AI insights for the planner.
"""

from __future__ import annotations

import random
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.models.destination_label import DestinationLabel


def generate_planner_insight(
    db: Session,
    *,
    destination_ids: list[str],
) -> dict:
    """Generate a smart contextual insight based on selected destinations.

    Returns a dict with 'text' and 'type' keys.
    """
    if not destination_ids:
        return {
            "text": (
                "Mulai pilih destinasi wisata dari halaman Explore untuk "
                "mendapatkan insight personalisasi dari Cepot AI!"
            ),
            "type": "empty",
        }

    # Fetch destinations by external_id
    destinations = (
        db.query(Destination)
        .filter(
            Destination.external_id.in_(destination_ids),
            Destination.is_active.is_(True),
        )
        .all()
    )

    if not destinations:
        return {
            "text": (
                "Destinasi yang dipilih belum ditemukan dalam database. "
                "Coba pilih destinasi lain dari halaman Explore."
            ),
            "type": "not_found",
        }

    # Collect metadata
    categories = list({d.category for d in destinations if d.category})
    zones = list({d.tourism_zone for d in destinations if d.tourism_zone})
    dest_names = [d.name for d in destinations]

    # Get labels for selected destinations
    labels: list[str] = []
    for dest in destinations:
        if dest.labels and dest.labels.primary_intent:
            labels.append(dest.labels.primary_intent)

    unique_labels = list(set(labels))

    # Find related destinations in the same zone
    related_names: list[str] = []
    if zones:
        related = (
            db.query(Destination.name)
            .filter(
                Destination.tourism_zone.in_(zones),
                Destination.is_active.is_(True),
                Destination.display_status == "active_candidate",
                Destination.external_id.notin_(destination_ids),
            )
            .order_by(Destination.quality_score.desc().nullslast())
            .limit(3)
            .all()
        )
        related_names = [r[0] for r in related if r[0]]

    # Build smart insight text
    insight_templates = []

    if len(destinations) == 1:
        dest = destinations[0]
        zone_text = f"zona wisata {dest.tourism_zone}" if dest.tourism_zone else "area Bandung Raya"

        if related_names:
            related_text = _join_names(related_names)
            insight_templates.append(
                f"Wisatawan yang mengunjungi {dest.name} biasanya juga "
                f"mengunjungi {related_text} karena berada dalam satu "
                f"{zone_text} yang berdekatan."
            )

        if dest.labels and dest.labels.primary_intent:
            insight_templates.append(
                f"{dest.name} termasuk dalam kategori \"{dest.labels.primary_intent}\". "
                f"Cepot AI merekomendasikan menambahkan destinasi dengan tema serupa "
                f"untuk pengalaman perjalanan yang lebih kohesif."
            )

        if dest.avg_rating and dest.avg_rating >= 4.0 and dest.total_reviews:
            insight_templates.append(
                f"{dest.name} memiliki rating {dest.avg_rating:.1f} dari "
                f"{dest.total_reviews:,} ulasan. Destinasi ini sangat populer — "
                f"pertimbangkan untuk datang di pagi hari agar lebih nyaman."
            )

    elif len(destinations) >= 2:
        names_text = _join_names(dest_names)

        if len(zones) == 1 and zones[0]:
            insight_templates.append(
                f"Pilihan bagus! {names_text} berada dalam satu {zones[0]}, "
                f"sehingga perjalananmu bisa lebih efisien tanpa perlu berpindah jauh."
            )

        if len(categories) >= 2:
            cat_text = " dan ".join(categories[:2])
            insight_templates.append(
                f"Perjalananmu mencakup kombinasi wisata {cat_text}. "
                f"Variasi ini akan membuat pengalaman liburanmu lebih berkesan dan beragam!"
            )

        if related_names:
            related_text = _join_names(related_names[:2])
            insight_templates.append(
                f"Berdasarkan destinasi yang kamu pilih, Cepot AI juga merekomendasikan "
                f"{related_text} yang berada di area yang sama."
            )

        # Estimate total visit duration
        total_minutes = sum(
            d.estimated_duration_minutes or 90
            for d in destinations
        )
        hours = total_minutes // 60
        if hours >= 2:
            insight_templates.append(
                f"Total estimasi waktu kunjungan untuk {len(destinations)} destinasi "
                f"pilihanmu sekitar {hours} jam. Pastikan kamu mengatur waktu dengan baik "
                f"agar setiap tempat bisa dinikmati maksimal!"
            )

    # Pick best insight
    if insight_templates:
        text = random.choice(insight_templates)
    else:
        text = (
            f"Kamu telah memilih {len(destinations)} destinasi. "
            f"Cepot AI sedang menganalisis perjalanan terbaikmu!"
        )

    return {
        "text": text,
        "type": "insight",
        "destinationCount": len(destinations),
        "categories": categories,
        "zones": zones,
    }


def _join_names(names: list[str]) -> str:
    """Join names with commas and 'dan' for the last item."""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} dan {names[1]}"
    return ", ".join(names[:-1]) + f", dan {names[-1]}"
