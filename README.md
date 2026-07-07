# Herman Musik — Project Structure

Website rental tenda & taratak pesta pernikahan, disusun dengan arsitektur 3-layer:
**Frontend (HTML/CSS/JS)** → **Backend (Python Flask)** → **Database (MySQL)**

---

## 📁 Struktur Folder

```
herman_musik/
│
├── frontend/               ← Tampilan website (HTML, CSS, JS)
│   ├── index.html          ← Halaman utama
│   ├── css/
│   │   └── style.css       ← Semua styling
│   └── js/
│       └── main.js         ← Interaksi (modal, form, scroll, WA)
│
├── backend/                ← API Server (Python Flask)
│   ├── app.py              ← Semua endpoint API
│   ├── requirements.txt    ← Daftar library Python
│   └── .env.example        ← Template konfigurasi (salin ke .env)
│
└── database/
    └── schema.sql          ← Struktur tabel + data awal MySQL
```

---

## 🚀 Cara Menjalankan

### 1. Setup Database (MySQL)

```bash
# Masuk ke MySQL
mysql -u root -p

# Jalankan schema
source /path/to/herman_musik/database/schema.sql
# atau:
mysql -u root -p < database/schema.sql
```

### 2. Setup Backend (Python)

```bash
cd backend

# Buat virtual environment (opsional tapi disarankan)
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# Install library
pip install -r requirements.txt

# Salin dan isi konfigurasi database
cp .env.example .env
# Edit .env → isi DB_USER, DB_PASSWORD sesuai MySQL Anda

# Jalankan server
python app.py
# Server berjalan di: http://localhost:5000
```

### 3. Jalankan Frontend

Buka file `frontend/index.html` langsung di browser.

Atau gunakan live server (VS Code extension) agar fetch ke backend berjalan mulus.

---

## 🔌 Endpoint API

| Method | URL                  | Fungsi                              |
|--------|----------------------|-------------------------------------|
| GET    | /api/health          | Cek status server                   |
| POST   | /api/permintaan      | Simpan data dari form kontak        |
| GET    | /api/permintaan      | Ambil semua permintaan (admin)      |
| GET    | /api/produk          | Ambil daftar produk/layanan         |
| GET    | /api/paket           | Ambil daftar paket + item           |
| GET    | /api/testimoni       | Ambil testimoni yang sudah disetujui|
| POST   | /api/testimoni       | Kirim testimoni baru (pending)      |

---

## 🔄 Alur Data

```
Pengguna isi form → frontend/js/main.js
    ↓ fetch POST /api/permintaan
backend/app.py → validasi → simpan ke MySQL
    ↓
database/herman_musik → tabel permintaan
```

---

## 🛠️ Teknologi

| Layer    | Teknologi          |
|----------|--------------------|
| Frontend | HTML5, CSS3, JS    |
| Backend  | Python 3.x + Flask |
| Database | MySQL 8.x          |
| Font     | Google Fonts       |
| Gambar   | Unsplash CDN       |
