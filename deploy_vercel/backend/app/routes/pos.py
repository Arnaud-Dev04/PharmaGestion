"""
POS Routes — API endpoints for Point of Sale operations.

Endpoints:
    GET  /pos/products/search   — Search products with batch info
    POST /pos/cart/add          — Calculate FEFO allocation for cart
    POST /pos/checkout          — Finalize sale, deduct stock per batch
    GET  /pos/sale/{sale_id}    — Get POS sale details
    GET  /pos/history           — POS sales history
    POST /pos/batches           — Create a new batch (admin)
    GET  /pos/batches/{med_id}  — Get batches for a medicine
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_local_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user, get_admin_user
from app.services import pos_service
from app.schemas.pos import (
    CartAddRequest, CartAddResponse,
    POSCheckoutRequest, POSSaleResponse,
    ProductSearchResult,
    BatchCreate, BatchResponse,
)

# Create router
router = APIRouter()
logger = logging.getLogger("pos_routes")


# ============================================================================
# LEGACY STOCK SYNC
# ============================================================================

@router.post(
    "/sync-stock",
    summary="Sync legacy stock — auto-create batches for medicines without any"
)
async def sync_stock(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """Force sync: create default batches for medicines with stock but no batches."""
    try:
        created = pos_service.sync_legacy_stock(db)
        return {"message": f"{created} lot(s) auto-créé(s)", "created": created}
    except Exception as e:
        logger.error(f"sync_stock failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur sync: {str(e)}")


# ============================================================================
# PRODUCT SEARCH
# ============================================================================

@router.get(
    "/products/search",
    response_model=list[ProductSearchResult],
    summary="Search products for POS (with batch info)"
)
async def search_products(
    q: str = Query("", description="Search query (name or code). Empty = all products"),
    limit: int = Query(20, ge=1, le=50, description="Max results"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Search products by name or code for POS use.
    
    Returns products with available batches sorted by expiration date (FEFO).
    If query is empty, returns all products with stock.
    """
    results = pos_service.search_products(db, q, limit)
    return results


@router.get(
    "/products/top",
    response_model=list[ProductSearchResult],
    summary="Get top/frequent products"
)
async def get_top_products(
    limit: int = Query(10, ge=1, le=20, description="Max results"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get most frequently sold products for quick access.
    Falls back to products with highest stock if no sales history exists.
    """
    try:
        results = pos_service.get_top_products(db, limit)
        return results
    except Exception as e:
        logger.error(f"get_top_products failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur chargement produits fréquents: {str(e)}"
        )


# ============================================================================
# CART OPERATIONS
# ============================================================================

@router.post(
    "/cart/add",
    response_model=CartAddResponse,
    summary="Calculate FEFO allocation for cart item"
)
async def cart_add(
    request: CartAddRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Calculate which batches will be used for a given product quantity.
    
    Uses FEFO (First Expired First Out): allocates from the batch with
    the earliest expiration date first. If one batch doesn't have enough,
    it moves to the next batch.
    
    This is a **read-only** operation — no stock is deducted.
    The frontend stores the allocations and sends them at checkout.
    
    **Accessible to**: All authenticated users
    
    **Errors**:
    - 400: Insufficient stock or no available batches
    - 404: Medicine not found
    """
    try:
        result = pos_service.cart_add(db, request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/cart/remove",
    summary="Remove item from cart (frontend-managed)"
)
async def cart_remove(
    medicine_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Cart removal is handled entirely on the frontend.
    
    This endpoint exists for API completeness but simply returns success.
    The frontend manages the cart state and removes items locally.
    """
    return {"status": "ok", "message": "Cart is managed on frontend"}


# ============================================================================
# CHECKOUT
# ============================================================================

@router.post(
    "/checkout",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Finalize POS sale — deduct stock per batch"
)
async def checkout(
    checkout_data: POSCheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Finalize a POS sale transaction.
    
    This endpoint:
    1. Validates all batch allocations have sufficient stock
    2. Creates a POS sale with UUID for future sync
    3. Creates sale items linked to specific batches
    4. Deducts stock per batch (not global)
    5. Updates medicine total quantity
    6. All within a single atomic transaction
    
    **Accessible to**: All authenticated users
    
    **Errors**:
    - 400: Insufficient stock, expired batch, or validation error
    - 404: Medicine or batch not found
    """
    try:
        sale = pos_service.checkout(
            db=db,
            user_id=current_user.id,
            checkout_data=checkout_data
        )
        
        return pos_service.enrich_pos_sale_response(sale)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RequestValidationError as e:
        # Erreurs de validation Pydantic (ex: allocations vides, champs manquants)
        error_msgs = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        logger.warning(f"Checkout validation error: {error_msgs}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Données invalides: {'; '.join(error_msgs)}"
        )
    except Exception as e:
        import traceback
        logger.error(f"Checkout unexpected error: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur checkout: {type(e).__name__}: {str(e)}"
        )


# ============================================================================
# SALE RETRIEVAL
# ============================================================================

@router.get(
    "/sale/{sale_id}",
    response_model=dict,
    summary="Get POS sale details"
)
async def get_pos_sale(
    sale_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get details of a specific POS sale, including batch allocations.
    
    **Accessible to**: All authenticated users
    """
    sale = pos_service.get_pos_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vente POS avec ID {sale_id} introuvable"
        )
    
    return pos_service.enrich_pos_sale_response(sale)


@router.post(
    "/sale/{sale_id}/cancel",
    response_model=dict,
    summary="Cancel POS sale and restore batch stock"
)
async def cancel_pos_sale(
    sale_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Cancel a POS sale, restore sold quantities to their original batches,
    and keep an audit trail in stock movements.
    """
    try:
        sale = pos_service.cancel_pos_sale(
            db=db,
            sale_id=sale_id,
            user_id=current_user.id,
        )
        return pos_service.enrich_pos_sale_response(sale)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/history",
    summary="Get POS sales history"
)
async def get_pos_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get POS sales history with pagination and date filters.
    
    **Accessible to**: All authenticated users
    """
    sales, total = pos_service.get_pos_sales_history(
        db=db,
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date
    )
    
    enriched = [pos_service.enrich_pos_sale_response(s) for s in sales]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": enriched
    }


# ============================================================================
# BATCH MANAGEMENT
# ============================================================================

@router.post(
    "/batches",
    response_model=BatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new batch/lot for a medicine"
)
async def create_batch(
    batch_data: BatchCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Create a new batch (lot) for a medicine.
    
    This also updates the medicine's total stock quantity.
    
    **Accessible to**: All authenticated users (Admin recommended)
    """
    try:
        batch = pos_service.create_batch(db, batch_data)
        
        return BatchResponse(
            id=batch.id,
            medicine_id=batch.medicine_id,
            medicine_name=batch.medicine.name if batch.medicine else "",
            batch_number=batch.batch_number,
            expiration_date=batch.expiration_date,
            quantity=batch.quantity,
            purchase_price=batch.purchase_price,
            is_active=batch.is_active,
            created_at=batch.created_at,
            updated_at=batch.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/batches/{medicine_id}",
    response_model=list[BatchResponse],
    summary="Get batches for a medicine"
)
async def get_batches(
    medicine_id: int,
    include_empty: bool = Query(False, description="Include empty batches"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Get all active batches for a medicine, sorted FEFO.
    
    **Accessible to**: All authenticated users
    """
    batches = pos_service.get_batches_for_medicine(db, medicine_id, include_empty)
    
    return [
        BatchResponse(
            id=b.id,
            medicine_id=b.medicine_id,
            medicine_name=b.medicine.name if b.medicine else "",
            batch_number=b.batch_number,
            expiration_date=b.expiration_date,
            quantity=b.quantity,
            purchase_price=b.purchase_price,
            is_active=b.is_active,
            created_at=b.created_at,
            updated_at=b.updated_at
        )
        for b in batches
    ]
