"""
Pharmac+ - Lanceur Simple
Lance le serveur et ouvre automatiquement le navigateur
"""

import uvicorn
import webbrowser
import threading
import time
import sys
import os

# Import de l'application FastAPI
from main import app

def start_server():
    """Démarre le serveur FastAPI"""
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="error"
    )

def open_browser():
    """Ouvre le navigateur après un délai"""
    time.sleep(3)  # Attend que le serveur démarre
    webbrowser.open('http://127.0.0.1:8000')
    print("\n" + "="*50)
    print("✓ Pharmac+ est lancé !")
    print("✓ Navigateur ouvert sur http://127.0.0.1:8000")
    print("="*50)
    print("\nPour arrêter : Fermez cette fenêtre ou appuyez sur CTRL+C")
    print("-"*50 + "\n")

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  PHARMAC+ - Gestion de Pharmacie")
    print("="*50)
    print("\n[⏳] Démarrage du serveur...")
    
    # Lance le navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Lance le serveur (bloquant)
    start_server()
