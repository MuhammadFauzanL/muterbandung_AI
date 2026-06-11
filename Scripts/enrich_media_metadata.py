import argparse
import difflib
import json
import math
import os
import re
import shutil
from collections import Counter
from datetime import datetime

import pandas as pd


CURATED_PATH = os.path.join("Dataset", "3_Curated", "DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
OUTPUT_PATH = CURATED_PATH
AUDIT_PATH = os.path.join("Dokumentasi_Sistem", "MEDIA_ENRICHMENT_AUDIT_2026-05-25.md")
GROUNDTRUTH_PATH = os.path.join("Dataset", "3_Curated", "media_groundtruth_audit.csv")
REVIEW_QUEUE_PATH = os.path.join("Dataset", "3_Curated", "media_match_review_queue.csv")

RAW_SOURCES = [
    {
        "source": "google_maps_extractor_2026_05_19",
        "path": os.path.join("Dataset", "dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv"),
        "priority": 1,
    },
    {
        "source": "apify_jam_buka_raw_2026_05_19",
        "path": os.path.join("Dataset", "1_Raw_Data", "apify_jam_buka_semua_lokasi_raw.csv"),
        "priority": 2,
    },
]

MEDIA_COLUMNS = [
    "media_available",
    "media_image_url",
    "media_destination_url",
    "media_website",
    "media_source",
    "media_place_id",
    "media_match_title",
    "media_match_score",
    "media_match_method",
    "media_audit_status",
    "media_audit_note",
]

FUZZY_ACCEPT_THRESHOLD = 0.94
REVIEW_THRESHOLD = 0.86

MANUAL_TITLE_OVERRIDES = {
    "Glamping Legok Kondang": "Glamping Legok Kondang Lodge",
    "Puncak Mega Gunung Puntang": "Puncak Mega (Gn Puntang)",
    "Kebun Teh Rancabali": "Perkebunan Teh RANCABALI",
    "Perkebunan Teh Malabar": "Kebun Teh Malabar",
    "Dusun Bambu": "Dusun Bambu Lembang",
    "Gunung Bohong": "Gn. Bohong",
    "Forest Walk Babakan Siliwangi": "Hutan Kota Babakan Siliwangi Bandung",
    "Museum Pendidikan Nasional UPI": "Museum Pendidikan Nasional Universitas Pendidikan Indonesia",
    "Observatorium Bosscha": "Bosscha",
    "Fairy Garden by The Lodge": "Fairy Garden Edutainment Park by The Lodge",
    "Bird & Bromelia Pavilion": "Bird Pavilion",
    "Hejo Forest Ciwidey": "Hejo Forest",
    "Barusen Hills Ciwidey": "Barusen Hills",
    "Victory Waterpark Soreang": "Victory Waterpark",
    "Southland Camp Ciwidey": "Southland Camp",
    "Ecopark Curug Tilu Ciwidey": "Ecopark Curugtilu",
}

MANUAL_REJECT_TITLES = {
    "Curug Panganten": "Road/route result, not destination-level media.",
    "Gn. Tampomas": "Road result, not destination-level media.",
}


def clean_text(value):
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def normalize_name(value):
    text = clean_text(value).lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def valid_url(value):
    text = clean_text(value)
    if re.match(r"^https?://", text, flags=re.IGNORECASE):
        return text
    return ""


def read_raw_source(config):
    path = config["path"]
    if not os.path.exists(path):
        return []

    wanted_columns = {"title", "imageUrl", "url", "website", "placeId", "categoryName"}
    df = pd.read_csv(path, usecols=lambda column: column in wanted_columns)
    records = []
    for _, row in df.iterrows():
        title = clean_text(row.get("title"))
        if not title:
            continue
        image_url = valid_url(row.get("imageUrl"))
        destination_url = valid_url(row.get("url"))
        website = valid_url(row.get("website"))
        if not any([image_url, destination_url, website]):
            continue
        records.append({
            "source": config["source"],
            "priority": config["priority"],
            "title": title,
            "normalized_title": normalize_name(title),
            "image_url": image_url,
            "destination_url": destination_url,
            "website": website,
            "place_id": clean_text(row.get("placeId")),
            "category_name": clean_text(row.get("categoryName")),
            "media_completeness": int(bool(image_url)) + int(bool(destination_url)) + int(bool(website)),
        })
    return records


def load_raw_media():
    records = []
    for config in RAW_SOURCES:
        records.extend(read_raw_source(config))

    deduped = {}
    for record in records:
        key = record["normalized_title"]
        previous = deduped.get(key)
        if previous is None:
            deduped[key] = record
            continue
        current_sort = (record["media_completeness"], -record["priority"])
        previous_sort = (previous["media_completeness"], -previous["priority"])
        if current_sort > previous_sort:
            deduped[key] = record
    return list(deduped.values())


def best_fuzzy_match(name, raw_records):
    normalized = normalize_name(name)
    best = None
    best_score = 0.0
    for record in raw_records:
        title = record["normalized_title"]
        if not normalized or not title:
            continue
        score = difflib.SequenceMatcher(None, normalized, title).ratio()
        if score > best_score:
            best = record
            best_score = score
    return best, best_score


def find_manual_override(name, raw_by_title):
    override_title = MANUAL_TITLE_OVERRIDES.get(name)
    if not override_title:
        return None
    return raw_by_title.get(normalize_name(override_title))


def empty_media_result(name, best=None, score=0.0, method="missing", note="No reliable media match."):
    return {
        "media_available": False,
        "media_image_url": "",
        "media_destination_url": "",
        "media_website": "",
        "media_source": "",
        "media_place_id": "",
        "media_match_title": clean_text(best.get("title")) if best else "",
        "media_match_score": round(float(score), 4),
        "media_match_method": method,
        "media_audit_status": "needs_review" if method == "review_candidate" else "missing",
        "media_audit_note": note,
    }


def accepted_media_result(record, score, method, note):
    return {
        "media_available": True,
        "media_image_url": record["image_url"],
        "media_destination_url": record["destination_url"],
        "media_website": record["website"],
        "media_source": record["source"],
        "media_place_id": record["place_id"],
        "media_match_title": record["title"],
        "media_match_score": round(float(score), 4),
        "media_match_method": method,
        "media_audit_status": "accepted",
        "media_audit_note": note,
    }


def match_media(name, raw_records, raw_by_title):
    if name in MANUAL_REJECT_TITLES:
        best, score = best_fuzzy_match(name, raw_records)
        return empty_media_result(
            name,
            best=best,
            score=score,
            method="manual_reject",
            note=MANUAL_REJECT_TITLES[name],
        )

    manual = find_manual_override(name, raw_by_title)
    if manual:
        return accepted_media_result(manual, 1.0, "manual_override", "Accepted by explicit title override.")

    normalized = normalize_name(name)
    exact = raw_by_title.get(normalized)
    if exact:
        return accepted_media_result(exact, 1.0, "exact_normalized_title", "Exact normalized title match.")

    best, score = best_fuzzy_match(name, raw_records)
    if best and score >= FUZZY_ACCEPT_THRESHOLD:
        return accepted_media_result(best, score, "fuzzy_high_confidence", "Fuzzy score above strict acceptance threshold.")
    if best and score >= REVIEW_THRESHOLD:
        return empty_media_result(
            name,
            best=best,
            score=score,
            method="review_candidate",
            note="Fuzzy candidate below strict acceptance threshold; manual review required.",
        )
    return empty_media_result(name, best=best, score=score)


def write_markdown_audit(curated, raw_records, enriched, review_queue):
    status_counts = Counter(enriched["media_audit_status"])
    method_counts = Counter(enriched["media_match_method"])
    active_mask = enriched.get("display_status", pd.Series([""] * len(enriched))).astype(str).eq("active_candidate")
    active_rows = enriched[active_mask] if active_mask.any() else enriched
    active_with_media = int(active_rows["media_available"].sum())

    top_review = review_queue.head(25)
    lines = [
        "# Media Enrichment Audit - 2026-05-25",
        "",
        "## Verdict",
        "",
        "```text",
        "PASSED WITH REVIEW QUEUE",
        "```",
        "",
        "Media URL dan link destinasi sudah diperkaya secara konservatif. Hanya match yang exact, fuzzy sangat tinggi, atau override eksplisit yang diaktifkan.",
        "",
        "## Source Audit",
        "",
        f"- Curated rows: {len(curated)}",
        f"- Raw media candidates after dedupe: {len(raw_records)}",
        f"- Output dataset: `{OUTPUT_PATH}`",
        f"- Groundtruth audit CSV: `{GROUNDTRUTH_PATH}`",
        f"- Review queue CSV: `{REVIEW_QUEUE_PATH}`",
        "",
        "## Match Summary",
        "",
        f"- Accepted media rows: {int(enriched['media_available'].sum())}/{len(enriched)}",
        f"- Active candidate rows with media: {active_with_media}/{len(active_rows)}",
        f"- Needs review/missing rows: {len(enriched) - int(enriched['media_available'].sum())}",
        "",
        "Status counts:",
        "",
        "```json",
        json.dumps(dict(status_counts), indent=2, sort_keys=True),
        "```",
        "",
        "Method counts:",
        "",
        "```json",
        json.dumps(dict(method_counts), indent=2, sort_keys=True),
        "```",
        "",
        "## Safety Policy",
        "",
        "- URL gambar/link hanya aktif jika `media_available=true`.",
        "- Match borderline tidak dimasukkan ke evidence pack; masuk `media_match_review_queue.csv`.",
        "- Road-level result seperti `Jl. Curug Panganten` dan `Jl. Gn. Tampomas` ditolak manual.",
        "- LLM validator tetap menolak URL yang tidak ada di `candidate.media`.",
        "",
        "## Review Queue Sample",
        "",
        "| location_id | location_name | suggested_title | score | note |",
        "|---|---|---|---:|---|",
    ]
    if top_review.empty:
        lines.append("| - | - | - | - | - |")
    else:
        for _, row in top_review.iterrows():
            lines.append(
                "| {location_id} | {location_name} | {title} | {score:.3f} | {note} |".format(
                    location_id=clean_text(row.get("location_id")),
                    location_name=clean_text(row.get("location_name")).replace("|", "/"),
                    title=clean_text(row.get("media_match_title")).replace("|", "/"),
                    score=float(row.get("media_match_score") or 0),
                    note=clean_text(row.get("media_audit_note")).replace("|", "/"),
                )
            )

    lines.extend([
        "",
        "## Next Checks",
        "",
        "- Jalankan unit test recommender dan LLM guard.",
        "- Restart Flask agar dataset enriched terbaca.",
        "- Jalankan live API smoke test untuk memastikan `recommendations[].media.available` dan `llm_evidence_pack.candidates[].media.available` sinkron.",
        "- Jalankan groundtruth dan QC live.",
    ])

    os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
    with open(AUDIT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def enrich_media(curated_path=CURATED_PATH, output_path=OUTPUT_PATH, dry_run=False):
    curated = pd.read_csv(curated_path)
    raw_records = load_raw_media()
    raw_by_title = {record["normalized_title"]: record for record in raw_records}

    enriched = curated.copy()
    for column in MEDIA_COLUMNS:
        if column in enriched.columns:
            enriched = enriched.drop(columns=[column])

    results = []
    for _, row in curated.iterrows():
        name = clean_text(row.get("location_name"))
        result = match_media(name, raw_records, raw_by_title)
        results.append(result)

    media_df = pd.DataFrame(results)
    enriched = pd.concat([enriched, media_df], axis=1)

    review_queue = enriched[enriched["media_audit_status"].isin(["needs_review", "missing"])][[
        "location_id",
        "location_name",
        "media_match_title",
        "media_match_score",
        "media_match_method",
        "media_audit_status",
        "media_audit_note",
    ]].copy()
    review_queue = review_queue.sort_values(["media_audit_status", "media_match_score"], ascending=[False, False])

    groundtruth = enriched[[
        "location_id",
        "location_name",
        "media_available",
        "media_image_url",
        "media_destination_url",
        "media_website",
        "media_source",
        "media_match_title",
        "media_match_score",
        "media_match_method",
        "media_audit_status",
        "media_audit_note",
    ]].copy()

    if not dry_run:
        if os.path.exists(output_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{output_path}.bak_media_{timestamp}"
            shutil.copyfile(output_path, backup_path)

        enriched.to_csv(output_path, index=False)
        groundtruth.to_csv(GROUNDTRUTH_PATH, index=False)
        review_queue.to_csv(REVIEW_QUEUE_PATH, index=False)
        write_markdown_audit(curated, raw_records, enriched, review_queue)

    return {
        "rows": len(enriched),
        "raw_media_candidates": len(raw_records),
        "accepted": int(enriched["media_available"].sum()),
        "missing_or_review": int((~enriched["media_available"]).sum()),
        "status_counts": dict(Counter(enriched["media_audit_status"])),
        "method_counts": dict(Counter(enriched["media_match_method"])),
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(description="Enrich curated tourism dataset with audited media metadata.")
    parser.add_argument("--dry-run", action="store_true", help="Audit only; do not write files.")
    args = parser.parse_args()
    summary = enrich_media(dry_run=args.dry_run)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
