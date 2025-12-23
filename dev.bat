@echo off
TITLE Development Server - Sistem Arsip SMKN 7 Bandung
echo ======================================================
echo   MENJALANKAN SERVER DEVELOPMENT
echo   Sistem Tupoksi Arsiparis v2.0
echo   Mode: Development (Debug Enabled)
echo ======================================================
echo.

call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: Gagal mengaktifkan virtual environment.
    echo Jalankan setup.bat terlebih dahulu.
    pause
    exit /b 1
)

echo Menjalankan server dalam mode development...
set FLASK_ENV=development
set FLASK_DEBUG=1
python serve.py

if %errorlevel% neq 0 (
    echo ERROR: Gagal menjalankan server development.
    echo Periksa log error di atas.
)

pause