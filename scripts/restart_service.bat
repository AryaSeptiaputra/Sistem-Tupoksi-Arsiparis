@echo off
setlocal enabledelayedexpansion
TITLE Restart ArsipSMKN7 Service
COLOR 0B

echo ======================================================
echo   RESTART SERVICE ARSIP SMKN 7
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

:: Set paths (navigate to root first)
cd /d "%~dp0\.."
set APP_DIR=%cd%
set SERVICE_NAME=ArsipSMKN7

:: Cek NSSM
if not exist "%APP_DIR%\nssm.exe" (
    echo [ERROR] nssm.exe tidak ditemukan!
    pause
    exit /b 1
)

echo [1/3] Memeriksa status service...
"%APP_DIR%\nssm.exe" status %SERVICE_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Service %SERVICE_NAME% tidak ditemukan!
    echo Install service terlebih dahulu dengan: scripts\install_service.bat
    pause
    exit /b 1
)

echo [2/3] Merestart service...
"%APP_DIR%\nssm.exe" restart %SERVICE_NAME%
if %errorlevel% neq 0 (
    echo [ERROR] Gagal restart service!
    pause
    exit /b 1
)

echo Menunggu service untuk start kembali...
timeout /t 5 >nul

echo [3/3] Verifikasi status...
"%APP_DIR%\nssm.exe" status %SERVICE_NAME%

echo.
echo ======================================================
echo   SERVICE BERHASIL DIRESTART!
echo ======================================================
echo.
echo Service: %SERVICE_NAME%
echo Akses : http://127.0.0.1:8000
echo.
pause
