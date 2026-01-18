"""
Medicine service layer - Business logic for medicines, families, and types.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional, Tuple
from datetime import date

from app.models.medicine import Medicine, MedicineFamily, MedicineType
from app.schemas.medicine import (
    MedicineCreate, MedicineUpdate,
    MedicineFamilyCreate, MedicineFamilyUpdate,
    MedicineTypeCreate, MedicineTypeUpdate
)


# ============================================================================
# MEDICINE FAMILY OPERATIONS
# ============================================================================

def get_families(db: Session) -> List[MedicineFamily]:
    """Get all medicine families."""
    return db.query(MedicineFamily).order_by(MedicineFamily.name).all()


def get_family_by_id(db: Session, family_id: int) -> Optional[MedicineFamily]:
    """Get a medicine family by ID."""
    return db.query(MedicineFamily).filter(MedicineFamily.id == family_id).first()


def create_family(db: Session, family_data: MedicineFamilyCreate) -> MedicineFamily:
    """Create a new medicine family."""
    family = MedicineFamily(name=family_data.name)
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


def update_family(db: Session, family_id: int, family_data: MedicineFamilyUpdate) -> Optional[MedicineFamily]:
    """Update a medicine family."""
    family = get_family_by_id(db, family_id)
    if not family:
        return None
    
    family.name = family_data.name
    db.commit()
    db.refresh(family)
    return family


def delete_family(db: Session, family_id: int) -> bool:
    """Delete a medicine family if not used by any medicine."""
    family = get_family_by_id(db, family_id)
    if not family:
        return False
    
    # Check if family is used by medicines
    medicine_count = db.query(Medicine).filter(Medicine.family_id == family_id).count()
    if medicine_count > 0:
        return False
    
    db.delete(family)
    db.commit()
    return True


# ============================================================================
# MEDICINE TYPE OPERATIONS
# ============================================================================

def get_types(db: Session) -> List[MedicineType]:
    """Get all medicine types."""
    return db.query(MedicineType).order_by(MedicineType.name).all()


def get_type_by_id(db: Session, type_id: int) -> Optional[MedicineType]:
    """Get a medicine type by ID."""
    return db.query(MedicineType).filter(MedicineType.id == type_id).first()


def create_type(db: Session, type_data: MedicineTypeCreate) -> MedicineType:
    """Create a new medicine type."""
    med_type = MedicineType(name=type_data.name)
    db.add(med_type)
    db.commit()
    db.refresh(med_type)
    return med_type


def update_type(db: Session, type_id: int, type_data: MedicineTypeUpdate) -> Optional[MedicineType]:
    """Update a medicine type."""
    med_type = get_type_by_id(db, type_id)
    if not med_type:
        return None
    
    med_type.name = type_data.name
    db.commit()
    db.refresh(med_type)
    return med_type


def delete_type(db: Session, type_id: int) -> bool:
    """Delete a medicine type if not used by any medicine."""
    med_type = get_type_by_id(db, type_id)
    if not med_type:
        return False
    
    # Check if type is used by medicines
    medicine_count = db.query(Medicine).filter(Medicine.type_id == type_id).count()
    if medicine_count > 0:
        return False
    
    db.delete(med_type)
    db.commit()
    return True


# ============================================================================
# MEDICINE OPERATIONS
# ============================================================================

def get_medicines(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    family_id: Optional[int] = None,
    type_id: Optional[int] = None,
    is_low_stock: Optional[bool] = None,
    is_expired: Optional[bool] = None
) -> Tuple[List[Medicine], int]:
    """
    Get medicines with pagination and filters.
    
    Returns:
        Tuple of (medicines list, total count)
    """
    query = db.query(Medicine).filter(Medicine.is_active == True)
    
    # Apply filters
    if search:
        search_filter = or_(
            Medicine.name.ilike(f"%{search}%"),
            Medicine.code.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if family_id:
        query = query.filter(Medicine.family_id == family_id)
    
    if type_id:
        query = query.filter(Medicine.type_id == type_id)
    
    if is_low_stock:
        query = query.filter(Medicine.quantity <= Medicine.min_stock_alert)
    
    if is_expired:
        today = date.today()
        query = query.filter(
            and_(
                Medicine.expiry_date.isnot(None),
                Medicine.expiry_date <= today
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    medicines = query.order_by(Medicine.name).offset(offset).limit(page_size).all()
    
    return medicines, total


def get_medicine_by_id(db: Session, medicine_id: int) -> Optional[Medicine]:
    """Get a medicine by ID."""
    return db.query(Medicine).filter(Medicine.id == medicine_id).first()


def get_medicine_by_code(db: Session, code: str) -> Optional[Medicine]:
    """Get a medicine by code."""
    return db.query(Medicine).filter(Medicine.code == code).first()


def create_medicine(db: Session, medicine_data: MedicineCreate) -> Medicine:
    """Create a new medicine."""
    # Auto-generate code if not provided
    if not medicine_data.code:
        import time
        # Generate a unique code based on timestamp
        medicine_data.code = f"MED-{int(time.time()*1000)}"
        
    # Calculate Total Units per Packaging (Box)
    total_units = medicine_data.blisters_per_box * medicine_data.units_per_blister
    
    # Store this as units_per_packaging (compatibility)
    medicine_data.units_per_packaging = total_units
    
    # CONVERT QUANTITY: Input is now expected to be in Total Units from frontend
    # medicine_data.quantity = medicine_data.quantity * total_units
    
    # Alert threshold is also expected in Total Units
    # medicine_data.min_stock_alert = medicine_data.min_stock_alert * total_units
        
    medicine = Medicine(**medicine_data.model_dump())
    db.add(medicine)
    db.commit()
    db.refresh(medicine)
    return medicine


def update_medicine(db: Session, medicine_id: int, medicine_data: MedicineUpdate) -> Optional[Medicine]:
    """Update a medicine."""
    medicine = get_medicine_by_id(db, medicine_id)
    if not medicine:
        return None
    
    # Update only provided fields
    update_data = medicine_data.model_dump(exclude_unset=True)
    
    # Handle unit hierarchy update
    current_blisters = update_data.get('blisters_per_box', medicine.blisters_per_box)
    current_units_per_blister = update_data.get('units_per_blister', medicine.units_per_blister)
    
    new_total_units = current_blisters * current_units_per_blister
    
    # Update total units default
    update_data['units_per_packaging'] = new_total_units
    
    # If quantity is being updated, assume input is ALREADY In UNITS from frontend
    # if 'quantity' in update_data and update_data['quantity'] is not None:
    #     update_data['quantity'] = update_data['quantity'] * new_total_units
        
    # Same for alert threshold
    # if 'min_stock_alert' in update_data and update_data['min_stock_alert'] is not None:
    #     update_data['min_stock_alert'] = update_data['min_stock_alert'] * new_total_units

    for field, value in update_data.items():
        setattr(medicine, field, value)
    
    db.commit()
    db.refresh(medicine)
    return medicine


from app.models.sales import SaleItem
from fastapi import HTTPException

def delete_medicine(db: Session, medicine_id: int) -> bool:
    """Delete a medicine."""
    medicine = get_medicine_by_id(db, medicine_id)
    if not medicine:
        return False
    
    # Check for existing sales using this medicine
    existing_sales = db.query(SaleItem).filter(SaleItem.medicine_id == medicine_id).first()
    
    if existing_sales:
        # Soft delete because sales history exists
        medicine.is_active = False
        db.commit()
    else:
        # Hard delete if no history (cleaner)
        db.delete(medicine)
        db.commit()
        
    return True


# ============================================================================
# STOCK ALERTS
# ============================================================================

def get_low_stock_medicines(db: Session) -> List[Medicine]:
    """Get medicines with low stock (quantity <= min_stock_alert)."""
    return db.query(Medicine).filter(
        Medicine.quantity <= Medicine.min_stock_alert
    ).order_by(Medicine.quantity).all()


def get_expired_medicines(db: Session) -> List[Medicine]:
    """Get expired medicines (expiry_date <= today)."""
    today = date.today()
    return db.query(Medicine).filter(
        and_(
            Medicine.expiry_date.isnot(None),
            Medicine.expiry_date <= today
        )
    ).order_by(Medicine.expiry_date).all()


def get_expiring_soon_medicines(db: Session, days: int = 180) -> List[Medicine]:
    """Get medicines expiring soon (today < expiry_date <= today + days)."""
    today = date.today()
    cutoff = today + timedelta(days=days)
    from datetime import timedelta # Ensure timedelta is imported or use from top level
    
    return db.query(Medicine).filter(
        and_(
            Medicine.expiry_date > today,
            Medicine.expiry_date <= cutoff
        )
    ).order_by(Medicine.expiry_date).all()


def get_stock_alerts(db: Session) -> Tuple[List[Medicine], List[Medicine]]:
    """
    Get all stock alerts.
    
    Returns:
        Tuple of (low_stock medicines, expired medicines)
    """
    low_stock = get_low_stock_medicines(db)
    expired = get_expired_medicines(db)
    return low_stock, expired
