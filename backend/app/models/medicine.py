"""
Medicine-related models: Medicine, MedicineFamily, MedicineType.
"""

from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModelMixin


class MedicineFamily(Base, BaseModelMixin):
    """
    Dynamic medicine family/category.
    Examples: Antibiotiques, Antipaludiques, Antidouleurs, etc.
    """
    __tablename__ = "medicine_families"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    # Relationship
    medicines = relationship("Medicine", back_populates="family")
    
    def __repr__(self):
        return f"<MedicineFamily(id={self.id}, name='{self.name}')>"


class MedicineType(Base, BaseModelMixin):
    """
    Dynamic medicine type/packaging.
    Examples: Plaquette, Flacon, Ampoule, Sachet, etc.
    """
    __tablename__ = "medicine_types"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationship
    medicines = relationship("Medicine", back_populates="type")
    
    def __repr__(self):
        return f"<MedicineType(id={self.id}, name='{self.name}')>"


class Medicine(Base, BaseModelMixin):
    """
    Main medicine/product model.
    
    Attributes:
        code: Unique product code/SKU
        name: Medicine name
        family_id: Reference to MedicineFamily
        type_id: Reference to MedicineType
        quantity: Current stock quantity
        price_buy: Purchase price (from supplier)
        price_sell: Selling price (to customer)
        expiry_date: Expiration date
        min_stock_alert: Minimum stock threshold for alerts
    """
    __tablename__ = "medicines"
    
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    family_id = Column(Integer, ForeignKey("medicine_families.id"), nullable=True)
    type_id = Column(Integer, ForeignKey("medicine_types.id"), nullable=True)
    quantity = Column(Float, default=0.0, nullable=False)
    price_buy = Column(Float, nullable=False)
    price_sell = Column(Float, nullable=False)
    expiry_date = Column(Date, nullable=True)
    min_stock_alert = Column(Integer, default=10, nullable=False)
    expiry_alert_threshold = Column(Integer, default=30, nullable=False) # Alert X days before expiry
    is_active = Column(Boolean, default=True, nullable=False) # Soft delete flag
    
    # New fields for detailed unit tracking
    dosage_form = Column(String(50), nullable=True)  # e.g. Comprimé, Sirop
    packaging = Column(String(50), nullable=True)    # e.g. Boîte
    
    # Hierarchy: Carton -> Box -> Blister -> Unit
    boxes_per_carton = Column(Integer, default=1, nullable=True)   # e.g. 50 Boîtes per Carton
    carton_type = Column(String(50), default="Carton", nullable=True) # Customize container name

    # Hierarchy: Box -> Blister -> Unit
    blisters_per_box = Column(Integer, default=1, nullable=True)   # e.g. 10 Plaquettes per Boîte
    units_per_blister = Column(Integer, default=1, nullable=True)  # e.g. 10 Comprimés per Plaquette
    
    # units_per_packaging previously used for direct division. 
    # We will keep it for compatibility or migration, but new logic relies on the above.
    units_per_packaging = Column(Integer, default=1, nullable=True) # DEPRECATED or used as total units per box?
    
    # Relationships
    family = relationship("MedicineFamily", back_populates="medicines")
    type = relationship("MedicineType", back_populates="medicines")
    sale_items = relationship("SaleItem", back_populates="medicine")
    restock_items = relationship("RestockItem", back_populates="medicine")
    
    def __repr__(self):
        return f"<Medicine(id={self.id}, code='{self.code}', name='{self.name}', qty={self.quantity})>"
