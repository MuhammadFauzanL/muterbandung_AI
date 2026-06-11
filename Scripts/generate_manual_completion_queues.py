import json
import os
import urllib.parse
from collections import Counter

import pandas as pd


CURATED_PATH = os.path.join("Dataset", "3_Curated", "DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
MEDIA_QUEUE_PATH = os.path.join("Dataset", "3_Curated", "manual_media_fill_queue.csv")
DATA_QUEUE_PATH = os.path.join("Dataset", "3_Curated", "manual_data_fill_queue.csv")
REALWORLD_QUEUE_PATH = os.path.join("Dataset", "3_Curated", "manual_realworld_verification_queue.csv")
REPORT_PATH = os.path.join("Dokumentasi_Sistem", "MANUAL_COMPLETION_QUEUES_AUDIT_2026-05-25.md")

ACTIVE_STATUS = "active_candidate"

CRITICAL_VALUE_FIELDS = [
    "jam_buka_weekday",
    "jam_tutup_weekday",
    "jam_buka_weekend",
    "jam_tutup_weekend",
    "avg_rating",
]

FACILITY_FLAGS = [
    "parking_verified",
    "wheelchair_accessible_verified",
    "toilet_verified",
    "mushola_verified",
    "pet_friendly_verified",
    "open_24h_verified",
]

CONTEXT_FLAGS = [
    "night_verified",
    "indoor_verified",
    "child_friendly_verified",
    "coordinate_verified",
    "safety_verified",
    "price_verified",
]


def clean_value(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def is_blank(value):
    return clean_value(value) == ""


def bool_is_true(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def search_url(query, mode):
    encoded = urllib.parse.quote_plus(query)
    if mode == "maps":
        return f"https://www.google.com/maps/search/{encoded}"
    if mode == "images":
        return f"https://www.google.com/search?tbm=isch&q={encoded}"
    return f"https://www.google.com/search?q={encoded}"


def priority_for(row, base="MEDIUM"):
    if clean_value(row.get("display_status")) == ACTIVE_STATUS:
        return base
    if base == "HIGH":
        return "MEDIUM"
    return "LOW"


def build_media_queue(df):
    rows = []
    media_missing = df[df["media_available"].map(bool_is_true) != True].copy()
    for _, row in media_missing.iterrows():
        active = clean_value(row.get("display_status")) == ACTIVE_STATUS
        name = clean_value(row.get("location_name"))
        rows.append({
            "location_id": clean_value(row.get("location_id")),
            "location_name": name,
            "display_status": clean_value(row.get("display_status")),
            "curation_action": clean_value(row.get("curation_action")),
            "category": clean_value(row.get("category")),
            "priority": "HIGH" if active else "LOW",
            "current_media_available": clean_value(row.get("media_available")),
            "suggested_raw_title": clean_value(row.get("media_match_title")),
            "suggested_match_score": clean_value(row.get("media_match_score")),
            "suggested_match_method": clean_value(row.get("media_match_method")),
            "audit_note": clean_value(row.get("media_audit_note")),
            "google_search_url": search_url(f"{name} Bandung wisata", "search"),
            "google_maps_search_url": search_url(f"{name} Bandung", "maps"),
            "google_image_search_url": search_url(f"{name} Bandung wisata", "images"),
            "new_media_image_url": "",
            "new_media_destination_url": "",
            "new_media_website": "",
            "new_media_source_note": "",
            "reviewer_status": "todo",
            "reviewer_note": "",
        })
    return pd.DataFrame(rows).sort_values(["priority", "suggested_match_score"], ascending=[True, False])


def add_data_issue(rows, row, issue_type, field_name, current_value, priority, note=""):
    rows.append({
        "location_id": clean_value(row.get("location_id")),
        "location_name": clean_value(row.get("location_name")),
        "display_status": clean_value(row.get("display_status")),
        "curation_action": clean_value(row.get("curation_action")),
        "category": clean_value(row.get("category")),
        "priority": priority,
        "issue_type": issue_type,
        "field_name": field_name,
        "current_value": clean_value(current_value),
        "new_value": "",
        "source_url": "",
        "reviewer_status": "todo",
        "reviewer_note": note,
    })


def build_data_queue(df):
    rows = []
    for _, row in df.iterrows():
        is_active = clean_value(row.get("display_status")) == ACTIVE_STATUS

        for field in CRITICAL_VALUE_FIELDS:
            if field not in df.columns:
                continue
            if is_blank(row.get(field)):
                add_data_issue(
                    rows,
                    row,
                    "missing_value",
                    field,
                    row.get(field),
                    priority_for(row, "HIGH" if field.startswith("jam_") else "MEDIUM"),
                    "Isi nilai baru jika data terpercaya sudah ditemukan.",
                )

        if "sentiment_available" in df.columns and not bool_is_true(row.get("sentiment_available")):
            add_data_issue(
                rows,
                row,
                "sentiment_unavailable",
                "sentiment_available",
                row.get("sentiment_available"),
                priority_for(row, "MEDIUM"),
                "Sentiment belum tersedia; isi hanya jika ada pipeline sentiment/review baru yang valid.",
            )

        if is_active and "coordinate_verified" in df.columns and not bool_is_true(row.get("coordinate_verified")):
            add_data_issue(
                rows,
                row,
                "verification_needed",
                "coordinate_verified",
                row.get("coordinate_verified"),
                "HIGH",
                "Koordinat aktif perlu dicek ulang sebelum dipakai untuk ranking dekat.",
            )

        if is_active and "price_verified" in df.columns and not bool_is_true(row.get("price_verified")):
            add_data_issue(
                rows,
                row,
                "verification_needed",
                "price_verified",
                row.get("price_verified"),
                "HIGH",
                "Harga aktif perlu dicek ulang.",
            )

        if is_active and clean_value(row.get("review_status")) in {"needs_reverification", "needs_review"}:
            add_data_issue(
                rows,
                row,
                "status_review",
                "review_status",
                row.get("review_status"),
                "HIGH",
                clean_value(row.get("curation_note")) or "Status destinasi perlu review manual.",
            )

    if not rows:
        return pd.DataFrame(columns=[
            "location_id",
            "location_name",
            "display_status",
            "curation_action",
            "category",
            "priority",
            "issue_type",
            "field_name",
            "current_value",
            "new_value",
            "source_url",
            "reviewer_status",
            "reviewer_note",
        ])
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    queue = pd.DataFrame(rows)
    queue["_priority_order"] = queue["priority"].map(order).fillna(9)
    queue = queue.sort_values(["_priority_order", "location_id", "field_name"]).drop(columns=["_priority_order"])
    return queue


def build_realworld_queue(df):
    rows = []
    active_df = df[df["display_status"].astype(str) == ACTIVE_STATUS].copy()
    for _, row in active_df.iterrows():
        unverified_facilities = [
            field for field in FACILITY_FLAGS
            if field in df.columns and not bool_is_true(row.get(field))
        ]
        unverified_context = [
            field for field in CONTEXT_FLAGS
            if field in df.columns and not bool_is_true(row.get(field))
        ]
        if not unverified_facilities and not unverified_context:
            continue
        rows.append({
            "location_id": clean_value(row.get("location_id")),
            "location_name": clean_value(row.get("location_name")),
            "category": clean_value(row.get("category")),
            "display_status": clean_value(row.get("display_status")),
            "priority": "HIGH" if any(flag in unverified_context for flag in ["coordinate_verified", "safety_verified", "price_verified"]) else "MEDIUM",
            "unverified_facility_flags": "|".join(unverified_facilities),
            "unverified_context_flags": "|".join(unverified_context),
            "verified_flags_to_set_true": "",
            "flags_to_keep_false": "",
            "evidence_url": "",
            "reviewer_status": "todo",
            "reviewer_note": "",
        })
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    queue = pd.DataFrame(rows)
    if queue.empty:
        return queue
    queue["_priority_order"] = queue["priority"].map(order).fillna(9)
    return queue.sort_values(["_priority_order", "location_id"]).drop(columns=["_priority_order"])


def write_report(media_queue, data_queue, realworld_queue):
    media_priority = Counter(media_queue.get("priority", []))
    data_issue = Counter(data_queue.get("issue_type", []))
    data_priority = Counter(data_queue.get("priority", []))
    realworld_priority = Counter(realworld_queue.get("priority", []))

    lines = [
        "# Manual Completion Queues Audit - 2026-05-25",
        "",
        "## Summary",
        "",
        f"- Media missing rows: {len(media_queue)}",
        f"- Non-media data issues: {len(data_queue)}",
        f"- Real-world verification rows: {len(realworld_queue)}",
        "",
        "## Output CSV",
        "",
        f"- `{MEDIA_QUEUE_PATH}`",
        f"- `{DATA_QUEUE_PATH}`",
        f"- `{REALWORLD_QUEUE_PATH}`",
        "",
        "## Media Queue",
        "",
        "```json",
        json.dumps(dict(media_priority), indent=2, sort_keys=True),
        "```",
        "",
        "## Non-Media Data Queue",
        "",
        "Issue counts:",
        "",
        "```json",
        json.dumps(dict(data_issue), indent=2, sort_keys=True),
        "```",
        "",
        "Priority counts:",
        "",
        "```json",
        json.dumps(dict(data_priority), indent=2, sort_keys=True),
        "```",
        "",
        "## Real-World Verification Queue",
        "",
        "```json",
        json.dumps(dict(realworld_priority), indent=2, sort_keys=True),
        "```",
        "",
        "## Fill Rules",
        "",
        "- Isi kolom `new_*` atau `new_value` saja; jangan ubah kolom konteks lama saat review manual.",
        "- Untuk media, minimal isi `new_media_image_url` atau `new_media_destination_url` dengan URL HTTP yang benar.",
        "- Untuk data non-media, isi `source_url` bila mengambil dari sumber eksternal.",
        "- Untuk real-world flags, isi `verified_flags_to_set_true` dengan nama flag yang sudah terbukti benar, dipisahkan `|`.",
        "- Setelah selesai, jalankan pipeline apply/merge terpisah agar perubahan tetap auditable.",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    df = pd.read_csv(CURATED_PATH)
    media_queue = build_media_queue(df)
    data_queue = build_data_queue(df)
    realworld_queue = build_realworld_queue(df)

    media_queue.to_csv(MEDIA_QUEUE_PATH, index=False)
    data_queue.to_csv(DATA_QUEUE_PATH, index=False)
    realworld_queue.to_csv(REALWORLD_QUEUE_PATH, index=False)
    write_report(media_queue, data_queue, realworld_queue)

    summary = {
        "media_missing_rows": len(media_queue),
        "data_issue_rows": len(data_queue),
        "realworld_verification_rows": len(realworld_queue),
        "outputs": [MEDIA_QUEUE_PATH, DATA_QUEUE_PATH, REALWORLD_QUEUE_PATH, REPORT_PATH],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
