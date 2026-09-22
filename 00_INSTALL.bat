@echo off
setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo        DirectDrop - One Click Install
echo ============================================
echo.
echo Install DirectDrop on BOTH laptops.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] Installation failed. Read the message above.
  pause
  exit /b 1
)
echo.
echo [OK] Installation completed successfully.
echo DirectDrop will run in the background after Windows logon.
echo.
pause
