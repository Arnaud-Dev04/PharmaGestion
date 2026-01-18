"""
FastAPI application entry point.
Main application configuration and startup.
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database import init_local_db, get_local_db
from app.core.license import license_service
import uvicorn
import os
import sys
import threading
import socket
import time
import webview
import ctypes  # Ajout pour cacher la console
from contextlib import asynccontextmanager
import json

# FORCE HIDE CONSOLE ON STARTUP (ONLY IN FROZEN MODE)
if getattr(sys, "frozen", False) and sys.platform == "win32":
    try:
        # 1. Cacher la fenêtre existante (si elle existe)
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        # 2. Se détacher explicitement de la console
        ctypes.windll.kernel32.FreeConsole()
    except Exception:
        pass

# REDIRECT LOGS TO FILE (ONLY IN FROZEN MODE)
if getattr(sys, "frozen", False):
    try:
        log_dir = os.path.join(os.environ.get('APPDATA', '.'), 'PharmaGestion')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_file = open(os.path.join(log_dir, 'backend.log'), 'w')
        sys.stdout = log_file
        sys.stderr = log_file
    except Exception:
        pass

# =========================
# LIFESPAN EVENT HANDLER
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[*] Starting Pharmacy Management System...")
    print("[*] Initializing local database...")
    # #region agent log
    try:
        with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"id": "log_lifespan_start", "timestamp": int(time.time() * 1000), "location": "main.py:53", "message": "Lifespan startup started", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    except: pass
    # #endregion
    try:
        init_local_db()
        # #region agent log
        try:
            with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"id": "log_db_init_success", "timestamp": int(time.time() * 1000), "location": "main.py:58", "message": "Database initialization succeeded", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        except: pass
        # #endregion
        print("[OK] Local database initialized successfully!")
        print("[OK] Application started successfully!")
    except Exception as e:
        # #region agent log
        try:
            with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"id": "log_db_init_error", "timestamp": int(time.time() * 1000), "location": "main.py:60", "message": "Database initialization error", "data": {"error": str(e), "type": type(e).__name__}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        except: pass
        # #endregion
        print(f"[ERROR] Error during startup: {e}")
    yield
    # Shutdown (if needed)
    print("[*] Shutting down...")

# =========================
# CREATE FASTAPI APP
# =========================

app = FastAPI(
    title="Pharmacy Management System",
    description="Backend API for pharmacy management with offline/online sync support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# LICENSE MIDDLEWARE
# =========================

@app.middleware("http")
async def check_license_middleware(request: Request, call_next):

    if (
        request.method == "OPTIONS"
        or request.url.path.startswith("/assets")
        or request.url.path in [
            "/", "/index.html",
            "/license/status",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    ):
        return await call_next(request)

    # License check is now handled in dependencies.py to allow Super Admin access
    # and to use database session for expiration date check.
    
    return await call_next(request)

@app.get("/license/status", tags=["License"])
async def get_license_status(db: Session = Depends(get_local_db)):
    """
    Get current license status.
    Public endpoint - no authentication required.
    Returns license validity and expiration information.
    """
    status = license_service.get_license_status(db)
    
    # Map backend format to frontend format
    is_expired = status["status"] == "expired"
    is_valid = status["status"] in ["valid", "warning"]
    days_remaining = status.get("days_remaining", 0)
    
    return {
        "is_valid": is_valid,
        "is_expired": is_expired,
        "days_remaining": days_remaining,
        "message": status.get("message", "")
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}

# =========================
# ROUTES
# =========================

from app.routes import (
    auth_router,
    metrics_router,
    stock_router,
    config_router,
    suppliers_router,
    sales_router,
    dashboard_router,
    reports_router,
    settings_router,
    admin_router,
    users_router,
    customers_router
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(metrics_router, tags=["Metrics"])
app.include_router(stock_router, prefix="/stock", tags=["Stock"])
app.include_router(config_router, prefix="/config", tags=["Configuration"])
app.include_router(suppliers_router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(sales_router, prefix="/sales", tags=["Sales"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(customers_router, prefix="/customers", tags=["Customers"])

# =========================
# SERVE REACT FRONTEND
# =========================

if getattr(sys, "frozen", False):
    # En mode frozen (PyInstaller)
    ELECTRON_MODE_CHECK = os.environ.get("PHARMA_ELECTRON_MODE", "false").lower() == "true"
    
    if ELECTRON_MODE_CHECK:
        # Vérifier si on est vraiment en mode production Electron
        # En production : sys.executable est dans resources/backend/
        # En dev : sys.executable est dans backend/dist/
        exe_dir = os.path.dirname(sys.executable)
        
        # Vérifier si le dossier parent s'appelle "resources" (production) ou autre (dev)
        parent_dir = os.path.dirname(exe_dir)
        parent_name = os.path.basename(parent_dir)
        
        print(f"[DEBUG] sys.executable: {sys.executable}")
        print(f"[DEBUG] exe_dir: {exe_dir}")
        print(f"[DEBUG] parent_dir: {parent_dir}")
        print(f"[DEBUG] parent_name: {parent_name}")
        
        if parent_name == "resources":
            # MODE PRODUCTION ELECTRON
            # Structure : resources/backend/PharmaBackend.exe
            # Frontend dans : resources/frontend/
            resources_dir = parent_dir
            frontend_dist = os.path.join(resources_dir, "frontend")
            print(f"[*] Mode: PRODUCTION ELECTRON")
            print(f"[DEBUG] frontend_dist (resources/frontend): {frontend_dist}")
        else:
            # MODE DÉVELOPPEMENT (backend frozen mais lancé depuis le projet)
            # Structure : C:/projet/backend/dist/PharmaBackend.exe
            # exe_dir = C:/projet/backend/dist
            # parent_dir = C:/projet/backend
            # On doit remonter encore pour atteindre C:/projet/
            project_root = os.path.dirname(parent_dir)  # Remonter de "backend" vers le projet
            frontend_dist = os.path.join(project_root, "frontend", "dist")
            print(f"[*] Mode: DÉVELOPPEMENT (backend frozen)")
            print(f"[DEBUG] project_root: {project_root}")
            print(f"[DEBUG] frontend_dist (projet/frontend/dist): {frontend_dist}")
    else:
        # Mode standalone PyInstaller
        frontend_dist = os.path.join(sys._MEIPASS, "frontend_dist")
        print(f"[DEBUG] Mode standalone - frontend_dist: {frontend_dist}")
else:
    # Mode développement (Python script direct)
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    print(f"[DEBUG] Mode développement (script) - frontend_dist: {frontend_dist}")

print(f"[*] Frontend path résolu: {frontend_dist}")
print(f"[*] Frontend path existe: {os.path.exists(frontend_dist)}")

index_html_path = os.path.join(frontend_dist, "index.html")
print(f"[*] index.html path: {index_html_path}")
print(f"[*] index.html existe: {os.path.exists(index_html_path)}")

if os.path.exists(frontend_dist) and not os.path.exists(index_html_path):
    print(f"[WARNING] Le dossier frontend existe mais index.html est manquant")
    try:
        print(f"[WARNING] Contenu du dossier: {os.listdir(frontend_dist)}")
    except Exception as e:
        print(f"[ERROR] Impossible de lister le contenu: {e}")

if (
    os.path.exists(frontend_dist)
    and os.path.exists(index_html_path)
):
    print("[OK] Frontend trouvé et prêt à être servi!")

    assets_path = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_path):
        app.mount(
            "/assets",
            StaticFiles(directory=assets_path),
            name="assets"
        )
        print(f"[OK] Assets montés depuis: {assets_path}")

    # Custom 404 handler for SPA
    # If a route is not found (and not an API/asset path), serve index.html
    from fastapi.exceptions import HTTPException
    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(404)
    async def spa_404_handler(request, exc):
        path = request.url.path
        # If it's an API route, doc, or asset that is missing, return actual 404
        if path.startswith("/api") or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/assets") or path.startswith("/openapi.json"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        
        # Otherwise serve index.html (React Router will handle the rest)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

else:
    print("[WARNING] Frontend dist folder not found. Running API only.")
    print(f"[WARNING] Chemin recherché: {frontend_dist}")
    if os.path.exists(frontend_dist):
        print(f"[WARNING] Le dossier existe mais index.html est manquant")
        try:
            print(f"[WARNING] Contenu du dossier: {os.listdir(frontend_dist)}")
        except Exception as e:
            print(f"[ERROR] Impossible de lister le contenu: {e}")

# =========================
# DESKTOP LAUNCHER
# =========================

def find_free_port(start=8000, end=8200):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free port available")

def run_api(port):
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        reload=False,
        log_config=None
    )

# =========================
# MAIN ENTRY
# =========================

if __name__ == "__main__":
    # Détecter si lancé en mode frozen (exécutable)
    IS_FROZEN = getattr(sys, "frozen", False)
    
    # Par défaut, on force le port 8000 pour la production
    PORT = 8000
    
    print(f"[*] ===== DÉMARRAGE DE PHARMAGESTION BACKEND =====")
    print(f"[*] Frozen mode: {IS_FROZEN}")
    print(f"[*] Target Port: {PORT}")

    # En mode frozen, on se comporte toujours comme un serveur API pour le frontend
    # On évite d'ouvrir une webview Python car le frontend Flutter/Electron s'en charge
    if IS_FROZEN:
        print(f"[*] Démarrage en mode PRODUCTION (Frozen)")
        print(f"[*] Le serveur écoute sur http://127.0.0.1:{PORT}")
        
        # #region agent log
        try:
            with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"id": "log_server_start_attempt", "timestamp": int(time.time() * 1000), "location": "main.py:339", "message": "Attempting to start server", "data": {"port": PORT, "host": "127.0.0.1"}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
        except: pass
        # #endregion
        try:
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=PORT,
                reload=False
            )
        except Exception as e:
            # #region agent log
            try:
                with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"id": "log_server_start_error", "timestamp": int(time.time() * 1000), "location": "main.py:346", "message": "Failed to start server on port 8000", "data": {"error": str(e), "type": type(e).__name__, "port": PORT}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
            except: pass
            # #endregion
            print(f"[ERROR] CRITICAL: Failed to start server on port {PORT}")
            print(f"[ERROR] Detail: {e}")
            raise
            
    else:
        # Mode développement (python main.py)
        # On garde le comportement dynamique pratique pour le dev
        try:
            # Essayer d'abord 8000
            PORT = 8000
            print(f"[*] Démarrage en mode DEV sur port {PORT}")
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=PORT,
                reload=True
            )
        except:
            # Si occupé, chercher un port libre
            PORT = find_free_port()
            print(f"[*] Port 8000 occupé, bascule sur {PORT}")
            run_api(PORT)
            webview.create_window("Pharmacy Dev", f"http://127.0.0.1:{PORT}")
            webview.start()
