@echo off
REM Script pour télécharger les Visual C++ Redistributables
REM Ces fichiers seront inclus dans l'installateur

echo ========================================
echo Téléchargement des Visual C++ Redistributables
echo ========================================
echo.

REM Créer le dossier pour les redistributables
if not exist "vcredist" mkdir vcredist

echo [1/2] Téléchargement de VC++ 2015-2022 Redistributable (x64)...
powershell -Command "& {Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vcredist\vc_redist.x64.exe'}"

if exist "vcredist\vc_redist.x64.exe" (
    echo ✅ VC++ x64 téléchargé avec succès
) else (
    echo ❌ Erreur lors du téléchargement de VC++ x64
    goto :error
)

echo.
echo [2/2] Téléchargement de VC++ 2015-2022 Redistributable (x86)...
powershell -Command "& {Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x86.exe' -OutFile 'vcredist\vc_redist.x86.exe'}"

if exist "vcredist\vc_redist.x86.exe" (
    echo ✅ VC++ x86 téléchargé avec succès
) else (
    echo ❌ Erreur lors du téléchargement de VC++ x86
    goto :error
)

echo.
echo ========================================
echo ✅ Téléchargement terminé avec succès!
echo ========================================
echo.
echo Les fichiers suivants ont été téléchargés:
dir /b vcredist\*.exe
echo.
echo Ces fichiers seront inclus dans l'installateur.
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo ❌ Erreur lors du téléchargement
echo ========================================
echo.
echo Vous pouvez télécharger manuellement depuis:
echo https://aka.ms/vs/17/release/vc_redist.x64.exe
echo https://aka.ms/vs/17/release/vc_redist.x86.exe
echo.
echo Placez les fichiers dans le dossier 'vcredist\'
echo.
pause
exit /b 1
