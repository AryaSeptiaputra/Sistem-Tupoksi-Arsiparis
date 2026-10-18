@echo off
TITLE Server Arsip SMKN 7 Bandung
cd /d "%~dp0\.."

call .venv\Scripts\activate

if not exist .env (
  echo File .env belum ada. Isi dulu lalu jalankan lagi.
  pause
  exit /b 1
)

REM Jalur start yang sama dengan service NSSM: serve.py (waitress, 4 thread, port 6001)
python serve.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server gagal berjalan. Periksa error di atas.
    pause
    exit /b 1
)
