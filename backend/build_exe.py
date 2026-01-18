import PyInstaller.__main__
import os
import sys
import shutil

# Nettoyage agressif des anciens builds pour garantir que --noconsole s'applique
print("🧹 Cleaning previous build artifacts...")
for dir_name in ['build', 'dist']:
    if os.path.exists(dir_name):
        try:
            shutil.rmtree(dir_name)
            print(f"   - Removed {dir_name}")
        except Exception as e:
            print(f"   - Failed to remove {dir_name}: {e}")

# Configuration PyInstaller pour le backend
# Inclut automatiquement toutes les DLLs Visual C++ nécessaires
pyinstaller_args = [
    'main.py',
    '--onefile',
    '--name=PharmaBackend',
    '--add-data=app;app',
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.loops',
    '--hidden-import=uvicorn.loops.auto',
    '--hidden-import=uvicorn.protocols',
    '--hidden-import=uvicorn.protocols.http',
    '--hidden-import=uvicorn.protocols.http.auto',
    '--hidden-import=uvicorn.protocols.websockets',
    '--hidden-import=uvicorn.protocols.websockets.auto',
    '--hidden-import=uvicorn.lifespan',
    '--hidden-import=uvicorn.lifespan.on',
    '--hidden-import=sqlite3',
    '--hidden-import=reportlab',
    '--hidden-import=reportlab.pdfgen',
    '--hidden-import=reportlab.lib',
    '--hidden-import=webview',
    '--collect-all=reportlab',
    '--noconsole',  # Pas de fenêtre console
    # Inclure toutes les DLLs binaires nécessaires (Visual C++ Runtime, etc.)
    '--collect-binaries=*',
]

# Ajouter le chemin des DLLs système Windows si disponible
if sys.platform == 'win32':
    # PyInstaller inclura automatiquement les DLLs Visual C++ Runtime
    pyinstaller_args.extend([
        '--noupx',  # Désactiver UPX pour éviter les problèmes de compatibilité
    ])

print("🔧 Building PharmaBackend.exe with all required DLLs...")
print("📦 This will include Visual C++ Runtime libraries (MSVCP140.dll, etc.)")
PyInstaller.__main__.run(pyinstaller_args)
