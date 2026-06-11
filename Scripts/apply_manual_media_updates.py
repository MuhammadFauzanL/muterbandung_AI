import argparse
import json
import os
import re
import shutil
from datetime import datetime

import pandas as pd


CURATED_PATH = os.path.join("Dataset", "3_Curated", "DATABASE_WISATA_LABELED_V2_REVIEWED.csv")
DEFAULT_INPUT_PATH = os.path.join("Dataset", "3_Curated", "media_manual_apply_ready.csv")
PREVIEW_PATH = os.path.join("Dataset", "3_Curated", "DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_PREVIEW.csv")

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


def clean_value(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def is_http_url(value):
    return re.match(r"^https?://", clean_value(value), flags=re.IGNORECASE) is not None


def ensure_media_columns(df):
    for column in MEDIA_COLUMNS:
        if column not in df.columns:
            if column == "media_available":
                df[column] = False
            elif column == "media_match_score":
                df[column] = 0.0
            else:
                df[column] = ""
    return df


def load_updates(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    updates = pd.read_csv(input_path)
    required = {
        "location_id",
        "new_media_image_url",
        "new_media_destination_url",
        "new_media_website",
    }
    missing = sorted(required - set(updates.columns))
    if missing:
        raise ValueError(f"Input file is missing required columns: {missing}")

    if "reviewer_status" in updates.columns:
        updates = updates[updates["reviewer_status"].astype(str).str.lower().eq("approved")].copy()
    if "validation_status" in updates.columns:
        updates = updates[updates["validation_status"].astype(str).str.lower().eq("valid")].copy()
    return updates


def validate_update_row(row):
    image_url = clean_value(row.get("new_media_image_url"))
    destination_url = clean_value(row.get("new_media_destination_url"))
    website = clean_value(row.get("new_media_website"))
    errors = []

    if not any([image_url, destination_url, website]):
        errors.append("No new media URL provided.")
    for field, url in [
        ("new_media_image_url", image_url),
        ("new_media_destination_url", destination_url),
        ("new_media_website", website),
    ]:
        if url and not is_http_url(url):
            errors.append(f"{field} is not an HTTP URL.")
    return errors


def apply_updates(curated, updates):
    curated = ensure_media_columns(curated.copy())
    applied = []
    skipped = []
    duplicate_ids = updates["location_id"][updates["location_id"].duplicated()].astype(str).tolist()
    if duplicate_ids:
        raise ValueError(f"Duplicate location_id values in update file: {sorted(set(duplicate_ids))}")

    for _, update in updates.iterrows():
        location_id = clean_value(update.get("location_id"))
        if not location_id:
            skipped.append({"location_id": "", "reason": "missing location_id"})
            continue

        errors = validate_update_row(update)
        if errors:
            skipped.append({"location_id": location_id, "reason": " | ".join(errors)})
            continue

        mask = curated["location_id"].astype(str) == location_id
        if not mask.any():
            skipped.append({"location_id": location_id, "reason": "location_id not found in curated dataset"})
            continue

        image_url = clean_value(update.get("new_media_image_url"))
        destination_url = clean_value(update.get("new_media_destination_url"))
        website = clean_value(update.get("new_media_website"))
        source_note = clean_value(update.get("new_media_source_note")) or "manual_colab_review"
        reviewer_note = clean_value(update.get("reviewer_note")) or "Filled from manual media Colab workflow."

        curated.loc[mask, "media_available"] = True
        curated.loc[mask, "media_image_url"] = image_url
        curated.loc[mask, "media_destination_url"] = destination_url
        curated.loc[mask, "media_website"] = website
        curated.loc[mask, "media_source"] = source_note
        curated.loc[mask, "media_place_id"] = clean_value(update.get("media_place_id"))
        curated.loc[mask, "media_match_title"] = clean_value(update.get("location_name")) or clean_value(curated.loc[mask, "location_name"].iloc[0])
        curated.loc[mask, "media_match_score"] = 1.0
        curated.loc[mask, "media_match_method"] = "manual_colab_review"
        curated.loc[mask, "media_audit_status"] = "accepted"
        curated.loc[mask, "media_audit_note"] = reviewer_note
        applied.append(location_id)

    return curated, applied, skipped


def main():
    parser = argparse.ArgumentParser(description="Apply approved manual media updates to curated dataset.")
    parser.add_argument("--input", default=DEFAULT_INPUT_PATH, help="CSV exported from Media_Fill_Google_Colab.ipynb.")
    parser.add_argument("--curated", default=CURATED_PATH, help="Curated dataset path.")
    parser.add_argument("--apply", action="store_true", help="Write changes to curated dataset with backup.")
    parser.add_argument("--dry-run", action="store_true", help="Write preview only; default when --apply is absent.")
    args = parser.parse_args()

    curated = pd.read_csv(args.curated)
    updates = load_updates(args.input)
    updated, applied, skipped = apply_updates(curated, updates)

    if args.apply:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{args.curated}.bak_manual_media_{timestamp}"
        shutil.copyfile(args.curated, backup_path)
        updated.to_csv(args.curated, index=False)
        output_path = args.curated
    else:
        updated.to_csv(PREVIEW_PATH, index=False)
        backup_path = None
        output_path = PREVIEW_PATH

    summary = {
        "input": args.input,
        "output": output_path,
        "backup": backup_path,
        "apply": bool(args.apply),
        "candidate_updates": int(len(updates)),
        "applied": int(len(applied)),
        "skipped": skipped,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
