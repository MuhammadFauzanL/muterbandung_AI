import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_QUEUE_PATH = Path("Wisata_Workspace/01_Dataset/3_Curated/targeted_data_completion_queue.csv")
DEFAULT_BATCH_OUTPUT = Path("Wisata_Workspace/01_Dataset/3_Curated/manual_review_batch3_remaining_46_after_status_facility_2026-05-27.csv")
DEFAULT_REPORT_OUTPUT = Path("Dokumentasi_Sistem/MANUAL_REVIEW_BATCH3_REMAINING_46_2026-05-27.md")


TASK_INSTRUCTIONS = {
    "active_status_verification": {
        "what_to_find": "Cek Google Maps/situs resmi/media sosial terbaru. Pastikan masih aktif, tutup, di luar scope, atau belum pasti.",
        "decision_options": "active | inactive | remove_scope | uncertain",
        "required_manual_fields": "reviewer_decision|evidence_url|latest_review_seen|reviewer_note",
    },
    "coordinate_verification": {
        "what_to_find": "Cek titik Google Maps/official. Isi latitude dan longitude jika titik dataset perlu diperbaiki atau konfirmasi coordinate_ok.",
        "decision_options": "coordinate_ok | coordinate_fix | uncertain",
        "required_manual_fields": "reviewer_decision|evidence_url|latitude|longitude|reviewer_note",
    },
    "rating_sentiment_completion": {
        "what_to_find": "Ambil rating rata-rata terbaru, jumlah review, dan ringkasan komentar utama. Tandai low_confidence jika review sedikit/tidak kuat.",
        "decision_options": "rating_filled | low_confidence | uncertain",
        "required_manual_fields": "reviewer_decision|evidence_url|avg_rating|total_ulasan|latest_review_seen|reviewer_note",
    },
    "media_completion": {
        "what_to_find": "Cari satu gambar representatif yang jelas dan relevan. Prioritaskan Google Maps/official/website tepercaya.",
        "decision_options": "media_filled | no_media_found | uncertain",
        "required_manual_fields": "reviewer_decision|evidence_url|media_image_url|media_source|reviewer_note",
    },
}


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def score(row):
    try:
        return int(float(row.get("impact_score") or 0))
    except ValueError:
        return 0


def select_rows(rows):
    selected = []
    seen = set()

    def add(subset):
        for row in subset:
            key = (row["location_id"], row["task_type"])
            if key in seen:
                continue
            selected.append(row)
            seen.add(key)

    p0_status = [
        row for row in rows
        if row.get("priority") == "P0" and row.get("task_type") == "active_status_verification"
    ]
    coordinates = [row for row in rows if row.get("task_type") == "coordinate_verification"]
    ratings = [row for row in rows if row.get("task_type") == "rating_sentiment_completion"]
    media_p1 = [
        row for row in rows
        if row.get("priority") == "P1" and row.get("task_type") == "media_completion"
    ]

    sorter = lambda row: (-score(row), row.get("location_name", ""))
    add(sorted(p0_status, key=sorter))
    add(sorted(coordinates, key=sorter))
    add(sorted(ratings, key=sorter))
    add(sorted(media_p1, key=sorter))
    return selected


def create_batch(
    queue_path=DEFAULT_QUEUE_PATH,
    batch_output=DEFAULT_BATCH_OUTPUT,
    report_output=DEFAULT_REPORT_OUTPUT,
):
    queue_path = Path(queue_path)
    batch_output = Path(batch_output)
    report_output = Path(report_output)

    with queue_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    selected = select_rows(rows)

    fieldnames = [
        "priority",
        "impact_score",
        "task_type",
        "location_id",
        "location_name",
        "category",
        "issue_codes",
        "fields_to_complete",
        "current_is_active_verified",
        "current_media_available",
        "current_sentiment_available",
        "current_avg_rating",
        "current_coordinate_verified",
        "what_to_find",
        "decision_options",
        "required_manual_fields",
        "reviewer_decision",
        "evidence_url",
        "latitude",
        "longitude",
        "avg_rating",
        "total_ulasan",
        "media_image_url",
        "media_source",
        "latest_review_seen",
        "reviewer_note",
    ]

    batch_output.parent.mkdir(parents=True, exist_ok=True)
    with batch_output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in selected:
            instruction = TASK_INSTRUCTIONS[row["task_type"]]
            writer.writerow({
                "priority": row.get("priority", ""),
                "impact_score": row.get("impact_score", ""),
                "task_type": row.get("task_type", ""),
                "location_id": row.get("location_id", ""),
                "location_name": row.get("location_name", ""),
                "category": row.get("category", ""),
                "issue_codes": row.get("issue_codes", ""),
                "fields_to_complete": row.get("fields_to_complete", ""),
                "current_is_active_verified": row.get("current_is_active_verified", ""),
                "current_media_available": row.get("current_media_available", ""),
                "current_sentiment_available": row.get("current_sentiment_available", ""),
                "current_avg_rating": row.get("current_avg_rating", ""),
                "current_coordinate_verified": row.get("current_coordinate_verified", ""),
                "what_to_find": instruction["what_to_find"],
                "decision_options": instruction["decision_options"],
                "required_manual_fields": instruction["required_manual_fields"],
                "reviewer_decision": "",
                "evidence_url": "",
                "latitude": "",
                "longitude": "",
                "avg_rating": "",
                "total_ulasan": "",
                "media_image_url": "",
                "media_source": "",
                "latest_review_seen": "",
                "reviewer_note": "",
            })

    write_report(report_output, queue_path, batch_output, selected, rows)
    return {
        "batch_output": str(batch_output),
        "report_output": str(report_output),
        "selected": selected,
        "queue_rows": rows,
    }


def write_report(report_output, queue_path, batch_output, selected, rows):
    report_output.parent.mkdir(parents=True, exist_ok=True)
    selected_counts = Counter(row["task_type"] for row in selected)
    queue_counts = Counter(row["task_type"] for row in rows)
    priority_counts = Counter(row["priority"] for row in rows)

    lines = [
        "# Manual Review Batch 3 Remaining 46 - 2026-05-27",
        "",
        f"Generated at: `{now_iso()}`",
        f"Queue source: `{queue_path}`",
        f"Batch file: `{batch_output}`",
        "",
        "## Current Queue Context",
        "",
        f"- Total queue tasks after status/facility apply: `{len(rows)}`",
        f"- Selected high-impact remaining tasks: `{len(selected)}`",
        "",
        "### Queue By Priority",
        "",
        "| Priority | Count |",
        "| --- | ---: |",
    ]
    for priority, count in sorted(priority_counts.items()):
        lines.append(f"| `{priority}` | {count} |")

    lines.extend(["", "### Queue By Task Type", "", "| Task Type | Count |", "| --- | ---: |"])
    for task, count in queue_counts.most_common():
        lines.append(f"| `{task}` | {count} |")

    lines.extend(["", "## Selected Batch 3", "", "| Task Type | Count |", "| --- | ---: |"])
    for task, count in selected_counts.most_common():
        lines.append(f"| `{task}` | {count} |")

    lines.extend(["", "## Items", "", "| Priority | Task | ID | Location | Fields |", "| --- | --- | --- | --- | --- |"])
    for row in selected:
        lines.append(
            f"| `{row['priority']}` | `{row['task_type']}` | `{row['location_id']}` | "
            f"{row['location_name']} | `{row['fields_to_complete']}` |"
        )

    report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    parser.add_argument("--batch-output", default=str(DEFAULT_BATCH_OUTPUT))
    parser.add_argument("--report-output", default=str(DEFAULT_REPORT_OUTPUT))
    args = parser.parse_args()
    result = create_batch(args.queue, args.batch_output, args.report_output)
    print(f"batch_output={result['batch_output']}")
    print(f"report_output={result['report_output']}")
    print(f"selected_rows={len(result['selected'])}")
    print(f"selected_counts={dict(Counter(row['task_type'] for row in result['selected']))}")


if __name__ == "__main__":
    main()
