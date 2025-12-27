@echo off
TITLE Server Arsip SMKN 7 Bandung
cd /d "%~dp0\.."

call .venv\Scripts\activate

if not exist .env (
  echo File .env belum ada. Isi dulu lalu jalankan lagi.
  pause
  exit /b 1
)

REM Gunakan waitress untuk serving produksi di Windows
waitress-serve --host=127.0.0.1 --port=8000 serve:app
