@echo off
REM Weditor launcher for MuMu emulator
REM Usage: just double-click this file or run: weditor_mumu.bat

chcp 65001 >nul

echo Starting Weditor for MuMu emulator-5554 ...
echo.
echo Weditor will open in your browser at http://localhost:17310
echo.
echo Tips:
echo 1. In the Weditor page, set "Device" to emulator-5554
echo 2. Click "Connect" button
echo 3. You can see the app UI tree and click coordinates
echo.
echo Press Ctrl+C in this window to stop Weditor
echo.

cd /d "%~dp0.."
.venv\Scripts\python.exe -m weditor
