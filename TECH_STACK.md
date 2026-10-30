# Tech Stack — Sistem Tupoksi Arsiparis

Dokumentasi teknologi yang digunakan pada project **Sistem Tupoksi Arsiparis** (aplikasi pengelolaan arsip SMKN 7 Bandung).

---

## Bahasa & Runtime

| Komponen | Teknologi | Versi |
|----------|-----------|-------|
| Bahasa Backend | Python | 3.8 (target Windows 7) |
| Bahasa Frontend | HTML, CSS, JavaScript (vanilla) | — |

---

## Backend

| Kategori | Teknologi | Versi | Keterangan |
|----------|-----------|-------|------------|
| Web Framework | **Flask** | 3.0.3 | Framework utama (struktur Blueprint) |
| Templating | **Jinja2** | 3.1.6 | Render halaman HTML |
| ORM | **SQLAlchemy** | 2.0.44 | Object Relational Mapping |
| Validasi & Config | **Pydantic** / **pydantic-settings** | 2.10.6 / 2.8.1 | Validasi data & manajemen konfigurasi `.env` |
| Authentication | **Flask-JWT-Extended** / **PyJWT** | 4.6.0 / 2.9.0 | Autentikasi berbasis JWT (token expire 12 jam) |
| Password Hashing | **argon2-cffi**, **passlib** | 25.1.0 / 1.7.4 | Hashing password (argon2) |
| CORS | **flask-cors** | 5.0.0 | Cross-Origin Resource Sharing |
| Kompresi | **Flask-Compress** (gzip/brotli) | 1.15 | Kompresi response (level 6, min 1KB) |
| Scheduler | **APScheduler** | 3.11.1 | Job terjadwal (retensi arsip otomatis harian 00:01 WIB) |

---

## Database

| Komponen | Teknologi | Versi | Keterangan |
|----------|-----------|-------|------------|
| RDBMS | **SQLite** | bawaan Python | Database utama, satu file tanpa server database |
| Connection String | `sqlite:///database/arsip.db` | — | NullPool; PRAGMA foreign_keys, WAL, busy_timeout 5000 ms |
| Fallback | **SQLite** | — | Didukung via NullPool untuk development |

---

## Frontend

| Kategori | Teknologi | Keterangan |
|----------|-----------|------------|
| Markup | HTML5 | Template di `app/static/html/` (di-render Jinja2) |
| Styling | CSS3 | CSS modular per-halaman + variabel (`variabels.css`, `layout.css`, `components.css`) |
| Scripting | JavaScript (Vanilla) | Tanpa framework; `api.js` sebagai layer komunikasi REST API |
| Arsitektur | SPA-like / Multi-page | Komunikasi backend via fetch ke endpoint REST |

---

## Server & Deployment

| Kategori | Teknologi | Versi | Keterangan |
|----------|-----------|-------|------------|
| WSGI Server | **Waitress** | 3.0.2 | Production server (`serve.py`, port default 6001/8080, 12 threads) |
| Dev Server | **Werkzeug** | 3.1.3 | Development server bawaan Flask |
| Kontainerisasi | **Docker** | — | `python:3.8-slim`, expose port 8080 |
| Reverse Proxy | IIS / Nginx | — | Untuk akses domain (lihat `docs/REVERSE_PROXY_SETUP.md`) |

---

## Testing & Tooling

| Kategori | Teknologi | Versi |
|----------|-----------|-------|
| Unit Testing | **pytest** (`requirements-dev.txt`) | 8.3.5 |
| Coverage | **pytest-cov** / **coverage** | 5.0.0 / 7.6.1 |
| End-to-end Testing | **Selenium** + Chrome (`requirements-dev.txt`, folder `e2e/`) | 4.27.1 |
| Environment Config | **python-dotenv** | 1.2.1 |
| Version Control | **Git** | — |

---

## Arsitektur Aplikasi

- **Pola:** Application Factory (`create_app()`) dengan registrasi **Blueprint** per modul.
- **Struktur layer:** `routes/` (controller) → `services/` (business logic) → `models/` (ORM) → `core/` (config & database).
- **Modul fungsional:** auth, user, classification, incoming/outgoing letter, diploma, log, backup, storage location, finance archive, employee archive, disposal, teacher, master reference.
- **Keamanan:** JWT, session cookie (HttpOnly, SameSite=Lax), password hashing (argon2).
- **Logging:** File-based logging (`logs/app.log`) + console.
- **Error handling:** Custom handler untuk HTTP 404 & 500.
