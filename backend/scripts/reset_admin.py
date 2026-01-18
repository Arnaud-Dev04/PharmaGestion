
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

def reset():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            print("Found admin user.")
            # Reset password using the app's hashing function
            user.password_hash = hash_password("admin123")
            user.role = "admin" # Ensure role is correct lowercase
            user.is_active = True
            db.commit()
            print("Password reset to 'admin123' and role set to 'admin'.")
            
        # Reset Pharmacist
        user_pharm = db.query(User).filter(User.username == "pharmacist").first()
        if user_pharm:
            print("Found pharmacist user.")
            user_pharm.password_hash = hash_password("pharmacist123")
            user_pharm.role = "pharmacist" 
            user_pharm.is_active = True
            db.commit()
            print("Password reset to 'pharmacist123'.")
        else:
            print("Pharmacist user not found. Creating...")
            user_pharm = User(
                username="pharmacist",
                password_hash=hash_password("pharmacist123"),
                role="pharmacist",
                is_active=True
            )
            db.add(user_pharm)
            db.commit()
            print("Pharmacist user created.")
    except Exception as e:
        print(f"Error details: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset()
