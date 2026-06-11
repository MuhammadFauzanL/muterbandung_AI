import nbformat as nbf


NOTEBOOK_PATH = "Notebooks/Media_Fill_Google_Colab.ipynb"


def md(source):
    return nbf.v4.new_markdown_cell(source)


def code(source):
    return nbf.v4.new_code_cell(source)


def build_notebook():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "colab": {
            "name": "Media_Fill_Google_Colab.ipynb",
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

    cells = [
        md("""# MuterBandung Media Fill - Google Colab

Notebook ini dibuat untuk mengisi **media saja** tanpa Apify.

Tujuan:

- Upload `manual_media_fill_queue.csv`.
- Buka link pencarian Google/Maps/Images yang sudah dibuat.
- Isi `new_media_image_url`, `new_media_destination_url`, dan/atau `new_media_website`.
- Validasi URL.
- Export CSV hasil: `manual_media_fill_queue_completed.csv` dan `media_manual_apply_ready.csv`.

Aturan aman:

- Minimal isi salah satu: `new_media_image_url` atau `new_media_destination_url`.
- Gunakan URL asli yang relevan dengan destinasi, bukan hasil raw match yang meragukan.
- `reviewer_status` harus `approved` agar bisa diterapkan ke dataset utama.
- Notebook ini tidak menulis dataset utama; apply dilakukan di project lokal dengan script terpisah.
"""),
        code("""import os
import re
import json
import time
import urllib.parse

import pandas as pd
import requests
from IPython.display import display, HTML

try:
    from google.colab import files
    IN_COLAB = True
except Exception:
    IN_COLAB = False

pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 120)
print("IN_COLAB:", IN_COLAB)
"""),
        md("""## 1. Upload Queue CSV

Upload file:

```text
Dataset/3_Curated/manual_media_fill_queue.csv
```

Jika Anda memakai Google Drive, Anda juga bisa set `QUEUE_PATH` ke path Drive setelah mount.
"""),
        code("""QUEUE_PATH = "manual_media_fill_queue.csv"

if IN_COLAB:
    uploaded = files.upload()
    if uploaded:
        QUEUE_PATH = next(iter(uploaded.keys()))

df = pd.read_csv(QUEUE_PATH)
print("Rows:", len(df))
display(df.head(10))
"""),
        md("""## 2. Pastikan Link Bantu Ada

Cell ini menambahkan link pencarian jika file yang diupload belum punya kolom bantuan.
"""),
        code("""def search_url(query, mode="search"):
    encoded = urllib.parse.quote_plus(str(query))
    if mode == "maps":
        return f"https://www.google.com/maps/search/{encoded}"
    if mode == "images":
        return f"https://www.google.com/search?tbm=isch&q={encoded}"
    return f"https://www.google.com/search?q={encoded}"

for col in ["new_media_image_url", "new_media_destination_url", "new_media_website", "new_media_source_note", "reviewer_status", "reviewer_note"]:
    if col not in df.columns:
        df[col] = ""

if "google_search_url" not in df.columns:
    df["google_search_url"] = df["location_name"].apply(lambda name: search_url(f"{name} Bandung wisata", "search"))
if "google_maps_search_url" not in df.columns:
    df["google_maps_search_url"] = df["location_name"].apply(lambda name: search_url(f"{name} Bandung", "maps"))
if "google_image_search_url" not in df.columns:
    df["google_image_search_url"] = df["location_name"].apply(lambda name: search_url(f"{name} Bandung wisata", "images"))

df["reviewer_status"] = df["reviewer_status"].fillna("todo").replace("", "todo")
print(df[["location_id", "location_name", "priority", "google_search_url", "google_maps_search_url", "google_image_search_url"]].head(5).to_string(index=False))
"""),
        md("""## 3. Tampilkan Batch Kerja

Gunakan batch ini untuk membuka Google Search, Google Maps, dan Google Images.

Isi URL dengan salah satu metode:

1. Edit file CSV template di Google Sheets, lalu upload lagi di bagian validasi.
2. Isi dictionary `manual_updates` di cell berikutnya.
"""),
        code("""def clickable(value, label):
    if not isinstance(value, str) or not value.startswith("http"):
        return ""
    return f'<a href="{value}" target="_blank">{label}</a>'

def show_work_batch(start=0, n=10, priority=None):
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
            "suggested_raw_title": row.get("suggested_raw_title", ""),
            "audit_note": row.get("audit_note", ""),
            "Search": clickable(row.get("google_search_url", ""), "Search"),
            "Maps": clickable(row.get("google_maps_search_url", ""), "Maps"),
            "Images": clickable(row.get("google_image_search_url", ""), "Images"),
        })
    html = pd.DataFrame(rows).to_html(escape=False, index=False)
    display(HTML(html))

show_work_batch(start=0, n=15, priority="HIGH")
"""),
        md("""## 4. Cara Isi Cepat Dengan Dictionary

Isi contoh di bawah. Hapus contoh atau tambah item baru sesuai kebutuhan.

`reviewer_status` wajib `approved` agar masuk file apply-ready.
"""),
        code("""manual_updates = [
    # Contoh:
    # {
    #     "location_id": "LOC-155",
    #     "new_media_image_url": "https://...",
    #     "new_media_destination_url": "https://www.google.com/maps/...",
    #     "new_media_website": "",
    #     "new_media_source_note": "manual_google_colab",
    #     "reviewer_status": "approved",
    #     "reviewer_note": "URL dicek manual dari Google Maps/website resmi.",
    # },
]

for update in manual_updates:
    loc_id = str(update.get("location_id", "")).strip()
    if not loc_id:
        continue
    mask = df["location_id"].astype(str) == loc_id
    if not mask.any():
        print("location_id tidak ditemukan:", loc_id)
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

Jika lebih nyaman, download template CSV, buka di Google Sheets/Excel, isi kolom `new_media_*`, lalu upload kembali.
"""),
        code("""TEMPLATE_PATH = "manual_media_fill_colab_template.csv"
df.to_csv(TEMPLATE_PATH, index=False)
print("Template saved:", TEMPLATE_PATH)

if IN_COLAB:
    files.download(TEMPLATE_PATH)
"""),
        code("""# Jalankan cell ini setelah Anda mengupload CSV yang sudah diedit.
# Kalau tidak perlu, biarkan SKIP_UPLOAD_EDITED = True.

SKIP_UPLOAD_EDITED = True

if IN_COLAB and not SKIP_UPLOAD_EDITED:
    uploaded = files.upload()
    edited_path = next(iter(uploaded.keys()))
    df = pd.read_csv(edited_path)
    print("Loaded edited file:", edited_path, "rows:", len(df))
    display(df.head())
"""),
        md("""## 6. Validasi URL

Validasi ini tidak sempurna, tapi cukup untuk mencegah URL kosong, format salah, dan beberapa URL mati.
"""),
        code("""def is_http_url(value):
    return isinstance(value, str) and re.match(r"^https?://", value.strip(), flags=re.I) is not None

def check_url_live(url, expect_image=False, timeout=10):
    url = str(url or "").strip()
    if not is_http_url(url):
        return False, "not_http_url"
    try:
        response = requests.get(url, timeout=timeout, stream=True, headers={"User-Agent": "Mozilla/5.0"})
        status = response.status_code
        content_type = response.headers.get("content-type", "")
        response.close()
    except Exception as exc:
        return False, f"request_error: {exc}"
    if status >= 400:
        return False, f"http_status_{status}"
    if expect_image and ("image" not in content_type.lower()) and ("googleusercontent.com" not in url):
        return False, f"not_image_content_type: {content_type}"
    return True, f"ok status={status} content_type={content_type}"

def validate_row(row, live_check=True):
    image_url = str(row.get("new_media_image_url", "") or "").strip()
    destination_url = str(row.get("new_media_destination_url", "") or "").strip()
    website = str(row.get("new_media_website", "") or "").strip()
    status = str(row.get("reviewer_status", "") or "").strip().lower()
    errors = []
    notes = []

    if status != "approved":
        return "skip", "reviewer_status is not approved"
    if not any([image_url, destination_url, website]):
        errors.append("no_new_media_url")
    for field, url in [("image", image_url), ("destination", destination_url), ("website", website)]:
        if url and not is_http_url(url):
            errors.append(f"{field}_not_http_url")
    if live_check:
        if image_url:
            ok, note = check_url_live(image_url, expect_image=True)
            notes.append(f"image:{note}")
            if not ok:
                errors.append("image_url_failed_live_check")
        for field, url in [("destination", destination_url), ("website", website)]:
            if url:
                ok, note = check_url_live(url, expect_image=False)
                notes.append(f"{field}:{note}")
                if not ok:
                    errors.append(f"{field}_url_failed_live_check")
    if errors:
        return "invalid", " | ".join(errors + notes)
    return "valid", " | ".join(notes) if notes else "format_ok"

LIVE_CHECK = True
results = df.apply(lambda row: validate_row(row, live_check=LIVE_CHECK), axis=1)
df["validation_status"] = [item[0] for item in results]
df["validation_note"] = [item[1] for item in results]

print(df["validation_status"].value_counts(dropna=False).to_string())
display(df[df["validation_status"].isin(["valid", "invalid"])][[
    "location_id", "location_name", "reviewer_status", "validation_status", "validation_note",
    "new_media_image_url", "new_media_destination_url", "new_media_website"
]].head(30))
"""),
        md("""## 7. Export Hasil

File penting:

- `manual_media_fill_queue_completed.csv`: semua row dengan status validasi.
- `media_manual_apply_ready.csv`: hanya row `approved` + `valid`, siap dipakai script apply lokal.
"""),
        code("""COMPLETED_PATH = "manual_media_fill_queue_completed.csv"
APPLY_READY_PATH = "media_manual_apply_ready.csv"

df.to_csv(COMPLETED_PATH, index=False)
apply_ready = df[(df["reviewer_status"].astype(str).str.lower() == "approved") & (df["validation_status"] == "valid")].copy()
apply_ready.to_csv(APPLY_READY_PATH, index=False)

print("completed rows:", len(df), "->", COMPLETED_PATH)
print("apply-ready rows:", len(apply_ready), "->", APPLY_READY_PATH)
display(apply_ready[[
    "location_id", "location_name", "new_media_image_url", "new_media_destination_url", "new_media_website", "new_media_source_note", "reviewer_note"
]].head(30))

if IN_COLAB:
    files.download(COMPLETED_PATH)
    files.download(APPLY_READY_PATH)
"""),
        md("""## 8. Langkah Lokal Setelah Download

Letakkan salah satu file hasil Colab ke project lokal, misalnya:

```text
Dataset/3_Curated/media_manual_apply_ready.csv
```

Lalu jalankan di project lokal:

```powershell
python -B Scripts/apply_manual_media_updates.py --input Dataset/3_Curated/media_manual_apply_ready.csv --dry-run
python -B Scripts/apply_manual_media_updates.py --input Dataset/3_Curated/media_manual_apply_ready.csv --apply
```

Setelah apply:

```powershell
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard
python -B Scripts/evaluate_groundtruth.py
python -B scratch_qc.py
```
"""),
    ]
    nb.cells = cells
    return nb


def main():
    nb = build_notebook()
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as handle:
        nbf.write(nb, handle)
    print(f"Created {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
