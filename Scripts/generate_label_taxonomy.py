import ast
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


SOURCE_DB = Path("DATABASE_WISATA_FINAL_PARIPURNA.csv")
OUTPUT_DIR = Path("Dataset") / "3_Curated"
LABELED_OUTPUT = OUTPUT_DIR / "DATABASE_WISATA_LABELED_V2.csv"
REVIEW_OUTPUT = OUTPUT_DIR / "label_review_queue.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "label_taxonomy_summary.md"

TAXONOMY = [
    "Alam",
    "Keluarga",
    "Ramah Anak",
    "Kuliner",
    "Belanja",
    "Edukasi",
    "Sejarah",
    "Budaya",
    "Spot Foto",
    "Santai/Healing",
    "Petualangan",
    "Religi",
    "Malam",
    "Indoor",
    "Outdoor",
    "Gratis",
]

UTILITY_LABELS = {"Gratis", "Malam", "Indoor", "Outdoor"}

CATEGORY_RULES = {
    "wisata alam": {"Alam": 4.0, "Outdoor": 2.5, "Spot Foto": 1.5, "Santai/Healing": 1.5},
    "rekreasi alam": {"Alam": 4.0, "Outdoor": 2.5, "Spot Foto": 1.5, "Santai/Healing": 1.5},
    "tempat camping": {"Alam": 3.5, "Petualangan": 3.5, "Outdoor": 2.5, "Santai/Healing": 1.0},
    "wisata petualangan": {"Petualangan": 4.5, "Alam": 3.0, "Outdoor": 2.5},
    "rekreasi keluarga": {"Keluarga": 4.5, "Ramah Anak": 2.5},
    "wahana air": {"Keluarga": 3.5, "Ramah Anak": 2.5, "Petualangan": 2.0, "Outdoor": 1.0},
    "wisata satwa": {"Keluarga": 3.5, "Ramah Anak": 3.0, "Edukasi": 3.0, "Outdoor": 1.5},
    "taman kota": {"Santai/Healing": 3.5, "Keluarga": 2.5, "Outdoor": 2.0, "Ramah Anak": 1.5, "Spot Foto": 1.0},
    "tempat belanja": {"Belanja": 5.0, "Indoor": 2.0, "Kuliner": 1.0, "Santai/Healing": 0.8},
    "tempat kuliner": {"Kuliner": 5.0, "Santai/Healing": 2.0},
    "tempat sejarah": {"Sejarah": 5.0, "Edukasi": 2.5, "Budaya": 1.5, "Spot Foto": 1.0},
    "tempat belajar": {"Edukasi": 5.0, "Indoor": 2.0, "Keluarga": 1.0},
    "tempat budaya": {"Budaya": 4.5, "Edukasi": 2.0, "Spot Foto": 1.0},
    "tempat seni": {"Budaya": 4.0, "Edukasi": 1.5, "Spot Foto": 2.0, "Indoor": 1.0},
    "desa wisata": {"Budaya": 3.5, "Keluarga": 2.0, "Edukasi": 1.5, "Outdoor": 1.5},
    "tempat ibadah": {"Religi": 5.0, "Budaya": 1.5, "Sejarah": 1.0},
    "penginapan wisata": {"Santai/Healing": 2.5, "Keluarga": 1.0},
}

KEYWORD_RULES = {
    "Alam": [
        "alam", "gunung", "curug", "air terjun", "danau", "situ", "bukit",
        "tebing", "hutan", "kebun teh", "perkebunan", "pemandian air panas",
        "camping", "glamping", "panorama", "pemandangan", "sejuk", "asri",
        "ranca", "lembah", "kawah", "sungai",
    ],
    "Keluarga": [
        "keluarga", "rekreasi keluarga", "anak", "anak-anak", "wahana",
        "eduwisata", "liburan keluarga", "family", "kids",
    ],
    "Ramah Anak": [
        "ramah anak", "anak", "anak-anak", "playground", "taman bermain",
        "balita", "kids", "wahana anak", "peternakan", "eduwisata",
    ],
    "Kuliner": [
        "kuliner", "restoran", "restaurant", "cafe", "kafe", "coffee",
        "eatery", "food court", "pujasera", "makanan", "warung",
        "rumah makan", "kopi", "sunda", "jajanan", "tempat makan",
    ],
    "Belanja": [
        "belanja", "mall", "mal", "shopping", "pusat perbelanjaan",
        "factory outlet", "outlet", "oleh-oleh", "souvenir", "pasar",
        "retailer", "toko", "buah tangan",
    ],
    "Edukasi": [
        "edukasi", "edukatif", "belajar", "museum", "sains", "science",
        "geologi", "sejarah", "peternakan", "pertanian", "interaktif",
        "eduwisata", "observatorium", "pembelajaran", "pengetahuan",
    ],
    "Sejarah": [
        "sejarah", "bersejarah", "heritage", "kolonial", "monumen",
        "gedung tua", "situs", "prasasti", "pahlawan", "asia afrika",
        "konferensi", "merdeka",
    ],
    "Budaya": [
        "budaya", "seni", "angklung", "galeri", "adat", "tradisional",
        "chinatown", "pecinan", "kerajinan", "kesenian", "sunda",
    ],
    "Spot Foto": [
        "foto", "spot foto", "instagram", "instagramable", "view",
        "pemandangan", "panorama", "sunrise", "sunset", "tebing",
        "bukit", "ikonik", "3d", "lanskap",
    ],
    "Santai/Healing": [
        "santai", "healing", "tenang", "ngobrol", "nongkrong",
        "ruang publik", "taman", "kopi", "coffee", "pemandangan",
        "sejuk", "view", "rileks", "refreshing",
    ],
    "Petualangan": [
        "petualangan", "outbound", "rafting", "atv", "camping",
        "glamping", "trekking", "hiking", "offroad", "flying fox",
        "ekstrem", "wahana ekstrem", "adventure",
    ],
    "Religi": [
        "masjid", "gereja", "vihara", "klenteng", "ibadah", "makam",
        "pesantren", "religi", "ziarah",
    ],
    "Malam": [
        "malam", "night", "24 jam", "nongkrong malam",
    ],
    "Indoor": [
        "indoor", "museum", "mall", "mal", "gedung", "bioskop",
        "galeri", "ruang pamer", "pusat perbelanjaan",
    ],
    "Outdoor": [
        "outdoor", "alam", "taman", "gunung", "curug", "danau",
        "situ", "hutan", "camping", "glamping", "kebun",
    ],
}

OLD_LABEL_MAP = {
    "Alam": "Alam",
    "Ramah Anak": "Ramah Anak",
    "Kuliner": "Kuliner",
    "Belanja": "Belanja",
    "Edukasi": "Edukasi",
    "Spot Foto": "Spot Foto",
    "Santai/Healing": "Santai/Healing",
    "Wahana Ekstrem": "Petualangan",
}

EXPECTED_BY_CATEGORY = {
    "wisata alam": {"Alam", "Outdoor"},
    "rekreasi alam": {"Alam", "Outdoor"},
    "tempat camping": {"Alam", "Petualangan", "Outdoor"},
    "wisata petualangan": {"Petualangan", "Alam", "Outdoor"},
    "rekreasi keluarga": {"Keluarga", "Ramah Anak"},
    "wahana air": {"Keluarga", "Ramah Anak", "Petualangan"},
    "wisata satwa": {"Keluarga", "Ramah Anak", "Edukasi"},
    "taman kota": {"Santai/Healing", "Keluarga", "Outdoor"},
    "tempat belanja": {"Belanja"},
    "tempat kuliner": {"Kuliner"},
    "tempat sejarah": {"Sejarah", "Edukasi"},
    "tempat belajar": {"Edukasi"},
    "tempat budaya": {"Budaya"},
    "tempat seni": {"Budaya", "Spot Foto"},
    "desa wisata": {"Budaya", "Keluarga", "Outdoor"},
    "tempat ibadah": {"Religi"},
}

BASE_AVOID_BY_CATEGORY = {
    "tempat belanja": {"Alam", "Sejarah", "Religi", "Petualangan"},
    "tempat sejarah": {"Kuliner", "Belanja", "Petualangan"},
    "tempat belajar": {"Belanja", "Kuliner", "Petualangan"},
    "tempat kuliner": {"Belanja", "Sejarah", "Religi", "Petualangan"},
    "wisata alam": {"Belanja", "Indoor", "Religi"},
    "rekreasi alam": {"Belanja", "Indoor", "Religi"},
    "taman kota": {"Belanja", "Petualangan", "Sejarah"},
    "tempat ibadah": {"Kuliner", "Belanja", "Petualangan"},
}


def clean_text(value):
    if pd.isna(value):
        return ""
    value = str(value).lower()
    value = re.sub(r"[^a-z0-9\s/\-&]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def parse_labels(value):
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except Exception:
        return []
    return []


def add_score(scores, evidence, label, points, reason):
    if label not in TAXONOMY:
        return
    scores[label] += points
    evidence[label].append(f"{reason} (+{points:g})")


def count_keyword_hits(text, keywords):
    hits = []
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, text):
            hits.append(keyword)
    return hits


def parse_close_hour(value):
    if not isinstance(value, str) or ":" not in value:
        return None
    try:
        hour, minute = value.split(":")[:2]
        return int(hour) * 60 + int(minute)
    except Exception:
        return None


def is_open_late(row):
    for column in ("jam_tutup_weekday", "jam_tutup_weekend"):
        close_minute = parse_close_hour(row.get(column))
        if close_minute is None:
            continue
        if close_minute >= 20 * 60 or close_minute <= 3 * 60:
            return True
    return False


def compute_confidence(scores, primary_intent, category):
    if not primary_intent:
        return 0.0
    ordered = sorted(scores.values(), reverse=True)
    top = ordered[0] if ordered else 0.0
    second = ordered[1] if len(ordered) > 1 else 0.0
    margin = max(0.0, top - second)
    expected = EXPECTED_BY_CATEGORY.get(category, set())
    alignment = 1.0 if primary_intent in expected else 0.0
    confidence = (
        min(1.0, top / 8.0) * 0.55
        + min(1.0, margin / 3.0) * 0.25
        + alignment * 0.20
    )
    return round(max(0.0, min(1.0, confidence)), 3)


def choose_labels(scores, avoid_labels):
    positive = [(label, score) for label, score in scores.items() if score > 0 and label not in avoid_labels]
    positive.sort(key=lambda item: (item[0] in UTILITY_LABELS, -item[1], item[0]))
    primary_pool = [item for item in positive if item[0] not in UTILITY_LABELS]
    primary = primary_pool[0][0] if primary_pool else (positive[0][0] if positive else "")

    strong_nonutility = [(label, score) for label, score in positive if score >= 3.0 and label not in UTILITY_LABELS]
    strong_utility = [(label, score) for label, score in positive if score >= 3.0 and label in UTILITY_LABELS]
    alternate_family_evidence = [
        label for label, _ in strong_nonutility
        if label not in {"Keluarga", "Ramah Anak"}
    ]
    core = []
    deferred = []
    for label, _ in strong_nonutility:
        if (
            label == "Ramah Anak"
            and "Keluarga" in core
            and len(alternate_family_evidence) >= 2
        ):
            deferred.append(label)
            continue
        core.append(label)
        if len(core) == 3:
            break
    if len(core) < 3:
        for label, _ in strong_utility:
            if label not in core:
                core.append(label)
            if len(core) == 3:
                break
    if primary and primary not in core:
        core = [primary] + core[:2]
    secondary = [
        label
        for label, score in positive
        if label not in core and score >= 1.5
    ][:3]
    for label in deferred:
        if label not in core and label not in secondary:
            secondary = ([label] + secondary)[:3]
    return primary, core, secondary


def label_row(row):
    category = clean_text(row.get("category"))
    subcategory = clean_text(row.get("subcategory"))
    description = clean_text(row.get("deskripsi_google"))
    tags = clean_text(row.get("tags_sintetis"))
    name = clean_text(row.get("location_name"))
    combined = " ".join([name, category, subcategory, description, tags])
    old_labels = parse_labels(row.get("multi_labels"))

    scores = defaultdict(float)
    evidence = defaultdict(list)

    for label, points in CATEGORY_RULES.get(category, {}).items():
        add_score(scores, evidence, label, points, f"category={row.get('category')}")

    weighted_texts = [
        (subcategory, 1.6, "subcategory"),
        (tags, 1.4, "tags"),
        (description, 1.0, "description"),
        (name, 0.8, "name"),
    ]
    for label, keywords in KEYWORD_RULES.items():
        for text, weight, source in weighted_texts:
            hits = count_keyword_hits(text, keywords)
            if hits:
                points = min(3.0, 0.75 * len(hits)) * weight
                shown = ", ".join(hits[:4])
                add_score(scores, evidence, label, round(points, 2), f"{source} keyword: {shown}")

    for old_label in old_labels:
        mapped = OLD_LABEL_MAP.get(old_label)
        if mapped:
            has_keyword_evidence = bool(count_keyword_hits(combined, KEYWORD_RULES.get(mapped, [])))
            category_supports_label = mapped in EXPECTED_BY_CATEGORY.get(category, set())
            points = 1.0 if has_keyword_evidence or category_supports_label else 0.25
            add_score(scores, evidence, mapped, points, f"old multi_labels={old_label}")

    if category == "rekreasi keluarga":
        if count_keyword_hits(combined, KEYWORD_RULES["Alam"]):
            add_score(scores, evidence, "Alam", 2.0, "family attraction with explicit nature evidence")
        if count_keyword_hits(combined, KEYWORD_RULES["Kuliner"]):
            add_score(scores, evidence, "Kuliner", 2.5, "family attraction with explicit culinary evidence")
        if count_keyword_hits(combined, KEYWORD_RULES["Petualangan"]):
            add_score(scores, evidence, "Petualangan", 1.5, "family attraction with adventure/outbound evidence")

    if category == "penginapan wisata" and count_keyword_hits(combined, KEYWORD_RULES["Alam"]):
        add_score(scores, evidence, "Alam", 1.5, "lodging attraction with explicit nature evidence")

    price_type = clean_text(row.get("price_type"))
    price_max = row.get("price_max")
    if price_type == "gratis" or (not pd.isna(price_max) and float(price_max) == 0):
        add_score(scores, evidence, "Gratis", 3.0, "price_type/price_max indicates free")

    if is_open_late(row):
        add_score(scores, evidence, "Malam", 1.5, "opening hours support night visit")

    # Risk-control penalties so incidental words do not become core intent too easily.
    if category in {"tempat belanja", "tempat sejarah", "tempat belajar", "tempat seni", "tempat budaya", "tempat kuliner", "tempat ibadah"}:
        if scores.get("Alam", 0) < 4.0:
            scores["Alam"] -= 2.5
            evidence["Alam"].append("penalty: non-nature primary category (-2.5)")
    if category != "tempat belanja" and scores.get("Belanja", 0) < 4.0:
        scores["Belanja"] -= 2.0
        evidence["Belanja"].append("penalty: not a primary shopping category (-2)")
    if category != "tempat kuliner" and scores.get("Kuliner", 0) < 4.0:
        scores["Kuliner"] -= 1.5
        evidence["Kuliner"].append("penalty: culinary evidence not dominant (-1.5)")

    avoid_labels = set(BASE_AVOID_BY_CATEGORY.get(category, set()))
    for label in TAXONOMY:
        if scores.get(label, 0) <= -1.5:
            avoid_labels.add(label)

    primary, core, secondary = choose_labels(scores, avoid_labels)
    confidence = compute_confidence(scores, primary, category)

    review_reasons = []
    expected = EXPECTED_BY_CATEGORY.get(category, set())
    if confidence < 0.65:
        review_reasons.append("confidence < 0.65")
    if primary and expected and primary not in expected:
        review_reasons.append("primary_intent does not align with category")
    if not core:
        review_reasons.append("no strong core label")
    if "Belanja" in core and category != "tempat belanja":
        review_reasons.append("Belanja core label outside shopping category")
    if "Alam" in core and category in {"tempat belanja", "tempat sejarah", "tempat belajar", "tempat kuliner", "tempat ibadah"}:
        review_reasons.append("Alam core label suspicious for non-nature category")
    if "Kuliner" in core and category not in {"tempat kuliner", "rekreasi keluarga", "tempat belanja", "taman kota"}:
        review_reasons.append("Kuliner core label needs attraction-level evidence")
    if "Ramah Anak" in core and not any(term in combined for term in ["anak", "keluarga", "playground", "wahana", "kids", "eduwisata"]):
        review_reasons.append("Ramah Anak lacks explicit evidence")
    if set(core).intersection(avoid_labels):
        review_reasons.append("core label conflicts with avoid_labels")

    reason_parts = []
    for label in [primary] + [x for x in core + secondary if x != primary]:
        if label and evidence.get(label):
            reason_parts.append(f"{label}: " + " | ".join(evidence[label][:3]))

    return {
        "primary_intent": primary,
        "core_labels": core,
        "secondary_labels": secondary,
        "avoid_labels": sorted(avoid_labels),
        "label_confidence": confidence,
        "needs_manual_review": bool(review_reasons),
        "review_reason": "; ".join(review_reasons),
        "label_reason": " || ".join(reason_parts),
        "label_scores_json": json.dumps({k: round(v, 3) for k, v in sorted(scores.items())}, ensure_ascii=False),
    }


def to_semicolon_list(value):
    if isinstance(value, list):
        return ";".join(value)
    return value


def main():
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Source database not found: {SOURCE_DB}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(SOURCE_DB)
    label_rows = [label_row(row) for _, row in df.iterrows()]
    label_df = pd.DataFrame(label_rows)
    out = pd.concat([df.copy(), label_df], axis=1)

    for column in ("core_labels", "secondary_labels", "avoid_labels"):
        out[column] = out[column].apply(to_semicolon_list)

    out["label_source"] = "auto_rule_v1"
    out["review_status"] = out["needs_manual_review"].map(lambda value: "needs_review" if value else "auto_approved")
    out["manual_primary_intent"] = ""
    out["manual_core_labels"] = ""
    out["manual_secondary_labels"] = ""
    out["manual_avoid_labels"] = ""

    out.to_csv(LABELED_OUTPUT, index=False, encoding="utf-8")

    review_columns = [
        "location_name",
        "category",
        "subcategory",
        "deskripsi_google",
        "tags_sintetis",
        "multi_labels",
        "primary_intent",
        "core_labels",
        "secondary_labels",
        "avoid_labels",
        "label_confidence",
        "review_reason",
        "label_reason",
        "manual_primary_intent",
        "manual_core_labels",
        "manual_secondary_labels",
        "manual_avoid_labels",
        "review_status",
    ]
    review_df = out[out["needs_manual_review"]].copy()
    review_df[review_columns].to_csv(REVIEW_OUTPUT, index=False, encoding="utf-8")

    primary_counts = Counter(out["primary_intent"])
    core_counts = Counter()
    for value in out["core_labels"]:
        core_counts.update([item for item in str(value).split(";") if item])
    reason_counts = Counter()
    for value in out.loc[out["needs_manual_review"], "review_reason"]:
        reason_counts.update([item.strip() for item in str(value).split(";") if item.strip()])

    approved = int((~out["needs_manual_review"]).sum())
    needs_review = int(out["needs_manual_review"].sum())
    summary_lines = [
        "# Label Taxonomy V2 Summary",
        "",
        f"- Source rows: {len(out)}",
        f"- Auto approved: {approved}",
        f"- Needs manual review: {needs_review}",
        f"- Review rate: {needs_review / len(out) * 100:.1f}%",
        "",
        "## Primary Intent Counts",
        *[f"- {label}: {count}" for label, count in primary_counts.most_common()],
        "",
        "## Core Label Counts",
        *[f"- {label}: {count}" for label, count in core_counts.most_common()],
        "",
        "## Review Reasons",
        *[f"- {reason}: {count}" for reason, count in reason_counts.most_common()],
        "",
        "## Output Files",
        f"- {LABELED_OUTPUT.as_posix()}",
        f"- {REVIEW_OUTPUT.as_posix()}",
    ]
    SUMMARY_OUTPUT.write_text("\n".join(summary_lines), encoding="utf-8")

    print("Label taxonomy generation completed.")
    print(f"Rows: {len(out)}")
    print(f"Auto approved: {approved}")
    print(f"Needs manual review: {needs_review}")
    print(f"Output: {LABELED_OUTPUT}")
    print(f"Review queue: {REVIEW_OUTPUT}")
    print(f"Summary: {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
