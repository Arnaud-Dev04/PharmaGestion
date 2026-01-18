"""
Stock routes - Medicine CRUD and stock alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_local_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user, get_admin_user
from app.schemas.medicine import (
    MedicineCreate, MedicineUpdate, MedicineResponse,
    StockAlertsResponse
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services import medicine_service

# Create router
router = APIRouter()


# Helper function to enrich medicine response
def enrich_medicine_response(medicine) -> dict:
    """Add calculated fields to medicine response."""
    response = MedicineResponse.model_validate(medicine)
    
    # Calculate fields
    response.is_low_stock = medicine.quantity <= medicine.min_stock_alert
    response.is_expired = (
        medicine.expiry_date is not None and 
        medicine.expiry_date <= date.today()
    )
    response.margin = medicine.price_sell - medicine.price_buy if medicine.price_sell and medicine.price_buy else 0.0
    
    return response


@router.get(
    "/medicines",
    response_model=PaginatedResponse[MedicineResponse],
    summary="List medicines with pagination and filters"
)
async def list_medicines(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    family_id: Optional[int] = Query(None, description="Filter by family ID"),
    type_id: Optional[int] = Query(None, description="Filter by type ID"),
    is_low_stock: Optional[bool] = Query(None, description="Filter low stock"),
    is_expired: Optional[bool] = Query(None, description="Filter expired"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get medicines list with pagination and filters.
    
    **Accessible to**: All authenticated users
    """
    medicines, total = medicine_service.get_medicines(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        family_id=family_id,
        type_id=type_id,
        is_low_stock=is_low_stock,
        is_expired=is_expired
    )
    
    # Enrich responses
    enriched_items = [enrich_medicine_response(m) for m in medicines]
    
    return PaginatedResponse.create(
        items=enriched_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/medicines/{medicine_id}",
    response_model=MedicineResponse,
    summary="Get a specific medicine"
)
async def get_medicine(
    medicine_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get a single medicine by ID.
    
    **Accessible to**: All authenticated users
    """
    medicine = medicine_service.get_medicine_by_id(db, medicine_id)
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    return enrich_medicine_response(medicine)


@router.post(
    "/medicines",
    response_model=MedicineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medicine (Admin only)"
)
async def create_medicine(
    medicine_data: MedicineCreate,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db)
):
    """
    Create a new medicine.
    
    **Accessible to**: Admin only
    """
    # Check if code already exists
    existing = medicine_service.get_medicine_by_code(db, medicine_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Medicine with code '{medicine_data.code}' already exists"
        )
    
    # Verify family and type exist if provided
    if medicine_data.family_id:
        family = medicine_service.get_family_by_id(db, medicine_data.family_id)
        if not family:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicine family with ID {medicine_data.family_id} not found"
            )
    
    if medicine_data.type_id:
        med_type = medicine_service.get_type_by_id(db, medicine_data.type_id)
        if not med_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicine type with ID {medicine_data.type_id} not found"
            )
    
    medicine = medicine_service.create_medicine(db, medicine_data)
    return enrich_medicine_response(medicine)


@router.put(
    "/medicines/{medicine_id}",
    response_model=MedicineResponse,
    summary="Update a medicine (Admin only)"
)
async def update_medicine(
    medicine_id: int,
    medicine_data: MedicineUpdate,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db)
):
    """
    Update a medicine.
    
    **Accessible to**: Admin only
    """
    # Check if code is being changed and if it already exists
    if medicine_data.code:
        existing = medicine_service.get_medicine_by_code(db, medicine_data.code)
        if existing and existing.id != medicine_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Medicine with code '{medicine_data.code}' already exists"
            )
    
    medicine = medicine_service.update_medicine(db, medicine_id, medicine_data)
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    return enrich_medicine_response(medicine)


@router.delete(
    "/medicines/{medicine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a medicine (Admin only)"
)
async def delete_medicine(
    medicine_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db)
):
    """
    Delete a medicine.
    
    **Accessible to**: Admin only
    """
    success = medicine_service.delete_medicine(db, medicine_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )


@router.get(
    "/alerts",
    response_model=StockAlertsResponse,
    summary="Get stock alerts (low stock + expired)"
)
async def get_stock_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get stock alerts: low stock and expired medicines.
    
    **Accessible to**: All authenticated users
    """
    low_stock, expired = medicine_service.get_stock_alerts(db)
    
    return StockAlertsResponse(
        low_stock=[enrich_medicine_response(m) for m in low_stock],
        expired=[enrich_medicine_response(m) for m in expired],
        total_alerts=len(low_stock) + len(expired)
    )


@router.get(
    "/medicines/expiring-soon",
    response_model=list[MedicineResponse],
    summary="Get medicines expiring soon (next 6 months)"
)
async def get_expiring_soon(
    days: int = Query(180, description="Days threshold"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get medicines expiring in the next N days (default 180 = 6 months).
    """
    medicines = medicine_service.get_expiring_soon_medicines(db, days)
    return [enrich_medicine_response(m) for m in medicines]
