"""Routes package."""

from .auth import router as auth_router
from .metrics import router as metrics_router
from .stock import router as stock_router
from .config import router as config_router
from .suppliers import router as suppliers_router
from .sales import router as sales_router
from .dashboard import router as dashboard_router
from .reports import router as reports_router
from .settings import router as settings_router
from .admin import router as admin_router
from .users import router as users_router
from .customers import router as customers_router

__all__ = [
    "auth_router",
    "metrics_router",
    "stock_router",
    "config_router",
    "suppliers_router",
    "sales_router",
    "dashboard_router",
    "reports_router",
    "settings_router",
    "admin_router",
    "users_router",
    "customers_router",
]
