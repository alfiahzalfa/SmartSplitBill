# 💵 Smart Split Bill

Aplikasi web berbasis Streamlit untuk membaca struk belanja menggunakan AI dan membagi tagihan ke beberapa orang.

---

## 🚀 Cara Menjalankan

### Tanpa Docker

```bash
# 1. Clone repo
git clone https://github.com/<username>/smart-split-bill.git
cd smart-split-bill

# 2. Buat virtual environment (Python 3.12+)
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan app
streamlit run app.py
```

Buka http://localhost:8501 di browser, lalu klik ⚙️ **Settings** untuk memasukkan API key.

### Dengan Docker

```bash
GOOGLE_API_KEY=isi_api_key_kamu docker compose up --build
```

---

## 🧠 Komparasi Model AI

### Model yang Dievaluasi

| Model | Tipe | Dijalankan Di | API Key |
|---|---|---|---|
| **Gemini 2.0 Flash** | Multimodal LLM | Cloud (Google) | ✅ Perlu |
| **Donut (naver-clova-ix/donut-base-finetuned-cord-v2)** | OCR-free Seq2Seq | Lokal (CPU/GPU) | ❌ Tidak perlu |

### Kriteria Analisis

#### 1. Akurasi Pembacaan (Kualitatif)

**Gemini 2.0 Flash**
- ✅ Membaca item dengan sangat akurat di berbagai jenis struk (restoran, supermarket, kafe)
- ✅ Mengekstrak pajak (PPN), service charge, dan diskon secara otomatis
- ✅ Mendukung teks Indonesia, Inggris, dan campuran
- ✅ Output JSON konsisten dan mudah di-parse
- ⚠️ Terkadang salah baca angka pada struk yang sangat blur
- **Rating: 9/10**

**Donut**
- ✅ Tidak perlu API key, berjalan sepenuhnya offline
- ✅ Akurasi bagus pada receipt standar English/Korea format POS
- ❌ Tidak mengekstrak additional charges (pajak, service) — perlu diisi manual
- ❌ Akurasi turun drastis pada receipt Indonesia
- ❌ Gagal pada layout struk yang tidak standar (multi-kolom, thermal print kusam)
- ❌ Single-item receipt bisa menyebabkan error parsing
- **Rating: 5/10**

#### 2. Kecepatan Inference

| Model | Rata-rata Waktu | Keterangan |
|---|---|---|
| Gemini 2.0 Flash | 3–6 detik | Tergantung koneksi internet |
| Donut (CPU) | 45–90 detik | Tergantung spesifikasi CPU |
| Donut (GPU CUDA) | 5–12 detik | Jika tersedia GPU |

#### 3. Analisis Tambahan

| Kriteria | Gemini | Donut |
|---|---|---|
| Biaya | Berbayar (free tier tersedia) | Gratis |
| Privasi | Data dikirim ke Google | Sepenuhnya lokal |
| Setup | Mudah (hanya butuh API key) | Perlu download model ~500MB |
| Multi-bahasa | ✅ | ⚠️ Terbatas English/Korea |
| Ekstrak pajak/service | ✅ Otomatis | ❌ Manual |
| Keandalan | Tinggi | Sedang |

### ✅ Model Dipilih: Gemini 2.0 Flash (Default)

**Alasan:**
- Akurasi jauh lebih tinggi untuk receipt Indonesia
- Mengekstrak semua field yang dibutuhkan (item, subtotal, additional charges, total) secara otomatis
- Google AI Studio menyediakan free tier yang cukup untuk kebutuhan prototype
- Waktu inference cepat (~3–6 detik) vs Donut di CPU yang memakan 45–90 detik

---

## 📷 Contoh Hasil Baca Model

### Struk 1 — Restoran Indonesia

**Input:** Struk makan siang dengan PPN 10% dan service charge 5%

**Output Gemini:**
```json
{
  "menus": [
    {"name": "Nasi Goreng Spesial", "count": 2, "price": 60000},
    {"name": "Es Teh Manis", "count": 3, "price": 21000},
    {"name": "Ayam Bakar", "count": 1, "price": 45000}
  ],
  "additional_charges": [
    {"name": "Service Charge 5%", "amount": 6300},
    {"name": "PPN 10%", "amount": 12600}
  ],
  "subtotal": 126000,
  "total": 144900
}
```
✅ Semua item benar, pajak dan service charge terdeteksi.

**Output Donut:** Hanya baca sebagian item, pajak tidak terdeteksi, nama item tidak akurat.

---

### Struk 2 — Minimarket

**Input:** Struk kasir minimarket dengan diskon member

**Output Gemini:**
```json
{
  "menus": [
    {"name": "Indomie Goreng", "count": 3, "price": 10500},
    {"name": "Aqua 600ml", "count": 2, "price": 8000},
    {"name": "Teh Botol Sosro", "count": 1, "price": 5500}
  ],
  "additional_charges": [
    {"name": "Diskon Member", "amount": -2400}
  ],
  "subtotal": 24000,
  "total": 21600
}
```
✅ Diskon berhasil ditangkap sebagai nilai negatif.

**Output Donut:** Gagal parse — format struk minimarket berbeda dari training data CORD.

---

## 📊 Evaluasi & Analisis (Step 3)

### A. Evaluasi Model AI

**Kelemahan:**
1. Gemini bergantung internet dan API key — tidak bisa dipakai offline
2. Donut akurasinya rendah untuk receipt Indonesia
3. Tidak ada confidence score — kita tidak tahu seberapa yakin model
4. Gambar struk yang sangat blur atau terlipat bisa menyebabkan hasil salah

**Ide Improvement:**
1. Fine-tune model open-source (misal Florence-2) pada dataset receipt Indonesia
2. Tambahkan image preprocessing: crop, straighten, denoise sebelum dikirim ke AI
3. Jalankan dua model sekaligus dan tampilkan perbedaan ke user untuk dikonfirmasi
4. Minta model untuk mengeluarkan confidence score per field

### B. Evaluasi Produk Web

**Kelemahan:**
1. Tidak ada fitur export — report tidak bisa disimpan sebagai PDF atau dibagikan
2. Refresh halaman menghapus semua data (tidak ada persistensi)
3. Setiap item hanya bisa diassign secara manual — tidak ada opsi "split rata ke semua"
4. UI kurang optimal di layar mobile
5. Tidak ada validasi jika user submit tanpa assign semua item

**Ide Improvement:**
1. Tambah tombol "Bagikan ke semua" untuk split rata otomatis
2. Export report ke PDF atau screenshot yang bisa dibagikan via WhatsApp
3. Simpan history struk sebelumnya
4. Buat versi mobile-first (PWA atau React Native)
5. Tambah fitur "split item tertentu secara merata" antar beberapa orang pilihan


