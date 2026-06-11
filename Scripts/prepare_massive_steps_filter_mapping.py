import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "MuterBandung_Behavior_Model_Workspace"
RAW_DIR = WORKSPACE / "01_Raw_Data" / "massive_steps_bandung"
CURATED_DIR = WORKSPACE / "03_Curated"
EVAL_DIR = WORKSPACE / "04_Evaluation"

DATE_TAG = "2026-06-10"

TABULAR_FILES = {
    "train": RAW_DIR / "tabular_train-00000-of-00001.parquet",
    "validation": RAW_DIR / "tabular_validation-00000-of-00001.parquet",
    "test": RAW_DIR / "tabular_test-00000-of-00001.parquet",
}


KEEP_RULES = [
    ("alam_santai", "core_wisata", [
        "park", "garden", "lake", "mountain", "trail", "scenic", "lookout",
        "zoo", "theme park", "water park", "beach", "campground", "outdoors"
    ]),
    ("budaya_edukasi", "core_wisata", [
        "museum", "historic", "monument", "landmark", "gallery", "art",
        "performing arts", "theater", "theatre", "public art", "cultural"
    ]),
    ("religi", "core_wisata", [
        "mosque", "church", "temple", "shrine", "religious", "spiritual center"
    ]),
    ("kuliner", "support_travel", [
        "restaurant", "cafe", "café", "coffee", "food", "bakery", "dessert",
        "tea", "ice cream", "snack", "noodle", "ramen", "sushi", "steak",
        "steakhouse", "pizza", "burger", "diner", "bistro", "juice",
        "fried chicken joint", "donut shop", "bbq joint", "cupcake shop",
        "breakfast spot", "soup place", "frozen yogurt shop"
    ]),
    ("belanja", "support_travel", [
        "shopping mall", "market", "department store", "bookstore",
        "clothing store", "arts & crafts", "souvenir", "gift shop",
        "boutique", "shopping"
    ]),
    ("penginapan", "support_travel", [
        "hotel", "resort", "hostel", "bed & breakfast", "guest house"
    ]),
    ("hiburan", "support_travel", [
        "multiplex", "arcade", "karaoke", "bowling", "cinema", "nightclub",
        "club", "concert", "music venue", "entertainment", "bar", "pub"
    ]),
]

EXCLUDE_RULES = [
    ("private_residential", [
        "home (private)", "residential", "housing", "apartment", "condo",
        "neighborhood", "boarding house"
    ]),
    ("education_daily", [
        "school", "university", "college", "classroom", "student center",
        "campus", "faculty"
    ]),
    ("work_office", [
        "office", "coworking", "factory", "warehouse", "conference room",
        "meeting room", "building"
    ]),
    ("infrastructure_transport", [
        "road", "parking", "gas station", "bus station", "train station",
        "airport", "taxi", "bridge", "intersection", "toll"
    ]),
    ("health_public_service", [
        "hospital", "clinic", "doctor", "pharmacy", "police", "fire station",
        "government", "embassy", "bank", "atm", "post office"
    ]),
    ("personal_service", [
        "salon", "barbershop", "spa", "gym", "laundry", "tailor",
        "automotive", "car wash"
    ]),
]


def norm(value):
    return str(value or "").strip().lower()


def contains_any(text, patterns):
    for pattern in patterns:
        escaped = re.escape(pattern)
        if re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text):
            return True
    return False


def map_category(category):
    text = norm(category)
    if not text:
        return {
            "mapping_status": "needs_review",
            "muterbandung_label": "",
            "mapping_group": "unknown",
            "rule_reason": "empty category",
        }

    # Daily-life categories should win before broad terms like "art" or "bar".
    for reason, patterns in EXCLUDE_RULES:
        if contains_any(text, patterns):
            return {
                "mapping_status": "excluded_noise",
                "muterbandung_label": "",
                "mapping_group": "noise",
                "rule_reason": "matched exclude rule: " + reason,
            }

    for label, group, patterns in KEEP_RULES:
        if contains_any(text, patterns):
            return {
                "mapping_status": "mapped_keep",
                "muterbandung_label": label,
                "mapping_group": group,
                "rule_reason": "matched keep rule: " + label,
            }

    return {
        "mapping_status": "needs_review",
        "muterbandung_label": "",
        "mapping_group": "needs_review",
        "rule_reason": "no confident mapping rule",
    }


def load_tabular():
    frames = []
    for split, path in TABULAR_FILES.items():
        if not path.exists():
            raise FileNotFoundError(path)
        frame = pd.read_parquet(path)
        frame["split"] = split
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    return data


def build_category_mapping(data):
    counts = (
        data.groupby("venue_category", dropna=False)
        .agg(
            checkin_count=("venue_category", "size"),
            unique_venues=("venue_id", "nunique"),
            unique_users=("user_id", "nunique"),
            unique_trails=("trail_id", "nunique"),
            missing_name=("name", lambda s: int(s.isna().sum())),
            missing_latitude=("latitude", lambda s: int(s.isna().sum())),
        )
        .reset_index()
        .sort_values(["checkin_count", "venue_category"], ascending=[False, True])
    )
    mapped = counts["venue_category"].apply(map_category).apply(pd.Series)
    result = pd.concat([counts, mapped], axis=1)
    result["missing_name_pct"] = (result["missing_name"] / result["checkin_count"] * 100).round(2)
    result["missing_latitude_pct"] = (result["missing_latitude"] / result["checkin_count"] * 100).round(2)
    return result


def apply_mapping(data, mapping):
    cols = [
        "venue_category",
        "mapping_status",
        "muterbandung_label",
        "mapping_group",
        "rule_reason",
    ]
    enriched = data.merge(mapping[cols], on="venue_category", how="left")
    enriched["mapping_status"] = enriched["mapping_status"].fillna("needs_review")
    enriched["muterbandung_label"] = enriched["muterbandung_label"].fillna("")
    enriched["mapping_group"] = enriched["mapping_group"].fillna("needs_review")
    return enriched


def build_sequences(filtered):
    ordered = filtered.sort_values(["trail_id", "timestamp", "venue_id"]).copy()
    trail_rows = []
    for trail_id, group in ordered.groupby("trail_id", sort=False):
        labels = [label for label in group["muterbandung_label"].tolist() if label]
        categories = group["venue_category"].astype(str).tolist()
        venue_ids = group["venue_id"].astype(str).tolist()
        if len(labels) < 2:
            continue
        trail_rows.append({
            "trail_id": trail_id,
            "user_id": group["user_id"].iloc[0],
            "split": group["split"].iloc[0],
            "sequence_length": len(labels),
            "category_sequence": " > ".join(labels),
            "raw_category_sequence": " > ".join(categories),
            "venue_id_sequence": " > ".join(venue_ids),
            "target_next_category": labels[-1],
            "history_categories": " > ".join(labels[:-1]),
        })
    return pd.DataFrame(trail_rows)


def main():
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    data = load_tabular()
    mapping = build_category_mapping(data)
    enriched = apply_mapping(data, mapping)
    filtered = enriched[enriched["mapping_status"].eq("mapped_keep")].copy()
    needs_review = mapping[mapping["mapping_status"].eq("needs_review")].copy()
    excluded = mapping[mapping["mapping_status"].eq("excluded_noise")].copy()
    sequences = build_sequences(filtered)

    mapping_path = CURATED_DIR / f"MASSIVE_STEPS_BANDUNG_CATEGORY_MAPPING_CANDIDATE_{DATE_TAG}.csv"
    filtered_path = CURATED_DIR / f"MASSIVE_STEPS_BANDUNG_FILTERED_CHECKINS_CANDIDATE_{DATE_TAG}.csv"
    sequences_path = CURATED_DIR / f"MASSIVE_STEPS_BANDUNG_CATEGORY_SEQUENCE_CANDIDATE_{DATE_TAG}.csv"
    needs_review_path = EVAL_DIR / f"MASSIVE_STEPS_BANDUNG_CATEGORY_MAPPING_NEEDS_REVIEW_{DATE_TAG}.csv"
    excluded_path = EVAL_DIR / f"MASSIVE_STEPS_BANDUNG_EXCLUDED_NOISE_CATEGORIES_{DATE_TAG}.csv"
    summary_path = EVAL_DIR / f"MASSIVE_STEPS_BANDUNG_FILTERING_MAPPING_SUMMARY_{DATE_TAG}.json"

    mapping.to_csv(mapping_path, index=False, encoding="utf-8-sig")
    filtered.to_csv(filtered_path, index=False, encoding="utf-8-sig")
    sequences.to_csv(sequences_path, index=False, encoding="utf-8-sig")
    needs_review.to_csv(needs_review_path, index=False, encoding="utf-8-sig")
    excluded.to_csv(excluded_path, index=False, encoding="utf-8-sig")

    status_counts = mapping["mapping_status"].value_counts().to_dict()
    row_status_counts = enriched["mapping_status"].value_counts().to_dict()
    label_counts = filtered["muterbandung_label"].value_counts().to_dict()
    summary = {
        "created_at": DATE_TAG,
        "source": "CRUISEResearchGroup/Massive-STEPS-Bandung",
        "raw_rows": int(len(data)),
        "raw_categories": int(data["venue_category"].nunique()),
        "mapping_status_counts_categories": {str(k): int(v) for k, v in status_counts.items()},
        "mapping_status_counts_rows": {str(k): int(v) for k, v in row_status_counts.items()},
        "filtered_rows": int(len(filtered)),
        "filtered_row_pct": round(float(len(filtered) / len(data) * 100), 2),
        "filtered_unique_trails": int(filtered["trail_id"].nunique()),
        "filtered_unique_users": int(filtered["user_id"].nunique()),
        "filtered_unique_venues": int(filtered["venue_id"].nunique()),
        "filtered_label_counts": {str(k): int(v) for k, v in label_counts.items()},
        "sequence_rows": int(len(sequences)),
        "sequence_split_counts": {str(k): int(v) for k, v in sequences["split"].value_counts().to_dict().items()} if len(sequences) else {},
        "outputs": {
            "category_mapping": str(mapping_path),
            "filtered_checkins": str(filtered_path),
            "category_sequences": str(sequences_path),
            "needs_review_categories": str(needs_review_path),
            "excluded_noise_categories": str(excluded_path),
        },
        "decision": (
            "Use mapped_keep rows for next-category baseline. "
            "Excluded categories are not deleted from raw data; they are held out from behavior training candidate."
        ),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
