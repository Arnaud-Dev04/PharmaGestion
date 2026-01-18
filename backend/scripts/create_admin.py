"""
Script to create initial admin user.
Run this script once to bootstrap the system with an admin account.
"""

import getpass
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password


def create_admin_user():
    """Create initial admin user."""
    print("=" * 60)
    print("CREATE INITIAL ADMIN USER")
    print("=" * 60)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if any users exist
        user_count = db.query(User).count()
        
        if user_count > 0:
            print(f"\n[INFO] Database already has {user_count} user(s).")
            response = input("Do you want to create another admin user? (y/n): ")
            if response.lower() != 'y':
                print("[CANCELLED] No user created.")
                return
        
        # Get admin credentials
        print("\nEnter admin credentials:")
        username = input("Username (default: admin): ").strip() or "admin"
        
        # Check if username exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"\n[ERROR] Username '{username}' already exists!")
            return
        
        # Get password (hidden input)
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 4:
                print("[ERROR] Password must be at least 4 characters long.")
                continue
            
            password_confirm = getpass.getpass("Confirm password: ")
            if password != password_confirm:
                print("[ERROR] Passwords do not match. Try again.")
                continue
            
            break
        
        # Create admin user
        admin_user = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Admin user created successfully!")
        print("=" * 60)
        print(f"Username: {admin_user.username}")
        print(f"Role: {admin_user.role.value}")
        print(f"Active: {admin_user.is_active}")
        print(f"ID: {admin_user.id}")
        print("=" * 60)
        print("\nYou can now login using these credentials.")
        print("Start the server: uvicorn main:app --reload")
        print("API Docs: http://localhost:8000/docs")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Failed to create admin user: {e}")
    
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
