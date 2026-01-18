"""
Dashboard service layer - Analytics and aggregation logic.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, cast, Date
from datetime import datetime, timedelta, date
from typing import List, Dict, Any

from app.models.medicine import Medicine
from app.models.sales import Sale


from typing import Optional

def get_stats(db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get key metrics for the dashboard.
    
    Returns:
        Dict containing:
        - total_medicines: Total distinct medicines (count of rows)
        - sales_this_week: Sum of sales amounts for current week
        - medicines_expired: Count of expired medicines
        - medicines_low_stock: Count of low stock medicines
    """
    import traceback

    # Define today at the start
    today = date.today()

    # 1. Total medicines
    try:
        total_medicines = db.query(Medicine).filter(Medicine.is_active == True).count()
    except Exception:
        print("Error getting total medicines:")
        traceback.print_exc()
        total_medicines = 0
    
    # 2. Weekly sales
    try:
        week_ago = today - timedelta(days=7)
        weekly_sales = db.query(func.sum(Sale.total_amount)).filter(
            func.date(Sale.date) >= week_ago
        ).scalar() or 0
    except Exception:
        print("Error getting weekly sales:")
        traceback.print_exc()
        weekly_sales = 0

    # 3. Total suppliers
    try:
        from app.models.supplier import Supplier
        total_suppliers = db.query(Supplier).count()
    except Exception:
        print("Error getting total suppliers:")
        traceback.print_exc()
        total_suppliers = 0

    # 4. Total revenue
    try:
        total_revenue = db.query(func.sum(Sale.total_amount)).scalar() or 0
    except Exception:
        print("Error getting total revenue:")
        traceback.print_exc()
        total_revenue = 0
    
    # 5. Expired medicines (expired_medicines)
    try:
        expired_medicines = db.query(Medicine).filter(
            and_(
                Medicine.expiry_date.isnot(None),
                Medicine.expiry_date <= today,
                Medicine.is_active == True
            )
        ).count()
    except Exception:
        print("Error getting expired medicines:")
        traceback.print_exc()
        expired_medicines = 0
    
    # 6. Low stock medicines (low_stock_medicines)
    try:
        low_stock_medicines = db.query(Medicine).filter(
            Medicine.quantity <= Medicine.min_stock_alert,
            Medicine.is_active == True
        ).count()
    except Exception:
        print("Error getting low stock medicines:")
        traceback.print_exc()
        low_stock_medicines = 0

    # 7. Cancelled sales
    try:
        from app.models.sales import SaleStatus
        
        query = db.query(Sale).filter(Sale.status == SaleStatus.CANCELLED)
        
        if start_date and end_date:
            dt_start_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            dt_end_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(
                func.date(Sale.date) >= dt_start_obj,
                func.date(Sale.date) <= dt_end_obj
            )
            
        cancelled_sales = query.count()
    except Exception:
        print("Error getting cancelled sales:")
        traceback.print_exc()
        cancelled_sales = 0

    # 8. Recent sales
    try:
        recent_sales = []
        # Récupérer les 5 dernières ventes
        recent_sales_data = db.query(Sale).order_by(Sale.date.desc()).limit(5).all()
        for sale in recent_sales_data:
            recent_sales.append({
                "id": sale.id,
                "code": sale.code,
                "total_amount": float(sale.total_amount),
                "date": sale.date.isoformat() if sale.date else None
            })
    except Exception:
        print("Error getting recent sales:")
        traceback.print_exc()
        recent_sales = []

    # Expiring soon logic update:
    try:
        # Check if expiry_date is between today and today + expiry_alert_threshold days
        from sqlalchemy import text
        
        expiring_soon_data = db.query(Medicine).filter(
            Medicine.expiry_date > today,
            Medicine.is_active == True,
            text(f"expiry_date <= date('{today}', '+' || expiry_alert_threshold || ' days')")
        ).order_by(Medicine.expiry_date).limit(10).all()
        
        expiring_soon = [
            {
                "name": m.name,
                "code": m.code,
                "expiry_date": m.expiry_date,
                "quantity": m.quantity
            } for m in expiring_soon_data
        ]
    except Exception:
        print("Error getting expiring soon:")
        traceback.print_exc()
        expiring_soon = []
        
    # Low stock details
    try:
        low_stock_data = db.query(Medicine).filter(
            Medicine.quantity <= Medicine.min_stock_alert,
            Medicine.is_active == True
        ).order_by(Medicine.quantity.asc()).limit(10).all()
        
        low_stock_list = [
            {
                "name": m.name,
                "code": m.code,
                "quantity": m.quantity,
                "min_stock": m.min_stock_alert
            } for m in low_stock_data
        ]
    except Exception:
        print("Error getting low stock list:")
        traceback.print_exc()
        low_stock_list = []
    
    return {
        "total_medicines": total_medicines,
        "weekly_sales": float(weekly_sales),
        "total_suppliers": total_suppliers,
        "expired_medicines": expired_medicines,
        "low_stock_medicines": low_stock_medicines,
        "total_revenue": float(total_revenue),
        "cancelled_sales": cancelled_sales,
        "recent_sales": recent_sales,
        "expiring_soon": expiring_soon,
        "low_stock_list": low_stock_list
    }


def get_cancelled_sales_details(db: Session, limit: int = 50, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get detailed list of cancelled sales.
    """
    try:
        from app.models.sales import Sale, SaleStatus
        from app.models.user import User
        
        query = db.query(Sale, User).outerjoin(
            User, Sale.cancelled_by == User.id
        ).filter(
            Sale.status == SaleStatus.CANCELLED
        )
        
        if start_date and end_date:
            dt_start_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            dt_end_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(
                func.date(Sale.date) >= dt_start_obj,
                func.date(Sale.date) <= dt_end_obj
            )
            
        query = query.order_by(
            Sale.cancelled_at.desc()
        ).limit(limit)
        
        results = query.all()
        
        detailed_sales = []
        for sale, canceller in results:
            sale_items = []
            for item in sale.items:
                sale_items.append({
                    "medicine_name": item.medicine.name if item.medicine else "Unknown"
                })

            # Determine name to display
            # Request: "je veux un nom complet de l'utilisateur"
            user_name = "N/A"
            if canceller:
                if canceller.first_name and canceller.last_name:
                    user_name = f"{canceller.first_name} {canceller.last_name}"
                elif canceller.username:
                    user_name = canceller.username
            
            detailed_sales.append({
                "id": sale.id,
                "user_id": sale.user_id, # Original seller
                "user_name": user_name, # The one who cancelled
                "date": sale.date,
                "cancelled_at": sale.cancelled_at,
                "total_amount": sale.total_amount,
                "items": sale_items
            })
            
        return detailed_sales
    except Exception:
        import traceback
        print("Error getting cancelled sales details:")
        traceback.print_exc()
        return []


def get_revenue_chart_data(db: Session, days: int = 7, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get daily revenue for the last N days.
    
    Args:
        db: Database session
        days: Number of days to verify (default 7)
        
    Returns:
        List of dicts with 'date' and 'amount'
    """
    try:
        if start_date and end_date:
            # Use provided range
            dt_start_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            dt_end_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            start_date_val = dt_start_obj
            end_date_val = dt_end_obj
        else:
            # Use last N days
            end_date_val = date.today()
            start_date_val = end_date_val - timedelta(days=days - 1)
        
        daily_sales = db.query(
            func.date(Sale.date).label('sale_date'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            func.date(Sale.date) >= start_date_val,
            func.date(Sale.date) <= end_date_val
        ).group_by(
            func.date(Sale.date)
        ).all()
        
        # Convert result to dict
        sales_map = {str(d[0]): float(d[1] or 0) for d in daily_sales}
        
        # Generate full list
        chart_data = []
        current_date = start_date_val
        while current_date <= end_date_val:
            date_str = current_date.isoformat()
            chart_data.append({
                "date": date_str,
                "amount": sales_map.get(date_str, 0.0)
            })
            current_date += timedelta(days=1)
            
        return chart_data
    except Exception:
        import traceback
        print("Error getting revenue chart data:")
        traceback.print_exc()
        return []


def get_top_selling_products(db: Session, limit: int = 15, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get top selling products/medicines.
    
    Args:
        db: Database session
        limit: Number of top products to return (default 5)
        
    Returns:
        List of dicts with medicine info and total sold quantity
    """
    from app.models.sales import SaleItem
    
    try:
        # Group sale items by medicine and sum quantities
        query = db.query(
            Medicine.id,
            Medicine.name,
            Medicine.code,
            func.sum(SaleItem.quantity).label('total_sold')
        ).join(
            SaleItem, SaleItem.medicine_id == Medicine.id
        )
        
        if start_date and end_date:
            # Need to join with Sale to filter by date
            query = query.join(Sale, SaleItem.sale_id == Sale.id)
            dt_start_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            dt_end_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(
                func.date(Sale.date) >= dt_start_obj,
                func.date(Sale.date) <= dt_end_obj
            )
            
        top_products = query.group_by(
            Medicine.id, Medicine.name, Medicine.code
        ).order_by(
            func.sum(SaleItem.quantity).desc()
        ).limit(limit).all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "total_sold": int(p.total_sold or 0)
            } for p in top_products
        ]
    except Exception:
        import traceback
        print("Error getting top selling products:")
        traceback.print_exc()
        return []


def get_sales_by_day_of_week(db: Session, days: int = 7) -> List[Dict[str, Any]]:
    """
    Aggregate sales by day of week.
    Returns list of {day: "Monday", amount: 123.0}
    """
    try:
        from app.models.sales import Sale
        from sqlalchemy import text
        
        start_date = date.today() - timedelta(days=days - 1)
        
        # SQLite strftime('%w', date) returns 0 (Sunday) - 6 (Saturday)
        results = db.query(
            func.strftime('%w', Sale.date).label('dow'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            func.date(Sale.date) >= start_date
        ).group_by(text('dow')).all()
        
        # Map 0-6 to day names
        days_map = {
            '0': 'Sunday', '1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', 
            '4': 'Thursday', '5': 'Friday', '6': 'Saturday'
        }
        
        results_dict = {str(r[0]): float(r[1] or 0) for r in results}
        
        data = []
        for i in range(7):
            idx = str(i)
            data.append({
                "day": days_map[idx],
                "amount": results_dict.get(idx, 0.0)
            })
            
        return data
    except Exception:
        import traceback
        print("Error getting sales by day of week:")
        traceback.print_exc()
        return []


def get_sales_by_hour(db: Session, days: int = 7) -> List[Dict[str, Any]]:
    """
    Aggregate sales by hour of day.
    Returns list of {hour: 0-23, amount: 123.0}
    """
    try:
        from app.models.sales import Sale
        from sqlalchemy import text
        
        start_date = date.today() - timedelta(days=days - 1)
        
        results = db.query(
            func.strftime('%H', Sale.date).label('hour'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            func.date(Sale.date) >= start_date
        ).group_by(text('hour')).order_by(text('hour')).all()
        
        results_dict = {int(r[0]): float(r[1] or 0) for r in results}
        
        data = []
        # Fill all 24 hours
        for h in range(24):
            data.append({
                "hour": h,
                "amount": results_dict.get(h, 0.0)
            })
            
        return data
    except Exception:
        import traceback
        print("Error getting sales by hour:")
        traceback.print_exc()
        return []

