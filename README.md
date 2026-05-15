# 💵 Smart Split Bill AI

Selamat datang di **Smart Split Bill AI**! 
Ini adalah prototipe aplikasi web berbasis Streamlit yang dirancang untuk membantumu membagi tagihan makan (atau belanja) bareng teman-teman tanpa perlu menghitung manual. Cukup foto struknya, dan AI akan membagi secara otomatis. 

---

## 🚀 Cara Menjalankan Aplikasi

Kamu bisa mencoba menjalankan aplikasi ini di komputermu sendiri. Berikut langkah-langkahnya:

**Menjalankan secara lokal (Tanpa Docker):**
1. Buka terminal dan salin repositori ini ke komputermu:
   ```bash
   git clone https://github.com/alfiahzalfa/smart-split-bill.git
   cd smart-split-bill
   ```
2. Buat ruang virtual (*virtual environment*) agar instalasinya rapi:
   ```bash
   python -m venv venv
   ```
   Lalu aktifkan dengan perintah `source venv/bin/activate` (untuk Linux/Mac) atau `venv\Scripts\activate` (untuk Windows).
3. Instal semua *library* yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan aplikasinya:
   ```bash
   streamlit run app.py
   ```
5. Buka `http://localhost:8501` di browsermu. Jangan lupa, klik tombol ⚙️ **Settings** di pojok kanan atas untuk memilih model yang akan digunakansebelum mengunggah struk, ya!

**Menjalankan menggunakan Docker:**
Kamu bisa langsung menjalankannya dengan satu perintah ini (pastikan sudah membuat.env yang berisi *API Key*-nya):
```bash
docker compose up --build
```

---

## 🧠 Eksperimen & Pemilihan Model AI 

Dalam membangun prototipe ini, saya membandingkan tiga model, yaitu Groq, Gemini, dan Donut. 

### 1. Gemini 2.0 Flash 
- **Kelebihan:** 
  - Akurasi pembacaan struk yang sangat tinggi.
  - Bagus dalam membedakan harga item dengan biaya tambahan (PPN, *Service Charge*, Diskon).
  - Hasil ekstrasinya juga bagus.
- **Kekurangan:** 
  - Membutuhkan koneksi internet dan *API Key* Google. Limitnya kecil, sehingga sering hanya bisa digunakan sebentar.
- **Analisis:** Gemini memberikan hasil yang paling seimbang antara kecepatan dan ketepatan, mampu mengatasi foto struk yang sedikit miring atau memiliki *background* acak dengan sangat baik.

### 2. Groq 
- **Kelebihan:** 
  - Kecepatan pemrosesan yang lumayan cepat.
  - Mampu memahami instruksi ekstraksi dengan baik.
- **Kekurangan:** 
  - Terkadang kurang teliti menangkap label pajak atau diskon jika tata letak struknya berantakan.
  - Membutuhkan koneksi internet dan *API Key* Groq.
- **Analisis:** Groq tidak kalah dengan Gemini, hasilnya sangat memuaskan untuk struk standar, menjadikannya alternatif lain dari Gemini jika Gemini sedang mencapai limit.

### 3. Donut 
- **Kelebihan:** 
  - Berjalan 100% secara lokal (*offline*).
  - Tidak memerlukan *API Key*.
- **Kekurangan:** 
  - Terkadang tidak dapat membaca struk jika struk yang diupload kusam atau terlipat.
  - Tidak bisa mendeteksi pajak/biaya tambahan secara otomatis.
  - Waktu komputasi yang lambat jika dijalankan di CPU.
- **Analisis:** Karena Donut adalah model yang dijalankan murni di perangkat keras komputer saya (CPU), waktu pemrosesannya paling lama dibaningkan 2 model yang lain. Model ini juga sering mengembalikan *output* kosong jika kualitas foto sedikit saja tidak sesuai dengan standar *dataset* latihannya.

---

## Evaluasi & Saran

### 1. Evaluasi dari Sisi Model AI 
- **Kelemahan:** 
  - Ketergantungan penuh pada model *cloud* (seperti Gemini) membuat aplikasi ini tidak bisa dipakai tanpa koneksi internet atau jika *limit* API gratisnya habis. 
  - Tidak ada metrik tingkat keyakinan (*confidence score*), sehingga jika gambar struk sangat buram dan AI salah menebak angka, sistem tidak bisa memberikan peringatan kepada pengguna.
- **Saran:** 
  - Menambahkan fitur *image preprocessing* otomatis (misal: mempertajam gambar atau meluruskan rotasi) sebelum gambar dikirim ke AI. 
  - Melakukan *fine-tuning* pada model *open-source* yang ringan (seperti Florence-2) khusus untuk *dataset* struk di Indonesia, agar kita memiliki alternatif model lokal (*offline*) yang cepat dan akurat.

### 2. Evaluasi dari Sisi Aplikasi Web
- **Kelemahan:** 
  - Data bersifat sementara (*session state*). Jika pengguna tidak sengaja menutup *browser* atau me-*refresh* halaman, mereka harus mengulangi proses dari awal.
  - Belum ada fitur untuk mengekspor atau membagikan tagihan akhir secara praktis ke orang lain.
- **Saran:** 
  - Mengintegrasikan *database* (misalnya SQLite/PostgreSQL) dan fitur *Login* agar riwayat *split bill* bisa tersimpan aman.


