"""
Pharmac+ Desktop Application Launcher
Lance l'application dans une fenêtre native (pas de navigateur)
"""

import webview
import threading
import time
import uvicorn
import sys
import os

# Import de l'application FastAPI
from main import app

def start_server():
    """Démarre le serveur FastAPI en arrière-plan"""
    # Redirect stdout/stderr pour éviter les erreurs en mode console=False
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="error",
        access_log=False
    )

def main():
    """Point d'entrée principal de l'application desktop"""
    
    # Démarre le serveur dans un thread séparé
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Attend que le serveur démarre
    print("Démarrage du serveur...")
    time.sleep(3)
    
    # Crée la fenêtre de l'application
    window = webview.create_window(
        title='Pharmac+ - Gestion de Pharmacie',
        url='http://127.0.0.1:8000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(1000, 600)
    )
    
    # Lance l'interface graphique
    webview.start(debug=False)

if __name__ == '__main__':
    main()
