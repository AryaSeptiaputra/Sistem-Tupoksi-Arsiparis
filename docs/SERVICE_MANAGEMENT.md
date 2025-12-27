# Service Management Scripts - NSSM Helper

File-file batch untuk manajemen Windows Service dengan NSSM.

## 📁 File yang Tersedia

- **install_service.bat** - Install aplikasi sebagai Windows Service
- **uninstall_service.bat** - Hapus service dari sistem
- **restart_service.bat** - Restart service
- **service_status.bat** - Cek status service

## 🚀 Cara Penggunaan

### 1. Download NSSM

Sebelum menggunakan script ini, download NSSM terlebih dahulu:

1. Kunjungi: https://nssm.cc/download
2. Download versi terbaru (zip)
3. Ekstrak file zip
4. Copy `nssm.exe` dari folder `win64` ke root folder aplikasi ini (sejajar dengan install_service.bat)

### 2. Install Service

**Klik kanan** → **Run as administrator** pada:
```
install_service.bat
```

Script akan:
- ✅ Cek prerequisite (NSSM, Python, Waitress)
- ✅ Install service dengan nama "ArsipSMKN7"
- ✅ Set auto-start on boot
- ✅ Konfigurasi restart on failure
- ✅ Set log output ke `logs/`
- ✅ Start service otomatis

**Setelah selesai, service akan running dan auto-start setiap boot Windows.**

### 3. Cek Status Service

```
service_status.bat
```

Tidak perlu administrator. Akan menampilkan status service (RUNNING/STOPPED).

### 4. Restart Service

**Klik kanan** → **Run as administrator** pada:
```
restart_service.bat
```

Berguna setelah:
- Update code
- Edit `.env`
- Install dependencies baru

### 5. Uninstall Service

**Klik kanan** → **Run as administrator** pada:
```
uninstall_service.bat
```

Hapus service dari sistem (aplikasi tetap bisa dijalankan manual dengan `run.bat`).

## 🔧 Manual Command (Alternatif)

Jika ingin gunakan command manual:

```powershell
# Install (PowerShell Admin)
.\nssm.exe install ArsipSMKN7 "C:\path\.venv\Scripts\waitress-serve.exe" --host=127.0.0.1 --port=8000 serve:app
.\nssm.exe set ArsipSMKN7 AppDirectory "C:\path\to\app"
.\nssm.exe set ArsipSMKN7 Start SERVICE_AUTO_START
.\nssm.exe start ArsipSMKN7

# Status
.\nssm.exe status ArsipSMKN7

# Restart
.\nssm.exe restart ArsipSMKN7

# Stop
.\nssm.exe stop ArsipSMKN7

# Uninstall
.\nssm.exe remove ArsipSMKN7 confirm
```

## 📋 Konfigurasi Service

### Nama Service
```
ArsipSMKN7
```

### Display Name
```
Arsip SMKN 7
```

### Description
```
Sistem Arsip SMKN 7 Bandung - Production Server
```

### Command Line
```
waitress-serve.exe --host=127.0.0.1 --port=8000 serve:app
```

### Working Directory
```
C:\path\to\aplikasi
```

### Startup Type
```
Automatic
```

### Restart on Failure
```
Yes (delay 5 seconds)
```

### Log Files
```
logs/service_output.log  (stdout)
logs/service_error.log   (stderr)
```

## 🔍 Troubleshooting

### Service tidak mau start

1. Cek log error:
   ```
   logs\service_error.log
   ```

2. Pastikan `.env` sudah diisi dengan benar

3. Test manual dulu:
   ```cmd
   .venv\Scripts\activate
   waitress-serve --host=127.0.0.1 --port=8000 serve:app
   ```

4. Jika manual jalan tapi service tidak, reinstall:
   ```
   uninstall_service.bat
   install_service.bat
   ```

### Port sudah digunakan

Edit `.env`:
```env
PORT=8001
```

Lalu restart service.

### Service hilang setelah update Windows

Reinstall service:
```
install_service.bat
```

### Ingin ganti port atau konfigurasi

1. Uninstall service dulu
2. Edit `.env` atau script
3. Install ulang service

## 🎯 Keuntungan Menggunakan Service

✅ **Auto-start**: Otomatis jalan saat Windows boot  
✅ **Auto-restart**: Restart otomatis jika crash  
✅ **Background**: Jalan di background tanpa terminal  
✅ **Isolasi**: Tidak terpengaruh user logout  
✅ **Management**: Mudah kontrol lewat Services.msc  

## 📞 Verifikasi Service

### Via Services.msc
1. Tekan `Win+R`
2. Ketik `services.msc`
3. Enter
4. Cari "Arsip SMKN 7"
5. Status harus "Running"

### Via Browser
Buka: http://127.0.0.1:8000

### Via Command
```cmd
netstat -an | findstr :8000
```
Harus ada: `127.0.0.1:8000 LISTENING`

## ⚠️ Penting

- **Semua operasi service butuh Administrator privileges**
- **Backup dulu sebelum uninstall** (data aman, tapi config service hilang)
- **Log dirotasi manual** (belum otomatis, cek size berkala)
- **Port default 8000** (loopback only untuk keamanan)
- **Gunakan reverse proxy** (IIS/Nginx) untuk akses publik

## 📚 Referensi

- NSSM Documentation: https://nssm.cc/usage
- Waitress: https://docs.pylonsproject.org/projects/waitress/
- Reverse Proxy Guide: [docs/REVERSE_PROXY_SETUP.md](REVERSE_PROXY_SETUP.md)
