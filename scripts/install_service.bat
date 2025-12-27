@echo off
setlocal enabledelayedexpansion
TITLE Install ArsipSMKN7 sebagai Windows Service
COLOR 0E

echo ======================================================
echo   INSTALL APLIKASI SEBAGAI WINDOWS SERVICE
echo ======================================================
echo.

:: Cek apakah dijalankan sebagai Administrator
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
set PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe
set WAITRESS_EXE=%APP_DIR%\.venv\Scripts\waitress-serve.exe
set SERVICE_NAME=ArsipSMKN7

echo [1/6] Memeriksa file yang diperlukan...

:: Cek NSSM
if not exist "%APP_DIR%\nssm.exe" (
    echo [ERROR] nssm.exe tidak ditemukan!
    echo.
    echo Download NSSM dari: https://nssm.cc/download
    echo Ekstrak dan copy nssm.exe ke folder: %APP_DIR%
    pause
    exit /b 1
)

:: Cek Virtual Environment
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Virtual environment tidak ditemukan!
    echo.
    echo Jalankan scripts\setup.bat terlebih dahulu.
    pause
    exit /b 1
)

:: Cek Waitress
if not exist "%WAITRESS_EXE%" (
    echo [ERROR] Waitress tidak terinstall!
    echo.
    echo Jalankan: .venv\Scripts\activate
    echo Lalu: pip install waitress
    pause
    exit /b 1
)

:: Cek .env
if not exist "%APP_DIR%\.env" (
    echo [WARNING] File .env tidak ditemukan!
    echo Service akan dibuat tapi mungkin tidak berjalan dengan benar.
    echo Pastikan untuk mengisi .env sebelum start service.
    pause
)

echo [2/6] Memeriksa apakah service sudah ada...
sc query %SERVICE_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Service %SERVICE_NAME% sudah terdaftar!
    echo.
    choice /C YN /M "Hapus dan install ulang service"
    if errorlevel 2 (
        echo Instalasi dibatalkan.
        pause
        exit /b 0
    )
    echo Menghapus service lama...
    "%APP_DIR%\nssm.exe" stop %SERVICE_NAME% >nul 2>&1
    "%APP_DIR%\nssm.exe" remove %SERVICE_NAME% confirm >nul 2>&1
    timeout /t 2 >nul
)

echo [3/6] Menginstall service...
"%APP_DIR%\nssm.exe" install %SERVICE_NAME% "%WAITRESS_EXE%" --host=127.0.0.1 --port=8000 serve:app
if %errorlevel% neq 0 goto :err

echo [4/6] Mengatur konfigurasi service...

:: Set working directory
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% AppDirectory "%APP_DIR%"
if %errorlevel% neq 0 goto :err

:: Set description
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% Description "Sistem Arsip SMKN 7 Bandung - Production Server"
if %errorlevel% neq 0 goto :err

:: Set display name
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% DisplayName "Arsip SMKN 7"
if %errorlevel% neq 0 goto :err

:: Set startup type to automatic
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% Start SERVICE_AUTO_START
if %errorlevel% neq 0 goto :err

:: Set log output
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% AppStdout "%APP_DIR%\logs\service_output.log"
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% AppStderr "%APP_DIR%\logs\service_error.log"

:: Set restart on failure
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% AppExit Default Restart
"%APP_DIR%\nssm.exe" set %SERVICE_NAME% AppRestartDelay 5000

echo [5/6] Memulai service...
"%APP_DIR%\nssm.exe" start %SERVICE_NAME%
if %errorlevel% neq 0 goto :err

:: Tunggu sebentar untuk memastikan service start
timeout /t 3 >nul

echo [6/6] Verifikasi status service...
"%APP_DIR%\nssm.exe" status %SERVICE_NAME%
if %errorlevel% neq 0 goto :err

echo.
echo ======================================================
echo   SERVICE BERHASIL DIINSTALL!
echo ======================================================
echo.
echo Service Name    : %SERVICE_NAME%
echo Status          : RUNNING
echo Startup Type    : Automatic
echo Port            : 8000 (localhost only)
echo Log Output      : logs\service_output.log
echo Log Error       : logs\service_error.log
echo.
echo Perintah berguna:
echo   - Start service   : nssm start %SERVICE_NAME%
echo   - Stop service    : nssm stop %SERVICE_NAME%
echo   - Restart service : nssm restart %SERVICE_NAME%
echo   - Status service  : nssm status %SERVICE_NAME%
echo   - Hapus service   : scripts\uninstall_service.bat
echo.
echo Akses aplikasi: http://127.0.0.1:8000
echo Untuk akses via domain, setup reverse proxy (lihat docs\REVERSE_PROXY_SETUP.md)
echo.
pause
goto :eof

:err
echo.
echo [ERROR] Terjadi kesalahan saat instalasi service!
echo Periksa log di atas untuk detail error.
echo.
pause
exit /b 1
