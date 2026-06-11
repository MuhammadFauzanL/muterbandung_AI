# Deep EDA Findings — MuterBandung Dataset
Analisis eksplorasi mendalam terhadap seluruh aset data MuterBandung.

---

## A. Profil Data Master (232 Lokasi Wisata)

| Metrik | Nilai |
|---|---|
| Total Lokasi | 232 |
| Kategori | 16 jenis |
| Sub-Kategori | 91 jenis |
| Sebaran GPS | 126 km (diameter) |
| Harga Rata-rata | Rp 18.836 (min) — Rp 30.685 (max) |
| Lokasi Gratis | 56 (24%) |
| Termahal | Rp 450.000 |

### Distribusi Kategori (Top 5)
1. **Wisata Alam** — 83 lokasi (35.8%)
2. **Rekreasi Keluarga** — 38 lokasi (16.4%)
3. **Taman Kota** — 21 lokasi (9.1%)
4. **Tempat Belajar** — 15 lokasi (6.5%)
5. **Tempat Camping** — 10 lokasi (4.3%)

---

## B. Profil Data Ulasan (16.120 Reviews)

| Metrik | Nilai |
|---|---|
| Total Ulasan | 16.120 |
| Lokasi Tercakup | 226 dari 232 |
| Rating Rata-rata | 4.45 / 5.0 |
| Panjang Teks Rata-rata | 227 karakter |
| Bahasa Dominan | Indonesia (69%), Inggris (12%) |

### Distribusi Rating (Imbalanced!)
| Rating | Jumlah | Proporsi |
|---|---|---|
| ⭐ 5 | 11.022 | 68.4% |
| ⭐ 4 | 3.092 | 19.2% |
| ⭐ 3 | 948 | 5.9% |
| ⭐ 2 | 299 | 1.9% |
| ⭐ 1 | 759 | 4.7% |

> [!WARNING]
> **Imbalanced Data**: Rating 5 mendominasi 68% dataset. Model NLP WAJIB menggunakan teknik *Class Weighting* atau *SMOTE* agar tidak bias menebak semua ulasan "Positif".

---

## C. Temuan Kunci & Potensi Kebaruan (Novelty)

### 🔥 Temuan 1: "Mahal ≠ Bagus" (Korelasi Negatif Harga-Rating)
```
Korelasi Pearson (Harga vs Rating): -0.14
```
> **Ini adalah temuan menarik untuk Capstone!** Tempat wisata yang **lebih mahal** justru cenderung mendapat **rating lebih rendah**. Hipotesis: Pengunjung yang membayar mahal memiliki ekspektasi yang lebih tinggi, sehingga lebih kritis dalam memberikan ulasan.
>
> **Nilai Akademis:** Temuan ini bisa dijadikan sub-bab tersendiri dalam BAB pembahasan sebagai "*Price-Expectation Gap Analysis*".

### 🔥 Temuan 2: Kata Kunci Aspek Tervalidasi dari Data Nyata
Top 20 kata paling sering muncul membuktikan bahwa **aspek-aspek ABSA kita sudah tepat sasaran:**

| Aspek yang Direncanakan | Kata Bukti dari EDA | Frekuensi |
|---|---|---|
| 🏞️ Pemandangan/View | `foto` (1.277x), `taman` (1.560x) | Tinggi |
| 💰 Harga/Value | `tiket` (2.004x), `harga` (1.408x), `masuk` (2.355x) | Sangat Tinggi |
| 🚻 Fasilitas/Akses | `parkir` (1.811x), `jalan` (2.051x), `area` (1.477x) | Sangat Tinggi |
| 👨‍👩‍👧 Keluarga/Anak | `anak` (1.577x), `cocok` (1.512x) | Tinggi |
| 😌 Kenyamanan | `nyaman` (1.359x), `bagus` (2.063x) | Tinggi |
| ⚠️ Kekurangan | `kurang` (1.261x) | Tinggi |

> [!IMPORTANT]
> **Aspek Baru Terdeteksi: "Kesesuaian untuk Anak/Keluarga"!** Kata `anak` muncul 1.577 kali — ini adalah aspek yang BELUM kita rencanakan di arsitektur awal. Menambahkan aspek **Family-Friendliness** akan menjadi nilai tambah yang sangat kuat untuk Capstone Anda.

### 🔥 Temuan 3: Data Pendukung yang Belum Dimanfaatkan

| Dataset | Isi | Potensi |
|---|---|---|
| `jenis_kawasan_wisata_primer` (91 row) | Pemetaan resmi kawasan wisata dari Dinas Pariwisata Bandung | **Cross-reference** dengan kategori kita untuk validasi resmi |
| `daftar_perusahaan_jasa_perjalanan` (239 row) | Daftar 239 biro perjalanan di Bandung | Bisa ditambahkan sebagai fitur *"Travel Agent Density"* (Potensi wisata berdasarkan banyaknya agen wisata di sekitar lokasi) |

### 🔥 Temuan 4: Distribusi Harga yang Sangat Informatif

| Segmen Harga | Jumlah Lokasi | Potensi Fitur |
|---|---|---|
| Gratis (Rp 0) | 56 | Rekomendasi "Budget Traveler" |
| Murah (Rp 1 - 15K) | 79 | Rekomendasi "Hemat" |
| Menengah (Rp 15K - 50K) | 84 | Rekomendasi "Standard" |
| Premium (Rp 50K - 200K) | 13 | Rekomendasi "Premium Experience" |

> **Novelty**: Sistem MuterBandung bisa memiliki fitur **Budget-Aware Recommendation** yang unik — sistem tidak hanya merekomendasikan berdasarkan *rating*, tapi juga mencocokkan dengan **kantong** pengguna.

### 🔥 Temuan 5: Polarisasi Rating Lokasi

| Status | Contoh | Keterangan |
|---|---|---|
| Rating Sempurna (5.0) | Kampung Singkur, Danau Biru Situ Cilembang | Lokasi tersembunyi (*hidden gem*) dengan ulasan sedikit tapi sangat positif |
| Rating Rendah (< 3.5) | Bird Pavilion (2.35), LEMBANG Wonderland (3.20) | Lokasi populer yang mengecewakan — **kandidat untuk fitur "Avoid List"** |

---

## D. Rekomendasi Fitur Baru untuk Sistem Rekomendasi

Berdasarkan temuan EDA di atas, berikut adalah fitur-fitur baru yang berpotensi memperkuat kebaruan Capstone:

### 1. `family_score` — Skor Kesesuaian Keluarga (BARU!)
Diturunkan dari frekuensi kata `anak`, `keluarga`, `cocok`, `bermain` di ulasan.

### 2. `price_segment` — Segmentasi Harga Otomatis
Mengkategorikan lokasi ke dalam Gratis/Murah/Menengah/Premium berdasarkan harga tiket.

### 3. `popularity_tier` — Tingkat Popularitas
Berdasarkan jumlah ulasan: Viral (>200), Populer (50-200), Cukup Dikenal (10-50), Tersembunyi (<10).

### 4. `value_for_money` — Rasio Kualitas vs Harga
Rumus: `avg_rating / log(price_min + 1)`. Semakin tinggi, semakin "worth it".

### 5. `controversy_score` — Tingkat Kontroversi
Dihitung dari standar deviasi rating. Jika SD tinggi (bintang 1 & 5 banyak), lokasi tersebut kontroversial.

---

## E. Kesimpulan Strategis

> [!TIP]
> **Data Anda sudah dalam status GOLDEN STATE.** Tidak ada kebocoran Geospatial, Pricing, maupun Categorical. Semua 16.120 ulasan siap diproses.
>
> **Kebaruan terkuat Capstone Anda** terletak pada 3 hal:
> 1. **Aspect-Based Sentiment** (bukan sentiment biasa)
> 2. **Budget-Aware Recommendation** (Geospatial + Harga + Sentimen)
> 3. **Family-Friendliness Score** (aspek baru yang terdeteksi dari EDA)
>
> Ketiga hal ini membuat MuterBandung BUKAN sekadar "Google Maps clone", melainkan **Smart Tourism Advisor** yang memahami konteks pengunjung.
