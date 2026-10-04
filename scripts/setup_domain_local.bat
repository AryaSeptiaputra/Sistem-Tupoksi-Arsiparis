@echo off
echo ========================================
echo   Setup Domain Lokal
echo ========================================
echo.

REM Jalankan sebagai Administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: Script ini harus dijalankan sebagai Administrator!
    echo Klik kanan script ini, pilih "Run as Administrator"
    pause
    exit /b 1
)

set HOSTS_FILE=C:\Windows\System32\drivers\etc\hosts

echo Masukkan nama domain yang diinginkan (contoh: arsiparis.local atau arsip.smk.local)
set /p DOMAIN_NAME="Domain name: "

echo Masukkan IP Address PC Server (contoh: 192.168.2.192)
set /p IP_ADDRESS="IP Address: "

echo.
echo Menambahkan ke hosts file...
echo %IP_ADDRESS% %DOMAIN_NAME% >> %HOSTS_FILE%

echo.
echo ========================================
echo   Domain lokal berhasil ditambahkan!
echo ========================================
echo.
echo Sekarang Anda bisa akses dengan:
echo   http://%DOMAIN_NAME%:6001
echo.
echo CATATAN:
echo - Lakukan ini di SETIAP device yang ingin akses
echo - Atau gunakan DNS Server untuk jaringan sekolah
echo.
pause
