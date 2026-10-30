@echo off
REM Double-click this on the Windows laptop. Same as:
REM   powershell -File scripts\install_windows.ps1
cd /d "%~dp0\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_windows.ps1" %*
if errorlevel 1 pause
