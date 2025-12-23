# 🚀 Deployment & Monitoring Guide

Panduan lengkap untuk deploy dan monitor aplikasi Sistem Tupoksi Arsiparis di production environment.

## 📋 Prerequisites

- Docker & Docker Compose
- MySQL 8.0 atau MariaDB 10.5+
- Redis (untuk caching - optional)
- Nginx (untuk reverse proxy - optional)
- SSL Certificate (recommended untuk production)

## 🐳 Quick Start dengan Docker

### 1. Setup Environment
```bash
# Clone repository
git clone https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis.git
cd Sistem-Tupoksi-Arsiparis

# Copy environment template
cp .env.example .env

# Edit .env dengan konfigurasi yang sesuai
nano .env
```

### 2. Deploy dengan Docker Compose
```bash
# Build dan start semua services
docker-compose up -d

# Lihat logs
docker-compose logs -f app

# Check health
curl http://localhost/health/health
```

### 3. Setup Database
```bash
# Masuk ke container database
docker-compose exec db mysql -u root -p arsiparis_smk7

# Import schema jika diperlukan
docker-compose exec app python seed_master.py
docker-compose exec app python seed_admin.py
```

## 🔍 Health Checks & Monitoring

### Health Check Endpoints
```bash
# General health check
GET /health/health

# Application metrics
GET /health/metrics

# Response format:
{
  "status": "healthy",
  "timestamp": "2025-12-23T10:00:00Z",
  "version": "2.0.0",
  "services": {
    "database": {"status": "healthy", "message": "OK"}
  },
  "system": {
    "memory_usage_percent": 45.2,
    "cpu_usage_percent": 12.5
  }
}
```

### Monitoring dengan Docker
```bash
# Container health
docker-compose ps

# Resource usage
docker stats

# Logs real-time
docker-compose logs -f --tail=100 app
```

## 🔧 Manual Deployment (Tanpa Docker)

### 1. Setup Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv -y

# Install MySQL
sudo apt install mysql-server-8.0 -y
sudo mysql_secure_installation
```

### 2. Setup Application
```bash
# Clone dan setup
git clone https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis.git
cd Sistem-Tupoksi-Arsiparis

# Setup virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Configure database connection

# Setup database
python seed_master.py
python seed_admin.py
```

### 3. Setup Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/arsiparis.service

# Add content:
[Unit]
Description=Sistem Tupoksi Arsiparis
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/.venv/bin
ExecStart=/path/to/your/app/.venv/bin/python serve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

# Enable dan start service
sudo systemctl enable arsiparis
sudo systemctl start arsiparis
sudo systemctl status arsiparis
```

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Gunakan strong random keys untuk JWT_SECRET_KEY
- ✅ Jangan commit file .env ke Git
- ✅ Gunakan environment-specific secrets

### 2. Database Security
```sql
-- Create dedicated user
CREATE USER 'arsiparis_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON arsiparis_smk7.* TO 'arsiparis_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Network Security
- ✅ Gunakan HTTPS di production
- ✅ Setup firewall (ufw/iptables)
- ✅ Rate limiting aktif
- ✅ CORS properly configured

## 📊 Performance Monitoring

### Key Metrics to Monitor
- **Response Time**: < 500ms untuk API calls
- **Error Rate**: < 1% dari total requests
- **Database Connections**: Monitor pool usage
- **Memory Usage**: < 80% dari available RAM
- **CPU Usage**: Monitor spikes

### Log Analysis
```bash
# View application logs
tail -f logs/production.log

# Search for errors
grep "ERROR" logs/production.log

# Monitor API usage
grep "GET\|POST" logs/production.log | head -20
```

## 🔄 Backup & Recovery

### Automated Backup
```bash
# Database backup script
mysqldump -u arsiparis_user -p arsiparis_smk7 > backup_$(date +%Y%m%d_%H%M%S).sql

# File backup
tar -czf storage_backup_$(date +%Y%m%d).tar.gz storage/
```

### Recovery Procedure
```bash
# Restore database
mysql -u arsiparis_user -p arsiparis_smk7 < backup_file.sql

# Restore files
tar -xzf storage_backup.tar.gz
```

## 🚨 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check MySQL service
sudo systemctl status mysql

# Test connection
mysql -u arsiparis_user -p -e "SELECT 1"
```

**2. Port Already in Use**
```bash
# Find process using port 8080
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

**3. Memory Issues**
```bash
# Check memory usage
free -h

# Restart service
sudo systemctl restart arsiparis
```

**4. Permission Issues**
```bash
# Fix storage permissions
sudo chown -R www-data:www-data storage/
sudo chmod -R 755 storage/
```

## 📈 Scaling Considerations

### Horizontal Scaling
- ✅ Stateless application design
- ✅ Database connection pooling
- ✅ Redis untuk session storage
- ✅ Load balancer (nginx)

### Vertical Scaling
- ✅ Monitor resource usage
- ✅ Database query optimization
- ✅ Caching implementation
- ✅ CDN untuk static files

## 🔧 Maintenance Tasks

### Daily
- ✅ Monitor logs untuk errors
- ✅ Check disk space usage
- ✅ Verify backup integrity

### Weekly
- ✅ Update dependencies
- ✅ Security patches
- ✅ Performance review

### Monthly
- ✅ Full system backup
- ✅ Log rotation
- ✅ Capacity planning

---

## 📞 Support

Jika mengalami masalah deployment:

1. Check `/health/health` endpoint
2. Review application logs
3. Verify database connectivity
4. Check system resources

**Version:** 2.0.0
**Last Updated:** December 2025