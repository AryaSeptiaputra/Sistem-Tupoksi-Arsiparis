@echo off
setlocal enabledelayedexpansion
TITLE Uninstall ArsipSMKN7 Service
COLOR 0C

echo ======================================================
echo   HAPUS SERVICE ARSIP SMKN 7
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
    echo Tidak dapat menghapus service tanpa NSSM.
    pause
    exit /b 1
)

echo [1/3] Memeriksa service...
sc query %SERVICE_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Service %SERVICE_NAME% tidak ditemukan.
    echo Service mungkin sudah dihapus atau belum pernah diinstall.
    pause
    exit /b 0
)

echo Service ditemukan: %SERVICE_NAME%
echo.
echo [WARNING] Tindakan ini akan menghapus service dari sistem!
choice /C YN /M "Lanjutkan menghapus service"
if errorlevel 2 (
    echo Penghapusan dibatalkan.
    pause
    exit /b 0
)

echo.
echo [2/3] Menghentikan service...
"%APP_DIR%\nssm.exe" stop %SERVICE_NAME%
timeout /t 2 >nul

echo [3/3] Menghapus service...
"%APP_DIR%\nssm.exe" remove %SERVICE_NAME% confirm

if %errorlevel% equ 0 (
    echo.
    echo ======================================================
    echo   SERVICE BERHASIL DIHAPUS!
    echo ======================================================
    echo.
    echo Service %SERVICE_NAME% telah dihapus dari sistem.
    echo Aplikasi masih dapat dijalankan manual dengan run.bat
    echo Atau install ulang sebagai service dengan install_service.bat
) else (
    echo.
    echo [ERROR] Gagal menghapus service!
    echo Coba restart komputer lalu jalankan script ini lagi.
)

echo.
pause
