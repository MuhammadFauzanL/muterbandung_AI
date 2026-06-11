import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from oleh_oleh_recommender import OlehOlehRecommender


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "OlehOleh_Workspace" / "04_Evaluation"
DETAIL_PATH = OUT_DIR / "OLEH_OLEH_RECOMMENDER_MANUAL_QUERY_AUDIT_DETAIL_2026-06-10.csv"
TESTS_PATH = OUT_DIR / "OLEH_OLEH_RECOMMENDER_MANUAL_QUERY_AUDIT_TESTS_2026-06-10.csv"
SUMMARY_PATH = OUT_DIR / "OLEH_OLEH_RECOMMENDER_MANUAL_QUERY_AUDIT_SUMMARY_2026-06-10.json"

FARM_HOUSE = {"user_lat": -6.8329, "user_lon": 107.6057}
LEMBANG_CENTER = {"user_lat": -6.8116, "user_lon": 107.6170}

TESTS = [
    {"id": "OO-AUD-001", "query": "snack murah Bandung", "top_k": 5, "expect_top_categories": ["snack_keripik"], "top_n": 4},
    {"id": "OO-AUD-002", "query": "snack di bawah 50 ribu", "top_k": 10, "expect_top_categories": ["snack_keripik"], "top_n": 4, "max_price_min": 50000},
    {"id": "OO-AUD-003", "query": "oleh-oleh tahan perjalanan jauh", "top_k": 8, "expect_durability_any_top_n": ["tinggi"], "top_n": 5},
    {"id": "OO-AUD-004", "query": "camilan di bus untuk rombongan", "top_k": 5, "expect_top_categories": ["snack_keripik"], "top_n": 3},
    {"id": "OO-AUD-005", "query": "oleh-oleh untuk keluarga", "top_k": 5, "expect_any_results": True},
    {"id": "OO-AUD-006", "query": "buah tangan keluarga Bandung", "top_k": 5, "expect_any_results": True},
    {"id": "OO-AUD-007", "query": "souvenir Bandung", "top_k": 5, "expect_top_categories": ["souvenir_non_makanan"], "top_n": 1, "expect_name_contains": ["Karma"]},
    {"id": "OO-AUD-008", "query": "kaos souvenir Bandung", "top_k": 5, "expect_top_categories": ["souvenir_non_makanan"], "top_n": 1, "expect_name_contains": ["Karma"]},
    {"id": "OO-AUD-009", "query": "kurma haji umroh Bandung", "top_k": 5, "expect_top_categories": ["haji_umroh_kurma"], "top_n": 1, "expect_name_contains": ["Bakulsaudi"]},
    {"id": "OO-AUD-010", "query": "paket hampers haji umroh", "top_k": 5, "expect_top_categories": ["haji_umroh_kurma"], "top_n": 1},
    {"id": "OO-AUD-011", "query": "tahu susu Lembang", "top_k": 5, "expect_top_categories": ["tahu_tempe"], "top_n": 2, "forbid_top_categories": ["olahan_susu"]},
    {"id": "OO-AUD-012", "query": "tempe spesial Lembang", "top_k": 5, "expect_top_categories": ["tahu_tempe"], "top_n": 2},
    {"id": "OO-AUD-013", "query": "susu murni Lembang", "top_k": 5, "expect_top_categories": ["olahan_susu"], "top_n": 3},
    {"id": "OO-AUD-014", "query": "yoghurt segar Lembang", "top_k": 5, "expect_top_categories": ["olahan_susu"], "top_n": 3},
    {"id": "OO-AUD-015", "query": "bolu susu Lembang", "top_k": 5, "expect_top_categories": ["kue_bolu_pastry"], "top_n": 5},
    {"id": "OO-AUD-016", "query": "brownies susu Lembang", "top_k": 5, "expect_top_categories": ["kue_bolu_pastry"], "top_n": 5, "expect_name_contains_any_top_n": ["Brownies"]},
    {"id": "OO-AUD-017", "query": "donat susu Lembang", "top_k": 5, "expect_top_categories": ["kue_bolu_pastry"], "top_n": 3, "expect_name_contains": ["Donatsu"]},
    {"id": "OO-AUD-018", "query": "almond crispy cheese Bandung", "top_k": 5, "expect_top_categories": ["kue_bolu_pastry"], "top_n": 3, "expect_name_contains_any_top_n": ["Kasohor"]},
    {"id": "OO-AUD-019", "query": "kue balok Lembang", "top_k": 5, "expect_top_categories": ["kue_bolu_pastry"], "top_n": 3, "expect_name_contains_any_top_n": ["Kue Balok"]},
    {"id": "OO-AUD-020", "query": "makanan fresh Lembang", "top_k": 6, "expect_durability_any_top_n": ["rendah"], "top_n": 4},
    {"id": "OO-AUD-021", "query": "makanan basah langsung dimakan", "top_k": 6, "expect_durability_any_top_n": ["rendah"], "top_n": 4},
    {"id": "OO-AUD-022", "query": "oleh-oleh di bawah 20 ribu", "top_k": 10, "max_price_min": 20000},
    {"id": "OO-AUD-023", "query": "oleh-oleh di bawah 50 ribu", "top_k": 10, "max_price_min": 50000},
    {"id": "OO-AUD-024", "query": "oleh-oleh murah untuk rombongan", "top_k": 8, "max_price_min": 50000},
    {"id": "OO-AUD-025", "query": "oleh-oleh premium untuk keluarga", "top_k": 5, "expect_any_results": True},
    {"id": "OO-AUD-026", "query": "makanan kering ringan Bandung", "top_k": 5, "expect_top_categories": ["snack_keripik"], "top_n": 3},
    {"id": "OO-AUD-027", "query": "oleh-oleh dekat Farm House Lembang", "top_k": 5, "sort_by": "nearest", **FARM_HOUSE, "expect_distance_sorted": True},
    {"id": "OO-AUD-028", "query": "snack murah dekat Farm House", "top_k": 5, "sort_by": "nearest", **FARM_HOUSE, "expect_top_categories": ["snack_keripik"], "top_n": 4, "expect_distance_sorted": True},
    {"id": "OO-AUD-029", "query": "oleh-oleh dekat pusat Lembang radius 2 km", "top_k": 10, "sort_by": "nearest", "max_distance_km": 2, **LEMBANG_CENTER, "expect_distance_lte": 2},
    {"id": "OO-AUD-030", "query": "oleh-oleh murah dekat Lembang di bawah 50 ribu", "top_k": 10, "sort_by": "balanced", "max_price": 50000, **LEMBANG_CENTER, "max_price_min": 50000},
    {"id": "OO-AUD-031", "query": "oleh-oleh non makanan", "top_k": 5, "expect_top_categories": ["souvenir_non_makanan"], "top_n": 1},
    {"id": "OO-AUD-032", "query": "produk susu fresh untuk anak", "top_k": 5, "expect_top_categories": ["olahan_susu"], "top_n": 3},
    {"id": "OO-AUD-033", "query": "oleh-oleh praktis banyak rasa", "top_k": 5, "expect_any_results": True},
    {"id": "OO-AUD-034", "query": "camilan grosir murah", "top_k": 5, "expect_top_categories": ["snack_keripik"], "top_n": 4},
    {"id": "OO-AUD-035", "query": "hantaran resmi Bandung", "top_k": 5, "expect_any_results": True},
    {"id": "OO-AUD-036", "query": "oleh-oleh tahan lama non makanan", "top_k": 5, "expect_durability_any_top_n": ["tinggi"], "top_n": 5},
]


def check_test(test, result):
    recs = result.get("recommendations", [])
    top_n = int(test.get("top_n", min(test.get("top_k", 5), len(recs))))
    top = recs[:top_n]
    issues = []
    if test.get("expect_any_results") and not recs:
        issues.append("no_results")
    expected_categories = set(test.get("expect_top_categories", []))
    if expected_categories:
        bad = [rec for rec in top if rec.get("category") not in expected_categories]
        if bad:
            issues.append("unexpected_category_top_n=" + ",".join(f"{rec.get('rank')}:{rec.get('category')}" for rec in bad))
    forbidden = set(test.get("forbid_top_categories", []))
    if forbidden:
        bad = [rec for rec in top if rec.get("category") in forbidden]
        if bad:
            issues.append("forbidden_category_top_n=" + ",".join(f"{rec.get('rank')}:{rec.get('category')}" for rec in bad))
    for needle in test.get("expect_name_contains", []):
        if not recs or needle.lower() not in recs[0].get("name", "").lower():
            issues.append(f"top1_name_missing={needle}")
    for needle in test.get("expect_name_contains_any_top_n", []):
        if not any(needle.lower() in rec.get("name", "").lower() for rec in top):
            issues.append(f"top_n_name_missing={needle}")
    if "max_price_min" in test:
        limit = float(test["max_price_min"])
        bad = [rec for rec in recs if rec.get("price_min_idr") is not None and float(rec.get("price_min_idr")) > limit]
        if bad:
            issues.append("price_min_above_limit=" + ",".join(f"{rec.get('rank')}:{rec.get('price_min_idr')}" for rec in bad[:5]))
    if test.get("expect_distance_lte") is not None:
        limit = float(test["expect_distance_lte"])
        bad = [rec for rec in recs if rec.get("distance_km") is not None and float(rec.get("distance_km")) > limit + 1e-9]
        if bad:
            issues.append("distance_above_limit=" + ",".join(f"{rec.get('rank')}:{rec.get('distance_km')}" for rec in bad[:5]))
    if test.get("expect_distance_sorted"):
        distances = [rec.get("distance_km") for rec in recs if rec.get("distance_km") is not None]
        if distances != sorted(distances):
            issues.append("distance_not_sorted")
    expected_durability = set(test.get("expect_durability_any_top_n", []))
    if expected_durability and not any(rec.get("daya_tahan_produk_class") in expected_durability for rec in top):
        issues.append("expected_durability_not_found_top_n=" + ",".join(sorted(expected_durability)))
    if any(not rec.get("main_recommendation_eligible", True) for rec in recs):
        issues.append("non_main_eligible_returned")
    return issues


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = OlehOlehRecommender()
    result_rows = []
    summary_rows = []

    for test in TESTS:
        payload = {
            key: value
            for key, value in test.items()
            if key in {"query", "top_k", "sort_by", "user_lat", "user_lon", "max_distance_km", "max_price"}
        }
        result = engine.recommend(**payload)
        issues = check_test(test, result)
        status = "PASS" if not issues else "REVIEW"
        summary_rows.append({
            "test_id": test["id"],
            "query": test["query"],
            "status": status,
            "issues": "; ".join(issues),
            "detected_categories": ";".join(result.get("detected_categories", [])),
            "after_filtering": result.get("after_filtering"),
            "top1": result["recommendations"][0]["name"] if result.get("recommendations") else "",
            "top1_category": result["recommendations"][0]["category"] if result.get("recommendations") else "",
        })
        for rec in result.get("recommendations", []):
            result_rows.append({
                "test_id": test["id"],
                "query": test["query"],
                "status": status,
                "issues": "; ".join(issues),
                "rank": rec.get("rank"),
                "name": rec.get("name"),
                "category": rec.get("category"),
                "score": rec.get("score"),
                "base_score": rec.get("base_score"),
                "query_score": rec.get("query_score"),
                "distance_km": rec.get("distance_km"),
                "distance_label": rec.get("distance_label"),
                "produk_utama": rec.get("produk_utama"),
                "price_range": rec.get("price_range"),
                "price_min_idr": rec.get("price_min_idr"),
                "price_max_idr": rec.get("price_max_idr"),
                "price_bucket": rec.get("price_bucket"),
                "price_confidence": rec.get("price_confidence"),
                "daya_tahan_produk": rec.get("daya_tahan_produk"),
                "daya_tahan_produk_class": rec.get("daya_tahan_produk_class"),
                "cocok_untuk": rec.get("cocok_untuk"),
                "best_use_case": rec.get("best_use_case"),
                "warnings": ";".join(rec.get("warnings", [])),
                "main_recommendation_eligible": rec.get("main_recommendation_eligible"),
            })

    with DETAIL_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result_rows[0].keys()))
        writer.writeheader()
        writer.writerows(result_rows)

    with TESTS_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    status_counts = {}
    for row in summary_rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    summary = {
        "created_at": "2026-06-10",
        "dataset_path": str(engine.dataset_path),
        "test_count": len(TESTS),
        "result_rows": len(result_rows),
        "status_counts": status_counts,
        "review_tests": [row for row in summary_rows if row["status"] != "PASS"],
        "detail_csv": str(DETAIL_PATH),
        "test_summary_csv": str(TESTS_PATH),
        "notes": [
            "Harga memakai estimasi manual, bukan harga resmi real-time.",
            "Query audit menguji harga, produk, daya tahan, kategori, dan jarak.",
            "Status REVIEW berarti perlu dilihat, bukan otomatis gagal fatal.",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
