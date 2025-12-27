# Struktur Folder - Sistem Arsip SMKN 7 Bandung

```
Sistem Tupoksi Arsiparis/
│
├── 📄 Root Files (Essential Only)
│   ├── README.md                    # Dokumentasi utama
│   ├── requirements.txt             # Python dependencies
│   ├── .gitignore                   # Git configuration
│   ├── .env.example                 # Environment template
│   └── .env                         # Environment (local, don't commit)
│
├── 📂 app/                          # Source code aplikasi
│   ├── __init__.py
│   ├── main.py                      # Entry point (bisa pindah ke serve.py)
│   ├── routes/
│   ├── models/
│   ├── utils/
│   └── ...
│
├── 📂 serve.py                      # Waitress entry point (di root level ok)
│
├── 📂 scripts/                      # Helper scripts untuk deployment
│   ├── setup.bat                    # Setup aplikasi
│   ├── run.bat                      # Jalankan aplikasi
│   ├── install_service.bat          # Install Windows service
│   ├── uninstall_service.bat        # Uninstall service
│   ├── restart_service.bat          # Restart service
│   └── service_status.bat           # Check service status
│
├── 📂 config/                       # Konfigurasi aplikasi
│   ├── production.py                # Config produksi
│   ├── development.py               # Config development
│   └── testing.py                   # Config testing
│
├── 📂 docs/                         # Dokumentasi lengkap
│   ├── INSTALLATION.md              # Panduan instalasi
│   ├── REVERSE_PROXY_SETUP.md       # Setup domain & SSL
│   ├── SERVICE_MANAGEMENT.md        # Manajemen service NSSM
│   ├── API_DOCUMENTATION.md         # API docs
│   └── TROUBLESHOOTING.md           # FAQ & troubleshooting
│
├── 📂 assets/                       # Static files (CSS, JS, images)
│   ├── css/                         # Stylesheet
│   ├── js/                          # JavaScript
│   ├── img/                         # Images
│   └── html/                        # HTML templates (atau pindah ke app/templates)
│
├── 📂 database/                     # Database migrations & seeds
│   ├── migrations/                  # (Opsional) Alembic migrations
│   └── seeders/                     # Seed data scripts (bisa pindah sini)
│
├── 📂 storage/                      # Runtime data
│   ├── documents/
│   ├── uploads/
│   └── backups/
│
├── 📂 logs/                         # Application logs
│   ├── production.log               # Production log
│   ├── service_output.log           # Service stdout
│   └── service_error.log            # Service stderr
│
├── 📂 tests/                        # Unit & integration tests
│   ├── test_*.py
│   └── conftest.py
│
├── 📂 .github/                      # GitHub config
│   └── workflows/                   # CI/CD pipelines
│
├── 📂 .venv/                        # Python virtual environment (don't commit)
│
└── 📂 __pycache__/                  # Cache (don't commit)
```

---

## 📋 Perubahan Struktur

### Sebelum (Berantakan):
```
- INSTALLATION.md
- OPTIMIZATION_*.md
- setup.bat
- run.bat
- install_service.bat
- install_optimizations.bat
- main.py
- serve.py
```

### Sesudah (Terorganisir):
```
scripts/
├── setup.bat
├── run.bat
├── install_service.bat
└── ...

docs/
├── INSTALLATION.md
├── OPTIMIZATION_*.md
└── ...

app/
├── main.py
└── ...
```

---

## 🔄 Rencana Reorganisasi

1. **Folder `scripts/`**
   - `setup.bat` ← dari root
   - `run.bat` ← dari root
   - `install_service.bat` ← dari root
   - `uninstall_service.bat` ← dari root
   - `restart_service.bat` ← dari root
   - `service_status.bat` ← dari root

2. **Folder `docs/`** (expand)
   - `INSTALLATION.md` ← dari root
   - `REVERSE_PROXY_SETUP.md` ← sudah ada di sini
   - `SERVICE_MANAGEMENT.md` ← sudah ada di sini
   - `OPTIMIZATION_*.md` ← dari root
   - Buat: `TROUBLESHOOTING.md`
   - Buat: `API_DOCUMENTATION.md`

3. **Folder `database/`** (rename dari `seeders/`)
   - `seeders/` → `database/seeders/`
   - Tambah: `database/migrations/`

4. **Update wrapper scripts di root**
   - Buat symbolic link atau wrapper yang memanggil scripts dari folder `scripts/`
   - Atau buat shortcut `.bat` di root yang call ke `scripts/`

---

## ✅ Keuntungan Struktur Baru

✅ **Rapi & Profesional** - Mudah navigasi & maintain  
✅ **Scalable** - Mudah tambah fitur tanpa clutter  
✅ **Follow Convention** - Standard Python project structure  
✅ **Deploy-friendly** - Jelas mana script, mana source code, mana docs  
✅ **CI/CD Ready** - Pipeline lebih jelas strukturnya  

---

## 🔧 Langkah Implementasi

1. Buat folder baru (`scripts/`, `config/`, expand `docs/`, `database/`)
2. Pindah file ke folder yang sesuai
3. Update path di `.bat` files & Python code
4. Test berjalan dengan baik
5. Update `.gitignore` jika perlu
6. Commit ke Git

**Estimasi waktu:** 15-30 menit (semua otomatis dengan script)

Mau saya lanjutkan implementasi? Saya bisa:
- Buat folder structure
- Pindah file (copy, jangan delete)
- Update path references
- Test semuanya
