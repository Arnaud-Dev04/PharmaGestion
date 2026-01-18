
import sys
import os
from datetime import datetime

# Add backend directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.models.medicine import Medicine, MedicineFamily, MedicineType
from app.models.sales import Sale, SaleItem, SaleType
from app.schemas.sales import SaleCreate, SaleItemCreate, PaymentMethod
from app.services import sales_service, medicine_service

def test_sale_flow():
    db = SessionLocal()
    try:
        print("1. Setup: Ensuring Admin user exists...")
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("Admin not found! Please run reset_admin.py first.")
            return

        print("2. Setup: Creating/Getting a Test Medicine...")
        # Check for existing test medicine
        med = db.query(Medicine).filter(Medicine.code == "TEST-DOLIPRANE").first()
        if not med:
            med = Medicine(
                name="Doliprane Test 1000mg",
                code="TEST-DOLIPRANE",
                quantity=100.0, # 100 boxes
                price_buy=1000.0,
                price_sell=1500.0,
                expiry_date=datetime(2026, 1, 1),
                min_stock_alert=10,
                dosage_form="Comprimé",
                packaging="Boîte",
                units_per_packaging=8.0, # 8 pills per box
                family_id=None,
                type_id=None
            )
            db.add(med)
            db.commit()
            db.refresh(med)
            print(f"Created medicine: {med.name} (ID: {med.id}, Stock: {med.quantity})")
        else:
            # Reset stock for test consistency
            med.quantity = 100.0
            db.commit()
            print(f"Using existing medicine: {med.name} (ID: {med.id}, Stock Reset to: {med.quantity})")

        print("\n3. Testing: Creating a Sale Payload...")
        # Scenario: Sell 1 Box AND 4 Units (0.5 Box)
        # Total Quantity to deduct = 1.5 boxes
        # Total Price = 1500 + (1500/8 * 4) = 1500 + 750 = 2250
        
        item_box = SaleItemCreate(
            medicine_id=med.id,
            quantity=1,
            sale_type="packaging",
            discount_percent=0.0
        )
        
        item_pills = SaleItemCreate(
            medicine_id=med.id,
            quantity=4, # 4 pills
            sale_type="unit",
            discount_percent=10.0 # 10% discount on pills
        )
        
        sale_data = SaleCreate(
            items=[item_box, item_pills],
            payment_method="cash", # Use string "cash" to match modified model
            discount_percent=0.0,
            customer_phone="79000000", # Test Customer Creation
            customer_first_name="Jean",
            customer_last_name="Testeur"
        )
        
        print("4. Execution: Calling sales_service.create_sale()...")
        sale = sales_service.create_sale(db, admin.id, sale_data)
        
        print("\n5. Verification: Sale Created Successfully!")
        print(f"   Sale ID: {sale.id}")
        print(f"   Code: {sale.code}")
        print(f"   Total Amount: {sale.total_amount} FBu")
        
        # Verify Price
        # Box: 1500
        # Pills: 4 * (1500/8) = 750. Discount 10% -> 675.
        # Total Expected: 2175
        print(f"   Expected Total: 2175.0 FBu. Actual: {sale.total_amount} FBu")
        
        # Verify Stock
        db.refresh(med)
        print(f"   New Stock: {med.quantity} (Expected: 100 - 1 - 0.5 = 98.5)")
        
        if abs(med.quantity - 98.5) < 0.001:
            print("   [SUCCESS] Stock updated correctly.")
        else:
            print("   [FAILURE] Stock update incorrect.")

        if sale.total_amount == 2175.0:
            print("   [SUCCESS] Price calculation correct.")
        else:
            print("   [FAILURE] Price calculation incorrect.")

    except Exception as e:
        print(f"\n[FATAL ERROR] Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_sale_flow()
