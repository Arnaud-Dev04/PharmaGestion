import PyInstaller.__main__
import os

# Build launcher executable
PyInstaller.__main__.run([
    'launcher.py',
    '--onefile',
    # Removed --noconsole to show debug info
    '--name=PharmaGestion',
    '--icon=NONE',
])
