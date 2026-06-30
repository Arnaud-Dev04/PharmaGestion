"""
Medicine Pricing service — Business logic for pricing CRUD and calculations.

CONNECTED SYSTEM: Creating a pricing entry auto-creates/updates:
  - Medicine (unique identity)
  - Batch (lot with expiry + stock)
  - StockMovement (journal entry)
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import date, timedelta
from typing import Optional, Tuple, List
import logging

from app.models.medicine_pricing import MedicinePricing
from app.models.medicine import Medicine
from app.models.batch import Batch
from app.models.stock_movement import StockMovement
from app.schemas.medicine_pricing import MedicinePricingCreate, MedicinePricingUpdate

logger = logging.getLogger("medicine_pricing_service")


# ============================================================================
# PRICE CALCULATION
# ============================================================================

def calculate_prices(data: MedicinePricingCreate) -> dict:
    """Calculate all prices and totals based on the pricing mode."""
    mode = data.prix_mode.value if hasattr(data.prix_mode, 'value') else data.prix_mode
    achat = data.achat_carton

    # Totals
    total_boites = data.nb_cartons * data.boites_par_carton
    total_plaquettes = total_boites * data.plaquettes_par_boite
    total_comprimes = total_plaquettes * data.comprimes_par_plaquette

    vente_carton = data.vente_carton
    vente_boite = data.vente_boite
    vente_plaquette = data.vente_plaquette
    vente_comprime = data.vente_comprime
    marge_pct = data.marge_pct

    if mode == "pct_marge":
        vente_carton = achat * (1 + (marge_pct or 0) / 100)
        vente_boite = vente_carton / data.boites_par_carton if data.boites_par_carton > 0 else 0
        vente_plaquette = vente_boite / data.plaquettes_par_boite if data.plaquettes_par_boite > 0 else 0
        vente_comprime = vente_plaquette / data.comprimes_par_plaquette if data.comprimes_par_plaquette > 0 else 0

    elif mode == "carton_fixe":
        vente_boite = vente_carton / data.boites_par_carton if data.boites_par_carton > 0 else 0
        vente_plaquette = vente_boite / data.plaquettes_par_boite if data.plaquettes_par_boite > 0 else 0
        vente_comprime = vente_plaquette / data.comprimes_par_plaquette if data.comprimes_par_plaquette > 0 else 0
        if achat > 0:
            marge_pct = ((vente_carton - achat) / achat) * 100

    # mode == "manuel": all prices already set by user

    # Benefit calculation
    valeur_achat_totale = data.nb_cartons * achat
    valeur_vente_totale = total_comprimes * vente_comprime
    benefice_estime = valeur_vente_totale - valeur_achat_totale

    # Calculate per-unit purchase prices
    # In manual mode, prefer user-entered PA values; otherwise auto-calculate
    if mode == "manuel":
        achat_boite = data.achat_boite if data.achat_boite > 0 else (
            achat / data.boites_par_carton if data.boites_par_carton > 0 else 0
        )
        achat_plaquette = data.achat_plaquette if data.achat_plaquette > 0 else (
            achat_boite / data.plaquettes_par_boite if data.plaquettes_par_boite > 0 else 0
        )
        achat_comprime = data.achat_comprime if data.achat_comprime > 0 else (
            achat_plaquette / data.comprimes_par_plaquette if data.comprimes_par_plaquette > 0 else 0
        )
    else:
        achat_boite = achat / data.boites_par_carton if data.boites_par_carton > 0 else 0
        achat_plaquette = achat_boite / data.plaquettes_par_boite if data.plaquettes_par_boite > 0 else 0
        achat_comprime = achat_plaquette / data.comprimes_par_plaquette if data.comprimes_par_plaquette > 0 else 0

    return {
        "vente_carton": round(vente_carton, 2),
        "vente_boite": round(vente_boite, 2),
        "vente_plaquette": round(vente_plaquette, 2),
        "vente_comprime": round(vente_comprime, 2),
        "marge_pct": round(marge_pct, 2) if marge_pct is not None else None,
        "benefice_estime": round(benefice_estime, 2),
        "total_boites": total_boites,
        "total_plaquettes": total_plaquettes,
        "total_comprimes": total_comprimes,
        # Multi-level purchase prices
        "achat_comprime": round(achat_comprime, 2),
        "achat_boite": round(achat_boite, 2),
        "achat_plaquette": round(achat_plaquette, 2),
    }


# ============================================================================
# AUTO CODE GENERATION
# ============================================================================

def _generate_medicine_code(db: Session) -> str:
    """Generate unique medicine code: MED-NNNN."""
    last = db.query(Medicine).order_by(Medicine.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"MED-{next_num:04d}"


# ============================================================================
# DUPLICATE DETECTION (R3/R4)
# ============================================================================

def _find_duplicate(db: Session, nom: str, lot: str) -> Optional[MedicinePricing]:
    """
    R3/R4: Check for existing pricing with same name + lot.
    Returns the existing entry if found.
    """
    return db.query(MedicinePricing).filter(
        func.lower(MedicinePricing.nom) == nom.strip().lower(),
        func.lower(MedicinePricing.lot) == lot.strip().lower(),
    ).first()


def _find_medicine_by_name(db: Session, nom: str) -> Optional[Medicine]:
    """Find an existing Medicine by normalized name."""
    return db.query(Medicine).filter(
        func.lower(Medicine.name) == nom.strip().lower(),
        Medicine.is_active == True,
    ).first()


# ============================================================================
# CREATE PRICING (CONNECTED SYSTEM)
# ============================================================================

def create_pricing(db: Session, data: MedicinePricingCreate) -> MedicinePricing:
    """
    Create a new pricing entry WITH automatic system connection.
    
    Flow:
    1. Calculate prices
    2. Check for duplicates (R3/R4)
       - Same name + same lot + same price → merge quantities
       - Same name + same lot + different price → update prices
       - New entry → create
    3. Find or create Medicine
    4. Create Batch
    5. Create StockMovement (type='entree')
    6. Create MedicinePricing with medicine_id
    """
    calculated = calculate_prices(data)
    
    # --- Step 1: Duplicate detection (R3/R4) ---
    existing = _find_duplicate(db, data.nom, data.lot)
    
    if existing:
        # R3: Same name + same lot → merge quantities
        logger.info(f"Doublon détecté: {data.nom} lot {data.lot} — fusion des quantités")
        
        existing.nb_cartons += data.nb_cartons
        existing.total_boites += calculated["total_boites"]
        existing.total_plaquettes += calculated["total_plaquettes"]
        existing.total_comprimes += calculated["total_comprimes"]
        
        # Update prices to latest values
        existing.achat_carton = data.achat_carton
        existing.vente_carton = calculated["vente_carton"]
        existing.vente_boite = calculated["vente_boite"]
        existing.vente_plaquette = calculated["vente_plaquette"]
        existing.vente_comprime = calculated["vente_comprime"]
        existing.marge_pct = calculated["marge_pct"]
        
        # Recalculate benefit
        valeur_achat = existing.nb_cartons * existing.achat_carton
        valeur_vente = existing.total_comprimes * existing.vente_comprime
        existing.benefice_estime = round(valeur_vente - valeur_achat, 2)
        
        # Update the linked Medicine stock
        if existing.medicine_id:
            medicine = db.query(Medicine).filter(Medicine.id == existing.medicine_id).first()
            if medicine:
                medicine.quantity += calculated["total_comprimes"]
                _update_medicine_prices(medicine, calculated, data)
        
        # Update existing Batch quantity
        if existing.medicine_id:
            batch = db.query(Batch).filter(
                Batch.medicine_id == existing.medicine_id,
                func.lower(Batch.batch_number) == data.lot.strip().lower(),
            ).first()
            if batch:
                batch.quantity += calculated["total_comprimes"]
            else:
                batch = _create_batch(db, existing.medicine_id, data, calculated)
        
        # Create stock movement for the additional quantity
        if existing.medicine_id:
            _create_stock_movement(
                db, existing.medicine_id,
                batch.id if batch else None,
                existing.id,
                calculated["total_comprimes"],
                f"Fusion lot {data.lot} (+{calculated['total_comprimes']} unités)"
            )
        
        db.commit()
        db.refresh(existing)
        return existing
    
    # --- Step 2: Find or create Medicine ---
    medicine = _find_medicine_by_name(db, data.nom)
    
    if medicine:
        # Existing medicine — update stock and prices
        medicine.quantity += calculated["total_comprimes"]
        _update_medicine_prices(medicine, calculated, data)
        logger.info(f"Medicine existant mis à jour: {medicine.name} (ID:{medicine.id})")
    else:
        # New medicine — create
        code = _generate_medicine_code(db)
        medicine = Medicine(
            code=code,
            name=data.nom.strip(),
            code_barres=None,
            dci=data.dci,
            forme_galenique=data.forme,
            dosage_form=data.forme,
            quantity=calculated["total_comprimes"],
            min_stock_alert=data.seuil_alerte,
            expiry_alert_threshold=data.alerte_jours or 30,
            is_active=True,
            # Conditionnement
            boxes_per_carton=data.boites_par_carton,
            blisters_per_box=data.plaquettes_par_boite,
            units_per_blister=data.comprimes_par_plaquette,
            units_per_packaging=data.plaquettes_par_boite * data.comprimes_par_plaquette,
            # Traçabilité
            lot_fabricant=data.lot,
            date_entree_stock=data.date_reception or date.today(),
            expiry_date=data.date_peremption,
            fournisseur=data.fournisseur,
            # Prix
            price_buy=calculated["achat_boite"],
            price_sell=calculated["vente_boite"],
            prix_achat_unite=calculated["achat_comprime"],
            prix_vente_unite=calculated["vente_comprime"],
            prix_achat_boite=calculated["achat_boite"],
            prix_vente_boite=calculated["vente_boite"],
            prix_achat_plaquette=calculated["achat_plaquette"],
            prix_vente_plaquette=calculated["vente_plaquette"],
            prix_achat_carton=data.achat_carton,
            prix_vente_carton=calculated["vente_carton"],
        )
        db.add(medicine)
        db.flush()  # Get medicine.id
        logger.info(f"Nouveau Medicine créé: {medicine.name} (code:{code}, ID:{medicine.id})")

    # --- Step 3: Create MedicinePricing entry ---
    entry = MedicinePricing(
        medicine_id=medicine.id,
        nom=data.nom.strip(),
        dci=data.dci,
        forme=data.forme,
        dosage=data.dosage,
        lot=data.lot.strip(),
        fournisseur=data.fournisseur,
        bon_livraison=data.bon_livraison,
        date_reception=data.date_reception,
        date_peremption=data.date_peremption,
        nb_cartons=data.nb_cartons,
        boites_par_carton=data.boites_par_carton,
        plaquettes_par_boite=data.plaquettes_par_boite,
        comprimes_par_plaquette=data.comprimes_par_plaquette,
        total_boites=calculated["total_boites"],
        total_plaquettes=calculated["total_plaquettes"],
        total_comprimes=calculated["total_comprimes"],
        prix_mode=data.prix_mode.value,
        achat_carton=data.achat_carton,
        achat_boite=calculated["achat_boite"],
        achat_plaquette=calculated["achat_plaquette"],
        achat_comprime=calculated["achat_comprime"],
        vente_carton=calculated["vente_carton"],
        vente_boite=calculated["vente_boite"],
        vente_plaquette=calculated["vente_plaquette"],
        vente_comprime=calculated["vente_comprime"],
        marge_pct=calculated["marge_pct"],
        benefice_estime=calculated["benefice_estime"],
        seuil_alerte=data.seuil_alerte,
        seuil_niveau=data.seuil_niveau,
        emplacement=data.emplacement,
        alerte_peremption=data.alerte_peremption,
        alerte_jours=data.alerte_jours if data.alerte_peremption else None,
        ordonnance=data.ordonnance.value,
    )
    db.add(entry)
    db.flush()

    # --- Step 4: Create Batch ---
    batch = _create_batch(db, medicine.id, data, calculated)

    # --- Step 5: Create StockMovement ---
    _create_stock_movement(
        db, medicine.id, batch.id, entry.id,
        calculated["total_comprimes"],
        f"Enregistrement lot {data.lot}"
    )

    db.commit()
    db.refresh(entry)
    
    logger.info(
        f"Pricing #{entry.id} créé pour {data.nom} — "
        f"Medicine #{medicine.id}, Batch #{batch.id}, "
        f"{calculated['total_comprimes']} unités"
    )
    
    return entry


def _update_medicine_prices(medicine: Medicine, calculated: dict, data: MedicinePricingCreate):
    """Update a Medicine's multi-level prices and traceability from a new pricing entry."""
    medicine.prix_achat_unite = calculated["achat_comprime"]
    medicine.prix_vente_unite = calculated["vente_comprime"]
    medicine.prix_achat_boite = calculated["achat_boite"]
    medicine.prix_vente_boite = calculated["vente_boite"]
    medicine.prix_achat_plaquette = calculated["achat_plaquette"]
    medicine.prix_vente_plaquette = calculated["vente_plaquette"]
    medicine.prix_achat_carton = data.achat_carton
    medicine.prix_vente_carton = calculated["vente_carton"]
    # Legacy compat
    medicine.price_buy = calculated["achat_boite"]
    medicine.price_sell = calculated["vente_boite"]
    # Traceability
    medicine.lot_fabricant = data.lot
    medicine.date_entree_stock = data.date_reception or date.today()
    medicine.fournisseur = data.fournisseur
    # Update conditionnement
    medicine.boxes_per_carton = data.boites_par_carton
    medicine.blisters_per_box = data.plaquettes_par_boite
    medicine.units_per_blister = data.comprimes_par_plaquette
    medicine.units_per_packaging = data.plaquettes_par_boite * data.comprimes_par_plaquette
    medicine.forme_galenique = data.forme
    medicine.dosage_form = data.forme
    if data.dci:
        medicine.dci = data.dci
    # Update expiry to nearest
    if data.date_peremption:
        if medicine.expiry_date is None or data.date_peremption < medicine.expiry_date:
            medicine.expiry_date = data.date_peremption


def _create_batch(db: Session, medicine_id: int, data: MedicinePricingCreate, calculated: dict) -> Batch:
    """Create a Batch linked to a Medicine from pricing data."""
    from datetime import timedelta
    
    expiry = data.date_peremption or (date.today() + timedelta(days=730))
    
    batch = Batch(
        medicine_id=medicine_id,
        batch_number=data.lot.strip(),
        expiration_date=expiry,
        quantity=calculated["total_comprimes"],
        purchase_price=calculated["achat_comprime"],
        is_active=True,
    )
    db.add(batch)
    db.flush()
    return batch


def _create_stock_movement(
    db: Session,
    medicine_id: int,
    batch_id: Optional[int],
    pricing_id: Optional[int],
    quantite: int,
    motif: str,
):
    """Create a stock movement journal entry."""
    movement = StockMovement(
        medicine_id=medicine_id,
        batch_id=batch_id,
        pricing_id=pricing_id,
        type="entree",
        quantite=quantite,
        motif=motif,
        reference=f"PRICING-{pricing_id}" if pricing_id else None,
    )
    db.add(movement)


# ============================================================================
# READ
# ============================================================================

def get_pricings(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
) -> Tuple[List[MedicinePricing], int]:
    """Get paginated pricing entries with optional search."""
    query = db.query(MedicinePricing)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                MedicinePricing.nom.ilike(search_term),
                MedicinePricing.lot.ilike(search_term),
                MedicinePricing.fournisseur.ilike(search_term),
                MedicinePricing.dci.ilike(search_term),
            )
        )

    total = query.count()
    entries = (
        query.order_by(MedicinePricing.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return entries, total


def get_pricing_by_id(db: Session, pricing_id: int) -> Optional[MedicinePricing]:
    """Get a single pricing entry by ID."""
    return db.query(MedicinePricing).filter(MedicinePricing.id == pricing_id).first()


# ============================================================================
# UPDATE
# ============================================================================

def update_pricing(db: Session, pricing_id: int, data: MedicinePricingUpdate) -> Optional[MedicinePricing]:
    """Update a pricing entry and recalculate derived fields."""
    entry = get_pricing_by_id(db, pricing_id)
    if not entry:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, 'value'):  # Handle enums
            setattr(entry, field, value.value)
        else:
            setattr(entry, field, value)

    # Recalculate totals
    entry.total_boites = entry.nb_cartons * entry.boites_par_carton
    entry.total_plaquettes = entry.total_boites * entry.plaquettes_par_boite
    entry.total_comprimes = entry.total_plaquettes * entry.comprimes_par_plaquette

    # Recalculate prices based on mode
    if entry.prix_mode == "pct_marge" and entry.marge_pct:
        entry.vente_carton = round(entry.achat_carton * (1 + entry.marge_pct / 100), 2)
        entry.vente_boite = round(entry.vente_carton / entry.boites_par_carton, 2) if entry.boites_par_carton > 0 else 0
        entry.vente_plaquette = round(entry.vente_boite / entry.plaquettes_par_boite, 2) if entry.plaquettes_par_boite > 0 else 0
        entry.vente_comprime = round(entry.vente_plaquette / entry.comprimes_par_plaquette, 2) if entry.comprimes_par_plaquette > 0 else 0
    elif entry.prix_mode == "carton_fixe":
        entry.vente_boite = round(entry.vente_carton / entry.boites_par_carton, 2) if entry.boites_par_carton > 0 else 0
        entry.vente_plaquette = round(entry.vente_boite / entry.plaquettes_par_boite, 2) if entry.plaquettes_par_boite > 0 else 0
        entry.vente_comprime = round(entry.vente_plaquette / entry.comprimes_par_plaquette, 2) if entry.comprimes_par_plaquette > 0 else 0
        if entry.achat_carton > 0:
            entry.marge_pct = round(((entry.vente_carton - entry.achat_carton) / entry.achat_carton) * 100, 2)

    # Recalculate benefit
    valeur_achat = entry.nb_cartons * entry.achat_carton
    valeur_vente = entry.total_comprimes * entry.vente_comprime
    entry.benefice_estime = round(valeur_vente - valeur_achat, 2)

    db.commit()
    db.refresh(entry)
    return entry


# ============================================================================
# DELETE
# ============================================================================

def delete_pricing(db: Session, pricing_id: int) -> bool:
    """Delete a pricing entry."""
    entry = get_pricing_by_id(db, pricing_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True


# ============================================================================
# ALERTS
# ============================================================================

def get_pricing_alerts(db: Session) -> dict:
    """Get pricing entries with alerts (expiring soon or low stock)."""
    six_months = date.today() + timedelta(days=180)

    expiring = db.query(MedicinePricing).filter(
        MedicinePricing.date_peremption != None,
        MedicinePricing.date_peremption <= six_months,
        MedicinePricing.date_peremption > date.today(),
    ).all()

    low_stock = db.query(MedicinePricing).filter(
        MedicinePricing.total_comprimes <= MedicinePricing.seuil_alerte
    ).all()

    return {
        "expiring_soon": expiring,
        "low_stock": low_stock,
        "total_alerts": len(expiring) + len(low_stock),
    }


# ============================================================================
# AUTOCOMPLETE
# ============================================================================

def get_autocomplete_names(db: Session, query: str, limit: int = 10) -> List[str]:
    """Get distinct medication names for autocomplete suggestions."""
    search_term = f"%{query}%"
    results = db.query(MedicinePricing.nom).filter(
        MedicinePricing.nom.ilike(search_term)
    ).distinct().limit(limit).all()
    return [r[0] for r in results]
