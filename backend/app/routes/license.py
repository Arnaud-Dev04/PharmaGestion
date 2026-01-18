"""
License routes - Public endpoint for license status checks.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_local_db
from app.core.license import license_service

router = APIRouter()

@router.get("/status")
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
