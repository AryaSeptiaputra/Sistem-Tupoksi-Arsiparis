@echo off
TITLE Setup Produksi - Sistem Arsip SMKN 7 Bandung
COLOR 0B

echo ======================================================
echo   MEMULAI SETUP PRODUKSI SISTEM ARSIP SMKN 7
echo ======================================================

:: 1. Membuat file .env jika belum ada
echo [1/6] Mengecek konfigurasi file .env...
if not exist .env (
    echo Menghasilkan file .env baru...
    (
        echo # --- DATABASE CONFIGURATION ---
        echo DATABASE_URL=mysql+pymysql://root:password@localhost/arsiparis_smk7
        echo.
        echo # --- SECURITY ---
        echo JWT_SECRET_KEY=5584c6c09bd32c2db66d179a24a5f04f488a4428c37269a17358ca7554dccb09
        echo SECRET_KEY=77b8c3d2e1a4f5b6c7d8e9f0a1b2c3d4
        echo.
        echo # --- ENVIRONMENT ---
        echo FLASK_ENV=production
        echo FLASK_DEBUG=0
        echo.
        echo # --- LOGGING ---
        echo LOG_FILE_PATH=%~dp0logs\production.log
    ) > .env
    echo File .env berhasil dibuat.
) else (
    echo File .env sudah ada. Lewati.
)

:: 2. Membuat Virtual Environment jika belum ada
if not exist .venv (
    echo [2/6] Membuat Virtual Environment...
    python -m venv .venv
) else (
    echo [2/6] Virtual Environment sudah ada. Lewati.
)

:: 3. Aktivasi Venv dan Install Dependencies
echo [3/6] Menginstal pustaka dari requirements.txt...
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

:: 4. Membuat Folder Penyimpanan (Storage)
echo [4/6] Membuat struktur folder penyimpanan arsip...
if not exist storage\documents\incoming_letters mkdir storage\documents\incoming_letters
if not exist storage\documents\outgoing_letters mkdir storage\documents\outgoing_letters
if not exist storage\documents\employee_archives mkdir storage\documents\employee_archives
if not exist storage\documents\finance_archives mkdir storage\documents\finance_archives
if not exist storage\documents\diplomas mkdir storage\documents\diplomas
if not exist logs mkdir logs

:: 5. Seeding Data Master dan Admin
echo [5/6] Memasukkan data referensi dan akun admin ke database...
python seed_master.py
python seed_admin.py

:: 6. Selesai
echo [6/6] Setup selesai!
echo ======================================================
echo   Aplikasi siap digunakan. 
echo   Gunakan jalankan_arsip.bat untuk memulai server.
echo ======================================================
pause