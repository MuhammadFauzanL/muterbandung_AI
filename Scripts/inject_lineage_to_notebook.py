import nbformat
import os

def inject_lineage():
    notebook_path = 'Notebooks/wisata_traning.ipynb'
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
            
        markdown_content = """# 🗃️ DATA LINEAGE (REKAM JEJAK DATA MUTERBANDUNG)
**PENTING**: Bab ini mendokumentasikan asal-muasal seluruh data yang diproses di dalam *notebook* ini.

Jika Anda bertanya: *"Dari mana asal 34.150 ulasan yang digunakan untuk melatih AI ini?"*
Jawabannya adalah dari aliran data (Pipeline) berikut:

1. **TAHAP SUMBER (RAW APIFY SCRAPING):**
   - Data asli disedot (*scraped*) dari Google Maps menggunakan layanan Apify. File mentah fisiknya masih tersimpan di folder `Dataset/` (Contoh: `apify_reviews_tambahan_batch1.csv` sebesar ~15 MB).
2. **TAHAP PENGGABUNGAN & PEMBERSIHAN:**
   - Script `gabung_semua_review.py` dan `credible_data_cleaning.py` menghancurkan 146 kolom tak berguna dari Apify, menghapus duplikat, dan menormalisasi nama wisata agar cocok dengan Master Database. Menghasilkan file murni `MASTER_REVIEWS_ENRICHED.csv` (34.150 baris).
3. **TAHAP PELATIHAN AI (INDOBERT):**
   - File murni tersebut diproses di Google Colab (menggunakan GPU T4) untuk melakukan *Fine-Tuning* pada model `indobenchmark/indobert-base-p1` (Akurasi akhir 89.91%).
4. **TAHAP HASIL AKHIR (DATABASE PARIPURNA):**
   - Skor prediksi dari IndoBERT, dikombinasikan dengan *Multi-Label Auto-Tagging*, lalu dilebur bersama database lokasi. Menghasilkan produk akhir `DATABASE_WISATA_FINAL_PARIPURNA.csv`.

*(Rincian lengkap dan diagram alur dapat dilihat di dokumen `Dokumentasi_Sistem/DATA_LINEAGE_REPORT.md`)*
---
"""
        
        # Create new markdown cell
        new_md_cell = nbformat.v4.new_markdown_cell(markdown_content)
        
        # Insert at the very beginning (index 0)
        nb.cells.insert(0, new_md_cell)
        
        # Save notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
            
        print(f'Berhasil menyuntikkan bab Data Lineage ke bagian paling awal {notebook_path}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    inject_lineage()
