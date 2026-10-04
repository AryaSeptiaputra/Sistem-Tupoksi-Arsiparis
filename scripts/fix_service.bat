@echo off
setlocal enabledelayedexpansion
TITLE Fix ArsipSMKN7 Service
COLOR 0E

echo ======================================================
echo   PERBAIKI SERVICE YANG BERMASALAH
echo ======================================================
echo.

:: Cek Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Script ini harus dijalankan sebagai Administrator!
    echo.
    echo Klik kanan file ini dan pilih "Run as administrator"
    pause
    exit /b 1
)

cd /d "%~dp0\.."
set APP_DIR=%cd%
set SERVICE_NAME=ArsipSMKN7

echo [1/3] Menghentikan service yang bermasalah...
sc stop %SERVICE_NAME% >nul 2>&1
timeout /t 3 >nul

echo [2/3] Menghapus service...
"%APP_DIR%\nssm.exe" remove %SERVICE_NAME% confirm >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Service mungkin sudah tidak ada atau gagal dihapus
)
timeout /t 2 >nul

echo [3/3] Service berhasil dihapus!
echo.
echo Sekarang jalankan: scripts\install_service.bat
echo.
pause
