# Tech Stack — Sistem Tupoksi Arsiparis

Dokumentasi teknologi yang digunakan pada project **Sistem Tupoksi Arsiparis** (aplikasi pengelolaan arsip SMKN 7 Bandung).

---

## Bahasa & Runtime

| Komponen | Teknologi | Versi |
|----------|-----------|-------|
| Bahasa Backend | Python | 3.11 |
| Bahasa Frontend | HTML, CSS, JavaScript (vanilla) | — |

---

## Backend

| Kategori | Teknologi | Versi | Keterangan |
|----------|-----------|-------|------------|
| Web Framework | **Flask** | 3.1.2 | Framework utama (struktur Blueprint) |
| Templating | **Jinja2** | 3.1.6 | Render halaman HTML |
| ORM | **SQLAlchemy** | 2.0.44 | Object Relational Mapping |
| Migrasi DB | **Flask-Migrate** / Alembic | 4.1.0 / 1.17.1 | Version control skema database |
| Integrasi DB | **Flask-SQLAlchemy** | 3.1.1 | Integrasi SQLAlchemy ke Flask |
| Validasi & Config | **Pydantic** / **pydantic-settings** | 2.12.4 / 2.12.0 | Validasi data & manajemen konfigurasi `.env` |
| Authentication | **Flask-JWT-Extended** / **PyJWT** | 4.7.1 / 2.10.1 | Autentikasi berbasis JWT (token expire 12 jam) |
| Password Hashing | **bcrypt**, **argon2-cffi**, **passlib** | 4.1.2 / 25.1.0 / 1.7.4 | Hashing & enkripsi password |
| Kriptografi | **cryptography** | 46.0.3 | Operasi enkripsi |
| CORS | **flask-cors** | 6.0.1 | Cross-Origin Resource Sharing |
| Kompresi | **Flask-Compress** (gzip/brotli) | 1.23 | Kompresi response (level 6, min 1KB) |
| Scheduler | **APScheduler** | 3.11.1 | Job terjadwal (retensi arsip otomatis harian 00:01 WIB) |
| HTTP Client | **requests** | 2.32.5 | Permintaan HTTP |
| System Monitoring | **psutil** | 6.1.0 | Informasi sumber daya sistem |

---

## Database

| Komponen | Teknologi | Versi | Keterangan |
|----------|-----------|-------|------------|
| RDBMS | **MySQL** | — | Database utama (production) |
| Driver | **PyMySQL** | 1.1.2 | Driver MySQL berbasis Python murni |
| Driver | **mysqlclient** | 2.2.7 | Driver MySQL native (C) |
| Connection String | `mysql+pymysql://...` | — | Charset `utf8mb4`, QueuePool (pool_size 20, max_overflow 10, pool_recycle 3600) |
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
| Kontainerisasi | **Docker** | — | `python:3.11-slim`, expose port 8080 |
| Reverse Proxy | IIS / Nginx | — | Untuk akses domain (lihat `docs/REVERSE_PROXY_SETUP.md`) |

---

## Testing & Tooling

| Kategori | Teknologi | Versi |
|----------|-----------|-------|
| Unit Testing | **pytest** | 8.3.3 |
| Coverage | **pytest-cov** / **coverage** | 5.0.0 / 7.13.0 |
| Environment Config | **python-dotenv** | 1.2.1 |
| Version Control | **Git** | — |

---

## Arsitektur Aplikasi

- **Pola:** Application Factory (`create_app()`) dengan registrasi **Blueprint** per modul.
- **Struktur layer:** `routes/` (controller) → `services/` (business logic) → `models/` (ORM) → `core/` (config & database).
- **Modul fungsional:** auth, user, classification, incoming/outgoing letter, diploma, log, backup, storage location, finance archive, employee archive, disposal, teacher, master reference.
- **Keamanan:** JWT, session cookie (HttpOnly, SameSite=Lax), password hashing (bcrypt/argon2).
- **Logging:** File-based logging (`logs/app.log`) + console.
- **Error handling:** Custom handler untuk HTTP 404 & 500.
