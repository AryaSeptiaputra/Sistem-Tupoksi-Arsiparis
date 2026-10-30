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

Aplikasi menargetkan **Python 3.8** agar bisa dipasang di Windows 7, dan memakai **SQLite** (satu file, tanpa server database).

```bash
# 1. Clone & masuk direktori
git clone https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis.git
cd Sistem-Tupoksi-Arsiparis

# 2. Virtual environment dengan Python 3.8
#    Di mesin pengembangan bisa lewat uv: uv python install 3.8 && uv venv .venv --python 3.8
python -m venv .venv
.venv\Scriptsctivate

# 3. Install dependency (versi dikunci untuk Python 3.8)
#    requirements.txt untuk production; requirements-dev.txt menambah pytest
pip install -r requirements-dev.txt
```

Salin `.env.example` menjadi `.env`, lalu isi `JWT_SECRET_KEY` dan `SECRET_KEY` dengan nilai acak milik sendiri. `DATABASE_URL` default-nya `sqlite:///database/arsip.db`.

> ⚠️ **PENTING:** Jangan pernah push file `.env` ke GitHub dan jangan menulis nilai rahasia di dokumen mana pun.

```bash
# 4. Data awal dan akun operator
python database/seeders/seed_master.py
python scripts/akun.py buat --username <nip> --nama "<nama operator>"

# Atau, bila memindahkan data dari MySQL lama:
python scripts/migrate_mysql_to_sqlite.py --source "mysql+pymysql://user:sandi@localhost/nama_db"
```

Dependency diubah lewat `requirements.in` (aplikasi) atau `requirements-dev.in` (test), lalu kunci ulang untuk Python 3.8:

```bash
uv pip compile requirements.in --python-version 3.8 -o requirements.txt
uv pip compile requirements-dev.in --python-version 3.8 -o requirements-dev.txt
```

Bila memindahkan data dari MySQL lama, pasang driver-nya sementara: `pip install PyMySQL==1.1.2`.

### 2\. Menjalankan Server API

```bash
python main.py
```

### 3\. Testing

```bash
pytest tests
```

Test end-to-end lewat Chrome (Selenium). Server uji dan database sementara dibuat otomatis, jadi `.env` dan data project tidak tersentuh:

```bash
pytest e2e -v
```

Hasil per skenario ditulis ke `e2e/hasil/hasil.md`. Kalau ChromeDriver gagal diunduh otomatis, isi env `E2E_CHROMEDRIVER` dengan path `chromedriver.exe` yang versinya sama dengan Chrome.

### 4\. Instalasi di Windows 7 (laptop klien / PC sekolah)

1. Windows 7 **SP1** dengan update **KB2533623** sudah terpasang.
2. Pasang Python **3.8.10** dari installer resmi python.org (versi 3.8 terakhir yang punya installer Windows); centang *Add Python to PATH*.
3. Jalankan `scripts\setup.bat`, isi `.env`, lalu `scripts\install_service.bat` sebagai Administrator.
4. Python 3.8 dan Windows 7 sudah tidak mendapat patch keamanan: buka aplikasi hanya di jaringan lokal, jangan ke internet.

Checklist uji di device target: login, dashboard tampil dengan grafik, tambah/ubah/hapus surat, unggah lampiran, backup lalu restore.

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

## 🔧 Production Deployment & Sustainability

### Environment Setup
- Copy `.env.example` to `.env` and fill in the actual values.
- Use virtual environment: `python -m venv venv` and `venv\Scripts\activate` (Windows).

### Running in Production
- For development: `python main.py`
- For production: `python serve.py` (uses Waitress WSGI server)

### Docker
- Build: `docker build -t arsiparis-app .`
- Run: `docker run -p 8080:8080 arsiparis-app`

### Testing
- Run tests: `pytest tests`
- End-to-end (Chrome + Selenium): `pytest e2e -v`, hasil di `e2e/hasil/hasil.md`

### Logging
- Logs are configured to console and optionally to file specified in `.env`.

### CI/CD
- GitHub Actions runs tests on push/PR to main.

-----

**Happy Coding, Team\! 🚀**
Jika ada kendala koneksi antara Frontend dan Backend, segera diskusikan di grup.
