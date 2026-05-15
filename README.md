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

## 🧠 Eksperimen & Pemilihan Model AI (Step 1)

Dalam membangun prototipe ini, saya tidak menggunakan alat OCR konvensional seperti PyTesseract atau EasyOCR. Sebagai gantinya, saya meriset dan membandingkan tiga model *Vision-Language* (AI yang bisa melihat gambar). Berikut adalah analisis komparatif dari ketiga model tersebut:

### 1. Gemini 2.0 Flash (Google Cloud)
- **Kelebihan:** 
  - Akurasi pembacaan struk yang sangat tinggi, khususnya untuk format Indonesia.
  - Sangat cerdas dalam membedakan harga item makanan dengan biaya tambahan (PPN, *Service Charge*, Diskon).
  - *Output* berformat JSON yang konsisten.
- **Kekurangan:** 
  - Membutuhkan koneksi internet dan *API Key* Google.
- **Analisis:** Gemini memberikan hasil yang paling seimbang antara kecepatan dan ketepatan. Kecepatan *inference*-nya berkisar antara 3-6 detik. Ia mampu mengatasi foto struk yang sedikit miring atau memiliki *background* acak dengan sangat baik.

### 2. Groq (Cloud API Llama/Mixtral)
- **Kelebihan:** 
  - Kecepatan pemrosesan yang luar biasa kilat (berkat infrastruktur LPU Groq).
  - Mampu memahami instruksi ekstraksi JSON dengan baik layaknya model raksasa.
- **Kekurangan:** 
  - Terkadang kurang teliti menangkap label pajak atau diskon jika tata letak struknya berantakan.
  - Membutuhkan koneksi internet dan *API Key* Groq.
- **Analisis:** Groq adalah juara mutlak dalam hal kecepatan (waktu *inference* hanya 1-2 detik). Secara umum, akurasinya sangat memuaskan untuk struk standar, menjadikannya alternatif yang sangat solid jika Gemini sedang mencapai limit.

### 3. Donut (naver-clova-ix/donut-base-finetuned-cord-v2)
- **Kelebihan:** 
  - Berjalan 100% secara lokal (*offline*).
  - Tidak memerlukan *API Key* pihak ketiga, sehingga privasi data terjamin.
- **Kekurangan:** 
  - Akurasi sangat rendah untuk struk Indonesia atau struk kusam.
  - Tidak bisa mendeteksi pajak/biaya tambahan secara otomatis (hanya dilatih untuk membaca nama item dan harga).
  - Waktu komputasi yang sangat lambat jika dijalankan di CPU biasa.
- **Analisis:** Karena Donut adalah model berukuran kecil yang dijalankan murni di perangkat keras komputer saya (CPU), waktu pemrosesannya memakan 45 hingga 90 detik. Model ini juga sangat kaku dan sering mengembalikan *output* kosong jika kualitas foto sedikit saja tidak sesuai dengan standar *dataset* latihannya.

### ✅ Kesimpulan: Model yang Dipilih (Gemini 2.0 Flash)
Meskipun Groq menang dari segi kecepatan pemrosesan, saya pada akhirnya menetapkan **Gemini 2.0 Flash** sebagai model utama (*default*). Alasan terbesarnya adalah akurasi Gemini yang konsisten nyaris sempurna pada struk Indonesia dan kemampuannya memilah detail pajak. Hal ini membuat pengalaman pengguna menjadi jauh lebih dapat diandalkan tanpa harus banyak mengoreksi hasil pembacaan AI.

---

## 📷 Contoh Hasil Pembacaan Model

Untuk membuktikan kinerjanya, saya menguji model ini dengan dua struk yang berbeda:

### Struk 1: Makan Siang di Restoran
Struk ini memiliki kerumitan berupa adanya PPN 10% dan *Service Charge* 5%. 
- **Hasil Gemini:** Gemini sukses menyusun *output* JSON yang rapi. Ia menangkap "Nasi Goreng Spesial" (2 porsi), "Es Teh Manis" (3 porsi), dan "Ayam Bakar" (1 porsi). Ia juga dengan cerdas memisahkan *Service Charge* (Rp 6.300) dan PPN (Rp 12.600) dari subtotal.
- **Hasil Donut:** Donut hanya berhasil membaca nama item secara acak dan sama sekali mengabaikan adanya pajak dan biaya layanan.

### Struk 2: Belanja di Minimarket
Struk ini memiliki tantangan berupa adanya "Diskon Member" yang memotong harga total.
- **Hasil Gemini:** Hebatnya, Gemini mengenali diskon tersebut dan memasukkannya ke dalam kolom *Additional Charges* dengan nilai minus (negatif), sehingga saat aplikasi melakukan perhitungan total, harganya jadi sangat akurat.
- **Hasil Donut:** Model gagal mengekstrak data karena *layout* struk minimarket cukup berbeda dengan data latihannya.

---

## 📊 Evaluasi Keseluruhan & Ide Perbaikan (Step 3)

Setelah prototipe ini selesai dibangun, saya melakukan evaluasi kualitatif terhadap dua aspek utama dan memikirkan ide-ide untuk mengembangkannya lebih jauh:

### 1. Evaluasi dari Sisi Model AI (Pembaca Bill)
- **Kelemahan:** 
  - Ketergantungan penuh pada model *cloud* (seperti Gemini) membuat aplikasi ini tidak bisa dipakai tanpa koneksi internet atau jika *limit* API gratisnya habis. 
  - Tidak ada metrik tingkat keyakinan (*confidence score*), sehingga jika gambar struk sangat buram dan AI salah menebak angka, sistem tidak bisa memberikan peringatan kepada pengguna.
- **Ide Perbaikan:** 
  - Menambahkan fitur *image preprocessing* otomatis (misal: mempertajam gambar atau meluruskan rotasi) sebelum gambar dikirim ke AI. 
  - Melakukan *fine-tuning* pada model *open-source* yang ringan (seperti Florence-2) khusus untuk *dataset* struk di Indonesia, agar kita memiliki alternatif model lokal (*offline*) yang cepat dan akurat.

### 2. Evaluasi dari Sisi Aplikasi Web (Fungsionalitas & UX/UI)
- **Kelemahan:** 
  - Data bersifat sangat sementara (*session state*). Jika pengguna tidak sengaja menutup *browser* atau me-*refresh* halaman, mereka harus mengulangi proses pembagian dari awal.
  - Belum ada fitur untuk mengekspor atau membagikan tagihan akhir secara praktis ke orang lain (saat ini pengguna harus melakukan tangkapan layar manual).
  - Pembagian biaya tambahan (seperti pajak dan *service charge*) saat ini dikunci menjadi proporsional. Tidak ada opsi membaginya secara rata ("pukul rata").
- **Ide Perbaikan:** 
  - Mengintegrasikan *database* (misalnya SQLite/PostgreSQL) dan fitur *Login* agar riwayat *split bill* bisa tersimpan aman.
  - Menambahkan tombol "Bagikan ke WhatsApp" yang akan menghasilkan teks ringkasan tagihan per orang secara otomatis (lengkap dengan nomor rekening).
  - Memberikan *toggle* opsi tambahan agar pengguna bebas memilih apakah pajak/layanan ingin dibagi secara proporsional atau dibagi rata ke semua partisipan.


