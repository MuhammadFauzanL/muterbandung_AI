from pathlib import Path

import nbformat as nbf


DATA_NOTEBOOK_PATH = Path("Notebooks/Data_Completion_Google_Colab.ipynb")
REALWORLD_NOTEBOOK_PATH = Path("Notebooks/Realworld_Verification_Google_Colab.ipynb")
MASTER_NOTEBOOK_PATH = Path("Notebooks/wisata_training.ipynb")
MASTER_MARKER = "MUTERBANDUNG_COLAB_RESEARCH_NOTEBOOKS_2026_05_25"


def md(source):
    return nbf.v4.new_markdown_cell(source)


def code(source):
    return nbf.v4.new_code_cell(source)


def notebook_metadata(name):
    return {
        "colab": {
            "name": name,
            "provenance": [],
        },
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3",
        },
        "language_info": {
            "name": "python",
        },
    }


def build_data_completion_notebook():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = notebook_metadata("Data_Completion_Google_Colab.ipynb")
    nb["cells"] = [
        md("""# MuterBandung Data Completion - Google Colab

Notebook ini dibuat untuk mengisi **data non-media** dari `manual_data_fill_queue.csv`.

Tujuan:

- Upload `manual_data_fill_queue.csv`.
- Buka link pencarian Google/Maps/official search.
- Isi `new_value`, `source_url`, `reviewer_status`, dan `reviewer_note`.
- Validasi nilai sebelum diekspor.
- Export `manual_data_fill_queue_completed.csv` dan `data_manual_apply_ready.csv`.

Aturan aman:

- Jangan mengarang data.
- `reviewer_status` harus `approved` agar masuk file apply-ready.
- `source_url` wajib URL HTTP/HTTPS, kecuali field internal seperti `sentiment_available=false` boleh memakai `internal:sentiment_lineage_audit`.
- Untuk `sentiment_available`, jangan set `true` kecuali pipeline sentiment yang valid benar-benar tersedia.
- Notebook ini tidak menulis dataset utama.
"""),
        code("""import re
import urllib.parse

import pandas as pd
from IPython.display import display, HTML

try:
    from google.colab import files
    IN_COLAB = True
except Exception:
    IN_COLAB = False

pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 140)
print("IN_COLAB:", IN_COLAB)
"""),
        md("""## 1. Upload Queue CSV

Upload file:

```text
Dataset/3_Curated/manual_data_fill_queue.csv
```
"""),
        code("""QUEUE_PATH = "manual_data_fill_queue.csv"

if IN_COLAB:
    uploaded = files.upload()
    if uploaded:
        QUEUE_PATH = next(iter(uploaded.keys()))

df = pd.read_csv(QUEUE_PATH).fillna("")
print("Rows:", len(df))
display(df.head(10))
"""),
        md("""## 2. Tambahkan Link Pencarian

Cell ini membuat link bantu pencarian untuk setiap lokasi dan field yang perlu dilengkapi.
"""),
        code("""def search_url(query, mode="search"):
    encoded = urllib.parse.quote_plus(str(query))
    if mode == "maps":
        return f"https://www.google.com/maps/search/{encoded}"
    return f"https://www.google.com/search?q={encoded}"

for col in ["new_value", "source_url", "reviewer_status", "reviewer_note"]:
    if col not in df.columns:
        df[col] = ""

df["reviewer_status"] = df["reviewer_status"].replace("", "todo").fillna("todo")
df["google_search_url"] = df.apply(
    lambda row: search_url(f"{row.get('location_name', '')} {row.get('field_name', '')} Bandung wisata"),
    axis=1,
)
df["google_maps_search_url"] = df["location_name"].apply(
    lambda name: search_url(f"{name} Bandung", mode="maps")
)
df["official_search_url"] = df["location_name"].apply(
    lambda name: search_url(f"{name} Bandung official website")
)

print("Fields to complete:")
print(df["field_name"].value_counts().to_string())
display(df[["location_id", "location_name", "priority", "issue_type", "field_name", "current_value"]].head(12))
"""),
        md("""## 3. Batch Kerja Dengan Link Klik

Gunakan `show_work_batch()` untuk menampilkan pekerjaan bertahap.
"""),
        code("""def clickable(value, label):
    if not isinstance(value, str) or not value.startswith("http"):
        return ""
    return f'<a href="{value}" target="_blank">{label}</a>'

def show_work_batch(start=0, n=15, priority=None, field_name=None):
    work = df.copy()
    if priority:
        work = work[work["priority"].astype(str).str.upper() == priority.upper()]
    if field_name:
        work = work[work["field_name"].astype(str) == field_name]
    batch = work.iloc[start:start+n].copy()
    rows = []
    for _, row in batch.iterrows():
        rows.append({
            "location_id": row.get("location_id", ""),
            "location_name": row.get("location_name", ""),
            "priority": row.get("priority", ""),
            "issue_type": row.get("issue_type", ""),
            "field_name": row.get("field_name", ""),
            "current_value": row.get("current_value", ""),
            "Search": clickable(row.get("google_search_url", ""), "Search"),
            "Maps": clickable(row.get("google_maps_search_url", ""), "Maps"),
            "Official": clickable(row.get("official_search_url", ""), "Official"),
        })
    display(HTML(pd.DataFrame(rows).to_html(escape=False, index=False)))

show_work_batch(start=0, n=15, priority="HIGH")
"""),
        md("""## 4. Isi Cepat Dengan Dictionary

Gunakan format ini jika ingin input langsung di notebook.

Contoh nilai:

- Jam: `09:00`
- Rating: `4.5`
- Boolean: `true` atau `false`
- Sentiment unavailable: `new_value=false`, `source_url=internal:sentiment_lineage_audit`
"""),
        code("""manual_updates = [
    # Contoh:
    # {
    #     "location_id": "LOC-016",
    #     "field_name": "jam_buka_weekday",
    #     "new_value": "09:00",
    #     "source_url": "https://...",
    #     "reviewer_status": "approved",
    #     "reviewer_note": "Dicek manual dari website/Google Maps.",
    # },
]

for update in manual_updates:
    loc_id = str(update.get("location_id", "")).strip()
    field_name = str(update.get("field_name", "")).strip()
    if not loc_id or not field_name:
        continue
    mask = (df["location_id"].astype(str) == loc_id) & (df["field_name"].astype(str) == field_name)
    if not mask.any():
        print("Tidak ditemukan:", loc_id, field_name)
        continue
    for key, value in update.items():
        if key in {"location_id", "field_name"}:
            continue
        if key not in df.columns:
            df[key] = ""
        df.loc[mask, key] = value

print("Approved rows:", int(df["reviewer_status"].astype(str).str.lower().eq("approved").sum()))
display(df[df["reviewer_status"].astype(str).str.lower().eq("approved")].head(20))
"""),
        md("""## 5. Alternatif: Download Template, Edit, Upload Ulang

Jika lebih nyaman, download template, isi di Google Sheets/Excel, lalu upload kembali.
"""),
        code("""TEMPLATE_PATH = "manual_data_fill_colab_template.csv"
df.to_csv(TEMPLATE_PATH, index=False)
print("Template saved:", TEMPLATE_PATH)

if IN_COLAB:
    files.download(TEMPLATE_PATH)
"""),
        code("""# Jalankan setelah Anda upload CSV hasil edit.
# Ubah SKIP_UPLOAD_EDITED menjadi False jika ingin memakai file hasil edit.

SKIP_UPLOAD_EDITED = True

if IN_COLAB and not SKIP_UPLOAD_EDITED:
    uploaded = files.upload()
    edited_path = next(iter(uploaded.keys()))
    df = pd.read_csv(edited_path).fillna("")
    print("Loaded edited file:", edited_path, "rows:", len(df))
    display(df.head())
"""),
        md("""## 6. Validasi Data

Validasi ini menjaga agar nilai kosong, format jam salah, rating di luar rentang, dan sumber tidak jelas tidak masuk file apply-ready.
"""),
        code("""TIME_FIELDS = {
    "jam_buka_weekday",
    "jam_tutup_weekday",
    "jam_buka_weekend",
    "jam_tutup_weekend",
}
BOOLEAN_FIELDS = {
    "coordinate_verified",
    "sentiment_available",
}
INTERNAL_SOURCE_FIELDS = {
    "sentiment_available",
}

def is_http_url(value):
    return isinstance(value, str) and re.match(r"^https?://", value.strip(), flags=re.I) is not None

def valid_source(value, field_name):
    value = str(value or "").strip()
    if is_http_url(value):
        return True
    if field_name in INTERNAL_SOURCE_FIELDS and value.startswith("internal:"):
        return True
    return False

def validate_value(field_name, value):
    field_name = str(field_name or "").strip()
    value = str(value or "").strip()
    if not value:
        return False, "new_value_empty"
    if field_name in TIME_FIELDS:
        if re.match(r"^([01]\\d|2[0-3]):[0-5]\\d$", value):
            return True, "ok_time"
        if value.lower() in {"tutup", "closed", "24 jam", "24h"}:
            return True, "ok_time_text"
        return False, "invalid_time_format"
    if field_name == "avg_rating":
        try:
            rating = float(value)
        except Exception:
            return False, "invalid_rating_number"
        if 0 <= rating <= 5:
            return True, "ok_rating"
        return False, "rating_out_of_range"
    if field_name in BOOLEAN_FIELDS:
        if value.lower() in {"true", "false", "1", "0", "yes", "no"}:
            return True, "ok_boolean"
        return False, "invalid_boolean"
    return True, "ok_generic"

def validate_row(row):
    status = str(row.get("reviewer_status", "")).strip().lower()
    if status != "approved":
        return False, "not_approved"
    field_name = str(row.get("field_name", "")).strip()
    value_ok, value_msg = validate_value(field_name, row.get("new_value", ""))
    if not value_ok:
        return False, value_msg
    if not valid_source(row.get("source_url", ""), field_name):
        return False, "source_url_invalid_or_missing"
    if field_name == "sentiment_available" and str(row.get("new_value", "")).strip().lower() in {"true", "1", "yes"}:
        note = str(row.get("reviewer_note", "")).lower()
        if "model" not in note and "pipeline" not in note:
            return False, "sentiment_true_requires_model_note"
    return True, "ok"

validation = df.apply(validate_row, axis=1, result_type="expand")
df["validation_pass"] = validation[0]
df["validation_note"] = validation[1]

print(df["validation_note"].value_counts().to_string())
display(df[["location_id", "location_name", "field_name", "new_value", "source_url", "reviewer_status", "validation_pass", "validation_note"]].head(30))
"""),
        md("""## 7. Export Hasil

Download:

- `manual_data_fill_queue_completed.csv` untuk arsip kerja penuh.
- `data_manual_apply_ready.csv` untuk diterapkan ke dataset utama di project lokal setelah audit.
"""),
        code("""COMPLETED_PATH = "manual_data_fill_queue_completed.csv"
APPLY_READY_PATH = "data_manual_apply_ready.csv"

df.to_csv(COMPLETED_PATH, index=False)
apply_ready = df[df["validation_pass"] == True].copy()
apply_ready.to_csv(APPLY_READY_PATH, index=False)

print("Completed rows:", len(df))
print("Apply-ready rows:", len(apply_ready))

if IN_COLAB:
    files.download(COMPLETED_PATH)
    files.download(APPLY_READY_PATH)
"""),
        md("""## 8. Setelah Dari Colab

Simpan `data_manual_apply_ready.csv` ke project lokal:

```text
Dataset/3_Curated/data_manual_apply_ready.csv
```

Tahap apply ke dataset utama sebaiknya dilakukan setelah audit file hasil Colab.
"""),
    ]
    return nb


def build_realworld_verification_notebook():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = notebook_metadata("Realworld_Verification_Google_Colab.ipynb")
    nb["cells"] = [
        md("""# MuterBandung Real-world Verification - Google Colab

Notebook ini dibuat untuk verifikasi manual flag real-world dari `manual_realworld_verification_queue.csv`.

Tujuan:

- Upload queue verifikasi real-world.
- Buka Google Search/Maps/official search.
- Tandai flag yang benar-benar terbukti.
- Export `manual_realworld_verification_completed.csv` dan `realworld_manual_apply_ready.csv`.

Aturan aman:

- Jangan set flag `true` tanpa bukti.
- `evidence_url` wajib HTTP/HTTPS untuk baris `approved`.
- Gunakan `flags_to_keep_false` untuk flag yang tidak ditemukan buktinya.
- Notebook ini tidak menulis dataset utama.
"""),
        code("""import re
import urllib.parse

import pandas as pd
from IPython.display import display, HTML

try:
    from google.colab import files
    IN_COLAB = True
except Exception:
    IN_COLAB = False

pd.set_option("display.max_columns", 100)
pd.set_option("display.max_colwidth", 160)
print("IN_COLAB:", IN_COLAB)
"""),
        md("""## 1. Upload Queue CSV

Upload file:

```text
Dataset/3_Curated/manual_realworld_verification_queue.csv
```
"""),
        code("""QUEUE_PATH = "manual_realworld_verification_queue.csv"

if IN_COLAB:
    uploaded = files.upload()
    if uploaded:
        QUEUE_PATH = next(iter(uploaded.keys()))

df = pd.read_csv(QUEUE_PATH).fillna("")
print("Rows:", len(df))
display(df.head(8))
"""),
        md("""## 2. Tambahkan Link Pencarian
"""),
        code("""def search_url(query, mode="search"):
    encoded = urllib.parse.quote_plus(str(query))
    if mode == "maps":
        return f"https://www.google.com/maps/search/{encoded}"
    return f"https://www.google.com/search?q={encoded}"

for col in ["verified_flags_to_set_true", "flags_to_keep_false", "evidence_url", "reviewer_status", "reviewer_note"]:
    if col not in df.columns:
        df[col] = ""

df["reviewer_status"] = df["reviewer_status"].replace("", "todo").fillna("todo")
df["google_search_url"] = df["location_name"].apply(lambda name: search_url(f"{name} Bandung fasilitas wisata"))
df["google_maps_search_url"] = df["location_name"].apply(lambda name: search_url(f"{name} Bandung", mode="maps"))
df["official_search_url"] = df["location_name"].apply(lambda name: search_url(f"{name} Bandung official website fasilitas"))

display(df[["location_id", "location_name", "priority", "unverified_facility_flags", "unverified_context_flags"]].head(10))
"""),
        md("""## 3. Batch Kerja Dengan Link Klik
"""),
        code("""def clickable(value, label):
    if not isinstance(value, str) or not value.startswith("http"):
        return ""
    return f'<a href="{value}" target="_blank">{label}</a>'

def show_work_batch(start=0, n=12, priority=None):
    work = df.copy()
    if priority:
        work = work[work["priority"].astype(str).str.upper() == priority.upper()]
    batch = work.iloc[start:start+n].copy()
    rows = []
    for _, row in batch.iterrows():
        rows.append({
            "location_id": row.get("location_id", ""),
            "location_name": row.get("location_name", ""),
            "priority": row.get("priority", ""),
            "facility_flags": row.get("unverified_facility_flags", ""),
            "context_flags": row.get("unverified_context_flags", ""),
            "Search": clickable(row.get("google_search_url", ""), "Search"),
            "Maps": clickable(row.get("google_maps_search_url", ""), "Maps"),
            "Official": clickable(row.get("official_search_url", ""), "Official"),
        })
    display(HTML(pd.DataFrame(rows).to_html(escape=False, index=False)))

show_work_batch(start=0, n=12, priority="HIGH")
"""),
        md("""## 4. Isi Cepat Dengan Dictionary

Format flag memakai pemisah `|`, contoh:

```text
parking_verified|toilet_verified|mushola_verified
```
"""),
        code("""manual_updates = [
    # Contoh:
    # {
    #     "location_id": "LOC-001",
    #     "verified_flags_to_set_true": "parking_verified|toilet_verified",
    #     "flags_to_keep_false": "pet_friendly_verified|open_24h_verified",
    #     "evidence_url": "https://...",
    #     "reviewer_status": "approved",
    #     "reviewer_note": "Dicek dari Google Maps/website resmi.",
    # },
]

for update in manual_updates:
    loc_id = str(update.get("location_id", "")).strip()
    if not loc_id:
        continue
    mask = df["location_id"].astype(str) == loc_id
    if not mask.any():
        print("Tidak ditemukan:", loc_id)
        continue
    for key, value in update.items():
        if key == "location_id":
            continue
        if key not in df.columns:
            df[key] = ""
        df.loc[mask, key] = value

print("Approved rows:", int(df["reviewer_status"].astype(str).str.lower().eq("approved").sum()))
display(df[df["reviewer_status"].astype(str).str.lower().eq("approved")].head(20))
"""),
        md("""## 5. Alternatif: Download Template, Edit, Upload Ulang
"""),
        code("""TEMPLATE_PATH = "manual_realworld_verification_colab_template.csv"
df.to_csv(TEMPLATE_PATH, index=False)
print("Template saved:", TEMPLATE_PATH)

if IN_COLAB:
    files.download(TEMPLATE_PATH)
"""),
        code("""# Jalankan setelah Anda upload CSV hasil edit.
# Ubah SKIP_UPLOAD_EDITED menjadi False jika ingin memakai file hasil edit.

SKIP_UPLOAD_EDITED = True

if IN_COLAB and not SKIP_UPLOAD_EDITED:
    uploaded = files.upload()
    edited_path = next(iter(uploaded.keys()))
    df = pd.read_csv(edited_path).fillna("")
    print("Loaded edited file:", edited_path, "rows:", len(df))
    display(df.head())
"""),
        md("""## 6. Validasi Verifikasi
"""),
        code("""def is_http_url(value):
    return isinstance(value, str) and re.match(r"^https?://", value.strip(), flags=re.I) is not None

def split_flags(value):
    return {item.strip() for item in str(value or "").split("|") if item.strip()}

def available_flags(row):
    return split_flags(row.get("unverified_facility_flags", "")) | split_flags(row.get("unverified_context_flags", ""))

def validate_row(row):
    status = str(row.get("reviewer_status", "")).strip().lower()
    if status != "approved":
        return False, "not_approved"
    if not is_http_url(row.get("evidence_url", "")):
        return False, "evidence_url_invalid_or_missing"
    true_flags = split_flags(row.get("verified_flags_to_set_true", ""))
    false_flags = split_flags(row.get("flags_to_keep_false", ""))
    if not true_flags and not false_flags:
        return False, "no_flag_decision"
    allowed = available_flags(row)
    unknown = (true_flags | false_flags) - allowed
    if unknown:
        return False, "unknown_flags: " + "|".join(sorted(unknown))
    overlap = true_flags & false_flags
    if overlap:
        return False, "flag_in_true_and_false: " + "|".join(sorted(overlap))
    return True, "ok"

validation = df.apply(validate_row, axis=1, result_type="expand")
df["validation_pass"] = validation[0]
df["validation_note"] = validation[1]

print(df["validation_note"].value_counts().to_string())
display(df[["location_id", "location_name", "verified_flags_to_set_true", "flags_to_keep_false", "evidence_url", "reviewer_status", "validation_pass", "validation_note"]].head(30))
"""),
        md("""## 7. Export Hasil

Download:

- `manual_realworld_verification_completed.csv`
- `realworld_manual_apply_ready.csv`
"""),
        code("""COMPLETED_PATH = "manual_realworld_verification_completed.csv"
APPLY_READY_PATH = "realworld_manual_apply_ready.csv"

df.to_csv(COMPLETED_PATH, index=False)
apply_ready = df[df["validation_pass"] == True].copy()
apply_ready.to_csv(APPLY_READY_PATH, index=False)

print("Completed rows:", len(df))
print("Apply-ready rows:", len(apply_ready))

if IN_COLAB:
    files.download(COMPLETED_PATH)
    files.download(APPLY_READY_PATH)
"""),
        md("""## 8. Setelah Dari Colab

Simpan `realworld_manual_apply_ready.csv` ke project lokal:

```text
Dataset/3_Curated/realworld_manual_apply_ready.csv
```

Tahap apply ke dataset utama dilakukan setelah audit file hasil Colab.
"""),
    ]
    return nb


def write_notebook(path, notebook):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        nbf.write(notebook, handle)
    print(f"Updated {path}")


def append_master_notebook():
    if not MASTER_NOTEBOOK_PATH.exists():
        print(f"Skip master notebook, not found: {MASTER_NOTEBOOK_PATH}")
        return

    with MASTER_NOTEBOOK_PATH.open("r", encoding="utf-8") as handle:
        notebook = nbf.read(handle, as_version=4)

    notebook.cells = [
        cell
        for cell in notebook.cells
        if MASTER_MARKER not in "".join(cell.get("source", ""))
    ]

    markdown = f"""## Colab Research Notebooks

`{MASTER_MARKER}`

Tahap ini menyiapkan notebook Google Colab untuk membantu pencarian data manual tanpa Apify. Colab dipakai untuk membuka link bantu, mengisi nilai hasil riset, memvalidasi input, lalu mengekspor file `apply_ready`.

Notebook yang disiapkan:

- `Notebooks/Media_Fill_Google_Colab.ipynb`
- `Notebooks/Data_Completion_Google_Colab.ipynb`
- `Notebooks/Realworld_Verification_Google_Colab.ipynb`

Prinsip:

- Colab tidak menulis dataset utama.
- Baris harus `reviewer_status=approved` agar masuk apply-ready.
- Dataset utama baru diubah setelah file hasil Colab diaudit lokal.
"""

    summary_code = """import pandas as pd

queues = {
    "media": "Dataset/3_Curated/manual_media_fill_queue.csv",
    "data": "Dataset/3_Curated/manual_data_fill_queue.csv",
    "realworld": "Dataset/3_Curated/manual_realworld_verification_queue.csv",
}

for name, path in queues.items():
    queue = pd.read_csv(path)
    print(name, "rows:", len(queue), "columns:", len(queue.columns))
"""

    notebook.cells.append(nbf.v4.new_markdown_cell(markdown))
    notebook.cells.append(nbf.v4.new_code_cell(summary_code))

    with MASTER_NOTEBOOK_PATH.open("w", encoding="utf-8") as handle:
        nbf.write(notebook, handle)
    print(f"Updated {MASTER_NOTEBOOK_PATH}")


def main():
    write_notebook(DATA_NOTEBOOK_PATH, build_data_completion_notebook())
    write_notebook(REALWORLD_NOTEBOOK_PATH, build_realworld_verification_notebook())
    append_master_notebook()


if __name__ == "__main__":
    main()
