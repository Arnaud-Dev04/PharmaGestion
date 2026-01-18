@echo off
echo ========================================
echo  BUILD PHARMAC+ INSTALLER
echo ========================================
echo.

REM Étape 0a : Nettoyage des processus
echo [0/6] Cleaning up processes...
call clean_processes.bat > nul
echo Processes cleaned.
echo.

REM Étape 0b : Télécharger Visual C++ Redistributables
echo [0/6] Downloading Visual C++ Redistributables...
if not exist "vcredist\vc_redist.x64.exe" (
    echo Visual C++ Redistributables not found, downloading...
    call download_vcredist.bat
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Failed to download VC++ Redistributables
        echo The installer will still be created but may not work on all systems.
        echo You can download them manually and run this script again.
        pause
    )
) else (
    echo Visual C++ Redistributables already downloaded!
)
echo.

REM Étape 1 : Créer le launcher invisible
echo [1/6] Creating Invisible Launcher...
call build_launcher.bat
if not exist "dist\PharmaGestion.exe" (
    echo ERROR: Failed to create launcher executable!
    pause
    exit /b 1
)
echo Launcher created!
echo.



REM Étape 2 : Build Flutter
echo [2/6] Building Flutter Windows App...
cd frontend1
call flutter build windows --release
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Flutter build failed!
    pause
    exit /b 1
)
cd ..
echo Flutter build complete!
echo.

REM Étape 3 : Build Backend
echo [3/6] Building Python Backend...
cd backend
python build_exe.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Backend build failed!
    pause
    exit /b 1
)
cd ..
echo Backend build complete!
echo.

REM Étape 4 : Préparer le dossier de release
echo [4/6] Preparing release folder...

if not exist "release" mkdir release
if exist "release\PharmaGestion" rmdir /s /q "release\PharmaGestion"
mkdir "release\PharmaGestion"

REM Copier le frontend Flutter
echo Copying Flutter app...
xcopy /E /I /Y "frontend1\build\windows\x64\runner\Release" "release\PharmaGestion\app"

REM Copier le backend
echo Copying backend...
mkdir "release\PharmaGestion\backend"
copy "backend\dist\PharmaBackend.exe" "release\PharmaGestion\backend\"

REM Copier la base de données vide
echo Copying database template...
copy "backend\pharmacy_local.db" "release\PharmaGestion\backend\" 2>nul || echo No database template found, will be created on first run.

REM Copier le launcher VBS
echo Copying launcher files...
copy "launcher.vbs" "release\PharmaGestion\"

echo Release folder prepared!
echo.


REM Étape 6 : Créer l'installateur avec Inno Setup
echo [6/6] Creating installer with Inno Setup...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
    if errorlevel 1 (
        echo ERROR: Inno Setup compilation failed!
        pause
        exit /b 1
    ) else (
        echo.
        echo ========================================
        echo  BUILD SUCCESSFUL!
        echo ========================================
        echo.
        echo Installer created: Output\PharmaGestion_Setup.exe
        echo.
        pause
        exit /b 0
    )
) else (
    echo.
    echo WARNING: Inno Setup not found!
    echo Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo.
    echo Manual files are ready in: release\PharmaGestion\
    echo You can create the installer manually with Inno Setup.
    echo.
    pause
    exit /b 0
)

