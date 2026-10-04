# Troubleshooting Windows Service

## Masalah: Service Status PAUSED

### Penyebab Umum:
1. **Unicode/Emoji Error** - Windows Service tidak support karakter Unicode
2. **Port sudah digunakan** - Port 8000 dipakai aplikasi lain
3. **Permission Error** - Service tidak punya akses ke folder/database
4. **Missing Dependencies** - Library Python belum terinstall

## Solusi Step-by-Step:

### 1. Fix Unicode Error (Sudah diperbaiki)
```
✅ Semua emoji di kode sudah diganti dengan ASCII
✅ Environment variable PYTHONIOENCODING=utf-8 sudah ditambahkan
```

### 2. Uninstall Service yang Bermasalah
```cmd
# Jalankan sebagai Administrator
cd scripts
fix_service.bat
```

### 3. Cek Port yang Digunakan
```powershell
# Cek apakah port 8000 digunakan
netstat -ano | findstr :8000

# Jika ada, matikan aplikasi atau ganti port di .env:
# PORT=8001
```

### 4. Install Ulang Service
```cmd
# Jalankan sebagai Administrator
cd scripts
install_service.bat
```

### 5. Verifikasi Service
```powershell
# Cek status
Get-Service ArsipSMKN7

# Cek log error
Get-Content logs\service_error.log -Tail 50
```

## Perintah Berguna:

### Kontrol Service
```cmd
# Start
nssm start ArsipSMKN7

# Stop
nssm stop ArsipSMKN7

# Restart
nssm restart ArsipSMKN7

# Status
nssm status ArsipSMKN7
```

### Cek Log
```cmd
# Output log
type logs\service_output.log

# Error log
type logs\service_error.log
```

### Konfigurasi Service
```cmd
# Edit konfigurasi via GUI
nssm edit ArsipSMKN7

# Lihat semua setting
nssm dump ArsipSMKN7
```

## Troubleshooting Lanjutan:

### Jika Port Conflict:
1. Edit `.env`:
   ```
   PORT=8001
   ```
2. Uninstall dan install ulang service

### Jika Database Error:
1. Pastikan MySQL berjalan:
   ```powershell
   Get-Service MySQL* | Start-Service
   ```
2. Test koneksi database:
   ```cmd
   .venv\Scripts\activate
   python -c "from app import db; print('DB OK')"
   ```

### Jika Permission Error:
1. Beri akses folder ke SYSTEM account:
   ```cmd
   icacls "%CD%" /grant:r "NT AUTHORITY\SYSTEM:(OI)(CI)F" /T
   ```

## Test Manual Sebelum Service:

Pastikan aplikasi jalan normal dulu:
```cmd
.venv\Scripts\activate
python serve.py
```

Akses http://127.0.0.1:8000 - jika OK, baru install service.

## Contact:
Jika masih bermasalah, screenshot error dan tanyakan ke dosen pembimbing.
