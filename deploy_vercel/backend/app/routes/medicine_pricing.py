"""
Medicine Pricing routes — API endpoints for the pricing module.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta

from app.database import get_local_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user, get_admin_user
from app.schemas.medicine_pricing import (
    MedicinePricingCreate,
    MedicinePricingUpdate,
    MedicinePricingResponse,
)
from app.schemas.common import PaginatedResponse
from app.services import medicine_pricing_service

router = APIRouter()


def enrich_pricing_response(entry) -> MedicinePricingResponse:
    """Add calculated alert fields to pricing response."""
    response = MedicinePricingResponse.model_validate(entry)

    # Check expiry alert (< 6 months from now)
    if entry.date_peremption:
        six_months_from_now = date.today() + timedelta(days=180)
        response.expire_bientot = (
            entry.date_peremption <= six_months_from_now
            and entry.date_peremption > date.today()
        )

    # Check stock alert
    response.stock_faible = entry.total_comprimes <= entry.seuil_alerte

    return response


@router.get(
    "/entries",
    response_model=PaginatedResponse[MedicinePricingResponse],
    summary="List pricing entries with pagination and search",
)
async def list_pricing_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, lot, supplier, or DCI"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db),
):
    """
    Get paginated pricing entries.

    **Accessible to**: All authenticated users
    """
    entries, total = medicine_pricing_service.get_pricings(db, page, page_size, search)
    enriched = [enrich_pricing_response(e) for e in entries]
    return PaginatedResponse.create(
        items=enriched, total=total, page=page, page_size=page_size
    )


@router.get(
    "/entries/{entry_id}",
    response_model=MedicinePricingResponse,
    summary="Get a specific pricing entry",
)
async def get_pricing_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db),
):
    """
    Get a single pricing entry by ID.

    **Accessible to**: All authenticated users
    """
    entry = medicine_pricing_service.get_pricing_by_id(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entrée de prix avec ID {entry_id} introuvable",
        )
    return enrich_pricing_response(entry)


@router.post(
    "/entries",
    response_model=MedicinePricingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pricing entry (Admin only)",
)
async def create_pricing_entry(
    data: MedicinePricingCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db),
):
    """
    Create a new medicine pricing entry.

    **Accessible to**: Admin only
    """
    entry = medicine_pricing_service.create_pricing(db, data)
    return enrich_pricing_response(entry)


@router.put(
    "/entries/{entry_id}",
    response_model=MedicinePricingResponse,
    summary="Update a pricing entry (Admin only)",
)
async def update_pricing_entry(
    entry_id: int,
    data: MedicinePricingUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db),
):
    """
    Update a pricing entry.

    **Accessible to**: Admin only
    """
    entry = medicine_pricing_service.update_pricing(db, entry_id, data)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entrée de prix avec ID {entry_id} introuvable",
        )
    return enrich_pricing_response(entry)


@router.delete(
    "/entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pricing entry (Admin only)",
)
async def delete_pricing_entry(
    entry_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db),
):
    """
    Delete a pricing entry.

    **Accessible to**: Admin only
    """
    success = medicine_pricing_service.delete_pricing(db, entry_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entrée de prix avec ID {entry_id} introuvable",
        )


@router.get(
    "/alerts",
    summary="Get pricing alerts (expiring soon + low stock)",
)
async def get_pricing_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db),
):
    """
    Get pricing entries with alerts.

    **Accessible to**: All authenticated users
    """
    alerts = medicine_pricing_service.get_pricing_alerts(db)
    return {
        "expiring_soon": [enrich_pricing_response(e) for e in alerts["expiring_soon"]],
        "low_stock": [enrich_pricing_response(e) for e in alerts["low_stock"]],
        "total_alerts": alerts["total_alerts"],
    }


@router.get(
    "/autocomplete",
    summary="Autocomplete medication names",
)
async def autocomplete_names(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db),
):
    """
    Returns distinct medication names matching the query for form autocomplete.

    **Accessible to**: All authenticated users
    """
    names = medicine_pricing_service.get_autocomplete_names(db, q, limit)
    return {"results": names}

