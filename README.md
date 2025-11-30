````markdown
# 📂 Sistem Tupoksi Arsiparis (Internal Team Documentation)

Halo Team! 👋

Selamat datang di repositori resmi **Sistem Tupoksi Arsiparis**. Proyek ini bertujuan untuk mendigitalisasi pengelolaan Tugas Pokok dan Fungsi (Tupoksi) Arsiparis agar lebih efisien, terstruktur, dan mudah dipantau.

Dokumen ini dirancang sebagai panduan teknis bagi kita semua. Karena tim ini terbagi menjadi **Backend (Python)** dan **Frontend (Native HTML/JS)**, sangat penting bagi kita untuk mematuhi struktur dan alur kerja yang ada di sini agar integrasi berjalan mulus tanpa konflik.

*Mari kita bangun kode yang bersih, rapi, dan minim bug!* 🚀

---

## 📂 Struktur Project Global

Berikut adalah pembagian folder agar file coding (statis) tidak tercampur dengan file data (dinamis), serta memisahkan area kerja Backend dan Frontend:

```text
.
├── app/                 # [Backend] Logic API & Konfigurasi Database
├── database/            # [Data] Kumpulan file .sql (Schema/Backup)
├── storage/             # [DATA] Tempat menyimpan file Surat & Rapot (Ganti nama dari 'assets' root)
│   ├── surat/
│   └── rapot/
├── frontend/            # [Frontend] Folder kerja tim Frontend
│   ├── index.html
│   ├── assets/          # [Frontend] File statis (CSS, JS, Logo Web)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
├── .env                 # [Config] File rahasia (Jangan dipush ke GitHub!)
├── main.py              # [Backend] Entry point server
├── seed_admin.py        # [Backend] Script data awal
├── test_api.py          # [Backend] Testing script
└── requirements.txt     # [Backend] Dependency Python
````

-----

## 🐍 Panduan Backend (Python)

Bagian ini khusus untuk tim yang mengurus API, Logic, dan Database.

### 1\. Setup Development

Ikuti langkah ini untuk menyiapkan environment lokal:

```bash
# 1. Clone & Masuk Direktori
git clone [https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis.git](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis.git)
cd Sistem-Tupoksi-Arsiparis

# 2. Setup Virtual Environment (Wajib!)
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt
```

#### 4\. Konfigurasi Environment (.env)

Buat file baru bernama `.env` di folder paling luar (root), lalu isi dengan konfigurasi berikut. Sesuaikan password database dengan settingan laptop masing-masing.

**Isi file `.env`:**

```ini
# Ganti 'password' dengan password database MySQL lokal kalian
DATABASE_URL=[URL yang dishare digrup]

# Key untuk keamanan login (Jangan disebar sembarangan)
JWT_SECRET_KEY=[Kode yang dishare digrup]
```

> ⚠️ **PENTING:** Jangan pernah push file `.env` ini ke GitHub\! Pastikan file ini sudah ada di dalam `.gitignore`.

```bash
# 5. Setup Database & Admin
# Import file .sql dari folder database/ jika diperlukan,
# lalu jalankan script ini untuk membuat user admin awal:
python seed_admin.py
```

### 2\. Menjalankan Server API

Pastikan server menyala agar tim Frontend bisa menarik data.

```bash
python main.py
```

Server berjalan di: `http://localhost:8000`

### 3\. Testing API

Sebelum push, pastikan tidak ada error logic:

```bash
python test_api.py
```

-----

## 🎨 Panduan Frontend (HTML, CSS, JS)

Bagian ini khusus untuk tim yang mengembangkan antarmuka pengguna. Kita menggunakan **Vanilla JS** (Tanpa Framework).

### 1\. Struktur Folder Frontend

Harap patuhi struktur ini di dalam folder `frontend/` agar kode rapi:

```text
frontend/
├── index.html           # Halaman Utama
├── pages/               # Halaman lain (Login, Dashboard, dll)
└── assets/
    ├── css/
    │   ├── style.css    # Style utama
    │   └── responsive.css
    ├── js/
    │   ├── api.js       # KONFIGURASI API (Penting!)
    │   └── main.js      # Logic DOM Manipulation
    └── images/
```

### 2\. Tools & Cara Jalanin

Karena kita butuh koneksi ke API, jangan buka file HTML langsung (double click).

1.  **Install:** Extension **"Live Server"** di VS Code.
2.  **Run:** Buka `index.html` -\> Klik kanan -\> **Open with Live Server**.
3.  **Syarat:** Pastikan teman Backend sudah menjalankan `python main.py` agar data muncul.

### 3\. Integrasi API (Standardisasi)

Untuk menghindari kode yang berantakan, **JANGAN** hardcode URL di setiap file. Gunakan pola `api.js` berikut.

**Buat file `assets/js/api.js`:**

```javascript
const BASE_URL = "http://localhost:8000"; // Sesuaikan port backend

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${BASE_URL}/${endpoint}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("API Error:", error);
    }
}
```

**Cara pakai di file JS lain (misal `main.js`):**

```javascript
// Pastikan api.js di-load duluan di HTML
// <script src="assets/js/api.js"></script>
// <script src="assets/js/main.js"></script>

document.addEventListener("DOMContentLoaded", async () => {
    // Tinggal panggil fungsinya
    const dataTupoksi = await fetchData("tupoksi");
    console.log(dataTupoksi);
});
```

### 4\. Styling Guidelines

  * Gunakan class naming *kebab-case* (contoh: `.btn-submit`, `.card-profile`).
  * Gunakan CSS Reset di baris pertama `style.css`.

-----

## 🤝 Workflow Tim (Git Flow)

Aturan main untuk semua developer (Backend & Frontend):

1.  **Dilarang Push ke `main`:** Branch `main` harus selalu bersih dan stabil.
2.  **Gunakan Branch Fitur:**
      * Backend: `be/nama-fitur` (contoh: `be/auth-login`)
      * Frontend: `fe/nama-halaman` (contoh: `fe/halaman-dashboard`)
3.  **Pull Request:** Jika fitur selesai, push ke branch masing-masing dan buat Pull Request di GitHub untuk di-review.

-----

**Happy Coding, Team\! 🚀**
Jika ada kendala koneksi antara Frontend dan Backend, segera diskusikan di grup.

```
```
