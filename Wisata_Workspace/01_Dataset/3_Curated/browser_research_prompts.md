# Browser Research Prompts for Label Review

Gunakan prompt umum ini untuk setiap destinasi:

```text
Anda adalah AI research agent dengan akses browser. Tolong verifikasi destinasi wisata berikut dari sumber web yang kredibel seperti Google Maps, situs resmi, artikel wisata lokal, media, atau halaman sosial resmi.

Tujuan: menentukan label final untuk sistem rekomendasi wisata Bandung Raya.

Yang harus diverifikasi:
1. Apakah tempat ini benar destinasi wisata dan masih relevan/aktif?
2. Apa daya tarik utama pengunjung datang ke sana?
3. Apakah cocok untuk keluarga dan/atau anak?
4. Apakah makanan/restoran/kuliner adalah daya tarik utama atau hanya fasilitas pendukung?
5. Apakah alam/view/outdoor adalah daya tarik utama atau hanya suasana tambahan?
6. Apakah ada unsur edukasi, budaya, sejarah, petualangan, religi, malam, indoor/outdoor?
7. Berikan rekomendasi:
   - primary_intent: 1 label
   - core_labels: maksimal 3 label utama
   - secondary_labels: maksimal 3 label tambahan
   - avoid_labels: label yang sebaiknya tidak dipakai
8. Sertakan alasan singkat dan link sumber.

Label yang boleh dipakai:
Alam, Keluarga, Ramah Anak, Kuliner, Belanja, Edukasi, Sejarah, Budaya, Spot Foto, Santai/Healing, Petualangan, Religi, Malam, Indoor, Outdoor, Gratis.

Format jawaban:
primary_intent:
core_labels:
secondary_labels:
avoid_labels:
confidence: 0-1
alasan:
sumber:
```

## Destinasi Yang Perlu Review

### 1. Ciwidey Valley Resort

```text
Destinasi: Ciwidey Valley Resort
Kategori saat ini: Penginapan Wisata
Subkategori: Resort wisata
Deskripsi lokal: Kamar dan cottage simpel di resor kelas atas yang menawarkan taman rekreasi air, restoran, dan spa.
Auto-label saat ini:
- primary_intent: Santai/Healing
- core_labels: Santai/Healing
- secondary_labels: Malam
- avoid_labels: Belanja
- confidence: 0.369
Alasan review: confidence < 0.65

Gunakan prompt umum di atas untuk memverifikasi apakah core label seharusnya Santai/Healing, Keluarga, Ramah Anak, Kuliner, Alam, atau Wahana Air/Petualangan.
```

### 2. Gantolle Paralayang Singajaya Cihampelas

```text
Destinasi: Gantolle Paralayang Singajaya Cihampelas
Kategori saat ini: Wisata Petualangan
Subkategori: Aktivitas petualangan
Deskripsi lokal: Area wisata alam ketinggian di perbukitan Singajaya, Cihampelas untuk olahraga paralayang dengan panorama Waduk Saguling.
Auto-label saat ini:
- primary_intent: Petualangan
- core_labels: Petualangan; Alam; Outdoor
- secondary_labels: Spot Foto; Malam
- avoid_labels: Belanja
- confidence: 0.609
Alasan review: confidence < 0.65

Verifikasi apakah Malam layak dipakai, dan apakah Spot Foto harus core atau secondary.
```

### 3. Happyfarm Ciwidey

```text
Destinasi: Happyfarm Ciwidey
Kategori saat ini: Wisata Satwa
Subkategori: Wisata farm
Deskripsi lokal: Wisata keluarga bertema peternakan edukatif, kebun binatang mini kelinci dan domba, wahana berkuda, Candy House.
Auto-label saat ini:
- primary_intent: Keluarga
- core_labels: Keluarga; Ramah Anak; Edukasi
- secondary_labels: Outdoor
- avoid_labels: Belanja
- confidence: 0.565
Alasan review: confidence < 0.65

Verifikasi apakah core terbaik adalah Keluarga, Ramah Anak, Edukasi, atau Alam.
```

### 4. Kebun Binatang Bandung

```text
Destinasi: Kebun Binatang Bandung
Kategori saat ini: Wisata Satwa
Subkategori: Wisata satwa
Deskripsi lokal: Taman margasatwa di Tamansari dengan lebih dari 800 satwa dan fungsi konservasi edukatif.
Auto-label saat ini:
- primary_intent: Edukasi
- core_labels: Edukasi; Ramah Anak; Keluarga
- secondary_labels: Santai/Healing; Outdoor
- avoid_labels: Belanja
- confidence: 0.589
Alasan review: confidence < 0.65; Ramah Anak lacks explicit evidence

Verifikasi apakah primary_intent sebaiknya Edukasi atau Keluarga, dan apakah Ramah Anak valid sebagai core.
```

### 5. Lembang Park & Zoo

```text
Destinasi: Lembang Park & Zoo
Kategori saat ini: Wisata Satwa
Subkategori: Wisata satwa
Deskripsi lokal: Kebun binatang kecil dengan harimau, reptil, kandang burung eksotis, taman hiburan, dan naik kuda poni.
Auto-label saat ini:
- primary_intent: Ramah Anak
- core_labels: Ramah Anak; Keluarga; Edukasi
- secondary_labels: Outdoor
- avoid_labels: Belanja
- confidence: 0.517
Alasan review: confidence < 0.65; Ramah Anak lacks explicit evidence

Verifikasi apakah primary_intent sebaiknya Keluarga, Ramah Anak, atau Edukasi.
```

### 6. Taman Alun-Alun Kota Cimahi

```text
Destinasi: Taman Alun-Alun Kota Cimahi
Kategori saat ini: Taman Kota
Subkategori: Ruang publik kota
Deskripsi lokal: Taman kota rindang dekat Masjid Agung, dengan taman bermain, kedai makanan, dan acara akhir pekan.
Auto-label saat ini:
- primary_intent: Santai/Healing
- core_labels: Santai/Healing; Ramah Anak; Outdoor
- secondary_labels: Keluarga; Gratis; Malam
- avoid_labels: Belanja; Petualangan; Sejarah
- confidence: 1.0
Alasan review: Ramah Anak lacks explicit evidence

Verifikasi apakah Ramah Anak layak jadi core karena ada taman bermain.
```

### 7. Rumah Guguk

```text
Destinasi: Rumah Guguk
Kategori saat ini: Wisata Satwa
Subkategori: Wisata hewan peliharaan
Deskripsi lokal: Destinasi rekreasi unik dan ramah anak untuk pencinta anjing, interaksi dengan puluhan ras anjing.
Auto-label saat ini:
- primary_intent: Ramah Anak
- core_labels: Ramah Anak; Keluarga; Edukasi
- secondary_labels: Outdoor
- avoid_labels: Belanja
- confidence: 0.530
Alasan review: confidence < 0.65

Verifikasi apakah Edukasi layak core atau cukup secondary, dan apakah primary lebih tepat Keluarga/Ramah Anak.
```

### 8. Cikole Jayagiri Resort

```text
Destinasi: Cikole Jayagiri Resort
Kategori saat ini: Penginapan Wisata
Subkategori: Resort wisata
Deskripsi lokal: Resort wisata alam di hutan pinus Lembang dengan kabin kayu, camping, interaksi rusa, dan outbound.
Auto-label saat ini:
- primary_intent: Alam
- core_labels: Alam
- secondary_labels: Petualangan; Santai/Healing; Keluarga
- avoid_labels: Belanja; Kuliner
- confidence: 0.514
Alasan review: confidence < 0.65

Verifikasi apakah core seharusnya Alam; Petualangan; Santai/Healing atau juga Keluarga.
```

### 9. Bird & Bromelia Pavilion

```text
Destinasi: Bird & Bromelia Pavilion
Kategori saat ini: Wisata Satwa
Subkategori: Taman burung
Deskripsi lokal: Taman burung edukatif di Pramestha Resort Town Lembang dengan sekitar 600 burung dan tanaman bromelia.
Auto-label saat ini:
- primary_intent: Ramah Anak
- core_labels: Ramah Anak; Edukasi; Keluarga
- secondary_labels: Santai/Healing; Outdoor
- avoid_labels: Belanja
- confidence: 0.496
Alasan review: confidence < 0.65; Ramah Anak lacks explicit evidence

Verifikasi apakah primary_intent paling tepat Edukasi, Keluarga, atau Ramah Anak.
```

### 10. Rengganis Suspension Bridge

```text
Destinasi: Rengganis Suspension Bridge
Kategori saat ini: Wisata Petualangan
Subkategori: Jembatan gantung
Deskripsi lokal: Jembatan gantung 370 meter di Ciwidey yang menghubungkan parkir ke pemandian air panas alami Kawah Rengganis.
Auto-label saat ini:
- primary_intent: Alam
- core_labels: Alam; Petualangan
- secondary_labels: Outdoor
- avoid_labels: Belanja; Kuliner
- confidence: 0.578
Alasan review: confidence < 0.65

Verifikasi apakah primary_intent seharusnya Petualangan atau Alam.
```

### 11. Driam Riverside

```text
Destinasi: Driam Riverside
Kategori saat ini: Penginapan Wisata
Subkategori: Resort wisata
Deskripsi lokal: Wisata tepi sungai di Pasirjambu dengan penginapan, restoran, river tubing, dan offroad.
Auto-label saat ini:
- primary_intent: Alam
- core_labels: Alam
- secondary_labels: Petualangan; Santai/Healing; Keluarga
- avoid_labels: Belanja
- confidence: 0.400
Alasan review: confidence < 0.65

Verifikasi apakah core perlu Alam; Petualangan; Kuliner atau Santai/Healing.
```

### 12. Pesona Nirwana Waterpark

```text
Destinasi: Pesona Nirwana Waterpark
Kategori saat ini: Wahana Air
Subkategori: Wahana air buatan
Deskripsi lokal: Taman wisata air dengan kolam renang, seluncur, sungai mengapung, dan food court.
Auto-label saat ini:
- primary_intent: Keluarga
- core_labels: Keluarga; Ramah Anak; Petualangan
- secondary_labels: Alam; Santai/Healing; Outdoor
- avoid_labels: Belanja
- confidence: 0.623
Alasan review: confidence < 0.65

Verifikasi apakah Ramah Anak valid core dan apakah Petualangan terlalu kuat atau tepat.
```

### 13. Penangkaran Rusa Kertamanah

```text
Destinasi: Penangkaran Rusa Kertamanah
Kategori saat ini: Wisata Satwa
Subkategori: Penangkaran rusa
Deskripsi lokal: Wisata edukasi keluarga di Margamukti Pangalengan untuk memberi makan dan berfoto dengan rusa jinak di alam terbuka.
Auto-label saat ini:
- primary_intent: Keluarga
- core_labels: Keluarga; Edukasi; Ramah Anak
- secondary_labels: Outdoor
- avoid_labels: Belanja; Kuliner
- confidence: 0.534
Alasan review: confidence < 0.65

Verifikasi apakah Alam/Outdoor harus core dan apakah Ramah Anak valid.
```

### 14. Tafso Barn

```text
Destinasi: Tafso Barn
Kategori saat ini: Tempat Kuliner
Subkategori: Restoran wisata
Deskripsi lokal: Restoran tematik bernuansa taman lereng bukit di Punclut dengan tempat duduk unik, spot foto, dan panorama alam sejuk.
Auto-label saat ini:
- primary_intent: Kuliner
- core_labels: Kuliner; Santai/Healing; Alam
- secondary_labels: Spot Foto; Malam; Outdoor
- avoid_labels: Belanja; Petualangan; Religi; Sejarah
- confidence: 0.950
Alasan review: Alam core label suspicious for non-nature category

Verifikasi apakah Alam sebaiknya core atau secondary karena daya tarik utamanya restoran/view.
```

### 15. Taman Kupu-Kupu Cihanjuang

```text
Destinasi: Taman Kupu-Kupu Cihanjuang
Kategori saat ini: Wisata Satwa
Subkategori: Wisata satwa
Deskripsi lokal: Taman edukasi keluarga 1,8 hektar di Parongpong dengan rumah kepompong dan insectarium.
Auto-label saat ini:
- primary_intent: Keluarga
- core_labels: Keluarga; Edukasi; Ramah Anak
- secondary_labels: Outdoor
- avoid_labels: Belanja; Kuliner
- confidence: 0.534
Alasan review: confidence < 0.65

Verifikasi apakah primary_intent lebih tepat Edukasi atau Keluarga.
```

### 16. Wahoo Waterworld

```text
Destinasi: Wahoo Waterworld
Kategori saat ini: Wahana Air
Subkategori: Waterworld
Deskripsi lokal: Waterpark 10 hektar di Kota Baru Parahyangan dengan wahana air dan seluncuran ekstrem RocketBLAST.
Auto-label saat ini:
- primary_intent: Keluarga
- core_labels: Keluarga; Petualangan
- secondary_labels: Ramah Anak
- avoid_labels: Belanja; Kuliner
- confidence: 0.534
Alasan review: confidence < 0.65

Verifikasi apakah Ramah Anak perlu core atau secondary, dan apakah Petualangan terlalu kuat.
```

### 17. Imah Seniman Lembang

```text
Destinasi: Imah Seniman Lembang
Kategori saat ini: Penginapan Wisata
Subkategori: Resort wisata
Deskripsi lokal: Resort dan destinasi wisata alam berkonsep tradisional di Lembang dengan kabin jerami tepi danau serta restoran khas Sunda.
Auto-label saat ini:
- primary_intent: Alam
- core_labels: Alam; Gratis
- secondary_labels: Santai/Healing; Budaya; Malam
- avoid_labels: Belanja
- confidence: 0.358
Alasan review: confidence < 0.65

Verifikasi apakah core seharusnya Alam; Santai/Healing; Kuliner atau Budaya.
```

### 18. Desa Wisata Buricak Burinong

```text
Destinasi: Desa Wisata Buricak Burinong
Kategori saat ini: Desa Wisata
Subkategori: Desa wisata
Deskripsi lokal: Kampung wisata berwarna-warni di pesisir Waduk Jatigede Sumedang dengan panorama waduk, Masjid Al-Kamil, dan aktivitas paralayang.
Auto-label saat ini:
- primary_intent: Budaya
- core_labels: Budaya
- secondary_labels: Alam; Keluarga; Spot Foto
- avoid_labels: Belanja
- confidence: 0.524
Alasan review: confidence < 0.65

Verifikasi apakah primary_intent lebih tepat Budaya, Alam, Spot Foto, atau Petualangan.
```
