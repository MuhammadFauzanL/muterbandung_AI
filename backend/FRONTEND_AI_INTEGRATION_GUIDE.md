# 🎨 Panduan Integrasi Frontend untuk AI MuterBandung

Dokumen ini ditujukan untuk tim UI/UX dan Frontend agar dapat menangani respons dari AI Agent secara maksimal.

---

## 🔌 Koneksi API
Akses utama melalui satu titik masuk: `https://[api-url]/api/recommend`.

### 1. Menangani "State" Chatbot
AI kami tidak hanya mengirim data tempat, tapi juga narasi.
*   **Field `answer`:** Berisi teks sapaan si Cepot. Wajib ditampilkan dalam balon chat.
*   **Field `recommendations`:** Array berisi data kartu wisata (Gambar, Jarak, Harga).

---

## 🛡️ Penanganan Keamanan & Out-of-Context
Sistem Backend akan memfilter pertanyaan yang "Aneh" (Politik, SARA, Hacking). 

**Yang Harus Dilakukan Frontend:**
*   Jika sistem mendeteksi pertanyaan luar konteks, Backend tetap mengirim **HTTP 200**, namun list `recommendations` akan **kosong**.
*   Frontend harus mengecek: `if (data.recommendations.length === 0)`.
*   Tampilkan pesan `answer` dari Cepot yang menolak secara halus. JANGAN menampilkan error merah (*Crash*), karena ini adalah fitur keamanan, bukan kerusakan sistem.

---

## ⏳ UX & Performance (Loading States)
Proses AI Hybrid (Cloudflare + Backend Ranker) memakan waktu:
*   **Normal:** 1.5 - 2 detik.
*   **Failover (Cadangan):** 3 - 5 detik (jika harus pindah ke OpenRouter).

**Rekomendasi UI:**
1.  Gunakan **Skeleton Screen** untuk kartu wisata.
2.  Tampilkan animasi "Cepot sedang mengetik..." agar user tidak merasa aplikasi nge-hang.
3.  Berikan pesan *feedback* jika waktu tunggu > 5 detik: *"Lalu lintas sedang padat, Cepot sedang berusaha mencari jalan..."*

---

## 🎭 Implementasi Persona (Halaman Beranda)
Frontend dapat mengirim preferensi user ke `/api/persona/home`.

**Cara Kerja:**
1.  User pilih "Vibe" (misal: "Alam").
2.  Backend membalas dengan `persona_id` (misal: `nature_seeker`).
3.  Frontend dapat mengubah **Gambar Hero** atau **Tema Warna** aplikasi sesuai ID tersebut agar terasa lebih personal.

---

## 👣 Integrasi Behaviour (Next Step Suggester)
Gunakan endpoint `/api/behaviour/next`.

**Contoh Kasus:**
*   User baru saja melihat detail kartu "Kawah Putih".
*   Frontend tembak API ini, dapatkan saran: "Kuliner".
*   Tampilkan di bawah halaman: *"Cape abis dari gunung? Enaknya lanjut Makan-makan nih!"*
