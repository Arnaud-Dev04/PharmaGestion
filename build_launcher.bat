@echo off
echo ========================================
echo  BUILD LAUNCHER (PyInstaller)
echo ========================================
echo.

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building launcher with PyInstaller...
pyinstaller PharmaGestion.spec

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller failed!
    exit /b 1
)

if exist "dist\PharmaGestion.exe" (
    echo.
    echo Launcher created successfully: dist\PharmaGestion.exe
    echo.
) else (
    echo.
    echo ERROR: Launcher executable not found after build!
    exit /b 1
)
