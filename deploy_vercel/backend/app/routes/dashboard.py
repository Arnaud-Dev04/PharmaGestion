"""
Dashboard routes - Endpoints for system statistics and analytics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_local_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.schemas.dashboard import DashboardStatsResponse
from app.services import dashboard_service

# Create router
router = APIRouter()


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    summary="Get dashboard statistics"
)
async def get_dashboard_stats(
    days: int = 7,
    start_date: str = None,
    end_date: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get key metrics for the dashboard.
    
    Returns:
        - Total medicines count
        - Sales amount for current week
        - Expired medicines count
        - Low stock medicines count
        - Revenue chart data (last 7 days)
    
    **Accessible to**: All authenticated users
    """
    # Get basic stats
    stats = dashboard_service.get_stats(db, start_date=start_date, end_date=end_date)
    
    # Get revenue chart data
    chart_data = dashboard_service.get_revenue_chart_data(db, days=days, start_date=start_date, end_date=end_date)
    
    # Get top selling products
    # Get top selling products
    top_products = dashboard_service.get_top_selling_products(
        db, 
        limit=15, 
        start_date=start_date, 
        end_date=end_date
    )
    
    # Get sales by day of week
    sales_by_day = dashboard_service.get_sales_by_day_of_week(db, days=days)
    
    # Get sales by hour
    sales_by_hour = dashboard_service.get_sales_by_hour(db, days=days)
    
    return {
        **stats,
        "revenue_chart": chart_data,
        "sales_by_day": sales_by_day,
        "sales_by_hour": sales_by_hour,
        "top_selling_products": top_products
    }


@router.get(
    "/cancelled-sales",
    summary="Get detailed cancelled sales"
)
async def get_cancelled_sales(
    limit: int = 50,
    start_date: str = None,
    end_date: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get list of cancelled sales with user details (who cancelled it).
    """
    return dashboard_service.get_cancelled_sales_details(
        db, 
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

