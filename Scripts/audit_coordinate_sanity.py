import math

import pandas as pd


DB_PATH = "Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv"
AUDIT_PATH = "Wisata_Workspace/01_Dataset/3_Curated/coordinate_audit.csv"

BANDUNG_CENTER = (-6.921765, 107.607069)
BANDUNG_RAYA_BOUNDS = {
    "lat_min": -7.40,
    "lat_max": -6.65,
    "lon_min": 107.25,
    "lon_max": 108.10,
}

AREA_DISTANCE_RULES = [
    (("sukawana",), 8.0, "Sukawana/Lembang coordinate too close to Bandung center"),
    (("lembang", "cikole", "jayagiri", "maribaya", "tangkuban", "grafika"), 7.0, "Lembang/Cikole coordinate too close to Bandung center"),
    (("ciwidey", "rancabali", "ranca upas", "kawah putih", "patenggang", "patuha"), 18.0, "Ciwidey/Rancabali coordinate too close to Bandung center"),
    (("pangalengan", "malabar", "wayang windu", "cukul", "cisanti"), 22.0, "Pangalengan/Malabar coordinate too close to Bandung center"),
    (("sumedang", "jatigede", "tampomas", "tanjung duriat", "cadas pangeran", "buricak"), 25.0, "Sumedang/Jatigede coordinate too close to Bandung center or outside strict scope"),
]


def haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0088
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def coerce_float(value):
    try:
        parsed = float(value)
        if math.isnan(parsed) or math.isinf(parsed):
            return None
        return parsed
    except Exception:
        return None


def text_blob(row):
    cols = ["location_name", "category", "subcategory", "tags_sintetis", "deskripsi_google"]
    return " ".join(str(row.get(col, "")) for col in cols).lower()


def audit_row(row):
    lat = coerce_float(row.get("latitude"))
    lon = coerce_float(row.get("longitude"))
    reasons = []
    distance_center = None

    if lat is None or lon is None:
        return False, None, "missing latitude/longitude"

    if lat == 0 or lon == 0:
        reasons.append("zero coordinate")

    if not (
        BANDUNG_RAYA_BOUNDS["lat_min"] <= lat <= BANDUNG_RAYA_BOUNDS["lat_max"]
        and BANDUNG_RAYA_BOUNDS["lon_min"] <= lon <= BANDUNG_RAYA_BOUNDS["lon_max"]
    ):
        reasons.append("outside broad Bandung Raya coordinate bounds")

    distance_center = haversine_km(BANDUNG_CENTER[0], BANDUNG_CENTER[1], lat, lon)
    blob = text_blob(row)
    for terms, min_distance, reason in AREA_DISTANCE_RULES:
        if any(term in blob for term in terms) and distance_center < min_distance:
            reasons.append(f"{reason}: {distance_center:.1f} km from Alun-Alun Bandung")
            break

    return len(reasons) == 0, distance_center, "; ".join(reasons)


def main():
    df = pd.read_csv(DB_PATH)
    verified_values = []
    distances = []
    reasons = []

    for _, row in df.iterrows():
        verified, distance_center, reason = audit_row(row)
        verified_values.append(bool(verified))
        distances.append(round(distance_center, 2) if distance_center is not None else None)
        reasons.append(reason)

    df["coordinate_verified"] = verified_values
    df["distance_from_alun_alun_km"] = distances
    df["coordinate_audit_reason"] = reasons

    audit_cols = [
        "location_name",
        "category",
        "display_status",
        "curation_action",
        "latitude",
        "longitude",
        "coordinate_verified",
        "distance_from_alun_alun_km",
        "coordinate_audit_reason",
    ]
    df.loc[~df["coordinate_verified"], audit_cols].to_csv(AUDIT_PATH, index=False)
    df.to_csv(DB_PATH, index=False)

    active = df[
        df["display_status"].fillna("").str.lower().eq("active_candidate")
        & ~df["curation_action"].fillna("").str.lower().eq("remove")
    ]
    print("Coordinate sanity audit completed")
    print(f"- Rows: {len(df)}")
    print(f"- Active rows: {len(active)}")
    print(f"- coordinate_verified false: {int((df['coordinate_verified'] == False).sum())}")
    print(f"- active coordinate_verified false: {int((active['coordinate_verified'] == False).sum())}")
    print(f"- audit file: {AUDIT_PATH}")


if __name__ == "__main__":
    main()
