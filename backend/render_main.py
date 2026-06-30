"""
render_main.py — Point d'entrée Render/Production (Linux).

Ce fichier est utilisé uniquement sur Render.
Il démarre uniquement l'API FastAPI sans le code Desktop Windows.
Start Command Render : uvicorn render_main:app --host 0.0.0.0 --port $PORT
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# ── Import des routes ─────────────────────────────────────────────────────────
from app.routes.auth import router as auth_router
from app.routes.metrics import router as metrics_router
from app.routes.stock import router as stock_router
from app.routes.config import router as config_router
from app.routes.suppliers import router as suppliers_router
from app.routes.sales import router as sales_router
from app.routes.dashboard import router as dashboard_router
from app.routes.reports import router as reports_router
from app.routes.settings import router as settings_router
from app.routes.admin import router as admin_router
from app.routes.users import router as users_router
from app.routes.customers import router as customers_router
from app.routes.medicine_pricing import router as medicine_pricing_router
from app.routes.pos import router as pos_router

# Routers optionnels (peuvent ne pas exister sur Render selon la version)
try:
    from app.routes.license import router as license_router
    _has_license = True
except ImportError:
    license_router = None
    _has_license = False

try:
    from app.routes.sync import router as sync_router
    _has_sync = True
except ImportError:
    sync_router = None
    _has_sync = False

from app.database import init_local_db


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialise la base de données au démarrage."""
    print("[Render] Initialisation de la base de données...")
    try:
        init_local_db()
        print("[Render] Base de données prête.")
    except Exception as e:
        print(f"[Render][WARNING] DB init warning: {e}")
    yield
    print("[Render] Arrêt du serveur.")


# ── Application FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="PharmaGestion API",
    description="Système de gestion de pharmacie — API REST",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(auth_router,             prefix="/auth",     tags=["Auth"])
app.include_router(metrics_router,                              tags=["Metrics"])
app.include_router(stock_router,            prefix="/stock",    tags=["Stock"])
app.include_router(config_router,           prefix="/config",   tags=["Config"])
app.include_router(suppliers_router,        prefix="/suppliers",tags=["Suppliers"])
app.include_router(sales_router,            prefix="/sales",    tags=["Sales"])
app.include_router(dashboard_router,        prefix="/dashboard",tags=["Dashboard"])
app.include_router(reports_router,          prefix="/reports",  tags=["Reports"])
app.include_router(settings_router,         prefix="/settings", tags=["Settings"])
app.include_router(admin_router,            prefix="/admin",    tags=["Admin"])
app.include_router(users_router,            prefix="/users",    tags=["Users"])
app.include_router(customers_router,        prefix="/customers",tags=["Customers"])
app.include_router(medicine_pricing_router, prefix="/pricing",  tags=["Pricing"])
app.include_router(pos_router,              prefix="/pos",      tags=["POS"])
if _has_license and license_router:
    app.include_router(license_router,      prefix="/license",  tags=["License"])
if _has_sync and sync_router:
    app.include_router(sync_router,         prefix="/sync",     tags=["Sync"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "PharmaGestion API", "version": "2.0.0"}


@app.get("/", tags=["Health"])
async def root():
    return {"message": "PharmaGestion API — v2.0.0", "docs": "/docs"}
