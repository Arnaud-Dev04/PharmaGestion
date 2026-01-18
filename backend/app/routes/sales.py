"""
Sales routes - POS endpoints for creating sales and generating invoices.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_local_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.schemas.sales import SaleCreate, SaleResponse, SaleItemResponse
from app.schemas.customer import CustomerResponse
from app.services import sales_service, pdf_service

# Create router
router = APIRouter()


def enrich_sale_response(sale, db: Session) -> dict:
    """Enrich sale response with calculated fields and nested data."""
    # Get items with medicine details
    items = []
    for item in sale.items:
        items.append(SaleItemResponse(
            id=item.id,
            medicine_id=item.medicine_id,
            medicine_name=item.medicine.name,
            medicine_code=item.medicine.code,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        ))
    
    # Calculate bonus earned
    bonus_earned = sales_service.calculate_bonus_points(sale.total_amount) if sale.customer else 0
    
    # Build response
    
    # helper for full name
    def get_full_name(user):
        if not user:
            return None
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        return user.username

    response_data = {
        "id": sale.id,
        "code": sale.code,
        "total_amount": sale.total_amount,
        "payment_method": sale.payment_method,
        "date": sale.date,
        "user_id": sale.user_id,
        "user_name": get_full_name(sale.user) or "Unknown",
        "status": getattr(sale, 'status', 'completed'),
        "cancelled_at": getattr(sale, 'cancelled_at', None),
        "customer_id": sale.customer_id,
        "items": items,
        "customer": CustomerResponse.model_validate(sale.customer) if sale.customer else None,
        "bonus_earned": bonus_earned,
        "cancelled_by": get_full_name(sale.cancelled_by_user),
        "cancelled_at": sale.cancelled_at
    }
    
    return response_data


@router.post(
    "/create",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sale (POS)"
)
async def create_sale(
    sale_data: SaleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Create a new sale transaction.
    
    This endpoint:
    - Validates stock availability
    - Creates or retrieves customer (if phone provided)
    - Generates invoice code
    - Creates sale and items
    - Decrements stock
    - Adds bonus points to customer
    
    **Accessible to**: All authenticated users (Admin, Pharmacist)
    
    **Errors**:
    - 400: Insufficient stock or validation error
    - 404: Medicine not found
    """
    try:
        sale = sales_service.create_sale(
            db=db,
            user_id=current_user.id,
            sale_data=sale_data
        )
        
        return enrich_sale_response(sale, db)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sale: {str(e)}"
        )



@router.get(
    "/history",
    summary="Get sales history with filters"
)
async def get_sales_history(
    page: int = 1,
    page_size: int = 50,
    start_date: str = None,
    end_date: str = None,
    min_amount: float = None,
    max_amount: float = None,
    user_id: int = None,
    status_filter: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get paginated sales history with optional filters.
    
    filters:
    - start_date (YYYY-MM-DD)
    - end_date (YYYY-MM-DD)
    - min_amount / max_amount
    - user_id
    - status_filter ("cancelled" or "completed")
    """
    from datetime import datetime
    
    # Process filters
    filters = {}
    if start_date:
        try:
            filters["start_date"] = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            pass
            
    if end_date:
        try:
            filters["end_date"] = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            pass
            
    if min_amount is not None:
        filters["min_amount"] = min_amount
        
    if max_amount is not None:
        filters["max_amount"] = max_amount
        
    if user_id:
        filters["user_id"] = user_id
        
    if status_filter:
        filters["status"] = status_filter
    
    # Get history
    sales, total = sales_service.get_sales_history(
        db=db,
        page=page,
        page_size=page_size,
        filters=filters
    )
    
    # Format response
    from app.schemas.common import PaginatedResponse
    
    # Enrich items
    enriched_sales = [enrich_sale_response(sale, db) for sale in sales]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        items=enriched_sales
    )



@router.post(
    "/{sale_id}/cancel",
    response_model=dict,
    summary="Cancel a sale (Restock items)"
)
async def cancel_sale(
    sale_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Cancel a sale, refund items to stock, and mark as cancelled.
    
    **Side effects**:
    - Updates Sale status to 'cancelled'
    - Increases Medicine stock by item quantity
    """
    from datetime import datetime
    
    # Get sale
    sale = sales_service.get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale with ID {sale_id} not found"
        )
        
    if sale.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale is already cancelled"
        )
    
    # Restore stock for each item
    for item in sale.items:
        medicine = item.medicine  # Access relationship
        if medicine:
            # We add back the quantity sold
            medicine.quantity += item.quantity
            
    # Update sale status
    sale.status = "cancelled"
    sale.cancelled_at = datetime.utcnow()
    sale.cancelled_by = current_user.id
    
    # If customer involved, should we revert points? 
    # For now, let's keep it simple. Usually points are deducted.
    # TODO: Implement point deduction if loyal program is strict.
    
    db.commit()
    db.refresh(sale)
    
    return {"message": "Sale cancelled successfully", "sale_id": sale.id}


@router.get(
    "/medicine-stats",
    summary="Get medicine sales statistics by period"
)
async def get_medicine_sales_stats(
    start_date: str = None,
    end_date: str = None,
    limit: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get aggregated sales statistics per medicine for a given period.
    
    Returns list of medicines with total quantity sold and revenue.
    Optional limit to get top N items.
    """
    from datetime import datetime, timedelta
    from app.models.sales import SaleItem, Sale
    from app.models.medicine import Medicine
    from sqlalchemy import func
    
    # Build query
    query = db.query(
        Medicine.id,
        Medicine.name,
        Medicine.code,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.total_price).label('total_revenue')
    ).join(
        SaleItem, SaleItem.medicine_id == Medicine.id
    ).join(
        Sale, Sale.id == SaleItem.sale_id
    )
    
    # Apply date filters
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Sale.date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            # Add one day to include the end date
            end = end + timedelta(days=1)
            query = query.filter(Sale.date < end)
        except ValueError:
            pass
    
    # Group and order
    query = query.group_by(
        Medicine.id, Medicine.name, Medicine.code
    ).order_by(
        func.sum(SaleItem.quantity).desc()
    )
    
    # Apply limit if provided
    if limit:
        query = query.limit(limit)
        
    results = query.all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "total_quantity": int(r.total_quantity or 0),
            "total_revenue": float(r.total_revenue or 0.0)
        }
        for r in results
    ]


@router.get(
    "/{sale_id}",
    response_model=dict,
    summary="Get sale details"
)
async def get_sale(
    sale_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get details of a specific sale.
    
    **Accessible to**: All authenticated users
    """
    sale = sales_service.get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale with ID {sale_id} not found"
        )
    
    return enrich_sale_response(sale, db)


@router.get(
    "/{sale_id}/invoice",
    summary="Download sale invoice as PDF"
)
async def download_invoice(
    sale_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download a PDF invoice for a sale.
    
    **Accessible to**: All authenticated users
    """
    try:
        # Get sale details
        sale = sales_service.get_sale_by_id(db, sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sale with ID {sale_id} not found"
            )
        
        # Prepare invoice data
        invoice_data = {
            "invoice_code": sale.code,
            "date": sale.date,  # Keep as datetime object
            "seller": sale.user.username if sale.user else "N/A",
            "customer": {
                "name": f"{sale.customer.first_name} {sale.customer.last_name}",
                "phone": sale.customer.phone,
                "points_earned": 0  # Calculate if needed
            } if sale.customer else None,
            "payment_method": sale.payment_method,
            "items": [
                {
                    "medicine_name": item.medicine.name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price
                }
                for item in sale.items
            ],
            "total_amount": sale.total_amount
        }
        
        # Generate PDF
        pdf_buffer = pdf_service.generate_invoice_pdf(invoice_data)
        
        # Return as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=invoice_{invoice_data['invoice_code']}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )



