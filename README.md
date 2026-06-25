# 🍛 Nusantara Recipe

**Aplikasi Desktop Manajemen Resep Masakan Indonesia**

---

## 📋 Deskripsi

**Nusantara Recipe** adalah aplikasi desktop untuk menyimpan, mencari, dan mengelola resep masakan Indonesia secara digital. Aplikasi ini hadir sebagai solusi untuk melestarikan kekayaan kuliner Nusantara dalam satu platform yang mudah digunakan oleh siapa saja.

Aplikasi mendukung dua peran pengguna:
- **User** — dapat mencari resep, melihat detail, dan menyimpan favorit
- **Admin** — dapat mengelola seluruh data resep dan kategori

---

## 👥 Anggota Kelompok

| Nama | NIM | Tanggung Jawab |
|------|-----|----------------|
| Muhammad Ridho Aidil Furqon | F1D02310127 | Database, Models, Export, Dashboard, Detail Resep |
| Maulida Citra Illiyyin | F1D02310145 | Login/Auth, Main Window, Stylesheet QSS, Profil, Kelola Kategori |
| Muharromi Ali Ilham | F1D02410082 | Daftar Resep, Form Dialog, Favorit, Navigasi, README |

---

## ✨ Fitur Utama

### 🔐 Autentikasi
- Login dan registrasi akun dengan validasi lengkap
- Sistem multi-role (Admin / User) dengan hak akses berbeda
- Password disimpan dalam bentuk hash SHA-256

### 🏠 Dashboard
- Ringkasan statistik: total resep, kategori, dan daerah asal
- Tabel 5 resep terbaru — klik langsung membuka detail
- Distribusi resep per kategori

### 📋 Daftar Resep
- Tampilan tabel lengkap dengan semua data resep
- **Search** by nama resep atau daerah asal (real-time)
- **Filter** berdasarkan kategori masakan
- **Sorting** 4 opsi: nama A–Z, Z–A, waktu masak tercepat/terlama
- Klik baris langsung membuka halaman Detail Resep

### 📖 Detail Resep
- Informasi lengkap: nama, kategori, daerah asal, waktu masak, porsi
- Daftar bahan-bahan dalam tabel
- Langkah memasak bernomor urut
- Tombol **Simpan Favorit** (toggle)
- Tombol **Export PDF** per resep

### ❤ Favorit
- Simpan resep favorit dengan satu klik
- Akses cepat ke resep yang sering digunakan
- Klik baris membuka Detail Resep

### 👤 Profil Saya
- Edit username dan email
- Ganti password dengan verifikasi password lama

### 🗂 Kelola Kategori *(Admin only)*
- Tambah, edit, dan hapus kategori masakan
- Konfirmasi penghapusan untuk mencegah kesalahan

### 📤 Export Data
- **Export CSV** — ekspor seluruh daftar resep ke file CSV (kompatibel Excel)
- **Export PDF** — ekspor detail resep per resep ke file PDF berformat rapi


| Halaman | Keterangan |
|---------|------------|
| Login | Dialog login/registrasi dengan header hijau |
| Dashboard | Statistik dan resep terbaru |
| Daftar Resep | Tabel dengan search, filter, dan sorting |
| Detail Resep | Bahan dan langkah memasak lengkap |
| Favorit | Daftar resep tersimpan |

---

## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/username/pv26-finalproject-nusantara_recipe.git
cd pv26-finalproject-nusantara_recipe
```

### 2. Buat Virtual Environment *(Opsional tapi direkomendasikan)*

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi

```bash
python main.py
```

### 5. Login

Gunakan akun default yang sudah tersedia:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |

> Database akan dibuat otomatis pada saat pertama kali aplikasi dijalankan.

---

## 📦 Dependensi

```
PySide6>=6.5.0
reportlab>=4.0.0
```

---

## 🗂 Struktur Proyek

```
pv26-finalproject-nusantararecipe/
│
├── main.py                    # Entry point aplikasi
├── requirements.txt           # Dependensi Python
├── README.md                  # Dokumentasi ini
│
├── assets/
│   └── style.qss              # Stylesheet global (tema hijau)
│
├── database/
│   ├── __init__.py
│   └── db.py                  # Inisialisasi & koneksi SQLite
│
├── models/
│   ├── __init__.py
│   └── models.py              # UserModel, RecipeModel, CategoryModel, FavoriteModel
│
├── ui/
│   ├── __init__.py
│   ├── login_dialog.py        # Dialog login & registrasi
│   ├── main_window.py         # Jendela utama & sidebar navigasi
│   ├── dashboard_page.py      # Halaman dashboard
│   ├── recipe_list_page.py    # Halaman daftar resep
│   ├── recipe_detail_page.py  # Halaman detail resep
│   ├── recipe_dialog.py       # Form tambah/edit resep (QDialog)
│   ├── favorites_page.py      # Halaman favorit
│   └── other_pages.py         # Halaman profil & kelola kategori
│
└── utils/
    ├── __init__.py
    └── export.py              # Fungsi export CSV & PDF
```

---

## 🗄 Skema Database

Aplikasi menggunakan **SQLite** dengan 6 tabel berelasi:

```
users          → menyimpan akun pengguna (role: admin/user)
categories     → kategori masakan (Soto, Padang, Jawa, dll)
recipes        → data resep utama
ingredients    → bahan-bahan per resep (relasi ke recipes)
steps          → langkah memasak per resep (relasi ke recipes)
favorites      → resep favorit per user (relasi many-to-many)
```

**Relasi antar tabel:**
- `categories` (1) → (N) `recipes`
- `users` (1) → (N) `recipes` *(created_by)*
- `recipes` (1) → (N) `ingredients`
- `recipes` (1) → (N) `steps`
- `users` (M) ↔ (N) `recipes` *via* `favorites`

---

## 🛠 Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Bahasa | Python 3.10+ |
| GUI Framework | PySide6 (Qt for Python) |
| Database | SQLite 3 |
| Export PDF | ReportLab |
| Export CSV | csv (built-in Python) |
| Styling | Qt Style Sheets (.qss) |
| Hashing | hashlib SHA-256 |

---

## 📝 Catatan Teknis

- Wajib menggunakan **PySide6** (bukan PyQt5 / PyQt6)
- Database `resep.db` dibuat otomatis — **tidak perlu setup manual**
- File `resep.db` **tidak di-push ke GitHub** (ada di `.gitignore`)
- Aplikasi berjalan **fullscreen** secara default
- Status bar menampilkan nama & NIM seluruh anggota kelompok

---