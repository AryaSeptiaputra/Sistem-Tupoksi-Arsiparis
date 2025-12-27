# 🚀 QUICK START - Sistem Tupoksi Arsiparis

Panduan cepat untuk menjalankan aplikasi.

---

## ⚡ 3 Langkah Setup (5 menit)

### 1️⃣ Setup Awal
```bash
scripts\setup.bat
```
✅ Membuat virtual environment  
✅ Install dependencies  
✅ Setup database (optional seed data)

### 2️⃣ Konfigurasi Environment
Buat file `.env` dari `.env.example`:
```
DATABASE_URL=mysql+pymysql://user:password@localhost/db
SECRET_KEY=your-secret-key-here
DEBUG=False
FLASK_PORT=8000
```

### 3️⃣ Jalankan Aplikasi
```bash
# Manual run (untuk testing)
scripts\run.bat

# Atau install sebagai Windows Service
scripts\install_service.bat
```

---

## 📁 Folder Structure

```
scripts/              ← Deployment scripts
├── setup.bat        ← Run first
├── run.bat          ← Run manually
└── install_service.bat  ← Register service

config/              ← Configuration files
├── .env            ← Environment variables
└── settings.py

docs/               ← Documentation
├── INSTALLATION.md
├── SERVICE_MANAGEMENT.md
└── OPTIMIZATION_README.md

database/           ← Database seeders
└── seeders/
    ├── seed_master.py
    └── seed_admin.py

logs/               ← Application logs
```

---

## 🎯 Akses Aplikasi

### Development
```
http://127.0.0.1:5000
```

### Production (Manual)
```
http://127.0.0.1:8000
```

### Production (Service)
```
http://127.0.0.1:8000
```

### Via Domain (Reverse Proxy)
```
http://yourdomain.com
https://yourdomain.com
```

---

## 📋 Service Commands

```bash
# Check status
scripts\service_status.bat

# Restart service
scripts\restart_service.bat

# Remove service
scripts\uninstall_service.bat
```

---

## 🔍 View Logs

```
Manual run:     logs/app.log
Service output: logs/service_output.log
Service errors: logs/service_error.log
```

---

## 📚 Full Documentation

| Document | Purpose |
|----------|---------|
| **INSTALLATION.md** | Detailed Windows setup |
| **REVERSE_PROXY_SETUP.md** | Domain + HTTPS setup |
| **SERVICE_MANAGEMENT.md** | Service management guide |
| **OPTIMIZATION_README.md** | Performance optimization |
| **FOLDER_STRUCTURE.md** | Complete folder layout |

---

## ✅ Checklist

- [ ] Run `scripts\setup.bat`
- [ ] Create `.env` file
- [ ] Configure database in `.env`
- [ ] Test with `scripts\run.bat`
- [ ] Install service: `scripts\install_service.bat`
- [ ] Check status: `scripts\service_status.bat`
- [ ] Access http://127.0.0.1:8000
- [ ] Setup reverse proxy (optional)

---

## 🆘 Troubleshooting

### Script won't run?
→ Make sure to run as Administrator

### Service won't start?
→ Check `logs/service_error.log` for errors

### Database connection error?
→ Verify DATABASE_URL in `.env`

### Port already in use?
→ Change FLASK_PORT in `.env`

---

**Next:** Read `docs/INSTALLATION.md` for detailed setup instructions.

Happy coding! 🎉
