from __future__ import annotations

import json
import shutil
import sys
from datetime import date
from pathlib import Path

import nbformat
import pandas as pd
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "Penginapan_Workspace"
RAW_DIR = WORKSPACE / "01_Raw_Data" / "generated_raw_csv"
CURATED_DIR = WORKSPACE / "02_Curated"
NOTEBOOK_DIR = WORKSPACE / "03_Notebooks"
SCRIPT_DIR = WORKSPACE / "06_Scripts"

NOTEBOOK_PATH = NOTEBOOK_DIR / "penginapan_training.ipynb"
ARCHIVE_PATH = NOTEBOOK_DIR / "archive" / "penginapan_training_before_decision_driven_2026-06-04.ipynb"

RAW_MASTER = RAW_DIR / "HOTEL_GOOGLE_SEARCH_RAW_MASTER_2026-06-02.csv"
SOURCE_INVENTORY = RAW_DIR / "HOTEL_GOOGLE_SEARCH_JSON_SOURCE_INVENTORY_2026-06-02.csv"
EXISTING_CANONICAL = CURATED_DIR / "HOTEL_CANONICAL_CIMAHI_2026-05-29.csv"
CANDIDATE = CURATED_DIR / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv"
DEDUPED = CURATED_DIR / "PENGINAPAN_DEDUPED_MASTER_BANDUNG_RAYA_2026-06-02.csv"
RAW_SUMMARY = CURATED_DIR / "hotel_google_search_raw_master_summary_2026-06-02.json"
CANDIDATE_SUMMARY = CURATED_DIR / "penginapan_canonical_candidate_summary_2026-06-02.json"
CANDIDATE_VALIDATION = CURATED_DIR / "penginapan_canonical_candidate_validation_2026-06-02.json"
AUDIT_SUMMARY = CURATED_DIR / "penginapan_canonical_candidate_automated_audit_2026-06-02.json"
FINDINGS = CURATED_DIR / "PENGINAPAN_CANONICAL_CANDIDATE_AUTOMATED_AUDIT_FINDINGS_2026-06-02.csv"
MANUAL_QUEUE = CURATED_DIR / "PENGINAPAN_MANUAL_REVIEW_QUEUE_AUTOMATED_AUDIT_2026-06-02.csv"
ADJUSTMENT_QUEUE = CURATED_DIR / "PENGINAPAN_AUTOMATED_AUDIT_ADJUSTMENT_PRIORITY_2026-06-02.csv"

TAG = "penginapan_decision_driven_audit_2026_06_04"
SNAPSHOT_DATE = date(2026, 6, 4).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tagged_markdown(source: str):
    cell = new_markdown_cell(source.strip())
    cell.metadata["tags"] = [TAG, "decision-documentation"]
    return cell


def tagged_code(source: str):
    cell = new_code_cell(source.strip())
    cell.metadata["tags"] = [TAG, "audit-code"]
    return cell


def decision(title: str, evidence: str, decision_text: str, next_step: str):
    return tagged_markdown(
        f"""
### Keputusan: {title}

**Bukti dari output sebelumnya**

{evidence}

**Keputusan snapshot {SNAPSHOT_DATE}**

{decision_text}

**Langkah berikutnya**

{next_step}

> Jika output cell sebelumnya berubah saat notebook dijalankan ulang, keputusan ini wajib ditinjau ulang sebelum proses dilanjutkan.
"""
    )


def current_metrics() -> dict:
    sys.path.insert(0, str(SCRIPT_DIR))
    import build_penginapan_canonical_candidate as pipeline

    raw_df = pipeline.load_raw_master(RAW_MASTER)
    existing_df = pipeline.load_existing_canonical(EXISTING_CANONICAL)
    pool_df = pipeline.prepare_pool(raw_df, existing_df)
    group_sizes = pool_df.groupby("dedupe_key").size()
    duplicate_groups = group_sizes[group_sizes > 1]
    duplicate_prefixes = (
        duplicate_groups.index.to_series().str.split("::").str[0].value_counts().to_dict()
    )

    candidate_df = pd.read_csv(CANDIDATE, dtype=str, keep_default_na=False)
    possible_key = (
        candidate_df["normalized_name"].astype(str)
        + "|"
        + candidate_df["latitude"].astype(str)
        + "|"
        + candidate_df["longitude"].astype(str)
    )
    possible_mask = possible_key.duplicated(keep=False)

    raw_summary = load_json(RAW_SUMMARY)
    candidate_summary = load_json(CANDIDATE_SUMMARY)
    audit_summary = load_json(AUDIT_SUMMARY)
    findings_df = pd.read_csv(FINDINGS, dtype=str, keep_default_na=False)
    adjustment_df = pd.read_csv(ADJUSTMENT_QUEUE, dtype=str, keep_default_na=False)

    return {
        "raw_records": int(raw_summary["raw_records"]),
        "raw_unique_names": int(raw_summary["raw_unique_names"]),
        "json_source_count": int(raw_summary["json_source_count"]),
        "json_processed_count": int(raw_summary["json_processed_count"]),
        "json_duplicate_file_count": int(raw_summary["json_duplicate_file_count"]),
        "pool_rows": int(candidate_summary["pool_rows"]),
        "candidate_rows": int(candidate_summary["candidate_rows"]),
        "dedupe_removed_rows": int(candidate_summary["dedupe_removed_rows"]),
        "duplicate_group_count": int(len(duplicate_groups)),
        "duplicate_rows": int(duplicate_groups.sum()),
        "duplicate_prefixes": duplicate_prefixes,
        "pool_room_level": int(pool_df["property_type"].eq("room_level_listing").sum()),
        "candidate_room_level": int(candidate_df["property_type"].eq("room_level_listing").sum()),
        "remaining_possible_groups": int(possible_key[possible_mask].nunique()),
        "remaining_possible_rows": int(possible_mask.sum()),
        "valid_region_rows": int(candidate_df["region_validation_label"].eq("bandung_raya_valid").sum()),
        "non_valid_region_rows": int(
            (~candidate_df["region_validation_label"].eq("bandung_raya_valid")).sum()
        ),
        "audit_gate": audit_summary["gate"],
        "audit_findings": int(audit_summary["finding_count"]),
        "audit_affected_rows": int(audit_summary["affected_row_count"]),
        "error_count": int((findings_df["severity"] == "ERROR").sum()),
        "priority_counts": adjustment_df["priority"].value_counts().to_dict(),
    }


def build_cells(metrics: dict) -> list:
    cells = []

    cells.append(
        tagged_markdown(
            f"""
# Penginapan Training: Decision-Driven Data Preparation dan Audit

Notebook ini mendokumentasikan proses persiapan dan audit dataset penginapan Bandung Raya sebagai rangkaian keputusan data engineering.

Pola wajib setiap tahap:

`tujuan kecil -> code/output -> keputusan -> langkah berikutnya`

Notebook ini menggunakan snapshot data terkontrol pada **{SNAPSHOT_DATE}**. Raw master tidak dibangun ulang otomatis dari JSON karena saat ini sudah mengandung koreksi manual yang dapat hilang jika proses flatten dijalankan tanpa correction layer.

Ruang lingkup:

1. Memastikan sumber dan artefak tersedia.
2. Memeriksa indikasi duplikasi.
3. Memeriksa kandidat duplikat kuat.
4. Memeriksa room-level listing.
5. Menjalankan dan mengevaluasi dedupe level 1.
6. Mengevaluasi kemungkinan duplikat yang tersisa.
7. Mengevaluasi region validation.
8. Menjalankan automated audit.
9. Menentukan prioritas P0/P1/P2.
10. Memastikan output final tersedia.

Status dataset pada tahap ini adalah **canonical candidate**, belum production canonical final.
"""
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 0 - Menetapkan Environment dan Artefak

**Tujuan kecil:** memastikan notebook dijalankan dari project yang benar dan seluruh file wajib tersedia sebelum audit dimulai.
"""
        )
    )
    cells.append(
        tagged_code(
            """
from pathlib import Path
import json
import subprocess
import sys

import pandas as pd
from IPython.display import display

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

WORKSPACE = PROJECT_ROOT / "Penginapan_Workspace"
RAW_DIR = WORKSPACE / "01_Raw_Data" / "generated_raw_csv"
CURATED_DIR = WORKSPACE / "02_Curated"
SCRIPT_DIR = WORKSPACE / "06_Scripts"

paths = {
    "raw_master": RAW_DIR / "HOTEL_GOOGLE_SEARCH_RAW_MASTER_2026-06-02.csv",
    "source_inventory": RAW_DIR / "HOTEL_GOOGLE_SEARCH_JSON_SOURCE_INVENTORY_2026-06-02.csv",
    "existing_canonical": CURATED_DIR / "HOTEL_CANONICAL_CIMAHI_2026-05-29.csv",
    "candidate": CURATED_DIR / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv",
    "deduped": CURATED_DIR / "PENGINAPAN_DEDUPED_MASTER_BANDUNG_RAYA_2026-06-02.csv",
    "raw_summary": CURATED_DIR / "hotel_google_search_raw_master_summary_2026-06-02.json",
    "candidate_summary": CURATED_DIR / "penginapan_canonical_candidate_summary_2026-06-02.json",
    "candidate_validation": CURATED_DIR / "penginapan_canonical_candidate_validation_2026-06-02.json",
    "audit_summary": CURATED_DIR / "penginapan_canonical_candidate_automated_audit_2026-06-02.json",
    "findings": CURATED_DIR / "PENGINAPAN_CANONICAL_CANDIDATE_AUTOMATED_AUDIT_FINDINGS_2026-06-02.csv",
    "manual_queue": CURATED_DIR / "PENGINAPAN_MANUAL_REVIEW_QUEUE_AUTOMATED_AUDIT_2026-06-02.csv",
    "adjustment_queue": CURATED_DIR / "PENGINAPAN_AUTOMATED_AUDIT_ADJUSTMENT_PRIORITY_2026-06-02.csv",
}

environment_check = pd.DataFrame(
    [
        {
            "artifact": name,
            "exists": path.exists(),
            "size_kb": round(path.stat().st_size / 1024, 1) if path.exists() else None,
            "modified": path.stat().st_mtime if path.exists() else None,
        }
        for name, path in paths.items()
    ]
)

print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"Python: {sys.executable}")
display(environment_check)
"""
        )
    )
    cells.append(
        decision(
            "Environment layak digunakan",
            "- Seluruh artefak wajib tersedia pada workspace penginapan.\n- Interpreter Python dan project root dapat ditemukan.",
            "Audit dapat dilanjutkan menggunakan artefak saat ini. Raw master diperlakukan sebagai snapshot terkontrol dan tidak di-flatten ulang otomatis.",
            "Audit sumber JSON dan inventory untuk memastikan lineage data dapat ditelusuri.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 1 - Audit Sumber Data

**Tujuan kecil:** menghitung jumlah sumber JSON, sumber yang diproses, file duplikat penuh, jumlah record, dan coverage query.
"""
        )
    )
    cells.append(
        tagged_code(
            """
raw_summary = json.loads(paths["raw_summary"].read_text(encoding="utf-8"))
inventory_df = pd.read_csv(paths["source_inventory"], dtype=str, keep_default_na=False)

source_metrics = pd.DataFrame(
    {
        "metric": [
            "JSON terdeteksi",
            "JSON diproses",
            "File duplikat penuh",
            "Raw records",
            "Unique names raw",
            "Unique property tokens",
        ],
        "value": [
            raw_summary["json_source_count"],
            raw_summary["json_processed_count"],
            raw_summary["json_duplicate_file_count"],
            raw_summary["raw_records"],
            raw_summary["raw_unique_names"],
            raw_summary["raw_unique_property_tokens"],
        ],
    }
)

display(source_metrics)
display(
    inventory_df[
        ["source_file", "duplicate_status", "processed", "query", "records_total", "unique_names_raw"]
    ].sort_values(["processed", "source_file"], ascending=[False, True])
)
"""
        )
    )
    cells.append(
        decision(
            "Sumber data diterima sebagai input audit",
            f"- JSON terdeteksi: **{metrics['json_source_count']}**.\n- JSON diproses: **{metrics['json_processed_count']}**.\n- File duplikat penuh yang dilewati: **{metrics['json_duplicate_file_count']}**.\n- Raw records: **{metrics['raw_records']}**.",
            "Lineage sumber cukup jelas untuk melanjutkan audit. File duplikat penuh tidak perlu diproses kembali karena hanya menggandakan data yang sama.",
            "Periksa raw master untuk melihat apakah duplikasi antar hasil pencarian masih signifikan.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 2 - Audit Raw Master dan Indikasi Duplikasi

**Tujuan kecil:** membandingkan jumlah row, nama unik, property token, sumber query, dan kelengkapan dasar sebelum dedupe.
"""
        )
    )
    cells.append(
        tagged_code(
            """
raw_df = pd.read_csv(paths["raw_master"], dtype=str, keep_default_na=False)
existing_df = pd.read_csv(paths["existing_canonical"], dtype=str, keep_default_na=False)

raw_audit = pd.DataFrame(
    {
        "metric": [
            "Raw master rows",
            "Existing canonical rows",
            "Raw unique names",
            "Raw unique property tokens",
            "Rows dengan koordinat",
            "Rows dengan rating",
            "Rows dengan review count",
        ],
        "value": [
            len(raw_df),
            len(existing_df),
            raw_df["name"].nunique(dropna=True),
            raw_df["property_token"].replace("", pd.NA).nunique(dropna=True),
            int(((raw_df["latitude"] != "") & (raw_df["longitude"] != "")).sum()),
            int((raw_df["overall_rating"] != "").sum()),
            int((raw_df["reviews"] != "").sum()),
        ],
    }
)

display(raw_audit)
display(raw_df["source_query_area"].value_counts().rename_axis("query_area").reset_index(name="rows"))
"""
        )
    )
    cells.append(
        decision(
            "Dedupe level 1 diperlukan",
            f"- Raw master berisi **{metrics['raw_records']}** rows, tetapi hanya **{metrics['raw_unique_names']}** nama unik.\n- Pool gabungan yang akan diperiksa berisi **{metrics['pool_rows']}** rows.",
            "Perbedaan besar antara jumlah rows dan nama unik menunjukkan banyak listing berulang antar query/page. Namun kesamaan nama saja belum cukup aman untuk menggabungkan data.",
            "Bangun kandidat duplikat kuat menggunakan dedupe key konservatif dan ukur bukti penggabungannya.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 3 - Kandidat Duplikat Kuat

**Tujuan kecil:** mengetahui berapa kelompok yang benar-benar memenuhi aturan dedupe level 1 dan sinyal apa yang digunakan.

Aturan dedupe level 1:

1. Prioritas pertama: `property_token` yang sama.
2. Jika token tidak tersedia: nama ternormalisasi dan koordinat rounded yang sama.
3. Jika koordinat tidak tersedia: hanya nama ternormalisasi yang benar-benar sama.
4. Pemilihan record utama mempertimbangkan tipe properti, sumber, kualitas data, reviews, rating, dan page.
"""
        )
    )
    cells.append(
        tagged_code(
            """
sys.path.insert(0, str(SCRIPT_DIR))
import build_penginapan_canonical_candidate as dedupe_pipeline

raw_for_pool = dedupe_pipeline.load_raw_master(paths["raw_master"])
existing_for_pool = dedupe_pipeline.load_existing_canonical(paths["existing_canonical"])
pool_df = dedupe_pipeline.prepare_pool(raw_for_pool, existing_for_pool)

group_sizes = pool_df.groupby("dedupe_key").size().sort_values(ascending=False)
duplicate_groups = group_sizes[group_sizes > 1]
duplicate_key_type = duplicate_groups.index.to_series().str.split("::").str[0].value_counts()

strong_duplicate_metrics = pd.DataFrame(
    {
        "metric": ["Pool rows", "Unique dedupe keys", "Duplicate groups", "Rows in duplicate groups", "Rows removable"],
        "value": [
            len(pool_df),
            group_sizes.size,
            len(duplicate_groups),
            int(duplicate_groups.sum()),
            int((duplicate_groups - 1).sum()),
        ],
    }
)

display(strong_duplicate_metrics)
display(duplicate_key_type.rename_axis("dedupe_key_type").reset_index(name="duplicate_groups"))
display(
    pool_df[pool_df["dedupe_key"].isin(duplicate_groups.head(10).index)][
        ["dedupe_key", "name", "property_type", "latitude", "longitude", "source_query_area", "data_quality_score"]
    ].sort_values(["dedupe_key", "name"])
)
"""
        )
    )
    cells.append(
        decision(
            "Aturan penggabungan dedupe level 1 diterima",
            f"- Ditemukan **{metrics['duplicate_group_count']}** kelompok duplikat kuat.\n- Kelompok tersebut mencakup **{metrics['duplicate_rows']}** rows.\n- Pengurangan potensial: **{metrics['dedupe_removed_rows']}** rows.\n- Tipe key kelompok aktif: **{metrics['duplicate_prefixes']}**.",
            "Pada snapshot ini, seluruh kelompok yang benar-benar digabung berasal dari `property_token` yang sama. Ini merupakan sinyal kuat, sehingga dedupe level 1 cukup aman untuk dijalankan. Aturan fallback tetap konservatif, tetapi tidak menjadi penyebab penggabungan aktif pada snapshot ini.",
            "Periksa room-level listing sebelum menjalankan dedupe agar unit/kamar tidak salah diperlakukan sebagai properti utama.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 4 - Audit Room-Level Listing

**Tujuan kecil:** mengetahui listing yang merepresentasikan kamar/unit, bukan properti utama.
"""
        )
    )
    cells.append(
        tagged_code(
            """
room_pool_df = pool_df[pool_df["property_type"].eq("room_level_listing")].copy()

print(f"Room-level listing pada pool: {len(room_pool_df)}")
display(
    room_pool_df[
        ["name", "normalized_name", "latitude", "longitude", "source_query_area", "property_token"]
    ].head(30)
)
"""
        )
    )
    cells.append(
        decision(
            "Room-level listing dipertahankan tetapi bukan kandidat ranking utama",
            f"- Room-level listing pada pool: **{metrics['pool_room_level']}**.\n- Setelah dedupe level 1 diperkirakan tersisa **{metrics['candidate_room_level']}**.",
            "Room-level listing tidak boleh dihapus otomatis karena dapat menyimpan informasi tipe kamar, unit, harga, atau gambar. Listing ini juga tidak boleh bersaing setara dengan properti utama.",
            "Jalankan dedupe level 1 tanpa menghapus room-level listing. Siapkan parent-child mapping pada tahap terpisah.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 5 - Menjalankan Dedupe Konservatif Level 1

**Tujuan kecil:** membangun ulang deduped master dan canonical candidate menggunakan aturan dedupe yang sudah diterima.

Catatan: proses ini membaca raw master terkontrol yang sudah tersedia. Proses tidak membangun ulang raw master dari JSON.
"""
        )
    )
    cells.append(
        tagged_code(
            """
dedupe_run = subprocess.run(
    [
        sys.executable,
        str(SCRIPT_DIR / "build_penginapan_canonical_candidate.py"),
        "--skip-notebook-update",
    ],
    check=True,
    capture_output=True,
    text=True,
)
print(dedupe_run.stdout.strip())

candidate_summary = json.loads(paths["candidate_summary"].read_text(encoding="utf-8"))
candidate_validation = json.loads(paths["candidate_validation"].read_text(encoding="utf-8"))

display(pd.DataFrame({
    "metric": ["Pool rows", "Candidate rows", "Rows removed", "Validation gate"],
    "value": [
        candidate_summary["pool_rows"],
        candidate_summary["candidate_rows"],
        candidate_summary["dedupe_removed_rows"],
        candidate_validation["gate"],
    ],
}))
"""
        )
    )
    cells.append(
        decision(
            "Dedupe level 1 diterima dengan peringatan",
            f"- Pool: **{metrics['pool_rows']}** rows.\n- Candidate: **{metrics['candidate_rows']}** rows.\n- Rows yang direduksi: **{metrics['dedupe_removed_rows']}**.",
            "Hasil dedupe level 1 diterima karena penggabungan aktif didukung property token yang sama. Status masih `canonical candidate`, bukan final, karena kemungkinan parent-child dan duplikat semantik masih perlu ditangani.",
            "Audit pola duplikasi yang masih tersisa setelah dedupe level 1.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 6 - Audit Kemungkinan Duplikat yang Tersisa

**Tujuan kecil:** mencari kandidat dengan nama ternormalisasi dan koordinat sama yang masih tersisa setelah dedupe level 1.

Kondisi ini tidak otomatis berarti duplikat. Kelompok dapat berisi properti utama, kamar, unit apartment, atau listing berbeda pada lokasi yang sama.
"""
        )
    )
    cells.append(
        tagged_code(
            """
candidate_df = pd.read_csv(paths["candidate"], dtype=str, keep_default_na=False)
possible_key = (
    candidate_df["normalized_name"].astype(str)
    + "|"
    + candidate_df["latitude"].astype(str)
    + "|"
    + candidate_df["longitude"].astype(str)
)
possible_mask = possible_key.duplicated(keep=False)
possible_df = candidate_df[possible_mask].copy()
possible_df["possible_duplicate_key"] = possible_key[possible_mask]

remaining_metrics = pd.DataFrame(
    {
        "metric": ["Candidate rows", "Possible duplicate rows", "Possible duplicate groups"],
        "value": [len(candidate_df), len(possible_df), possible_df["possible_duplicate_key"].nunique()],
    }
)
display(remaining_metrics)
display(
    possible_df[
        ["possible_duplicate_key", "penginapan_id", "name", "property_type", "overall_rating", "reviews"]
    ].sort_values(["possible_duplicate_key", "property_type", "name"]).head(40)
)
"""
        )
    )
    cells.append(
        decision(
            "Duplikat tersisa tidak boleh digabung otomatis",
            f"- Terdapat **{metrics['remaining_possible_groups']}** kelompok atau **{metrics['remaining_possible_rows']}** rows dengan nama ternormalisasi dan koordinat yang sama.",
            "Sinyal nama dan koordinat yang sama belum cukup untuk auto-merge karena dapat merepresentasikan parent-child, tipe kamar, atau unit berbeda. Kasus ini harus masuk P1/P2 review dan parent-child preparation.",
            "Lanjutkan region validation tanpa menghapus kelompok tersisa.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 7 - Region Validation

**Tujuan kecil:** memastikan kandidat berada dalam cakupan rough Bandung Raya dan mengidentifikasi border/outside/needs-review.

Region validation saat ini berbasis bounding coordinate dan bucket kasar. Hasilnya tidak boleh dianggap sebagai batas administratif presisi.
"""
        )
    )
    cells.append(
        tagged_code(
            """
region_counts = candidate_df["region_validation_label"].value_counts(dropna=False)
bucket_counts = candidate_df["region_bucket"].value_counts(dropna=False)
region_exceptions = candidate_df[~candidate_df["region_validation_label"].eq("bandung_raya_valid")]

display(region_counts.rename_axis("region_validation_label").reset_index(name="rows"))
display(bucket_counts.rename_axis("region_bucket").reset_index(name="rows"))
display(
    region_exceptions[
        ["penginapan_id", "name", "latitude", "longitude", "region_bucket", "region_validation_label", "region_validation_reason"]
    ]
)
"""
        )
    )
    cells.append(
        decision(
            "Region validation diterima sebagai filter kasar",
            f"- Kandidat `bandung_raya_valid`: **{metrics['valid_region_rows']}**.\n- Kandidat non-valid/needs-review: **{metrics['non_valid_region_rows']}**.",
            "Seluruh kandidat saat ini lolos rough Bandung Raya. Hasil ini cukup untuk filter awal rekomendasi, tetapi belum cukup untuk klaim wilayah administratif yang presisi.",
            "Jalankan automated audit untuk schema, ID, numeric range, missing data, room-level listing, dan possible duplicate.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 8 - Menjalankan Automated Audit

**Tujuan kecil:** menghasilkan gate dan daftar temuan tanpa mengubah data candidate.

Audit mencakup schema, ID, koordinat, region, rating, reviews, harga, quality score, property type, room-level listing, possible duplicate, dan missing field penting.
"""
        )
    )
    cells.append(
        tagged_code(
            """
audit_run = subprocess.run(
    [
        sys.executable,
        str(SCRIPT_DIR / "audit_penginapan_canonical_candidate.py"),
        "--skip-notebook-update",
    ],
    check=True,
    capture_output=True,
    text=True,
)
print(audit_run.stdout.strip())

audit_summary = json.loads(paths["audit_summary"].read_text(encoding="utf-8"))
findings_df = pd.read_csv(paths["findings"], dtype=str, keep_default_na=False)

display(pd.DataFrame({
    "metric": ["Gate", "Rows", "Findings", "Affected rows", "ERROR findings"],
    "value": [
        audit_summary["gate"],
        audit_summary["row_count"],
        audit_summary["finding_count"],
        audit_summary["affected_row_count"],
        int((findings_df["severity"] == "ERROR").sum()),
    ],
}))
display(findings_df["code"].value_counts().rename_axis("finding_code").reset_index(name="count"))
"""
        )
    )
    cells.append(
        decision(
            "Candidate dapat dilanjutkan dengan caveat, bukan dianggap final",
            f"- Audit gate: **{metrics['audit_gate']}**.\n- Temuan: **{metrics['audit_findings']}** pada **{metrics['audit_affected_rows']}** rows.\n- ERROR findings: **{metrics['error_count']}**.",
            "Tidak ada error yang memblokir dataset. Banyak temuan berasal dari field opsional yang kosong dan kasus manual review. Dataset boleh dipakai untuk pengembangan lanjutan jika sistem membaca quality flags dan tidak membuat klaim atas data yang kosong.",
            "Pisahkan tindakan P0/P1/P2 agar pekerjaan berikutnya terarah.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 9 - Prioritas Penyesuaian P0/P1/P2

**Tujuan kecil:** membedakan masalah yang memblokir penggunaan data dari masalah yang membutuhkan review atau caveat.

Definisi:

- **P0:** error yang harus diperbaiki sebelum data dipakai.
- **P1:** penting untuk kualitas ranking dan struktur parent-child.
- **P2:** peningkatan kualitas atau review lanjutan yang tidak memblokir.
"""
        )
    )
    cells.append(
        tagged_code(
            """
adjustment_df = pd.read_csv(paths["adjustment_queue"], dtype=str, keep_default_na=False)
manual_queue_df = pd.read_csv(paths["manual_queue"], dtype=str, keep_default_na=False)

display(adjustment_df["priority"].value_counts().rename_axis("priority").reset_index(name="rows"))
display(adjustment_df.head(40))
print(f"Manual review queue rows: {len(manual_queue_df)}")
"""
        )
    )
    cells.append(
        decision(
            "Fokus berikutnya adalah P1 duplicate review dan parent-child",
            f"- Priority queue saat ini: **{metrics['priority_counts']}**.\n- P0/error yang memblokir: **{metrics['error_count']}**.",
            "Dataset tidak memiliki P0 aktif. P1 tidak boleh diselesaikan dengan penghapusan massal. Room-level listing dan possible duplicate harus dipetakan menjadi parent-child atau ditinjau sebelum ranking final dan scraping review.",
            "Gunakan candidate sebagai dasar kerja, lalu buat parent-child preparation dan review target property utama.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Tahap 10 - Verifikasi Output Final Audit

**Tujuan kecil:** memastikan seluruh artefak hasil audit tersedia dan dapat digunakan oleh tahap berikutnya.
"""
        )
    )
    cells.append(
        tagged_code(
            """
final_artifacts = {
    "raw_master": paths["raw_master"],
    "deduped_master": paths["deduped"],
    "canonical_candidate": paths["candidate"],
    "automated_findings": paths["findings"],
    "manual_review_queue": paths["manual_queue"],
    "adjustment_priority_queue": paths["adjustment_queue"],
}

artifact_rows = []
for name, path in final_artifacts.items():
    row_count = None
    column_count = None
    if path.exists() and path.suffix.lower() == ".csv":
        preview = pd.read_csv(path, dtype=str, keep_default_na=False)
        row_count = len(preview)
        column_count = len(preview.columns)
    artifact_rows.append(
        {
            "artifact": name,
            "exists": path.exists(),
            "rows": row_count,
            "columns": column_count,
            "path": str(path),
        }
    )

display(pd.DataFrame(artifact_rows))
"""
        )
    )
    cells.append(
        decision(
            "Audit keseluruhan selesai untuk snapshot saat ini",
            f"- Canonical candidate tersedia dengan **{metrics['candidate_rows']}** rows.\n- Dedupe level 1 mereduksi **{metrics['dedupe_removed_rows']}** rows.\n- Audit gate: **{metrics['audit_gate']}** dan tidak memiliki ERROR aktif.",
            "Pondasi data cukup untuk melanjutkan pekerjaan struktur penginapan, tetapi belum menjadi canonical final. Candidate belum boleh dianggap bersih sepenuhnya dari parent-child atau duplikat semantik.",
            "Tahap terbaik selanjutnya adalah merancang parent-child mapping untuk room-level listing dan kelompok kemungkinan duplikat, kemudian membuat target scraping review hanya dari properti utama.",
        )
    )

    cells.append(
        tagged_markdown(
            """
## Ringkasan Keputusan Akhir

| Area | Keputusan |
|---|---|
| Sumber data | Diterima; lineage tersedia dan file duplikat penuh dilewati |
| Raw master | Dipakai sebagai snapshot terkontrol; jangan rebuild dari JSON sebelum correction layer tersedia |
| Dedupe level 1 | Diterima; penggabungan aktif didukung property token yang sama |
| Room-level listing | Dipertahankan; jangan diranking setara dengan properti utama |
| Possible duplicate tersisa | Jangan auto-merge; siapkan review dan parent-child |
| Region validation | Diterima sebagai rough filter, bukan batas administratif presisi |
| Automated audit | `PASS_WITH_WARNINGS`; tidak ada P0/error aktif |
| Status dataset | Canonical candidate, belum production canonical final |
| Next step | Parent-child mapping lalu target scraping review properti utama |
"""
        )
    )

    return cells


def build_notebook() -> None:
    metrics = current_metrics()
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if NOTEBOOK_PATH.exists() and not ARCHIVE_PATH.exists():
        shutil.copy2(NOTEBOOK_PATH, ARCHIVE_PATH)

    notebook = new_notebook(
        cells=build_cells(metrics),
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            },
            "project": {
                "name": "MuterBandung Penginapan",
                "purpose": "Decision-driven data preparation and audit",
                "snapshot_date": SNAPSHOT_DATE,
            },
        },
    )
    nbformat.write(notebook, NOTEBOOK_PATH)
    print(f"notebook={NOTEBOOK_PATH}")
    print(f"archive={ARCHIVE_PATH}")
    print(f"cells={len(notebook.cells)}")


if __name__ == "__main__":
    build_notebook()
