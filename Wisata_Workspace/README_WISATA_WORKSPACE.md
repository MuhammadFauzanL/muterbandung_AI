# Wisata Workspace - MuterBandung

Workspace ini berisi proses data wisata MuterBandung yang dipisahkan dari workspace penginapan/hotel. Tujuannya agar alur wisata, notebook wisata, input Apify wisata, dan dataset curated wisata tidak tercampur dengan proses hotel.

## Struktur Folder

| Folder | Fungsi |
|---|---|
| `01_Dataset/` | Semua dataset wisata: raw, intermediate, curated, evaluation, dan arsip. |
| `02_Notebooks/` | Notebook training, audit, Colab, NLP, media fill, dan data completion wisata. |
| `03_Dokumentasi/` | Ruang dokumentasi khusus wisata jika nanti ingin dipisahkan lebih jauh. |
| `04_Apify_Workspace/` | Input, output, dan script Apify untuk scraping/review wisata. |

## Dataset Utama Website

Dataset wisata utama yang dipakai recommender:

`Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`

File pendukung landmark:

`Wisata_Workspace/01_Dataset/3_Curated/landmark_aliases.csv`

Snapshot schema API:

`Wisata_Workspace/01_Dataset/4_Evaluation/api_schema_snapshot.json`

## Notebook Utama

Notebook utama proses wisata:

`Wisata_Workspace/02_Notebooks/wisata_training.ipynb`

Notebook ini tetap menjadi tempat utama dokumentasi proses wisata/training/curation, sesuai arahan sebelumnya.

## Catatan Runtime

Runtime website tetap berada di folder root:

| File | Fungsi |
|---|---|
| `Scripts/app.py` | Flask API dan route website. |
| `Scripts/recommender.py` | Mesin rekomendasi wisata. |
| `Scripts/templates/index.html` | Frontend utama. |
| `Scripts/static/style.css` | Styling frontend. |
| `Scripts/static/script.js` | Logic frontend. |

`Scripts/recommender.py` sudah diarahkan ke dataset wisata di workspace ini.

## Catatan Script Lama

Beberapa script eksplorasi lama di folder `Scripts/` masih bersifat historis. Script yang paling penting untuk runtime, validasi, targeted completion, manual review, dan audit koordinat sudah diarahkan ke path workspace wisata baru.

Jika ingin menjalankan script lama lain yang masih menyebut `Dataset/` atau `Notebooks/`, update path-nya dulu agar mengarah ke:

- `Wisata_Workspace/01_Dataset/`
- `Wisata_Workspace/02_Notebooks/`

## Prinsip Pemakaian

1. Jangan menimpa dataset curated utama tanpa backup.
2. Simpan proses wisata di workspace ini.
3. Simpan proses hotel/penginapan di `Penginapan_Workspace`.
4. Gunakan validation pipeline sebelum hasil data masuk ke recommender/LLM.
5. Jika ada data manual baru, apply ke curated dataset lalu jalankan validasi ulang.
