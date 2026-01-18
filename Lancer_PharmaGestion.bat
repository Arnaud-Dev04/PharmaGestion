@echo off
title Pharmacie Gestion - Lancement
color 0A
echo.
echo ========================================
echo   SYSTEME DE GESTION DE PHARMACIE
echo ========================================
echo.

REM Vérifier si le port 8000 est déjà occupé
echo Verification du port 8000...
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo.
    echo [ATTENTION] Le port 8000 est deja utilise!
    echo Arret des processus PharmaBackend existants...
    taskkill /IM PharmaBackend.exe /F >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo Processus nettoyes.
    echo.
)

echo Demarrage du serveur...
echo.

REM Demarrer le backend en arriere-plan
cd /d "%~dp0backend\dist"
if not exist "PharmaBackend.exe" (
    echo [ERREUR] PharmaBackend.exe introuvable!
    echo Chemin attendu: %~dp0backend\dist\PharmaBackend.exe
    pause
    exit /b 1
)

start /B "" "%~dp0backend\dist\PharmaBackend.exe"

REM Attendre que le serveur demarre
echo Attente du demarrage du serveur (5 secondes)...
timeout /t 5 /nobreak >nul

REM Vérifier que le backend écoute bien sur le port 8000
echo Verification du serveur...
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo.
    echo [OK] Serveur demarre avec succes sur le port 8000!
    echo.
    echo Ouverture du navigateur...
    start http://localhost:8000
    echo.
    echo ========================================
    echo Application lancee avec succes!
    echo Le navigateur devrait s'ouvrir automatiquement.
    echo.
    echo IMPORTANT: Ne fermez PAS cette fenetre !
    echo            Cela arreterait l'application.
    echo.
    echo Pour fermer l'application, fermez cette fenetre
    echo ou appuyez sur Ctrl+C.
    echo ========================================
    echo.
) else (
    echo.
    echo [ERREUR] Le serveur n'a pas demarre correctement!
    echo Le port 8000 n'est pas en ecoute.
    echo.
    echo Verifiez le fichier backend_log.txt pour plus d'informations.
    echo.
    pause
    exit /b 1
)

REM Garder la fenetre ouverte
:loop
timeout /t 10 /nobreak >nul
goto loop
