<div align="center">

# Tim Pengembang PIJAK
### Dicoding Capstone Project (PJK-GM056)

---

<table>
  <tr>
    <td align="center">
      <img width="128" height="128" src="https://github.com/user-attachments/assets/fac42ceb-3149-459e-85ce-8e8e327b9dc7" alt="Fauzan"><br>
      <a href="https://github.com/fauzanashshidiq">
        <img src="https://img.shields.io/badge/051-M.%20Fauzan%20A.-blue" alt="051 Badge">
      </a>
    </td>
    <td align="center">
      <img width="128" height="128" src="https://github.com/user-attachments/assets/800f0a8d-3503-4ce4-9266-99ce9a7c3f4b" alt="Rahardian"><br>
      <a href="https://github.com/rhrdianbaihaqi">
        <img src="https://img.shields.io/badge/023-M.%20Rahardian%20B.-blue" alt="023 Badge">
      </a>
    </td>
    <td align="center">
      <img width="128" height="128" src="https://github.com/user-attachments/assets/7e57a253-1aa2-40f9-94d2-6c13ed51cc37" alt="Nazwa"><br>
      <a href="https://github.com/nazwaym">
        <img src="https://img.shields.io/badge/007-Nazwa%20Yulianti-blue" alt="007 Badge">
      </a>
    </td>
    <td align="center">
      <img width="128" height="128" src="https://github.com/user-attachments/assets/b8239489-d715-409b-a883-3a8d4f0ca595" alt="Raflhy"><br>
      <a href="https://github.com/raflhyramadhan18">
        <img src="https://img.shields.io/badge/004-Raflhy%20Ramadhan-blue" alt="004 Badge">
      </a>
    </td>
  </tr>
</table>

<br>

# MuterBandung
**Smart Travel & Accommodation Recommender Berbasis AI**

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-Next.js-000000?style=flat-square&logo=next.js&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/API_Gateway-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI_Engine-Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Machine_Learning-PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/NLP-HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="HuggingFace">
</p>

---

</div>

## 1. Penjelasan Aplikasi MuterBandung
**MuterBandung** adalah sebuah platform pintar berbasis *Artificial Intelligence* (AI) dan *Natural Language Processing* (NLP) yang dirancang untuk menjadi asisten perjalanan pribadi Anda di kota Bandung dan sekitarnya. Aplikasi ini membantu wisatawan untuk menemukan destinasi wisata, tempat kuliner, hingga rekomendasi penginapan terdekat hanya dengan mengetikkan keinginan mereka secara natural (misalnya: *"cari tempat wisata alam yang dingin, murah, dan cocok untuk anak di daerah Lembang"*). 

Dengan memadukan pencarian semantik (pemahaman makna bahasa) dan kalkulasi geospasial (jarak koordinat GPS), MuterBandung memastikan rekomendasi yang diberikan sangat akurat dan relevan dengan niat pengguna.

## 2. Latar Belakang Masalah
Di era digital, pencarian destinasi wisata menggunakan aplikasi *travel* konvensional masih sering mengandalkan *filter* kaku (ceklis kategori atau rentang harga) dan pencarian kata kunci (*keyword matching*). Jika pengguna mencari "tempat sepi untuk merenung", sistem konvensional akan kesulitan. Akibatnya, wisatawan sering kewalahan dan kesulitan menemukan tempat yang benar-benar pas (*hidden gems*) sesuai dengan *mood* dan spesifikasi lokasi aktual yang mereka mau.

## 3. Tujuan Proyek
- **Pemahaman Bahasa Natural (NLP):** Memproses *query* bebas pengguna dan memahami makna di baliknya (intensi pencarian) tanpa terikat pada *filter* kaku.
- **Akurasi Geospasial (Location-Aware):** Mampu mengenali nama daerah (seperti Lembang, Dago, Jatinangor) lalu memberikan batasan radius jarak secara otomatis agar hasil rekomendasi benar-benar akurat secara geografis.
- **Rekomendasi Berbasis AI (RAG):** Memberikan rangkuman dan alasan mengapa suatu tempat direkomendasikan dengan gaya bahasa asisten lokal Sunda yang ramah.
- **Integrasi Cerdas:** Otomatisasi pencarian penginapan terdekat dari destinasi wisata yang telah dipilih.

## 4. Teknologi yang Digunakan
Proyek ini dibangun dengan arsitektur Tri-Service yang terintegrasi untuk stabilitas maksimal:
- **Frontend:** React.js, Next.js (App Router), TailwindCSS.
- **Core Backend API Proxy:** FastAPI (Python), Uvicorn, httpx (bertugas sebagai *gateway* asinkron).
- **Backend AI & ML:** Flask (Python), PyTorch, Pandas, NumPy.
- **Machine Learning & NLP:** Sentence-Transformers (model `firqaaa/indo-sentence-bert-base`), Scikit-Learn (TF-IDF).
- **Generative AI (LLM):** OpenRouter (Google Gemini / GPT-4o) untuk RAG.
- **Infrastruktur Hosting:** Vercel (Frontend), Hugging Face Spaces / Railway / VPS (Backend AI & Proxy).

## 5. Fitur Unggulan
- **Pencarian AI Semantik:** Secara cerdas menyamakan kata "murah" dengan "gratis" atau "terjangkau", serta mendeteksi nuansa seperti "alam", "romantis", atau "edukasi".
- **Location-Aware Enforcement & Fallback:** Memberlakukan batasan pencarian secara radial. Jika hasil terlalu sedikit, sistem otomatis melonggarkan radius (*fallback*) sebelum mengembalikan hasil kosong.
- **AI Chatbot:** Asisten *virtual* yang memberikan saran spesifik dan alasan logis berdasarkan dataset.
- **Rekomendasi Penginapan Sekitar:** Secara otomatis memetakan dan menyarankan hotel/villa terdekat dari wisata pilihan Anda.

## 6. Model AI Persona & Behaviour
MuterBandung tidak sekadar menampilkan data mentah, melainkan menyajikan pengalaman interaktif layaknya berbicara dengan warga lokal Bandung melalui rancangan pemodelan perilaku (Behaviour Model) dan karakter (Persona):
- **Persona "Cepot":** Sistem AI Chatbot kami dirancang dengan *System Prompting* khusus agar memiliki karakter "Cepot" — asisten lokal Sunda yang ramah, sopan (*handap asor*), santai, dan berpengetahuan luas tentang Bandung. Penjelasan destinasi tidak lagi terasa kaku dan robotik.
- **Behaviour Model (Anti-Halusinasi):** Algoritma dirancang secara cermat di mana model LLM *tidak memiliki hak* untuk menentukan hasil pencarian atau *ranking* destinasi. Model hanya bertindak sebagai **Interpreter** (Penerjemah Alasan) yang mengambil hasil pasti dari kalkulasi jarak dan skor TF-IDF *Backend AI Engine* kami. Mekanisme RAG (*Retrieval-Augmented Generation*) ketat ini memastikan AI tidak pernah mengarang informasi fiktif di luar dataset yang telah disurvei.

## 7. Arsitektur Tri-Service
Aplikasi ini memecah beban kerjanya ke dalam tiga *services* terpisah agar proses kalkulasi *Machine Learning* yang berat tidak membuat aplikasi *freeze*:

- **Frontend (Next.js)** 
  $\rightarrow$ Menangani antarmuka UI/UX interaktif untuk pengguna.
- **Backend Core API (FastAPI)** 
  $\rightarrow$ Bertindak sebagai API Gateway super cepat. Menerima *request* dan mem-bypass hal-hal ringan.
- **Backend AI Engine (Flask)** 
  $\rightarrow$ Menangani komputasi berat, memuat model NLP, dataset `.csv` ke dalam memori RAM, menghitung *cosine similarity*, dan memanggil layanan API LLM pihak ketiga.

## 8. Dokumentasi Antarmuka

<div align="center">

| Pencarian Cerdas | Detail Rekomendasi AI | Rekomendasi Penginapan |
|:---:|:---:|:---:|
| <img width="250" src="https://via.placeholder.com/250x500.png?text=UI+Pencarian+Cerdas" alt="Pencarian"> | <img width="250" src="https://via.placeholder.com/250x500.png?text=UI+Detail+AI" alt="Rekomendasi AI"> | <img width="250" src="https://via.placeholder.com/250x500.png?text=UI+Penginapan" alt="Penginapan"> |

*Catatan: Ganti gambar placeholder di atas dengan screenshot aktual aplikasi MuterBandung.*
</div>

## 9. Cara Instalasi Lokal untuk Development

### Struktur Folder
```text
📦 MuterBandung
 ┣ 📂 backend/                 # Mesin Backend AI (Flask + ML Models + NLP)
 ┣ 📂 backend_core/            # API Gateway Proxy (FastAPI)
 ┗ 📂 frontend/                # Aplikasi Antarmuka (Next.js)
```

Pastikan sistem Anda sudah terinstal Node.js dan Python (>=3.10).

**A. Clone Repositori**
```bash
git clone https://github.com/fauzanashshidiq/MuterBandung.git
cd MuterBandung
```

**B. Persiapan Backend AI Engine (Port 5000)**
1. `cd backend`
2. `python -m venv .venv` lalu `.venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. Buat `.env` dan masukkan `OPENROUTER_API_KEY`.
5. Jalankan server: `python app/main.py`

**C. Persiapan Backend Core API (Port 8001)**
1. Terminal baru: `cd backend_core`
2. `python -m venv .venv` lalu `.venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. Buat `.env` dan masukkan `BACKEND_AI_URL=http://localhost:5000`.
5. Jalankan server: `uvicorn app.main:app --reload --port 8001`

**D. Persiapan Frontend (Port 3000)**
1. Terminal baru: `cd frontend`
2. `npm install`
3. Buat `.env.local` dan tambahkan `NEXT_PUBLIC_API_URL=http://localhost:8001/api`
4. Jalankan aplikasi web: `npm run dev`

## 10. Kolaborasi Tim
Proyek ini merupakan hasil kerja keras dari tim **Capstone Project PJK-GM056 (Tim PIJAK)** di bawah naungan program Dicoding. Pengembangan dilakukan melalui pendekatan lintas disiplin yang meliputi peran Front-End Engineering, Back-End Engineering, serta Machine Learning Engineering.