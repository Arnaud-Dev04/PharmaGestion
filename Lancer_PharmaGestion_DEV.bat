@echo off
REM ========================================
REM   PharmaGestion - Development Launcher
REM ========================================

echo ========================================
echo   Demarrage de PharmaGestion (DEV)
echo ========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Check if backend venv exists
if not exist "%SCRIPT_DIR%backend\venv\" (
    echo [ERREUR] Environnement virtuel Python non trouve!
    echo Veuillez creer l'environnement virtuel d'abord:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start backend in a new window
echo [1/2] Demarrage du backend FastAPI...
start "PharmaGestion Backend" cmd /k "cd /d %SCRIPT_DIR%backend && venv\Scripts\activate && python main.py"

REM Wait for backend to start
echo [*] Attente du demarrage du backend (5 secondes)...
timeout /t 5 /nobreak >nul

REM Start Flutter frontend in a new window
echo [2/2] Demarrage du frontend Flutter...
start "PharmaGestion Frontend" cmd /k "cd /d %SCRIPT_DIR%frontend1 && flutter run -d windows"

echo.
echo ========================================
echo   PharmaGestion demarre!
echo ========================================
echo.
echo Backend: http://127.0.0.1:8000
echo Frontend: Fenetre Flutter
echo.
echo Fermez les fenetres de terminal pour arreter l'application.
echo.
pause
