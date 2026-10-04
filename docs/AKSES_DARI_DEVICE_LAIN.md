# Cara Mengakses dari Device Lain

## Langkah 1: Buka Firewall Windows

Jalankan **sebagai Administrator**:
```
scripts\allow_firewall.bat
```

Script ini akan membuka port 6001 (production) dan 5000 (development) di Windows Firewall.

## Langkah 2: Cek IP Komputer Server

Di komputer yang menjalankan aplikasi, buka PowerShell/CMD dan jalankan:
```
ipconfig
```

Cari **IPv4 Address** pada adapter yang aktif (biasanya Ethernet atau Wi-Fi).
Contoh: `192.168.1.100`

## Langkah 3: Jalankan Server

```
scripts\run.bat
```

Atau jika sudah install sebagai service:
```
scripts\restart_service.bat
```

## Langkah 4: Akses dari Device Lain

Dari device lain di jaringan yang sama:

1. Buka browser (Chrome, Firefox, Edge, dll)
2. Ketik alamat: `http://[IP-komputer-server]:6001`
3. Contoh: `http://192.168.1.100:6001`

### Login Default

- **Username:** Nomor identitas guru admin (NIP: `19880101001`)
- **Password:** `admin123`

## Mode Development

Jika menggunakan mode development (main.py):
- Port: **5000**
- URL: `http://[IP-komputer-server]:5000`

## Troubleshooting

### Tidak bisa akses dari device lain

1. **Cek firewall:**
   ```
   netsh advfirewall firewall show rule name="Sistem Tupoksi Arsiparis - Port 6001"
   ```

2. **Cek apakah server berjalan:**
   ```
   netstat -an | findstr :6001
   ```
   Pastikan ada hasil yang muncul.

3. **Cek koneksi jaringan:**
   - Pastikan komputer server dan device lain terhubung ke **jaringan WiFi/LAN yang sama**
   - Ping dari device lain: `ping [IP-komputer-server]`

4. **Antivirus/Firewall pihak ketiga:**
   - Jika menggunakan antivirus selain Windows Defender, buka port 6001 di antivirus tersebut

### Akses dari Internet (bukan jaringan lokal)

Jika ingin akses dari internet, Anda perlu:
1. **Port forwarding** di router
2. **Dynamic DNS** jika IP publik berubah-ubah
3. **SSL/HTTPS** untuk keamanan

Untuk deployment production, lihat dokumentasi:
- `docs/DEPLOY_WINDOWS_SERVER.md`
- `docs/REVERSE_PROXY_SETUP.md`

## Catatan Keamanan

⚠️ **Penting:**
- Jangan gunakan di jaringan publik tanpa SSL/HTTPS
- Ganti password default setelah login pertama
- Untuk production, gunakan reverse proxy (IIS/Nginx)
- Batasi akses hanya untuk IP yang diizinkan jika perlu
