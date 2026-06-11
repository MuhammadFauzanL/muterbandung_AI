from pathlib import Path

import pandas as pd


CURATED_DIR = Path("Dataset") / "3_Curated"
LABELED_PATH = CURATED_DIR / "DATABASE_WISATA_LABELED_V2.csv"
QUEUE_PATH = CURATED_DIR / "label_review_queue.csv"
DECISIONS_PATH = CURATED_DIR / "manual_label_review_decisions.csv"
FINAL_PATH = CURATED_DIR / "DATABASE_WISATA_LABELED_V2_REVIEWED.csv"


FINAL_COLUMNS = {
    "primary_intent": "final_primary_intent",
    "core_labels": "final_core_labels",
    "secondary_labels": "final_secondary_labels",
    "avoid_labels": "final_avoid_labels",
}

STATUS_BY_ACTION = {
    "keep": "reviewed_keep",
    "needs_review": "needs_reverification",
    "hide_temporarily": "temporarily_hidden",
    "remove": "remove_from_scope",
}


def _normalize_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _load_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return pd.read_csv(path)


def _ensure_text_columns(df, columns):
    for column in columns:
        if column not in df.columns:
            df[column] = ""
        df[column] = df[column].astype("object").where(df[column].notna(), "")
    return df


def _initialize_final_columns(df):
    for source, target in FINAL_COLUMNS.items():
        df[target] = df[source].fillna("")
    df["curation_action"] = "keep"
    df["display_status"] = "active_candidate"
    df["is_active_verified"] = ""
    df["manual_review_confidence"] = ""
    df["curation_note"] = ""
    df["final_label_source"] = "auto_rule_v1"
    _ensure_text_columns(df, [
        "manual_primary_intent",
        "manual_core_labels",
        "manual_secondary_labels",
        "manual_avoid_labels",
        "review_status",
    ])
    return df


def _apply_decision_to_labeled(df, decision):
    name = decision["location_name"]
    mask = df["location_name"] == name
    if not mask.any():
        raise ValueError(f"Decision location not found in labeled dataset: {name}")

    df.loc[mask, "final_primary_intent"] = decision["manual_primary_intent"]
    df.loc[mask, "final_core_labels"] = decision["manual_core_labels"]
    df.loc[mask, "final_secondary_labels"] = decision["manual_secondary_labels"]
    df.loc[mask, "final_avoid_labels"] = decision["manual_avoid_labels"]
    df.loc[mask, "curation_action"] = decision["action"]
    df.loc[mask, "display_status"] = decision["display_status"]
    df.loc[mask, "is_active_verified"] = _normalize_bool(decision["is_active_verified"])
    df.loc[mask, "manual_review_confidence"] = decision["manual_confidence"]
    df.loc[mask, "curation_note"] = decision["decision_note"]
    df.loc[mask, "final_label_source"] = "manual_browser_review_v1"
    df.loc[mask, "manual_primary_intent"] = decision["manual_primary_intent"]
    df.loc[mask, "manual_core_labels"] = decision["manual_core_labels"]
    df.loc[mask, "manual_secondary_labels"] = decision["manual_secondary_labels"]
    df.loc[mask, "manual_avoid_labels"] = decision["manual_avoid_labels"]
    df.loc[mask, "review_status"] = STATUS_BY_ACTION.get(decision["action"], decision["action"])
    df.loc[mask, "needs_manual_review"] = decision["action"] in {"needs_review", "hide_temporarily"}


def _apply_decision_to_queue(queue_df, decision):
    name = decision["location_name"]
    mask = queue_df["location_name"] == name
    if not mask.any():
        return
    queue_df.loc[mask, "manual_primary_intent"] = decision["manual_primary_intent"]
    queue_df.loc[mask, "manual_core_labels"] = decision["manual_core_labels"]
    queue_df.loc[mask, "manual_secondary_labels"] = decision["manual_secondary_labels"]
    queue_df.loc[mask, "manual_avoid_labels"] = decision["manual_avoid_labels"]
    queue_df.loc[mask, "manual_review_confidence"] = decision["manual_confidence"]
    queue_df.loc[mask, "curation_action"] = decision["action"]
    queue_df.loc[mask, "display_status"] = decision["display_status"]
    queue_df.loc[mask, "is_active_verified"] = _normalize_bool(decision["is_active_verified"])
    queue_df.loc[mask, "decision_note"] = decision["decision_note"]
    queue_df.loc[mask, "review_status"] = STATUS_BY_ACTION.get(decision["action"], decision["action"])


def main():
    labeled_df = _initialize_final_columns(_load_csv(LABELED_PATH))
    queue_df = _load_csv(QUEUE_PATH)
    _ensure_text_columns(queue_df, [
        "manual_primary_intent",
        "manual_core_labels",
        "manual_secondary_labels",
        "manual_avoid_labels",
        "manual_review_confidence",
        "curation_action",
        "display_status",
        "is_active_verified",
        "decision_note",
        "review_status",
    ])
    decisions_df = _load_csv(DECISIONS_PATH)

    decision_names = set(decisions_df["location_name"])
    missing_from_queue = sorted(decision_names - set(queue_df["location_name"]))
    if missing_from_queue:
        print("Warning: decisions not present in review queue:")
        for name in missing_from_queue:
            print(f"- {name}")

    for _, decision in decisions_df.iterrows():
        _apply_decision_to_labeled(labeled_df, decision)
        _apply_decision_to_queue(queue_df, decision)

    labeled_df.to_csv(FINAL_PATH, index=False, encoding="utf-8")
    queue_df.to_csv(QUEUE_PATH, index=False, encoding="utf-8")

    print("Manual browser review decisions applied.")
    print(f"Reviewed output: {FINAL_PATH}")
    print(f"Updated queue: {QUEUE_PATH}")
    print()
    print(labeled_df["curation_action"].value_counts(dropna=False).to_string())
    print()
    print(labeled_df["display_status"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
