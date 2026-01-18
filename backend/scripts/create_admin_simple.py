"""
Script simple pour créer un utilisateur admin.
Usage: python create_admin_simple.py
"""

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password


def create_admin_simple():
    """Créer un admin avec credentials par défaut."""
    
    # Credentials par défaut
    username = "admin"
    password = "admin123"
    
    print("=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60)
    print(f"\nUsername: {username}")
    print(f"Password: {password}")
    print("\n" + "=" * 60)
    
    db = SessionLocal()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(User.username == username).first()
        
        if existing_user:
            print(f"\n[INFO] User '{username}' already exists!")
            print(f"  ID: {existing_user.id}")
            print(f"  Role: {existing_user.role.value}")
            print(f"  Active: {existing_user.is_active}")
            return
        
        # Créer l'admin
        print("\n[*] Creating admin user...")
        
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
        print("[SUCCESS] Admin created successfully!")
        print("=" * 60)
        print(f"Username: {admin_user.username}")
        print(f"Password: {password}")
        print(f"Role: {admin_user.role.value}")
        print(f"ID: {admin_user.id}")
        print("=" * 60)
        print("\nYou can now login with these credentials:")
        print("  - Start server: uvicorn main:app --reload")
        print("  - Open docs: http://localhost:8000/docs")
        print("  - Login with admin/admin123")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Failed to create admin: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_simple()
