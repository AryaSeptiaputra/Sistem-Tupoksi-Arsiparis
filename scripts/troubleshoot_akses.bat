@echo off
echo ========================================
echo   Troubleshooting Akses dari Device Lain
echo ========================================
echo.

echo [1/5] Cek apakah server berjalan...
netstat -an | findstr :6001
if %errorLevel% NEQ 0 (
    echo [X] Server TIDAK berjalan di port 6001
    echo     Jalankan: scripts\run.bat
    echo.
    goto :firewall_check
) else (
    echo [OK] Server berjalan di port 6001
    echo.
)

:firewall_check
echo [2/5] Cek firewall rule...
netsh advfirewall firewall show rule name="Sistem Tupoksi Arsiparis - Port 6001" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] Firewall rule BELUM ada
    echo     Jalankan: scripts\allow_firewall.bat (as Administrator)
    echo.
) else (
    echo [OK] Firewall rule sudah ada
    netsh advfirewall firewall show rule name="Sistem Tupoksi Arsiparis - Port 6001"
    echo.
)

echo [3/5] Cek IP Address komputer ini...
echo ----------------------------------------
ipconfig | findstr /C:"IPv4"
echo ----------------------------------------
echo.

echo [4/5] Test akses lokal...
echo Mencoba akses http://localhost:6001 ...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:6001' -TimeoutSec 5 -UseBasicParsing; Write-Host '[OK] Server merespon dengan status:' $response.StatusCode } catch { Write-Host '[X] Server tidak merespon:' $_.Exception.Message }"
echo.

echo [5/5] Informasi serve.py...
echo ----------------------------------------
findstr /n "host.*=" serve.py | findstr -v "#"
echo ----------------------------------------
echo.
echo CATATAN: Pastikan host = '0.0.0.0' (bukan 127.0.0.1)
echo.

echo ========================================
echo   CHECKLIST untuk Device Lain
echo ========================================
echo.
echo [ ] Server sudah berjalan (cek hasil di atas)
echo [ ] Firewall sudah dibuka (jalankan allow_firewall.bat)
echo [ ] serve.py menggunakan host='0.0.0.0'
echo [ ] Device lain di jaringan WiFi/LAN yang SAMA
echo [ ] Akses dari device lain: http://[IP-di-atas]:6001
echo.
echo ========================================
echo   Quick Fix Commands
echo ========================================
echo.
echo Jika server belum jalan:
echo   scripts\run.bat
echo.
echo Jika firewall belum dibuka (run as Admin):
echo   scripts\allow_firewall.bat
echo.
echo Matikan firewall sementara untuk test (run as Admin):
echo   netsh advfirewall set allprofiles state off
echo.
echo Nyalakan kembali firewall (run as Admin):
echo   netsh advfirewall set allprofiles state on
echo.
pause
