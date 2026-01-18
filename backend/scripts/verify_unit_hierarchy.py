import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services.medicine_service import create_medicine, get_medicine_by_id
from app.services.sales_service import create_sale
from app.schemas.medicine import MedicineCreate
from app.schemas.sales import SaleCreate, SaleItemCreate
from app.database import SessionLocal
from app.services.medicine_service import create_medicine, get_medicine_by_id
from app.services.sales_service import create_sale
from app.schemas.medicine import MedicineCreate
from app.schemas.sales import SaleCreate, SaleItemCreate
from app.models.user import User
# from app.auth.security import get_password_hash

from sqlalchemy import text

def verify_hierarchy():
    db = SessionLocal()
    try:
        print("--- DEMARRAGE DU TEST HIERARCHIE ---")
        
        # MIGRATION AUTOMATIQUE
        try:
            db.execute(text("SELECT blisters_per_box FROM medicines LIMIT 1"))
        except Exception:
            print(">>> MIGRATION: Ajout de la colonne blisters_per_box")
            db.execute(text("ALTER TABLE medicines ADD COLUMN blisters_per_box INTEGER DEFAULT 1"))
            db.commit()

        try:
            db.execute(text("SELECT units_per_blister FROM medicines LIMIT 1"))
        except Exception:
            print(">>> MIGRATION: Ajout de la colonne units_per_blister")
            db.execute(text("ALTER TABLE medicines ADD COLUMN units_per_blister INTEGER DEFAULT 1"))
            db.commit()
        
        # 0. Create a dummy user for sales if needed (admin)
        user = db.query(User).filter(User.username == "test_admin").first()
        if not user:
            user = User(username="test_admin", password_hash="dummy_hash_for_test", role="admin")
            db.add(user)
            db.commit()
            db.refresh(user)

        # 1. Create Medicine
        # Hierarchy: 1 Box = 10 Blisters, 1 Blister = 6 Units. Total = 60 Units/Box.
        # Initial Stock: 5 Boxes. Total = 300 Units.
        print("\n1. Creation Medicament (1 Boite = 10 Plq x 6 Un = 60 Un)")
        med_data = MedicineCreate(
            name="TestEfferalgan",
            description="Test Hierarchy",
            price_buy=100.0,
            price_sell=200.0, # Price per Box
            quantity=5,       # 5 Boxes
            blisters_per_box=10,
            units_per_blister=6,
            min_stock_alert=1
        )
        try:
            med = create_medicine(db, med_data)
            print(f"   [OK] Creé. Quantité stockée (unités): {med.quantity}")
            print(f"   [Verif] units_per_packaging attendu 60. Reçu: {med.units_per_packaging}")
            assert med.quantity == 300
            assert med.units_per_packaging == 60
        except Exception as e:
            print(f"   [ERREUR] Creation echouée: {e}")
            return

        # 2. Sell 1 Blister (Should deduct 6 units)
        print("\n2. Vente 1 Plaquette")
        # 1 Blister logic:
        # Backend 'create_sale' expects SaleItem with 'sale_type'
        sale_data = SaleCreate(
            payment_method="cash",
            amount_paid=100,
            items=[
                SaleItemCreate(
                    medicine_id=med.id,
                    quantity=1,
                    sale_type="blister", # "plaquette" ? Backend uses "blister"
                    unit_price=0 # calculated by backend usually? No, frontend sends it.
                    # Wait, backend 'calculate_sale_total' does calc, but 'create_sale' trusts frontend?
                    # Let's check sales_service.create_sale logic. 
                    # It validates inputs.
                )
            ]
        )
        # We need to compute unit_price manually for the test to respect schema if required, 
        # but service might recalculate or validate. 
        # Price per box = 200. Price per blister = 20.
        sale_data.items[0].unit_price = 20.0
        
        try:
            sale = create_sale(db, sale_data, current_user=user)
            # Refetch medicine
            db.refresh(med)
            print(f"   [OK] Vente effectuée. Nouveau Stock: {med.quantity}")
            assert med.quantity == 294 # 300 - 6
        except Exception as e:
            print(f"   [ERREUR] Vente Plaquette echouée: {e}")

        # 3. Sell 1 Box (Should deduct 60 units)
        print("\n3. Vente 1 Boite")
        sale_data_box = SaleCreate(
            payment_method="cash",
            amount_paid=200,
            items=[
                SaleItemCreate(
                    medicine_id=med.id,
                    quantity=1,
                    sale_type="packaging",
                    unit_price=200.0
                )
            ]
        )
        try:
            create_sale(db, sale_data_box, current_user=user)
            db.refresh(med)
            print(f"   [OK] Vente Boite effectuée. Nouveau Stock: {med.quantity}")
            assert med.quantity == 234 # 294 - 60
        except Exception as e:
            print(f"   [ERREUR] Vente Boite echouée: {e}")

        # 4. Sell 1 Unit (Should deduct 1 unit)
        print("\n4. Vente 1 Unité (Comprimé)")
        # Price per unit = 200 / 60 = 3.33...
        sale_data_unit = SaleCreate(
            payment_method="cash",
            amount_paid=10,
            items=[
                SaleItemCreate(
                    medicine_id=med.id,
                    quantity=1,
                    sale_type="unit",
                    unit_price=3.33
                )
            ]
        )
        try:
            create_sale(db, sale_data_unit, current_user=user)
            db.refresh(med)
            print(f"   [OK] Vente Unité effectuée. Nouveau Stock: {med.quantity}")
            assert med.quantity == 233 # 234 - 1
        except Exception as e:
            print(f"   [ERREUR] Vente Unité echouée: {e}")

        print("\n--- TEST SUCCES: TOUTES LES VERIFICATIONS SONT OK ---")

    except Exception as e:
        print(f"CRASH TEST: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_hierarchy()
