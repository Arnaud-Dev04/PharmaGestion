import subprocess
import time
import sys
import os
import socket
from pathlib import Path

def check_backend_ready(max_attempts=30):
    """Vérifie si le backend est prêt en testant la connexion sur le port 8000"""
    for attempt in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            if result == 0:
                print(f"[OK] Backend ready after {attempt + 1} attempts")
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    # Déterminer le chemin d'installation
    if getattr(sys, 'frozen', False):
        # Mode PyInstaller
        app_dir = Path(sys.executable).parent
    else:
        # Mode développement
        app_dir = Path(__file__).parent
    
    backend_exe = app_dir / "backend" / "PharmaBackend.exe"
    frontend_exe = app_dir / "app" / "PharmaGest.exe"
    
    print("="*50)
    print("Starting PharmaGestion...")
    print("="*50)
    
    # Définir le dossier de logs dans APPDATA pour éviter les erreurs de permission
    # C:\Users\User\AppData\Roaming\PharmaGestion
    log_dir = Path(os.getenv('APPDATA')) / "PharmaGestion"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    error_log = log_dir / "launcher_error.txt"
    crash_log = log_dir / "launcher_crash.txt"

    # Vérifier que les fichiers existent
    if not backend_exe.exists():
        with open(error_log, "w") as f:
            f.write(f"[ERROR] Backend not found: {backend_exe}")
        return
    
    if not frontend_exe.exists():
        with open(error_log, "w") as f:
            f.write(f"[ERROR] Frontend not found: {frontend_exe}")
        return
    
    # Démarrer le backend en arrière-plan (avec console visible pour debug)
    print(f"[1/3] Starting backend: {backend_exe}")
    backend_process = subprocess.Popen(
        [str(backend_exe)],
        creationflags=0x08000000  # CREATE_NO_WINDOW - Console cachée
    )
    
    # Attendre que le backend soit prêt
    print("[2/3] Waiting for backend to be ready...")
    if not check_backend_ready():
        with open(error_log, "w") as f:
            f.write("[ERROR] Backend failed to start!")
        backend_process.terminate()
        return
    
    print("[OK] Backend is ready!")
    
    # Démarrer le frontend
    print(f"[3/3] Starting frontend: {frontend_exe}")
    frontend_process = subprocess.Popen([str(frontend_exe)])
    
    # Attendre que le frontend se ferme
    print("[OK] Application started successfully!")
    print("You can now close this window.")
    frontend_process.wait()
    
    # Tuer le backend
    print("\n" + "="*50)
    print("Stopping backend...")
    print("="*50)
    backend_process.terminate()
    try:
        backend_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        backend_process.kill()
    
    print("PharmaGestion closed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # En cas de crash global, on essaie d'écrire dans APPDATA
        try:
            log_dir = Path(os.getenv('APPDATA')) / "PharmaGestion"
            log_dir.mkdir(parents=True, exist_ok=True)
            crash_log = log_dir / "launcher_crash.txt"
            with open(crash_log, "w") as f:
                import traceback
                f.write(f"[ERROR] Unexpected error: {e}\n")
                traceback.print_exc(file=f)
        except:
            pass # Si même ça échoue, on ne peut rien faire silencieusement
