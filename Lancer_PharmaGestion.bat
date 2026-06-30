@echo off
setlocal enabledelayedexpansion
REM ========================================
REM   PharmaGestion - Production Launcher
REM ========================================

echo ========================================
echo   Demarrage de PharmaGestion (PROD)
echo ========================================
echo.

REM === Configuration Logs ===
set LOG_DIR=%APPDATA%\PharmaGestion
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set LOG_FILE=%LOG_DIR%\startup_log.txt

REM Redirect stdout and stderr to log file
call :Log "Debut du script de lancement"
goto :Start

:Log
echo [%DATE% %TIME%] %~1 >> "%LOG_FILE%"
exit /b

:Start
call :Log "Dossier du script: %~dp0"

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Check if backend executable exists
if not exist "%SCRIPT_DIR%PharmaBackend\PharmaBackend.exe" (
    call :Log "[ERREUR] PharmaBackend.exe non trouve!"
    echo [ERREUR] PharmaBackend.exe non trouve!
    echo Chemin recherche: %SCRIPT_DIR%PharmaBackend\PharmaBackend.exe
    echo.
    echo Pour le mode developpement, utilisez:
    echo   Lancer_PharmaGestion_DEV.bat
    echo.
    pause
    exit /b 1
)

REM Check if frontend executable exists
if not exist "%SCRIPT_DIR%frontend\PharmaGest.exe" (
    call :Log "[ERREUR] PharmaGest.exe non trouve!"
    echo [ERREUR] PharmaGest.exe non trouve!
    echo Chemin recherche: %SCRIPT_DIR%frontend\PharmaGest.exe
    echo.
    echo Pour le mode developpement, utilisez:
    echo   Lancer_PharmaGestion_DEV.bat
    echo.
    pause
    exit /b 1
)

REM === Kill existing processes to avoid port conflicts ===
echo [*] Nettoyage des anciens processus...
call :Log "Nettoyage des anciens processus..."
taskkill /F /IM PharmaBackend.exe >nul 2>&1
taskkill /F /IM PharmaGest.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM === Free port 8000 if still occupied ===
echo [*] Verification du port 8000...
call :Log "Verification du port 8000..."
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    call :Log "Port 8000 occupe, tentative de liberation..."
    echo [*] Port 8000 occupe, liberation en cours...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM Start backend
echo [1/2] Demarrage du backend...
call :Log "Demarrage du backend..."
start "" "%SCRIPT_DIR%PharmaBackend\PharmaBackend.exe"

REM Wait for backend to be ready (check health endpoint)
echo [*] Attente du backend (max 15 secondes)...
call :Log "Attente du backend..."
set READY=0
for /L %%i in (1,1,15) do (
    if !READY! equ 0 (
        timeout /t 1 /nobreak >nul
        powershell -Command "try { $null = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
        if !errorlevel! equ 0 (
            set READY=1
            echo [*] Backend pret! (%%i secondes)
            call :Log "Backend pret apres %%i secondes"
        )
    )
)

REM Fallback: if health check never succeeded, wait a fixed time
if %READY% equ 0 (
    call :Log "Backend health check timeout - attente fixe de 5s supplementaires"
    echo [*] Attente supplementaire de 5 secondes...
    timeout /t 5 /nobreak >nul
)

REM Start frontend
echo [2/2] Demarrage de l'interface...
call :Log "Demarrage de l'interface..."
start "" "%SCRIPT_DIR%frontend\PharmaGest.exe"

echo.
echo ========================================
echo   PharmaGestion demarre!
echo ========================================
echo.
REM Fin du script, la fenetre se ferme
call :Log "Script termine avec succes"
exit
