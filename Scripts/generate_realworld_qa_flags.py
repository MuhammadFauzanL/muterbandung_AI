import pandas as pd


DB_PATH = "Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv"
NIGHT_AUDIT_PATH = "Wisata_Workspace/01_Dataset/3_Curated/night_label_audit.csv"


def parse_labels(value):
    if not isinstance(value, str) or not value.strip() or value.lower() == "nan":
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def serialize_labels(labels):
    cleaned = []
    for label in labels:
        label = str(label).strip()
        if label and label not in cleaned:
            cleaned.append(label)
    return ";".join(cleaned)


def has_label(row, label):
    label_l = label.lower()
    labels = []
    for col in ["final_primary_intent", "final_core_labels", "final_secondary_labels"]:
        labels.extend(parse_labels(str(row.get(col, ""))))
    return any(item.lower() == label_l for item in labels)


def text_blob(row):
    cols = [
        "location_name", "category", "subcategory", "tags_sintetis", "deskripsi_google",
        "catatan_jam", "ulasan_positif", "ulasan_negatif"
    ]
    return " ".join(str(row.get(col, "")) for col in cols).lower()


def parse_time(value):
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    if not value or value in {"nan", "tutup", "closed"}:
        return None
    try:
        hour, minute = value.split(":")[:2]
        return int(hour) * 60 + int(minute)
    except Exception:
        return None


def is_open_at(open_value, close_value, check="20:00"):
    open_mins = parse_time(open_value)
    close_mins = parse_time(close_value)
    check_mins = parse_time(check)
    if open_mins is None or close_mins is None or check_mins is None:
        return False
    if open_mins <= close_mins:
        return open_mins <= check_mins <= close_mins
    return check_mins >= open_mins or check_mins <= close_mins


def verify_price(row):
    try:
        price_min = float(row.get("price_min", 0))
        price_max = float(row.get("price_max", 0))
    except Exception:
        return False
    price_type = str(row.get("price_type", "")).strip().lower()
    if price_min < 0 or price_max < 0 or price_max < price_min:
        return False
    if price_type == "gratis":
        return price_min == 0 and price_max == 0
    return price_max > 0


def verify_night(row):
    if not has_label(row, "Malam"):
        return False
    open_night = (
        is_open_at(row.get("jam_buka_weekday"), row.get("jam_tutup_weekday"))
        or is_open_at(row.get("jam_buka_weekend"), row.get("jam_tutup_weekend"))
    )
    if not open_night:
        return False

    text = text_blob(row)
    positive_terms = [
        "malam", "city light", "lampu kota", "night", "sunset", "matahari terbenam",
        "nongkrong", "cafe", "kafe", "kuliner", "restoran", "mall", "belanja",
        "alun-alun", "taman kota"
    ]
    has_context = any(term in text for term in positive_terms)
    category = str(row.get("category", "")).strip().lower()
    subcategory = str(row.get("subcategory", "")).strip().lower()
    risky_nature = (
        "curug" in str(row.get("location_name", "")).lower()
        or "air terjun" in text
        or category in {"wisata alam", "rekreasi alam"}
        or "daya tarik alam" in subcategory
    )
    if risky_nature and not any(term in text for term in ["city light", "lampu kota", "sunset", "matahari terbenam"]):
        return False
    return has_context


def verify_indoor(row):
    if not has_label(row, "Indoor"):
        return False
    text = text_blob(row)
    category = str(row.get("category", "")).strip().lower()
    indoor_categories = {"tempat belajar", "tempat belanja", "tempat seni", "tempat budaya", "tempat ibadah", "tempat sejarah"}
    terms = ["indoor", "dalam ruangan", "museum", "mall", "gedung", "galeri", "pusat perbelanjaan", "vihara", "gereja", "masjid"]
    return category in indoor_categories or any(term in text for term in terms)


def verify_child_friendly(row):
    if not has_label(row, "Ramah Anak"):
        return False
    text = text_blob(row)
    category = str(row.get("category", "")).strip().lower()
    child_categories = {"rekreasi keluarga", "wahana air", "wisata satwa", "taman kota", "tempat belajar"}
    terms = [
        "ramah anak", "anak", "playground", "area bermain", "taman bermain",
        "keluarga", "edukasi", "wahana anak", "mini zoo", "waterpark"
    ]
    return category in child_categories or any(term in text for term in terms)


def verify_by_terms(row, terms):
    text = text_blob(row)
    return any(term in text for term in terms)


def infer_crowd_level(row):
    text = text_blob(row)
    if any(term in text for term in ["tidak terlalu ramai", "tidak ramai", "sepi", "tenang", "hidden gem"]):
        return "low"
    if any(term in text for term in ["sangat ramai", "ramai", "padat", "antri", "antre", "crowded"]):
        return "high"
    if str(row.get("category", "")).strip().lower() in {"tempat belanja", "taman kota"}:
        return "medium"
    return "unknown"


def infer_shopping_subtype(row):
    category = str(row.get("category", "")).strip().lower()
    if category != "tempat belanja":
        return ""

    text = text_blob(row)
    if any(term in text for term in ["factory outlet", "outlet"]):
        return "Factory Outlet"
    if any(term in text for term in ["oleh-oleh", "oleh oleh", "souvenir", "buah tangan"]):
        return "Oleh-Oleh"
    if "pasar" in text:
        return "Pasar Wisata"
    if any(term in text for term in [
        "mall", "mal", "shopping center", "pusat perbelanjaan", "citywalk",
        "plaza", "square", "paskal", "cihampelas walk", "cwalk", "bip", "kings"
    ]):
        return "Mall"
    return "Belanja Umum"


def verify_open_24h(row):
    return (
        str(row.get("jam_buka_weekday", "")).strip() == "00:00"
        and str(row.get("jam_tutup_weekday", "")).strip() == "23:59"
        and str(row.get("jam_buka_weekend", "")).strip() == "00:00"
        and str(row.get("jam_tutup_weekend", "")).strip() == "23:59"
    )


def remove_label_from_column(value, label):
    return serialize_labels([item for item in parse_labels(str(value)) if item.lower() != label.lower()])


def add_label_to_column(value, label):
    labels = parse_labels(str(value))
    if label and label not in labels:
        labels.append(label)
    return serialize_labels(labels)


def append_reason(reasons, reason):
    if reason and reason not in reasons:
        reasons.append(reason)


def main():
    df = pd.read_csv(DB_PATH)
    night_before = (
        df["final_core_labels"].fillna("").str.contains("Malam", case=False)
        | df["final_secondary_labels"].fillna("").str.contains("Malam", case=False)
    ).sum()

    reasons = []
    removed_night = 0
    for idx, row in df.iterrows():
        row_reasons = [
            item.strip()
            for item in str(row.get("qa_flag_reason", "")).split(";")
            if item.strip() and item.strip().lower() != "nan"
        ]
        price_verified = verify_price(row)
        night_verified = verify_night(row)
        indoor_verified = verify_indoor(row)
        child_verified = verify_child_friendly(row)
        parking_verified = verify_by_terms(row, ["parkir", "parking", "area parkir", "lahan parkir"])
        wheelchair_verified = verify_by_terms(row, ["disabilitas", "kursi roda", "wheelchair", "aksesibel"])
        toilet_verified = verify_by_terms(row, ["toilet", "wc", "kamar mandi"])
        mushola_verified = verify_by_terms(row, ["mushola", "musala", "musholla", "tempat sholat", "masjid"])
        pet_friendly_verified = verify_by_terms(row, ["pet friendly", "boleh membawa hewan", "anjing peliharaan", "kucing peliharaan"])
        safety_verified = verify_by_terms(row, ["aman", "keamanan", "security", "penjagaan", "satpam"])
        open_24h_verified = verify_open_24h(row) and night_verified
        crowd_level = infer_crowd_level(row)
        shopping_subtype = infer_shopping_subtype(row)

        if has_label(row, "Malam") and not night_verified:
            df.at[idx, "final_core_labels"] = remove_label_from_column(row.get("final_core_labels", ""), "Malam")
            df.at[idx, "final_secondary_labels"] = remove_label_from_column(row.get("final_secondary_labels", ""), "Malam")
            df.at[idx, "final_avoid_labels"] = serialize_labels(parse_labels(str(row.get("final_avoid_labels", ""))) + ["Malam"])
            append_reason(row_reasons, "Malam label removed: not night_verified")
            removed_night += 1

        price_type = str(row.get("price_type", "")).strip().lower()
        is_free_entry = price_verified and price_type == "gratis" and row.get("price_min", 0) == 0 and row.get("price_max", 0) == 0
        avoid_labels = [label.lower() for label in parse_labels(str(row.get("final_avoid_labels", "")))]
        if is_free_entry and not has_label(row, "Gratis") and "gratis" not in avoid_labels:
            df.at[idx, "final_secondary_labels"] = add_label_to_column(row.get("final_secondary_labels", ""), "Gratis")
            append_reason(row_reasons, "Gratis label added: verified free entry")

        if not price_verified:
            append_reason(row_reasons, "price_not_verified")
        if has_label(row, "Indoor") and not indoor_verified:
            append_reason(row_reasons, "indoor_not_verified")
        if has_label(row, "Ramah Anak") and not child_verified:
            append_reason(row_reasons, "child_friendly_not_verified")
        if shopping_subtype in {"Factory Outlet", "Oleh-Oleh"}:
            append_reason(row_reasons, f"shopping_subtype={shopping_subtype}")

        df.at[idx, "price_verified"] = bool(price_verified)
        df.at[idx, "night_verified"] = bool(night_verified)
        df.at[idx, "indoor_verified"] = bool(indoor_verified)
        df.at[idx, "child_friendly_verified"] = bool(child_verified)
        df.at[idx, "parking_verified"] = bool(parking_verified)
        df.at[idx, "wheelchair_accessible_verified"] = bool(wheelchair_verified)
        df.at[idx, "toilet_verified"] = bool(toilet_verified)
        df.at[idx, "mushola_verified"] = bool(mushola_verified)
        df.at[idx, "pet_friendly_verified"] = bool(pet_friendly_verified)
        df.at[idx, "safety_verified"] = bool(safety_verified)
        df.at[idx, "open_24h_verified"] = bool(open_24h_verified)
        df.at[idx, "crowd_level"] = crowd_level
        df.at[idx, "shopping_subtype"] = shopping_subtype
        reasons.append("; ".join(row_reasons))

    df["qa_flag_reason"] = reasons

    night_after = (
        df["final_core_labels"].fillna("").str.contains("Malam", case=False)
        | df["final_secondary_labels"].fillna("").str.contains("Malam", case=False)
    ).sum()

    current_night = (
        df["final_core_labels"].fillna("").str.contains("Malam", case=False)
        | df["final_secondary_labels"].fillna("").str.contains("Malam", case=False)
    )
    removed_by_audit = df["qa_flag_reason"].fillna("").str.contains("Malam label removed", case=False)
    audit_df = df.loc[current_night | removed_by_audit, [
        "location_name",
        "category",
        "subcategory",
        "display_status",
        "jam_buka_weekday",
        "jam_tutup_weekday",
        "jam_buka_weekend",
        "jam_tutup_weekend",
        "final_core_labels",
        "final_secondary_labels",
        "final_avoid_labels",
        "night_verified",
        "qa_flag_reason",
    ]].copy()
    audit_df["night_audit_action"] = audit_df.apply(
        lambda row: "keep" if bool(row.get("night_verified")) else "remove",
        axis=1,
    )
    audit_df.to_csv(NIGHT_AUDIT_PATH, index=False)

    df.to_csv(DB_PATH, index=False)
    print("Real-world QA flags generated")
    print(f"- night labels before: {int(night_before)}")
    print(f"- night labels removed: {int(removed_night)}")
    print(f"- night labels after: {int(night_after)}")
    print(f"- price_verified false: {int((df['price_verified'] == False).sum())}")
    print(f"- indoor_verified true: {int((df['indoor_verified'] == True).sum())}")
    print(f"- child_friendly_verified true: {int((df['child_friendly_verified'] == True).sum())}")
    print(f"- parking_verified true: {int((df['parking_verified'] == True).sum())}")
    print(f"- wheelchair_accessible_verified true: {int((df['wheelchair_accessible_verified'] == True).sum())}")
    print(f"- toilet_verified true: {int((df['toilet_verified'] == True).sum())}")
    print(f"- mushola_verified true: {int((df['mushola_verified'] == True).sum())}")
    print(f"- safety_verified true: {int((df['safety_verified'] == True).sum())}")
    print(f"- shopping_subtypes: {df['shopping_subtype'].fillna('').value_counts().to_dict()}")
    print(f"- night audit file: {NIGHT_AUDIT_PATH}")


if __name__ == "__main__":
    main()
