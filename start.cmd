@echo off
rem One click on Windows: double-click this file.
where pwsh >nul 2>nul && (pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1") || (powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1")
pause
