@echo off
setlocal enabledelayedexpansion
TITLE Status Service ArsipSMKN7
COLOR 0B

:: Set paths (navigate to root first)
cd /d "%~dp0\.."
set APP_DIR=%cd%
set SERVICE_NAME=ArsipSMKN7

echo ======================================================
echo   STATUS SERVICE ARSIP SMKN 7
echo ======================================================
echo.

:: Cek NSSM
if not exist "%APP_DIR%\nssm.exe" (
    echo [INFO] NSSM tidak ditemukan. Menggunakan sc query...
    echo.
    sc query %SERVICE_NAME%
    echo.
    pause
    exit /b 0
)

:: Cek service dengan NSSM
"%APP_DIR%\nssm.exe" status %SERVICE_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Service %SERVICE_NAME% tidak terdaftar.
    echo.
    echo Install service dengan: scripts\install_service.bat
) else (
    echo Service Name : %SERVICE_NAME%
    echo Status       : 
    "%APP_DIR%\nssm.exe" status %SERVICE_NAME%
    echo.
    echo Detail lengkap:
    sc query %SERVICE_NAME%
    echo.
    echo Log Output:
    echo   - Output: logs\service_output.log
    echo   - Error : logs\service_error.log
)

echo.
echo Perintah lain:
echo   - Restart : scripts\restart_service.bat
echo   - Uninstall : scripts\uninstall_service.bat
echo.
pause
