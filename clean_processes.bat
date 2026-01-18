@echo off
echo ========================================
echo  NETTOYAGE DES PROCESSUS ZOMBIES
echo ========================================
echo.

echo [1/4] Arret du Backend (PharmaBackend.exe)...
taskkill /F /IM PharmaBackend.exe /T 2>nul
if %ERRORLEVEL% EQU 0 ( echo    - Backend arrete. ) else ( echo    - Aucun backend trouve. )

echo [2/4] Arret du Frontend (PharmaGestion.exe)...
taskkill /F /IM PharmaGestion.exe /T 2>nul
if %ERRORLEVEL% EQU 0 ( echo    - Frontend arrete. ) else ( echo    - Aucun frontend trouve. )

echo [3/4] Arret des processus Flutter (pharmac_plus.exe)...
taskkill /F /IM pharmac_plus.exe /T 2>nul
if %ERRORLEVEL% EQU 0 ( echo    - Processus Flutter arrete. ) else ( echo    - Aucun processus Flutter trouve. )

echo [4/4] Arret des installateurs bloques...
taskkill /F /IM PharmaGestion_Setup.exe /T 2>nul
taskkill /F /IM "Inno Setup Compiler.exe" /T 2>nul
taskkill /F /IM "Compil32.exe" /T 2>nul
taskkill /F /IM "ISCC.exe" /T 2>nul

echo [5/4] Force delete output file...
if exist "Output\PharmaGestion_Setup.exe" del /F /Q "Output\PharmaGestion_Setup.exe"

echo Waiting for handles to release...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  NETTOYAGE TERMINE
echo ========================================
echo.
echo Vous pouvez maintenant relancer le build.
REM pause - Removed to prevent hanging in automated build
