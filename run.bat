@echo off
TITLE Server Arsip SMKN 7 Bandung - Sistem Tupoksi Arsiparis
echo ======================================================
echo   MENJALANKAN SERVER ARSIP SMKN 7 BANDUNG
echo   Sistem Tupoksi Arsiparis v2.0
echo   Dengan dukungan Pagination untuk performa optimal
echo ======================================================
echo.

call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: Gagal mengaktifkan virtual environment.
    echo Pastikan virtual environment sudah dibuat dengan setup.bat
    pause
    exit /b 1
)

echo Memulai server Flask...
python serve.py

if %errorlevel% neq 0 (
    echo ERROR: Gagal menjalankan server.
    echo Periksa log error di atas.
)

pause