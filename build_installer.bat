@echo off
echo ========================================
echo   PharmaGestion - Build Installer
echo ========================================
echo.

REM === Configuration ===
set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend
set FRONTEND_DIR=%PROJECT_ROOT%frontend1
set BUILD_DIR=%PROJECT_ROOT%build
set DIST_DIR=%PROJECT_ROOT%dist
set OUTPUT_DIR=%PROJECT_ROOT%Output
set VCREDIST_DIR=%PROJECT_ROOT%vcredist

REM === Arret des processus en cours ===
echo [0/6] Arret des processus en cours...
taskkill /F /IM PharmaBackend.exe >nul 2>&1
taskkill /F /IM PharmaGest.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM === Nettoyage ===
echo [1/6] Nettoyage des anciens builds...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"

mkdir "%BUILD_DIR%"
mkdir "%DIST_DIR%"
mkdir "%OUTPUT_DIR%"

REM === Backend - Compilation avec PyInstaller ===
echo.
echo [2/6] Compilation du backend...
cd "%BACKEND_DIR%"

REM Activer l'environnement virtuel si disponible
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Compiler avec PyInstaller (mode onedir = demarrage rapide)
pyinstaller --noconfirm --name=PharmaBackend --noconsole ^
  --distpath="%DIST_DIR%" ^
  --workpath="%BUILD_DIR%\backend" ^
  --specpath="%BUILD_DIR%" ^
  --hidden-import=uvicorn.logging ^
  --hidden-import=uvicorn.loops ^
  --hidden-import=uvicorn.loops.auto ^
  --hidden-import=uvicorn.protocols ^
  --hidden-import=uvicorn.protocols.http ^
  --hidden-import=uvicorn.protocols.http.auto ^
  --hidden-import=uvicorn.protocols.websockets ^
  --hidden-import=uvicorn.protocols.websockets.auto ^
  --hidden-import=uvicorn.lifespan ^
  --hidden-import=uvicorn.lifespan.on ^
  --hidden-import=uvicorn.lifespan.off ^
  --hidden-import=passlib.handlers.bcrypt ^
  --hidden-import=bcrypt ^
  --hidden-import=email_validator ^
  --hidden-import=pydantic ^
  --hidden-import=pydantic_settings ^
  --hidden-import=dotenv ^
  --hidden-import=jose ^
  --hidden-import=reportlab ^
  --hidden-import=openpyxl ^
  --hidden-import=sqlalchemy.dialects.sqlite ^
  --hidden-import=multipart ^
  main.py

if errorlevel 1 (
    echo ERREUR: Echec de la compilation du backend
    pause
    exit /b 1
)

echo Backend compile avec succes!

REM === Frontend - Build Flutter Windows ===
echo.
echo [3/6] Compilation du frontend Flutter...
cd "%FRONTEND_DIR%"

REM Nettoyer et recuperer les dependances
call flutter clean
call flutter pub get

REM Build pour Windows
call flutter build windows --release

if errorlevel 1 (
    echo ERREUR: Echec de la compilation du frontend
    pause
    exit /b 1
)

echo Frontend compile avec succes!

REM === Copie des fichiers ===
echo.
echo [4/6] Preparation des fichiers...

REM Copier le frontend build
xcopy /E /I /Y "%FRONTEND_DIR%\build\windows\x64\runner\Release" "%DIST_DIR%\frontend"

REM Le backend est deja dans %DIST_DIR%\PharmaBackend\ (mode onedir)

REM Copier les scripts de lancement
if exist "%PROJECT_ROOT%\launcher.vbs" (
    copy "%PROJECT_ROOT%\launcher.vbs" "%DIST_DIR%\"
)
if exist "%PROJECT_ROOT%\Lancer_PharmaGestion.bat" (
    copy "%PROJECT_ROOT%\Lancer_PharmaGestion.bat" "%DIST_DIR%\"
)
if exist "%FRONTEND_DIR%\windows\runner\resources\app_icon.ico" (
    copy "%FRONTEND_DIR%\windows\runner\resources\app_icon.ico" "%DIST_DIR%\icon.ico"
)

echo Fichiers prepares!

REM === Telechargement VC++ Redistributables ===
echo.
echo [5/6] Verification des redistributables VC++...

if not exist "%VCREDIST_DIR%" mkdir "%VCREDIST_DIR%"

if not exist "%VCREDIST_DIR%\vc_redist.x64.exe" (
    echo Telechargement de VC++ Redistributable...
    if exist "%PROJECT_ROOT%\download_vcredist.bat" (
        call "%PROJECT_ROOT%\download_vcredist.bat"
    ) else if exist "%PROJECT_ROOT%\_ARCHIVE\root_scripts\download_vcredist.bat" (
        call "%PROJECT_ROOT%\_ARCHIVE\root_scripts\download_vcredist.bat"
    ) else (
        echo AVERTISSEMENT: Script de telechargement VC++ non trouve
        echo Telechargez manuellement depuis: https://aka.ms/vs/17/release/vc_redist.x64.exe
    )
)

REM === Creation de l'installateur avec Inno Setup ===
echo.
echo [6/6] Creation de l'installateur...

REM Creer le script Inno Setup
(
echo [Setup]
echo AppName=PharmaGestion
echo AppVersion=1.0.0
echo AppPublisher=PharmaGestion
echo DefaultDirName={localappdata}\PharmaGestion
echo DefaultGroupName=PharmaGestion
echo OutputDir=%OUTPUT_DIR%
echo OutputBaseFilename=PharmaGestion_Setup
echo Compression=lzma2
echo SolidCompression=yes
echo SetupIconFile=%DIST_DIR%\icon.ico
echo PrivilegesRequired=lowest
echo.
echo [Files]
echo Source: "%DIST_DIR%\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
echo Source: "%VCREDIST_DIR%\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: VCRedistNeedsInstall
echo.
echo [Tasks]
echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
echo.
echo [Icons]
echo Name: "{group}\PharmaGestion"; Filename: "{app}\launcher.vbs"; IconFilename: "{app}\icon.ico"
echo Name: "{autodesktop}\PharmaGestion"; Filename: "{app}\launcher.vbs"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
echo.
echo [Run]
echo Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installation de Visual C++ Redistributable..."; Check: VCRedistNeedsInstall
echo Filename: "{app}\launcher.vbs"; Description: "Lancer PharmaGestion"; Flags: nowait postinstall skipifsilent shellexec
echo.
echo [Code]
echo function VCRedistNeedsInstall: Boolean;
echo begin
echo   Result := True;
echo end;
) > "%BUILD_DIR%\installer.iss"

REM Compiler avec Inno Setup
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%BUILD_DIR%\installer.iss"
    
    if errorlevel 1 (
        echo ERREUR: Echec de la creation de l'installateur
        pause
        exit /b 1
    )
    
    echo.
    echo ========================================
    echo   BUILD TERMINE AVEC SUCCES!
    echo ========================================
    echo.
    echo Installateur cree: %OUTPUT_DIR%\PharmaGestion_Setup.exe
    echo.
) else (
    echo.
    echo AVERTISSEMENT: Inno Setup non trouve
    echo Les fichiers sont prets dans: %DIST_DIR%
    echo Installez Inno Setup pour creer l'installateur: https://jrsoftware.org/isdl.php
    echo.
)

pause
