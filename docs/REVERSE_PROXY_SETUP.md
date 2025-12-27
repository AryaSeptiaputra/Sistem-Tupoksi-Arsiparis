# Panduan Setup Reverse Proxy untuk Akses Domain

Dokumen ini menjelaskan cara mengonfigurasi reverse proxy di Windows Server agar aplikasi dapat diakses melalui nama domain (misal: `arsip.smkn7.sch.id`) alih-alih IP:Port.

---

## Konsep Dasar

```
Client Browser → http(s)://arsip.smkn7.sch.id (port 80/443)
                        ↓
                  Reverse Proxy (IIS/Nginx)
                        ↓
                  http://127.0.0.1:8000 (Waitress/Flask)
```

**Keuntungan:**
- Akses dengan domain profesional
- TLS/SSL termination di proxy
- Load balancing (opsional)
- Cache static assets
- Rate limiting & security headers

---

## Pilihan Reverse Proxy

### Opsi 1: IIS + URL Rewrite + ARR (Rekomendasi untuk Windows Server)
### Opsi 2: Nginx untuk Windows (Alternatif ringan)

---

## Opsi 1: Setup dengan IIS (Internet Information Services)

### Prasyarat
1. Install IIS melalui Server Manager → Add Roles and Features
2. Install module tambahan:
   - **URL Rewrite Module**: [Download dari Microsoft](https://www.iis.net/downloads/microsoft/url-rewrite)
   - **Application Request Routing (ARR)**: [Download dari Microsoft](https://www.iis.net/downloads/microsoft/application-request-routing)

### Langkah Instalasi

#### 1. Persiapan DNS
Pastikan domain/subdomain Anda mengarah ke IP server:
```
A Record: arsip.smkn7.sch.id → 103.xxx.xxx.xxx (IP Public Server)
```

#### 2. Buat Site Baru di IIS
1. Buka **IIS Manager** (`inetmgr`)
2. Klik kanan **Sites** → **Add Website**
3. Isi:
   - **Site name**: `ArsipSMKN7`
   - **Physical path**: `C:\inetpub\wwwroot\arsip` (buat folder kosong)
   - **Binding**: 
     - Type: `http`
     - IP: `All Unassigned`
     - Port: `80`
     - Host name: `arsip.smkn7.sch.id`
4. Klik **OK**

#### 3. Enable Proxy di ARR
1. Di IIS Manager, klik server name (level root)
2. Double-click **Application Request Routing Cache**
3. Klik **Server Proxy Settings** di panel kanan
4. Centang **Enable proxy**
5. Klik **Apply**

#### 4. Konfigurasi URL Rewrite
1. Klik site **ArsipSMKN7** yang baru dibuat
2. Double-click **URL Rewrite**
3. Klik **Add Rule(s)** → **Reverse Proxy**
4. Jika muncul prompt ARR, klik **OK**
5. Isi:
   - **Inbound Rules**: `127.0.0.1:8000`
   - Centang **Enable SSL Offloading**
6. Klik **OK**

#### 5. Edit Web.config (Fine-tuning)
Buat file `web.config` di `C:\inetpub\wwwroot\arsip\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyInboundRule" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://127.0.0.1:8000/{R:1}" />
                    <serverVariables>
                        <set name="HTTP_X_FORWARDED_PROTO" value="http" />
                        <set name="HTTP_X_FORWARDED_FOR" value="{REMOTE_ADDR}" />
                    </serverVariables>
                </rule>
            </rules>
        </rewrite>
        <httpProtocol>
            <customHeaders>
                <add name="X-Content-Type-Options" value="nosniff" />
                <add name="X-Frame-Options" value="SAMEORIGIN" />
            </customHeaders>
        </httpProtocol>
    </system.webServer>
</configuration>
```

#### 6. Setup HTTPS (SSL/TLS) - WAJIB untuk Produksi
1. Dapatkan sertifikat SSL (Let's Encrypt/Comodo/dll)
2. Import sertifikat ke Windows Certificate Store
3. Edit binding site:
   - Type: `https`
   - Port: `443`
   - Host name: `arsip.smkn7.sch.id`
   - SSL certificate: Pilih sertifikat yang sudah di-import
4. Update `web.config` → ganti `HTTP_X_FORWARDED_PROTO` value menjadi `https`

#### 7. Redirect HTTP ke HTTPS (Opsional tapi disarankan)
Tambahkan rule di `web.config`:

```xml
<rule name="HTTP to HTTPS redirect" stopProcessing="true">
    <match url="(.*)" />
    <conditions>
        <add input="{HTTPS}" pattern="off" />
    </conditions>
    <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
</rule>
```

---

## Opsi 2: Setup dengan Nginx untuk Windows

### Instalasi Nginx
1. Download Nginx untuk Windows: [nginx.org](https://nginx.org/en/download.html)
2. Ekstrak ke `C:\nginx`

### Konfigurasi
Edit `C:\nginx\conf\nginx.conf`:

```nginx
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Upstream Backend
    upstream flask_backend {
        server 127.0.0.1:8000;
    }

    # HTTP Server (Redirect ke HTTPS)
    server {
        listen 80;
        server_name arsip.smkn7.sch.id;
        return 301 https://$host$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name arsip.smkn7.sch.id;

        # SSL Certificate (ganti path)
        ssl_certificate      C:/nginx/ssl/cert.pem;
        ssl_certificate_key  C:/nginx/ssl/key.pem;

        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Client Max Body Size (untuk upload file)
        client_max_body_size 20M;

        # Static Files Cache (untuk assets)
        location /static/ {
            proxy_pass http://flask_backend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Proxy ke Flask
        location / {
            proxy_pass http://flask_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
```

### Jalankan Nginx sebagai Service
1. Download NSSM (lihat panduan sebelumnya)
2. Install Nginx sebagai service:
   ```batch
   nssm install NginxService "C:\nginx\nginx.exe"
   nssm set NginxService AppDirectory "C:\nginx"
   nssm set NginxService Start SERVICE_AUTO_START
   nssm start NginxService
   ```

---

## Konfigurasi Flask untuk Trust Proxy Headers

Edit `serve.py` untuk mendukung `X-Forwarded-For` dan `X-Forwarded-Proto`:

```python
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Trust X-Forwarded-* headers dari reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=1,      # X-Forwarded-For
    x_proto=1,    # X-Forwarded-Proto
    x_host=1,     # X-Forwarded-Host
    x_prefix=1    # X-Forwarded-Prefix
)

# ... rest of your app code ...
```

---

## Verifikasi Setup

### 1. Cek Service Running
- Waitress: `netstat -an | findstr :8000` → harus ada `127.0.0.1:8000 LISTENING`
- IIS: Buka Services.msc → pastikan `World Wide Web Publishing Service` running
- Nginx: `nssm status NginxService` → harus `SERVICE_RUNNING`

### 2. Test Local
```batch
curl http://127.0.0.1:8000/
```
Harus return response dari Flask.

### 3. Test Domain
```
curl http://arsip.smkn7.sch.id
curl https://arsip.smkn7.sch.id
```

### 4. Cek Headers
```batch
curl -I https://arsip.smkn7.sch.id
```
Verifikasi ada header keamanan: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`.

---

## Troubleshooting

### Error 502 Bad Gateway
- Cek Waitress berjalan di `127.0.0.1:8000`
- Cek Windows Firewall tidak block port 8000 (seharusnya tidak karena loopback)
- Restart proxy service

### Error 503 Service Unavailable
- Flask/Waitress crash atau tidak respond
- Cek log di `logs\production.log`
- Restart Waitress service

### Domain tidak resolve
- Cek DNS propagation (gunakan `nslookup arsip.smkn7.sch.id`)
- Cek firewall server membuka port 80/443
- Cek binding host name di IIS/Nginx sesuai domain

### SSL Certificate Error
- Pastikan certificate valid dan tidak expired
- Cek certificate chain lengkap (root + intermediate)
- Restart IIS/Nginx setelah install certificate

---

## Checklist Go-Live

- [ ] DNS record pointing ke server IP
- [ ] Firewall membuka port 80 dan 443
- [ ] SSL certificate valid dan ter-install
- [ ] Waitress running sebagai service (auto-start)
- [ ] Reverse proxy (IIS/Nginx) running dan configured
- [ ] Flask `ProxyFix` middleware aktif
- [ ] Test HTTP redirect ke HTTPS
- [ ] Test akses dari browser eksternal
- [ ] Security headers tervalidasi
- [ ] Backup configuration (web.config / nginx.conf)

---

## Referensi
- [IIS URL Rewrite Documentation](https://docs.microsoft.com/en-us/iis/extensions/url-rewrite-module/using-the-url-rewrite-module)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Flask ProxyFix Documentation](https://flask.palletsprojects.com/en/latest/deploying/proxy_fix/)
