"""
Vercel serverless entry point for FastAPI backend.
"""
import sys
import os

# ─── Fix Python path for Vercel ───
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(root_dir, "backend")
sys.path.insert(0, backend_dir)
sys.path.insert(0, root_dir)

# ─── Set environment variables BEFORE any import ───
# Use /tmp for SQLite on Vercel (only writable directory)
db_path = "/tmp/pharmacy_local.db"
os.environ["DB_URL_LOCAL"] = f"sqlite:///{db_path}"
# Disable MySQL remote DB (pymysql not available on Vercel)
os.environ["DB_URL_REMOTE"] = f"sqlite:///{db_path}"
os.environ.setdefault("SECRET_KEY", "pharma-gest-s3cur3-k3y-2026-vercel")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "720")
os.environ.setdefault("DEBUG", "False")

# ─── Create FastAPI app ───
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PharmaGestion API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Health check (always works) ───
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "platform": "vercel",
        "backend_dir": backend_dir,
        "exists": os.path.exists(os.path.join(backend_dir, "app")),
    }

# ─── Import backend and register routes ───
_init_error = None
try:
    from app.database import init_local_db
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
        customers_router,
        license_router,
        medicine_pricing_router,
        pos_router,
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
    app.include_router(license_router, prefix="/license", tags=["License"])
    app.include_router(medicine_pricing_router, prefix="/pricing", tags=["Pricing"])
    app.include_router(pos_router, prefix="/pos", tags=["POS"])

    # Initialize database in /tmp
    init_local_db()
    print("[OK] Backend fully initialized on Vercel")

except Exception as e:
    import traceback
    _init_error = traceback.format_exc()
    print(f"[ERROR] Backend init failed: {_init_error}")

# ─── Debug route (shows error details) ───
@app.get("/debug/error")
async def debug_error():
    return {
        "error": _init_error,
        "backend_dir": backend_dir,
        "exists_backend": os.path.exists(backend_dir),
        "exists_app": os.path.exists(os.path.join(backend_dir, "app")),
        "sys_path": sys.path[:8],
        "db_url": os.environ.get("DB_URL_LOCAL"),
        "cwd": os.getcwd(),
        "listdir_root": os.listdir(root_dir) if os.path.exists(root_dir) else "N/A",
    }
