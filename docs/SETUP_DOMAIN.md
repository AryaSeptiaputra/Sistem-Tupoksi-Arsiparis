# Setup Domain Public untuk Sistem Tupoksi Arsiparis

Panduan untuk menggunakan domain public (contoh: `arsiparis.smkn7bdg.sch.id`)

## Prerequisites

1. **Domain** yang sudah dibeli/terdaftar
2. **IP Public** yang static atau Dynamic DNS
3. **SSL Certificate** (gunakan Let's Encrypt gratis)
4. **IIS** atau **Nginx** sebagai reverse proxy

---

## Opsi A: Menggunakan IIS (Windows Server)

### 1. Install IIS dengan URL Rewrite & ARR

```powershell
# Install IIS
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer
Enable-WindowsOptionalFeature -Online -FeatureName IIS-ManagementConsole

# Download & Install:
# - URL Rewrite: https://www.iis.net/downloads/microsoft/url-rewrite
# - Application Request Routing (ARR): https://www.iis.net/downloads/microsoft/application-request-routing
```

### 2. Setup Reverse Proxy di IIS

1. Buka **IIS Manager**
2. Klik server → **Application Request Routing Cache**
3. Klik **Server Proxy Settings**
4. Enable proxy ✓

5. Klik kanan **Sites** → **Add Website**
   - Site name: `Arsiparis`
   - Binding: Port **80**, Host name: `arsiparis.smkn7bdg.sch.id`
   - Physical path: `C:\inetpub\wwwroot\arsiparis` (buat folder kosong)

6. Klik site → **URL Rewrite** → **Add Rule** → **Reverse Proxy**
   - Inbound: `arsiparis.smkn7bdg.sch.id`
   - Rewrite URL: `http://localhost:6001/{R:1}`

### 3. Setup SSL dengan Let's Encrypt

```powershell
# Install win-acme
choco install win-acme

# Jalankan win-acme
wacs.exe

# Pilih opsi untuk IIS site
# Domain: arsiparis.smkn7bdg.sch.id
```

---

## Opsi B: Menggunakan Nginx (Lebih Ringan)

### 1. Install Nginx for Windows

Download dari: https://nginx.org/en/download.html

### 2. Konfigurasi Nginx

Edit `nginx/conf/nginx.conf`:

```nginx
http {
    # ... existing config ...

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name arsiparis.smkn7bdg.sch.id;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name arsiparis.smkn7bdg.sch.id;

        # SSL Certificate (gunakan certbot untuk Let's Encrypt)
        ssl_certificate     C:/nginx/ssl/arsiparis.crt;
        ssl_certificate_key C:/nginx/ssl/arsiparis.key;
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        # Reverse Proxy ke aplikasi
        location / {
            proxy_pass http://127.0.0.1:6001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support (jika perlu)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Upload limit
        client_max_body_size 100M;
    }
}
```

### 3. Start Nginx

```cmd
cd C:\nginx
start nginx.exe
```

---

## Setup DNS

### A. Jika Menggunakan IP Public Static

1. Login ke **DNS Provider** (Cloudflare/Namecheap/dll)
2. Tambah **A Record**:
   - Name: `arsiparis` (atau `@` untuk root domain)
   - Type: `A`
   - Value: `[IP-Public-Server]`
   - TTL: Auto

### B. Jika Menggunakan IP Dynamic

1. Daftar di **Dynamic DNS** (No-IP, DuckDNS, dll)
2. Install **DDNS Client** di server
3. Buat CNAME record di DNS provider Anda:
   - Name: `arsiparis`
   - Type: `CNAME`
   - Value: `your-subdomain.ddns.net`

---

## Port Forwarding di Router

Jika server berada di belakang router:

1. Login ke **Router** (biasanya 192.168.1.1)
2. Cari menu **Port Forwarding** / **Virtual Server**
3. Tambahkan rule:
   - External Port: `80` → Internal IP: `192.168.2.192`, Internal Port: `80`
   - External Port: `443` → Internal IP: `192.168.2.192`, Internal Port: `443`

---

## Update Konfigurasi Aplikasi

Agar aplikasi mengenali domain dengan baik:

### File `.env`

```env
# Domain configuration
APP_URL=https://arsiparis.smkn7bdg.sch.id
ALLOWED_HOSTS=arsiparis.smkn7bdg.sch.id,localhost,127.0.0.1

# SSL/TLS
FORCE_HTTPS=true
```

### File `serve.py`

Pastikan sudah menggunakan `0.0.0.0` dan port `6001`.

---

## Checklist Deployment

- [ ] Domain sudah mengarah ke IP server (cek dengan `nslookup`)
- [ ] Firewall port 80 dan 443 sudah dibuka
- [ ] Port forwarding di router sudah dikonfigurasi (jika perlu)
- [ ] SSL certificate sudah terinstall
- [ ] Reverse proxy (IIS/Nginx) sudah berjalan
- [ ] Aplikasi Flask berjalan di `localhost:6001`
- [ ] Test akses: `https://arsiparis.smkn7bdg.sch.id`

---

## Testing

### 1. Test DNS

```cmd
nslookup arsiparis.smkn7bdg.sch.id
```

Pastikan IP yang muncul sesuai dengan IP server.

### 2. Test HTTP/HTTPS

```cmd
curl -I http://arsiparis.smkn7bdg.sch.id
curl -I https://arsiparis.smkn7bdg.sch.id
```

### 3. Test dari Browser

Buka browser dan akses:
```
https://arsiparis.smkn7bdg.sch.id
```

---

## Troubleshooting

### DNS tidak resolve
- Tunggu propagasi DNS (bisa 24-48 jam)
- Cek dengan `nslookup` atau online tools (whatsmydns.net)

### SSL Error
- Pastikan certificate valid dan tidak expired
- Cek certificate chain lengkap
- Browser mungkin perlu refresh cache

### 502 Bad Gateway
- Aplikasi Flask tidak berjalan
- Port 6001 tidak accessible
- Periksa log nginx/IIS

### 504 Gateway Timeout
- Aplikasi terlalu lambat merespons
- Tingkatkan timeout di reverse proxy

---

## Keamanan Tambahan

1. **Firewall**: Blok akses langsung ke port 6001 dari luar
2. **Rate Limiting**: Batasi request per IP
3. **WAF**: Web Application Firewall (Cloudflare gratis)
4. **Backup**: Jadwal backup otomatis database & files
5. **Monitoring**: Setup uptime monitoring (UptimeRobot gratis)

---

## Dokumentasi Terkait

- [REVERSE_PROXY_SETUP.md](REVERSE_PROXY_SETUP.md) - Detail setup reverse proxy
- [DEPLOY_WINDOWS_SERVER.md](DEPLOY_WINDOWS_SERVER.md) - Deployment di Windows Server
- [AKSES_DARI_DEVICE_LAIN.md](AKSES_DARI_DEVICE_LAIN.md) - Akses jaringan lokal
