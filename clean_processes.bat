@echo off
REM ========================================
REM   Clean Backend Processes
REM ========================================

echo Nettoyage des processus backend...

taskkill /F /IM PharmaBackend.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" 2>nul
taskkill /F /IM uvicorn.exe 2>nul

echo Processus nettoyes.
timeout /t 2 /nobreak >nul
