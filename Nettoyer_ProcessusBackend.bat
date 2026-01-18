@echo off
REM Script pour nettoyer tous les processus PharmaBackend en cours
title Nettoyage PharmaBackend
color 0C

echo ========================================
echo   NETTOYAGE PROCESSUS PHARMAGESTION
echo ========================================
echo.

REM Afficher les processus PharmaBackend en cours
echo Recherche des processus PharmaBackend en cours...
tasklist | findstr PharmaBackend
if %errorlevel% == 0 (
    echo.
    echo Processus PharmaBackend detectes.
    echo Arret de tous les processus...
    taskkill /IM PharmaBackend.exe /F
    echo.
    echo [OK] Processus arretes.
) else (
    echo.
    echo [OK] Aucun processus PharmaBackend en cours.
)

echo.
echo Verification du port 8000...
netstat -ano | findstr :8000
if %errorlevel% == 0 (
    echo.
    echo [ATTENTION] Le port 8000 est encore occupe.
    echo Identifiez et arretez manuellement le processus si necessaire.
) else (
    echo.
    echo [OK] Le port 8000 est libre.
)

echo.
echo ========================================
echo Nettoyage termine!
echo Vous pouvez maintenant lancer PharmaGestion.
echo ========================================
echo.
pause
