from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "Penginapan_Workspace"
CURATED_DIR = WORKSPACE / "02_Curated"
DOC_DIR = WORKSPACE / "04_Dokumentasi"

DEFAULT_CANDIDATE = CURATED_DIR / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv"
DEFAULT_MAPPING_CANDIDATE = CURATED_DIR / "PENGINAPAN_PARENT_CHILD_MAPPING_CANDIDATE_2026-06-05.csv"
DEFAULT_RELATIONS_FINAL = CURATED_DIR / "PENGINAPAN_PARENT_CHILD_RELATIONS_FINAL_2026-06-05.csv"
DEFAULT_PARENT_MASTER = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_2026-06-05.csv"
DEFAULT_CHILD_LISTINGS_FINAL = CURATED_DIR / "PENGINAPAN_CHILD_LISTINGS_FINAL_2026-06-05.csv"
DEFAULT_REVIEW_TARGETS = CURATED_DIR / "PENGINAPAN_REVIEW_SCRAPE_TARGETS_PARENT_MASTER_2026-06-05.csv"
DEFAULT_SUMMARY = CURATED_DIR / "penginapan_parent_master_final_summary_2026-06-05.json"
DEFAULT_VALIDATION = CURATED_DIR / "penginapan_parent_master_final_validation_2026-06-05.json"
DEFAULT_REPORT = DOC_DIR / "PENGINAPAN_PARENT_MASTER_FINAL_2026-06-05.md"

DETAIL_LISTING_RE = re.compile(
    r"(-\s*.*\b(?:room|kamar|bedroom|apartment|studio|villa|house)\b|"
    r"\b[1-9]\s*br\b|"
    r"\b(?:one|two|three|four|five|six)-bedroom\b|"
    r"\([^)]*room[^)]*\))",
    re.IGNORECASE,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value).strip()


def number(value):
    text = clean_text(value)
    if not text:
        return ""
    try:
        parsed = float(text)
    except ValueError:
        return ""
    if math.isnan(parsed):
        return ""
    if parsed.is_integer():
        return int(parsed)
    return round(parsed, 7)


def make_maps_search_url(query: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"


def review_confidence_label(reviews) -> str:
    count = number(reviews)
    if count == "":
        return "missing_review_confidence"
    if float(count) < 30:
        return "low_review_confidence"
    if float(count) < 200:
        return "medium_review_confidence"
    return "high_review_confidence"


def review_priority(row: pd.Series) -> str:
    rating = clean_text(row.get("overall_rating"))
    reviews = clean_text(row.get("reviews"))
    confidence = clean_text(row.get("review_confidence_label")) or review_confidence_label(reviews)
    if not rating or not reviews:
        return "missing_rating_or_review"
    if confidence == "low_review_confidence":
        return "low_review_confidence"
    if confidence == "medium_review_confidence":
        return "medium_review_confidence"
    return "high_review_confidence"


def maps_query(row: pd.Series) -> str:
    name = clean_text(row.get("name"))
    lat = clean_text(row.get("latitude"))
    lon = clean_text(row.get("longitude"))
    if lat and lon:
        return f"{name} {lat},{lon}"
    return f"{name} Bandung Jawa Barat"


def looks_detail_listing_name(value: str) -> bool:
    return bool(DETAIL_LISTING_RE.search(clean_text(value)))


def build_relations_final(mapping: pd.DataFrame) -> pd.DataFrame:
    accepted = mapping[mapping["parent_candidate_id"].map(clean_text).ne("")].copy()
    accepted = accepted.sort_values(["parent_candidate_id", "child_penginapan_id"]).reset_index(drop=True)
    rows = []
    for index, row in accepted.iterrows():
        rows.append(
            {
                "relation_id": f"PCRF-20260605-{index + 1:04d}",
                "manual_decision": "accept",
                "decision_source": "manual_review_google_check_2026_06_05",
                "is_final_relation": "True",
                "child_penginapan_id": clean_text(row.get("child_penginapan_id")),
                "child_name": clean_text(row.get("child_name")),
                "child_property_type": clean_text(row.get("child_property_type")),
                "parent_penginapan_id": clean_text(row.get("parent_candidate_id")),
                "parent_name": clean_text(row.get("parent_candidate_name")),
                "parent_property_type": clean_text(row.get("parent_property_type")),
                "relation_type": clean_text(row.get("relation_type")) or "room_of",
                "confidence_score": number(row.get("confidence_score")),
                "confidence_label": clean_text(row.get("confidence_label")),
                "match_basis": clean_text(row.get("match_basis")),
                "evidence": clean_text(row.get("evidence")),
                "notes": "Nama panjang dipahami sebagai nama properti + tipe kamar OTA.",
            }
        )
    return pd.DataFrame(rows)


def build_child_listings(candidate: pd.DataFrame, relations: pd.DataFrame) -> pd.DataFrame:
    relation_by_child = {
        clean_text(row["child_penginapan_id"]): row
        for _, row in relations.iterrows()
    }
    child_rows = candidate[candidate["property_type"].map(clean_text).eq("room_level_listing")].copy()
    rows = []
    for _, row in child_rows.iterrows():
        child_id = clean_text(row.get("penginapan_id"))
        relation = relation_by_child.get(child_id)
        rows.append(
            {
                "child_penginapan_id": child_id,
                "child_name": clean_text(row.get("name")),
                "child_property_type": clean_text(row.get("property_type")),
                "parent_penginapan_id": clean_text(relation.get("parent_penginapan_id")) if relation is not None else "",
                "parent_name": clean_text(relation.get("parent_name")) if relation is not None else "",
                "relation_status": "accepted_parent" if relation is not None else "child_without_final_parent",
                "is_main_ranking_candidate": "False",
                "latitude": clean_text(row.get("latitude")),
                "longitude": clean_text(row.get("longitude")),
                "overall_rating": clean_text(row.get("overall_rating")),
                "reviews": clean_text(row.get("reviews")),
                "price_lowest": clean_text(row.get("price_lowest")),
                "data_quality_score": clean_text(row.get("data_quality_score")),
                "data_quality_label": clean_text(row.get("data_quality_label")),
                "link": clean_text(row.get("link")),
                "primary_image_url": clean_text(row.get("primary_image_url")),
                "notes": "Disimpan sebagai child/detail, tidak tampil sebagai parent utama.",
            }
        )
    return pd.DataFrame(rows)


def build_parent_master(candidate: pd.DataFrame, child_listings: pd.DataFrame) -> pd.DataFrame:
    child_ids = set(child_listings["child_penginapan_id"].map(clean_text))
    parent = candidate[~candidate["penginapan_id"].map(clean_text).isin(child_ids)].copy()

    child_counts = (
        child_listings[child_listings["parent_penginapan_id"].map(clean_text).ne("")]
        .groupby("parent_penginapan_id")
        .size()
        .to_dict()
    )
    parent["is_parent_master"] = "True"
    parent["final_child_count"] = parent["penginapan_id"].map(lambda pid: int(child_counts.get(clean_text(pid), 0)))
    parent["has_final_child_listing"] = parent["final_child_count"].map(lambda value: "True" if int(value) > 0 else "False")
    parent["excluded_child_listing_count"] = len(child_ids)
    parent["name_looks_detail_listing"] = parent["name"].map(lambda value: "True" if looks_detail_listing_name(value) else "False")
    return parent


def build_review_targets(parent_master: pd.DataFrame, source_path: Path) -> pd.DataFrame:
    rows = []
    seen = set()
    for _, row in parent_master.iterrows():
        name = clean_text(row.get("name"))
        if not name:
            continue
        lat = clean_text(row.get("latitude"))
        lon = clean_text(row.get("longitude"))
        key = (name.lower(), lat, lon)
        if key in seen:
            continue
        seen.add(key)
        query = maps_query(row)
        rows.append(
            {
                "review_target_id": f"PHREV-20260605-{len(rows) + 1:04d}",
                "penginapan_id": clean_text(row.get("penginapan_id")),
                "name": name,
                "property_type": clean_text(row.get("property_type")),
                "latitude": number(lat),
                "longitude": number(lon),
                "overall_rating": number(row.get("overall_rating")),
                "reviews_existing": number(row.get("reviews")),
                "review_confidence_label": clean_text(row.get("review_confidence_label")) or review_confidence_label(row.get("reviews")),
                "review_scrape_priority": review_priority(row),
                "data_quality_score": number(row.get("data_quality_score")),
                "has_final_child_listing": clean_text(row.get("has_final_child_listing")),
                "final_child_count": number(row.get("final_child_count")),
                "name_looks_detail_listing": clean_text(row.get("name_looks_detail_listing")),
                "target_review_note": "check_name_match_first" if clean_text(row.get("name_looks_detail_listing")) == "True" else "parent_target",
                "google_maps_search_query": query,
                "google_maps_search_url": make_maps_search_url(query),
                "source_dataset": str(source_path),
            }
        )
    targets = pd.DataFrame(rows)
    if not targets.empty:
        targets = targets.sort_values(
            ["review_scrape_priority", "reviews_existing", "name"],
            ascending=[True, True, True],
        ).reset_index(drop=True)
        targets["review_target_id"] = [f"PHREV-20260605-{index + 1:04d}" for index in range(len(targets))]
    return targets


def validate_outputs(candidate: pd.DataFrame, relations: pd.DataFrame, parent_master: pd.DataFrame, child_listings: pd.DataFrame, review_targets: pd.DataFrame) -> dict:
    accepted_child_ids = set(relations["child_penginapan_id"].map(clean_text))
    all_child_ids = set(child_listings["child_penginapan_id"].map(clean_text))
    parent_ids = set(parent_master["penginapan_id"].map(clean_text))
    target_ids = set(review_targets["penginapan_id"].map(clean_text)) if not review_targets.empty else set()

    errors = []
    warnings = []
    accepted_in_parent = sorted(accepted_child_ids & parent_ids)
    any_child_in_parent = sorted(all_child_ids & parent_ids)
    child_in_targets = sorted(all_child_ids & target_ids)
    if accepted_in_parent:
        errors.append({"code": "ACCEPTED_CHILD_IN_PARENT_MASTER", "count": len(accepted_in_parent), "sample": accepted_in_parent[:10]})
    if any_child_in_parent:
        errors.append({"code": "ROOM_LEVEL_CHILD_IN_PARENT_MASTER", "count": len(any_child_in_parent), "sample": any_child_in_parent[:10]})
    if child_in_targets:
        errors.append({"code": "CHILD_IN_REVIEW_TARGETS", "count": len(child_in_targets), "sample": child_in_targets[:10]})

    unresolved_child_count = int(child_listings["relation_status"].eq("child_without_final_parent").sum())
    if unresolved_child_count:
        warnings.append({"code": "CHILD_WITHOUT_FINAL_PARENT", "count": unresolved_child_count, "message": "Child tetap ditahan dari parent master, tetapi parent final belum dipilih."})

    return {
        "generated_at": now_iso(),
        "gate": "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "errors": errors,
        "warnings": warnings,
        "candidate_rows": int(len(candidate)),
        "relations_final_rows": int(len(relations)),
        "parent_master_rows": int(len(parent_master)),
        "child_listings_rows": int(len(child_listings)),
        "review_target_rows": int(len(review_targets)),
        "accepted_child_in_parent_master": int(len(accepted_in_parent)),
        "any_child_in_parent_master": int(len(any_child_in_parent)),
        "child_in_review_targets": int(len(child_in_targets)),
        "child_without_final_parent": unresolved_child_count,
    }


def write_report(path: Path, summary: dict, validation: dict) -> None:
    text = f"""# Penginapan Parent Master Final - 2026-06-05

Tahap ini memisahkan parent dan child listing berdasarkan 13 relasi yang sudah direview manual.

## Output

- Relations final: `{summary['relations_final_path']}`
- Parent master: `{summary['parent_master_path']}`
- Child listings final: `{summary['child_listings_final_path']}`
- Review scrape targets: `{summary['review_targets_path']}`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Candidate rows | {summary['candidate_rows']} |
| Final accepted relations | {summary['relations_final_rows']} |
| Parent master rows | {summary['parent_master_rows']} |
| Child listing rows | {summary['child_listings_rows']} |
| Review target rows | {summary['review_target_rows']} |
| Validation gate | {validation['gate']} |

## Catatan Singkat

- Child tidak dihapus, hanya tidak masuk ranking utama.
- Parent master dipakai untuk ranking dan target scraping review.
- Child tanpa parent final tetap ditahan sebagai child, bukan dipromosikan ke parent.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(
    candidate_path: Path,
    mapping_candidate_path: Path,
    relations_final_path: Path,
    parent_master_path: Path,
    child_listings_final_path: Path,
    review_targets_path: Path,
    summary_path: Path,
    validation_path: Path,
    report_path: Path,
) -> tuple[dict, dict]:
    candidate = pd.read_csv(candidate_path, dtype=str, keep_default_na=False)
    mapping = pd.read_csv(mapping_candidate_path, dtype=str, keep_default_na=False)

    relations = build_relations_final(mapping)
    child_listings = build_child_listings(candidate, relations)
    parent_master = build_parent_master(candidate, child_listings)
    review_targets = build_review_targets(parent_master, parent_master_path)
    validation = validate_outputs(candidate, relations, parent_master, child_listings, review_targets)

    relations_final_path.parent.mkdir(parents=True, exist_ok=True)
    relations.to_csv(relations_final_path, index=False)
    parent_master.to_csv(parent_master_path, index=False)
    child_listings.to_csv(child_listings_final_path, index=False)
    review_targets.to_csv(review_targets_path, index=False)

    summary = {
        "generated_at": now_iso(),
        "candidate_path": str(candidate_path),
        "mapping_candidate_path": str(mapping_candidate_path),
        "relations_final_path": str(relations_final_path),
        "parent_master_path": str(parent_master_path),
        "child_listings_final_path": str(child_listings_final_path),
        "review_targets_path": str(review_targets_path),
        "candidate_rows": int(len(candidate)),
        "relations_final_rows": int(len(relations)),
        "parent_master_rows": int(len(parent_master)),
        "child_listings_rows": int(len(child_listings)),
        "child_listing_status_counts": child_listings["relation_status"].value_counts(dropna=False).to_dict(),
        "parent_with_child_count": int(parent_master["has_final_child_listing"].eq("True").sum()),
        "review_target_rows": int(len(review_targets)),
        "review_target_priority_counts": review_targets["review_scrape_priority"].value_counts(dropna=False).to_dict() if not review_targets.empty else {},
        "parent_name_detail_listing_flag_count": int(parent_master["name_looks_detail_listing"].eq("True").sum()),
        "review_target_detail_listing_flag_count": int(review_targets["name_looks_detail_listing"].eq("True").sum()) if not review_targets.empty else 0,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    validation_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(report_path, summary, validation)
    return summary, validation


def main() -> None:
    parser = argparse.ArgumentParser(description="Build final parent-child relations, parent master, child listings, and review targets.")
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--mapping-candidate", type=Path, default=DEFAULT_MAPPING_CANDIDATE)
    parser.add_argument("--relations-final", type=Path, default=DEFAULT_RELATIONS_FINAL)
    parser.add_argument("--parent-master", type=Path, default=DEFAULT_PARENT_MASTER)
    parser.add_argument("--child-listings-final", type=Path, default=DEFAULT_CHILD_LISTINGS_FINAL)
    parser.add_argument("--review-targets", type=Path, default=DEFAULT_REVIEW_TARGETS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    summary, validation = build(
        candidate_path=args.candidate,
        mapping_candidate_path=args.mapping_candidate,
        relations_final_path=args.relations_final,
        parent_master_path=args.parent_master,
        child_listings_final_path=args.child_listings_final,
        review_targets_path=args.review_targets,
        summary_path=args.summary,
        validation_path=args.validation,
        report_path=args.report,
    )
    print(f"relations_final_rows={summary['relations_final_rows']}")
    print(f"parent_master_rows={summary['parent_master_rows']}")
    print(f"child_listings_rows={summary['child_listings_rows']}")
    print(f"review_target_rows={summary['review_target_rows']}")
    print(f"validation_gate={validation['gate']}")
    print(f"accepted_child_in_parent_master={validation['accepted_child_in_parent_master']}")
    print(f"child_in_review_targets={validation['child_in_review_targets']}")


if __name__ == "__main__":
    main()
