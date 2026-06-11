import pandas as pd


DB_PATH = "Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv"
OVERRIDE_PATH = "Wisata_Workspace/01_Dataset/3_Curated/realworld_qa_overrides.csv"


def parse_labels(value):
    if not isinstance(value, str) or not value.strip():
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def serialize_labels(labels):
    cleaned = []
    for label in labels:
        label = str(label).strip()
        if label and label not in cleaned:
            cleaned.append(label)
    return ";".join(cleaned)


def remove_labels(current, labels_to_remove):
    labels = parse_labels(current)
    remove_set = {label.lower() for label in labels_to_remove}
    return serialize_labels([label for label in labels if label.lower() not in remove_set])


def add_labels(current, labels_to_add):
    labels = parse_labels(current)
    for label in labels_to_add:
        if label and label not in labels:
            labels.append(label)
    return serialize_labels(labels)


def coerce_bool(value):
    if not isinstance(value, str):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y"}


def main():
    df = pd.read_csv(DB_PATH)
    overrides = pd.read_csv(OVERRIDE_PATH).fillna("")

    applied = []
    missing = []

    for _, override in overrides.iterrows():
        name = str(override["location_name"]).strip()
        mask = df["location_name"].astype(str).str.strip().eq(name)
        if not mask.any():
            missing.append(name)
            continue

        idx = df.index[mask][0]
        for col in ["display_status", "curation_action", "price_type", "curation_note"]:
            value = override.get(col, "")
            if isinstance(value, str) and value.strip():
                df.at[idx, col] = value.strip()

        if str(override.get("is_active_verified", "")).strip():
            df.at[idx, "is_active_verified"] = coerce_bool(str(override["is_active_verified"]))

        for col in ["price_min", "price_max"]:
            value = override.get(col, "")
            if str(value).strip():
                df.at[idx, col] = int(float(value))

        remove_core = parse_labels(override.get("remove_core_labels", ""))
        remove_secondary = parse_labels(override.get("remove_secondary_labels", ""))
        add_avoid = parse_labels(override.get("add_avoid_labels", ""))

        if remove_core:
            df.at[idx, "final_core_labels"] = remove_labels(df.at[idx, "final_core_labels"], remove_core)
        if remove_secondary:
            df.at[idx, "final_secondary_labels"] = remove_labels(df.at[idx, "final_secondary_labels"], remove_secondary)
        if add_avoid:
            df.at[idx, "final_avoid_labels"] = add_labels(df.at[idx, "final_avoid_labels"], add_avoid)

        df.at[idx, "final_label_source"] = "realworld_qa_override"
        applied.append(name)

    df.to_csv(DB_PATH, index=False)

    print("Real-world QA overrides applied")
    print(f"- Applied: {len(applied)}")
    print(f"- Missing: {len(missing)}")
    if missing:
        for name in missing:
            print(f"  - {name}")

    status_counts = df["display_status"].fillna("").value_counts().to_dict()
    action_counts = df["curation_action"].fillna("").value_counts().to_dict()
    print(f"- display_status: {status_counts}")
    print(f"- curation_action: {action_counts}")


if __name__ == "__main__":
    main()
