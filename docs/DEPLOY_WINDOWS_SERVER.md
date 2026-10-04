# Panduan Deploy di Windows Server

Panduan singkat memasang aplikasi ini di server Windows (LAN maupun internet) menggunakan waitress + NSSM.

## Prasyarat
- Windows Server/Windows 10+ dengan akses Administrator.
- Python 3.x terpasang dan ada di PATH.
- MySQL server dapat diakses (lokal atau remote) dan kredensial siap.
- Port backend default 8000 bebas (atau siapkan port lain).
- File nssm.exe (unduh dari https://nssm.cc/download, pilih win64 untuk OS 64-bit).
- Kode aplikasi sudah disalin ke server (folder project lengkap).

## Langkah Instalasi
1) Salin NSSM
   - Ekstrak ZIP NSSM, ambil nssm.exe dari win64/.
   - Taruh nssm.exe di root folder project (sejajar dengan scripts/).

2) Siapkan .env (di root project)
   - Duplikasi .env.example jika ada, atau buat manual:
```
DATABASE_URL=mysql+pymysql://user:password@host:3306/nama_db
JWT_SECRET_KEY=isi_jwt_secret
SECRET_KEY=isi_flask_secret
FLASK_ENV=production
FLASK_DEBUG=0
PORT=8000
LOG_FILE_PATH=%cd%\logs\production.log
```
   - Sesuaikan host DB, nama DB, password, dan port jika tidak memakai 8000.

3) Jalankan setup
   - PowerShell (boleh non-admin):
```
cd "C:\Kuliah\Semester 7\Informatika Terapan\Sistem Tupoksi Arsiparis"
.\scripts\setup.bat
```
   - Script membuat .venv, install dependencies, membuat folder storage/logs, dan menawarkan seeding master/admin.

4) Install sebagai service (Admin)
   - Klik kanan scripts/install_service.bat -> Run as administrator.
   - Service ArsipSMKN7 dibuat, startup otomatis, restart-on-failure, log ke logs/service_output.log dan logs/service_error.log.
   - Listener waitress di 0.0.0.0:8000 (ubah port di .env + script jika perlu, lalu reinstall service).

5) Buka firewall
   - Untuk akses LAN langsung ke backend: buka inbound TCP port 8000.
   - Untuk akses internet: lebih aman hanya buka port 443 dan pakai reverse proxy (lihat di bawah).

6) Reverse proxy (disarankan untuk internet)
   - Pasang Nginx/IIS/Apache di server.
   - Terminate HTTPS di reverse proxy, lalu proxy ke http://127.0.0.1:8000.
   - Lihat docs/REVERSE_PROXY_SETUP.md untuk contoh konfigurasi.

## Operasi & Pemeliharaan
- Cek status service: scripts/service_status.bat
- Restart service (setelah update code/.env): scripts/restart_service.bat (Admin)
- Hapus service: scripts/uninstall_service.bat (Admin)
- Log: logs/service_output.log (stdout), logs/service_error.log (stderr)
- Update aplikasi:
  1) Stop service (restart_service.bat akan stop/start otomatis), atau nssm stop ArsipSMKN7.
  2) Tarik perubahan (git/paste).
  3) Install deps baru jika ada: .venv\Scripts\pip install -r requirements.txt
  4) Restart service.

## Uji Akses
- Lokal/LAN: http://<IP-server>:8000
- Lewat reverse proxy: https://<domain> (periksa sertifikat valid dan respon aplikasi)

## Catatan Keamanan
- Jangan expose port 8000 langsung ke internet tanpa TLS.
- Batasi akses DB hanya dari host yang diperlukan.
- Putar log jika ukuran membesar (saat ini belum otomatis).
- Simpan file .env dengan izin terbatas.

## Referensi
- Manajemen service: docs/SERVICE_MANAGEMENT.md
- Reverse proxy: docs/REVERSE_PROXY_SETUP.md
