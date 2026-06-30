"""Quick test script to debug checkout 500 error."""
import sys
import traceback

# Setup path
sys.path.insert(0, '.')

from app.database import get_local_db
from app.models.medicine import Medicine
from app.models.batch import Batch
from app.services import pos_service
from app.schemas.pos import POSCheckoutRequest, CheckoutItem, BatchAllocation

db = next(get_local_db())

# Step 1: Check medicine and batch
med = db.query(Medicine).first()
print(f"Medicine: {med.name}, qty={med.quantity}")

batch = db.query(Batch).filter(
    Batch.medicine_id == med.id,
    Batch.is_active == True,
    Batch.quantity > 0
).first()

if not batch:
    print("ERROR: No active batch found!")
    sys.exit(1)

print(f"Batch: id={batch.id}, qty={batch.quantity}, exp={batch.expiration_date}")

# Step 2: Try cart_add
try:
    from app.schemas.pos import CartAddRequest
    result = pos_service.cart_add(db, CartAddRequest(medicine_id=med.id, quantity=1))
    print(f"Cart add OK: allocations={len(result.allocations)}")
    alloc = result.allocations[0]
    print(f"  Allocation: batch_id={alloc.batch_id}, qty={alloc.quantity}")
except Exception as e:
    print(f"Cart add FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Try checkout
try:
    checkout_data = POSCheckoutRequest(
        items=[
            CheckoutItem(
                medicine_id=med.id,
                allocations=[
                    BatchAllocation(
                        batch_id=alloc.batch_id,
                        batch_number=alloc.batch_number,
                        expiration_date=alloc.expiration_date,
                        quantity=1
                    )
                ],
                quantity=1,
                unit_price=med.price_sell
            )
        ],
        payment_method="cash"
    )
    print(f"Checkout request created OK")
    
    sale = pos_service.checkout(db, user_id=1, checkout_data=checkout_data)
    print(f"Checkout OK! Sale: id={sale.id}, code={sale.code}")
    
    # Step 4: Try enrich
    enriched = pos_service.enrich_pos_sale_response(sale)
    print(f"Enrich OK! Keys: {list(enriched.keys())}")
    
except Exception as e:
    print(f"CHECKOUT FAILED: {type(e).__name__}: {e}")
    traceback.print_exc()
