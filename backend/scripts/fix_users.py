from app.database import init_local_db, get_local_db
from app.models.user import User
from app.models.sales import Sale

db = next(get_local_db())

print("--- USERS BEFORE ---")
users = db.query(User).all()
for u in users:
    print(f"ID: {u.id}, Name: {u.username}, Role: {u.role}")

targets = ["test-admin", "test-super", "test_admin", "test_super"]

for name in targets:
    user = db.query(User).filter(User.username == name).first()
    if user:
        print(f"\nDeleting {user.username} (ID: {user.id})...")
        # Delete related sales first (to be safe/clean)
        sales = db.query(Sale).filter(Sale.user_id == user.id).all()
        if sales:
            print(f"  Deleting {len(sales)} related sales...")
            for s in sales:
                db.delete(s)
            
        db.delete(user)
        db.commit()
        print("  Success.")
    else:
        pass

print("\n--- USERS AFTER ---")
users = db.query(User).all()
for u in users:
    print(f"ID: {u.id}, Name: {u.username}, Role: {u.role}")
