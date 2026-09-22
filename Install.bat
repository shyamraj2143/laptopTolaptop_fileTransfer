@echo off
setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo          DirectDrop Installer
echo ============================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if errorlevel 1 (
    echo.
    echo [ERROR] DirectDrop installation failed.
    echo Read the error above, then press any key to close.
    pause >nul
    exit /b 1
)

echo.
echo [OK] DirectDrop installation finished.
echo You can now close this window.
pause >nul
