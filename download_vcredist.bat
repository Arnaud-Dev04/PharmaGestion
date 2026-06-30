@echo off
REM ========================================
REM   Download Visual C++ Redistributable
REM ========================================

echo Telechargement de Visual C++ Redistributable...

set VCREDIST_DIR=%~dp0vcredist
if not exist "%VCREDIST_DIR%" mkdir "%VCREDIST_DIR%"

set VCREDIST_URL=https://aka.ms/vs/17/release/vc_redist.x64.exe
set VCREDIST_FILE=%VCREDIST_DIR%\vc_redist.x64.exe

if exist "%VCREDIST_FILE%" (
    echo VC++ Redistributable deja telecharge.
    exit /b 0
)

echo Telechargement depuis: %VCREDIST_URL%
powershell -Command "& {Invoke-WebRequest -Uri '%VCREDIST_URL%' -OutFile '%VCREDIST_FILE%'}"

if errorlevel 1 (
    echo ERREUR: Echec du telechargement
    exit /b 1
)

echo Telechargement termine: %VCREDIST_FILE%
exit /b 0
