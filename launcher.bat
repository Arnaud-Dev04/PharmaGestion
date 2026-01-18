@echo off
REM Launcher pour PharmaGestion
REM Démarre le backend puis l'application Flutter

echo Starting PharmaGestion...

REM Définir le dossier de données
set APPDATA_DIR=%APPDATA%\PharmaGestion
if not exist "%APPDATA_DIR%" mkdir "%APPDATA_DIR%"

REM Démarrer le backend en arrière-plan
echo Starting backend server...
start /B "" "%~dp0backend\PharmaBackend.exe"

REM Attendre que le backend démarre
timeout /t 3 /nobreak >nul

REM Démarrer l'application Flutter
echo Starting application...
start "" "%~dp0app\pharmac_plus.exe"

REM Attendre que l'application se ferme
:wait_loop
timeout /t 5 /nobreak >nul
tasklist /FI "IMAGENAME eq pharmac_plus.exe" 2>NUL | find /I /N "pharmac_plus.exe">NUL
if "%ERRORLEVEL%"=="0" goto wait_loop

REM Tuer le backend quand l'app se ferme
echo Stopping backend server...
taskkill /F /IM PharmaBackend.exe >nul 2>&1

exit
