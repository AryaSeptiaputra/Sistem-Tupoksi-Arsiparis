@echo off
setlocal enabledelayedexpansion
TITLE Setup Produksi - Sistem Arsip SMKN 7 Bandung
COLOR 0B

set PORT=8000

echo ======================================================
echo   MEMULAI SETUP PRODUKSI SISTEM ARSIP SMKN 7
echo ======================================================

:: Kembali ke root folder
cd /d "%~dp0\.."

:: 1. Membuat file .env jika belum ada
echo [1/6] Mengecek konfigurasi file .env...
if not exist .env (
    echo Menghasilkan file .env baru dengan placeholder...
    (
        echo # --- DATABASE CONFIGURATION ---
        echo DATABASE_URL=
        echo.
        echo # --- SECURITY ---
        echo JWT_SECRET_KEY=
        echo SECRET_KEY=
        echo.
        echo # --- ENVIRONMENT ---
        echo FLASK_ENV=production
        echo FLASK_DEBUG=0
        echo PORT=%PORT%
        echo.
        echo # --- LOGGING ---
        echo LOG_FILE_PATH=%cd%\logs\production.log
    ) > .env
    echo File .env dibuat. Harap isi nilai rahasia sebelum menjalankan server.
) else (
    echo File .env sudah ada. Lewati.
)

:: 2. Membuat Virtual Environment jika belum ada
if not exist .venv (
    echo [2/6] Membuat Virtual Environment...
    python -m venv .venv
    if %errorlevel% neq 0 goto :err
) else (
    echo [2/6] Virtual Environment sudah ada. Lewati.
)

:: 3. Aktivasi Venv dan Install Dependencies
echo [3/6] Menginstal pustaka dari requirements.txt...
call .venv\Scripts\activate
pip install --upgrade pip
if %errorlevel% neq 0 goto :err
pip install -r requirements.txt
if %errorlevel% neq 0 goto :err
pip install waitress
if %errorlevel% neq 0 goto :err

:: 4. Membuat Folder Penyimpanan (Storage)
echo [4/6] Membuat struktur folder penyimpanan arsip...
if not exist storage\documents\incoming_letters mkdir storage\documents\incoming_letters
if not exist storage\documents\outgoing_letters mkdir storage\documents\outgoing_letters
if not exist storage\documents\employee_archives mkdir storage\documents\employee_archives
if not exist storage\documents\finance_archives mkdir storage\documents\finance_archives
if not exist storage\documents\diplomas mkdir storage\documents\diplomas
if not exist logs mkdir logs

:: 5. Seeding Data Master dan Admin (opsional)
echo [5/6] Menjalankan seeding master/admin? (Y/N)
choice /C YN /M "Jalankan seeding sekarang"
if errorlevel 2 goto :skipseed
python database\seeders\seed_master.py
if %errorlevel% neq 0 goto :err
python database\seeders\seed_admin.py
if %errorlevel% neq 0 goto :err
:skipseed

:: 6. Selesai
echo [6/6] Setup selesai!
echo ======================================================
echo   Isi nilai rahasia di .env sebelum menjalankan server.
echo   Gunakan scripts\run.bat atau daftar sebagai service (disarankan) untuk produksi.
echo ======================================================
pause
goto :eof

:err
echo Terjadi kegagalan pada langkah sebelumnya. Periksa pesan di atas.
exit /b 1
